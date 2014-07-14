---
layout: post
title: "Extending Django's QuerySet to return approximate COUNTs"
date: 2014-07-13 16:19:16 +0100
comments: true
categories:
---

I was looking through the
[MySQL slow_log](http://dev.mysql.com/doc/refman/5.5/en/slow-query-log.html) for
YPlan and discovered that there were a lot of `SELECT COUNT(*)` queries going
on, which take a long time and cause a full table scan. These were coming from
the [Django admin](https://docs.djangoproject.com/en/1.6/ref/contrib/admin/),
which displays the total count on **every page**.


"Why is `SELECT COUNT(*)` such a slow query?" you might think, "surely MySQL
could just keep a number in the table metadata and update it on INSERT/DELETE."
Aha! You are *totally* right - for MyISAM tables&mdash;but Innodb (the only
storage engine that is a sane choice for your app's precious data) provides you
proper transactional support at the cost of such a metadata value. In the world
of transactions, you have to be able to isolate one transaction from another,
hence you can no longer store a single 'accurate' `COUNT(*)` value per table,
and instead, every time it is requested, a table scan ensues.


I'm not the only one with this problem, so I googled and found
[this great blog post](http://www.tablix.org/~avian/blog/archives/2011/07/django_admin_with_large_tables/)
by 'Avian' in 2011. This post is my update on that for newer Django versions
with some extra knowledge I've gained reading up on MySQL.


Here's my take:


```python
class ApproxCountQuerySet(QuerySet):
    """
    Avoid doing COUNT(*) on big tables because it's a full table scan; instead,
    if the table looks big, just extract an approximate count via MySQL's
    EXPLAIN statement.
    """

    def count(self):
        query = self.query
        if (
            not query.where and
            query.high_mark is None and
            query.low_mark == 0 and
            not query.select and
            not query.group_by and
            not query.having and
            not query.distinct
        ):
            cursor = connections[self.db].cursor()
            cursor.execute(
                "/*ApproxCountQuerySet*/ EXPLAIN SELECT COUNT(*) FROM %s",
                (self.model._meta.db_table,)
            )
            n = cursor.fetchone()[8]
            if n >= 1000:
                return n
        else:
            return super(ApproxCountQuerySet, self).count()
```


A few quick things to point out:


* If the approximate count is not larger than 1000, the exact count will be
  obtained anyway via the super call.

* We're using [`EXPLAIN`](http://dev.mysql.com/doc/refman/5.5/en/explain.html)
  to get MySQL to return the approximate count. This returns a tabular analysis
  of the query execution plan - including an estimate of the number of rows
  that will be searched (it may be quite a bit off, I've seen nearly 50% in the
  wild). More on `EXPLAIN` below.

* The query has a comment in it - this is good practice for any custom SQL as
  it makes the `slow_log` and other query digests easy to link back to the part
  in the app that made the query.

* The exact count will still be obtained with the super call if the query is
  any more complex than `MyModel.objects.count()`. This code is just the first
  stage of optimization to remove the worst `SELECT COUNT(*)` queries - most
  other queries should be able to narrow


Why use `EXPLAIN` and not `SHOW TABLE STATUS` as in Avian's blog? Because
`EXPLAIN` can be used to extract more detailed counts using index reads as well
- an extension left for the reader (i.e. I haven't needed this yet). But here's
an example MySQL session showing that `EXPLAIN`ing a simple WHERE clause on an
indexed column can extract an approximate count too. It's only 100% accurate in this
case because this table is small (from the example
[sakila database](http://dev.mysql.com/doc/sakila/en/)):

```sql
mysql> SHOW CREATE TABLE sakila.city\G
*************************** 1. row ***************************
       Table: city
Create Table: CREATE TABLE `city` (
  `city_id` smallint(5) unsigned NOT NULL AUTO_INCREMENT,
  `city` varchar(50) NOT NULL,
  `country_id` smallint(5) unsigned NOT NULL,
  `last_update` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`city_id`),
  KEY `idx_fk_country_id` (`country_id`),
  CONSTRAINT `fk_city_country` FOREIGN KEY (`country_id`) REFERENCES `country` (`country_id`) ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=601 DEFAULT CHARSET=utf8
1 row in set (0.00 sec)

mysql> SELECT COUNT(*) FROM sakila.city WHERE country_id = 23\G
*************************** 1. row ***************************
COUNT(*): 53
1 row in set (0.00 sec)

mysql> EXPLAIN SELECT COUNT(*) FROM sakila.city WHERE country_id = 23\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: city
         type: ref
possible_keys: idx_fk_country_id
          key: idx_fk_country_id
      key_len: 2
          ref: const
         rows: 53
        Extra: Using index
1 row in set (0.00 sec)
```


My second step in fixing this was to make sure this only applied in the admin
area of the app, and doesn't affect any business logic which might be relying
on exact counts. This is easy enough if you're using a custom admin base class
for every `Admin` class in your app:


```python
class MySuperDuperAdmin(Admin):
    def queryset(self, request):
        qs = super(MySuperDuperAdmin, self).queryset(request)
        qs = qs._clone(klass=ApproxCountQuerySet)
        return qs
```


The final issue I fixed was cosmetic, and might not apply for you. The admin
pages will report 'N total', but this may be misleading if someone in your
organization is using this count for any kind of analytics. Therefore, I added
a quick hack to make sure the word 'Approximately' is used next to this count,
without changing the templates (especially tricky if this is a small table
where the exact count is still returned).

Replacing lines at the end of `ApproxCountQuerySet.count`:

```python
            if n >= 1000:
                return ApproximateInt(n)
        else:
            return super(ApproxCountQuerySet, self).count()


class ApproximateInt(int):
    def __str__(self):
        return 'Approximately ' + super(ApproximateInt, self).__str__()
```
