---
layout: post
title: "Building a better DatabaseCache for Django on MySQL"
date: 2015-05-17 11:30:00 +0100
comments: true
categories: [django, mysql]
---

![Figure 1 - MySQLCache in the flesh]
({{ site.baseurl }}/assets/2015-05-17-building-mysqlcache.jpg)

I recently released version 0.1.10 of my library
**[django-mysql](https://github.com/adamchainz/django-mysql)**, for which the
main new feature was a backend for Django’s cache framework called
`MySQLCache`. This post covers some of the inspiration and improvements it has,
as well as a basic benchmark against Django’s built-in `DatabaseCache`.

**TL;DR** - it’s better than **DatabaseCache**, and if you’re using MySQL,
please try it out by following the instructions linked at the end.

## Why bother?

Django’s cache framework provides a generic API for key-value storage, and gets
used for a variety of caching tasks in applications. It ships with multiple
backends for popular technologies, including Redis and Memcached, as well as a
basic cross-RDBMS `DatabaseCache`. The `DatabaseCache` is recommended only for
smaller environments, and due to its supporting every RDBMS that Django does,
it is not optimized for speed. Redis and Memcached are the most popular cache
technologies to use, being specifically designed to do key-value storage; you
could even say Django’s cache framework is specifically designed to fit them.

If they work so well, why would anyone bother using `DatabaseCache`, and why
would I care about improving on it? Well, I have a few reasons:

* **Fewer moving parts**
  <br>
  If you can get away with just a database server, and not a database server
  *and* a memcached server/cluster, it’s easier to build and maintain your
  system. Adding more servers and libraries always increases the complexity of
  your system, and the number of potential problems.

* **Persistent data**
  <br>
  Memcache makes no persistence promises, with new keys overwriting old ones
  whenever necessary. Redis can run in a persistent mode, but is designed to be
  in-memory, and thus most apps tend to rely on their RDBMS for actually
  persistent data. If you have key-value data which your site relies on, it’s
  much better to keep it in a data store designed for durability and backed by
  disk than in an ephemeral memcached node.
  <br>
  <br>
  What kind of persistent data am I talking about? At YPlan we are using the
  rather excellent [Whoosh](https://pythonhosted.org/Whoosh/quickstart.html) to
  power our search feature, which uses a search index consisting of a few MB of
  files. We rebuild this regularly from the database in a **Celery** task, and
  have to store it somewhere for the webservers to pull it from. Memcached is
  too ephemeral and a filestore like S3 is just another moving part to worry
  about; by storing it in a `MySQLCache` table, we have the best of both.
  <br>
  <br>
  Another example would be counters. Whilst Memcached counters may be mostly
  reliable and useful for things like rate-limiting, when a node goes offline
  or a key gets bumped, you lose count. If you are in advertising this could be
  a particularly costly loss of clicks!

* **Large[r] data**
  <br>
  Memcache has a hard upper limit of 1MB for a value, for which the recommended
  solution is to compress and split your values - but then you have to deal
  with lost keys more often. 1MB is just a bit too small for our search index,
  even after compression. By contrast, Redis has a limit of 512MB, and MySQL
  can reach 1GB.


## MySQL Inspiration

I’ve also seen a few success stories for using MySQL as a key-value store:

* Sunny Gleason’s Percona Live presentation [“Practical Tips for Using MySQL as
  a Scalable Key-Value Store”](https://www.percona.com/live/mysql-conference-2013/sessions/practical-tips-using-mysql-scalable-key-value-store)
  walks through implementing every possible feature you could want, based on
  real-life experience of avoiding adding Memcached, Redis, Riak servers to
  systems.

* [“How FriendFeed uses MySQL to store schema-less
  data”](http://backchannel.org/blog/friendfeed-schemaless-mysql) covers a
  social network storing data no-relationally in MySQL.

* And at YPlan, using raw SQL, we’ve been using a key-value table for recording
  several GBs of per-customer data that our recommendation system produces,
  with great success.

## Development

When we first set up the Whoosh storage in cache, we used ``DatabaseCache``
since we knew we wanted the persistence. Unfortunately when I read the source
I realized it wouldn’t be very efficient or fast, due to its design which
caters to every database backend.

I created `MySQLCache` to correct as many problems as I could see by using
MySQL-specific syntax and features. My full list of improvements includes:

* **Using ``BLOB`` for value storage**
  <br>
  `DatabaseCache` uses a `TEXT` column with base64 encoding - I guess because
  not every RDBMS has a binary data type. Unfortunately this increases the size
  of every value by 33% owing to the unused bits, wasting network packets and
  disk space. `MySQLCache` uses MySQL’s binary data type `BLOB` to avoid wasted
  bits.

* **`SELECT COUNT(*)` on cull**
  <br>
  On every `set()` operation, `DatabaseCache` does a cull check to see if needs
  to remove any keys to remain under its specified max size. Unfortunately the
  only way it can do this is to run `SELECT COUNT(*)`, which will cause a table
  scan on most database backends, especially on MySQL+InnoDB, as I’ve [written
  about being slow before]
  ({% post_url 2014-07-16-extending-djangos-queryset-to-return-approximate-counts %}).
  <br>
  <br>
  With `MySQLCache` the cull-check behaviour becomes probabilistic, by default
  performing the `cull()` check on only 1% of `set()` operations - making 99%
  of your write operations faster at the sacrifice of going a bit over the
  specified maximum number of items. You can also disable the cull-on-set
  behaviour altogether by setting the probability to 0 and perform it yourself
  in a background task so it never affects your end users.

* **Making use of MySQL’s upsert syntax.**
  <br>
  This is an operation missing from many RDBMS’s, which included PostgreSQL up
  until a couple of weeks ago. An upsert allows a single statement to perform
  either an `UPDATE` of existing data or an `INSERT` to create new data,
  race-condition free - for a longer explanation, see the detailed [PostgreSQL
  wiki page]
  (https://wiki.postgresql.org/wiki/UPSERT#UPSERT_as_implemented_in_practice).
  <br>
  <br>
  MySQL has had the `INSERT .. ON DUPLICATE KEY UPDATE` statement for upserts
  for some time, which `MySQLCache` uses to implement the `add()`, `set()`, and
  `incr()` operations each with single queries. This avoids the race conditions
  that `DatabaseCache` is open to - the kind of behaviour that only crops up
  when your start-up actually gets popular and has many concurrent visitors.

* **The `*_many` operations all use single queries**
  <br>
  `DatabaseCache` avoids creating multi-row queries because the syntax varies
  more by RDBMS, and instead when you call the `set_many()` operation, it
  simply calls `set()` repeatedly. It didn’t take much to upgrade `MySQLCache`,
  to perform the `set_many()`, `get_many()`, etc. as single queries. Users only
  need to be aware of the protocol packet size limit in MySQL,
  `max_allowed_packet`, which can easily be hit when setting or getting
  multiple large values.

* **Automatic compression with `zlib`**
  <br>
  I copied this feature from `pylibmc`, which is a fast memcached client
  library. Even relatively small values of a few KB benefit from the reduction
  in network and storage size. `MySQLCache` also provides capacity for tuning
  the `zlib` compression level, or adding custom compression schemes.

## Benchmark

I’ve created and run a simple benchmark app, [available on GitHub]
(https://github.com/adamchainz/django-mysql-benchmark-cache). It tests the
configured backends with 1000 repeats of operations such as `set()`,
`set_many()`, and `get()` with randomly sized values. It’s not a perfect load
simulator, and it doesn’t use the network, but it gives an idea of the relative
speeds achievable by the different cache backends.

It runs `MySQLCache` with `MySQL`’s two most popular storage engines - the
non-transactional `MyISAM` and the default, transactional `InnoDB`, as well
as `DatabaseCache` and Django’s two Memcached backends, `MemcachedCache` and
`PyLibMCCache`.

I ran it locally with MariaDB (a MySQL fork) version 10.0.17 and memcached
version 1.4.22 on my Macbook Pro. The results are, in seconds per
1000-operation benchmark:

| Cache Alias         | set benchmark | set_many benchmark | get benchmark | get_many benchmark | delete benchmark | incr benchmark |
|---------------------|--------------:|-------------------:|--------------:|-------------------:|-----------------:|---------------:|
| `DatabaseCache`     |         1.023 |             42.193 |         0.237 |              8.621 |            6.216 |          1.084 |
| `MySQLCache_MyISAM` |         0.329 |              6.080 |         0.311 |              1.949 |            0.639 |          0.195 |
| `MySQLCache_Innodb` |         0.629 |              6.392 |         0.213 |              1.168 |            0.619 |          0.344 |
| `MemcachedCache`    |         0.102 |              1.460 |         0.089 |              1.308 |            1.068 |          0.082 |
| `PyLibMCCache`      |         0.075 |              2.218 |         0.061 |              0.488 |            1.725 |          0.057 |


`MySQLCache` clearly isn’t as fast as `MemcachedCache`, but to be fair, it *is*
writing to disk. Thankfully it has come out quite a bit faster than
`DatabaseCache`, especially on the `*_many` operations. I suspect the
performance gap gets much bigger as the table grows to tens of thousands, or
hundreds of thousands of rows, owing to the `SELECT COUNT(*)` behaviour - I
just didn’t have the patience to keep running the benchmark.

As for the storage engines, `MyISAM` is faster than `InnoDB` for `set()` but
slower for `get()` - not a great trade-off for caching where reads are much
more common than writes. Also, if most of your application uses `InnoDB` and
you mix it with `MyISAM`’s non-transactionality, it can lead to developer
confusion as to what to expect.

I would have liked to benchmark the `MEMORY` storage engine, which would avoid
writing to disk and be a fairer comparison with Memcached, but it can’t store
`BLOB` columns (large binary data). There is [a patch in the MySQL fork
**Percona Server**]
(https://www.percona.com/doc/percona-server/5.5/flexibility/improved_memory_engine.html)
to enable this, but I didn’t have time to try it and I guess most projects
wouldn’t switch MySQL version so easily to use a cache. Of course, as stated,
the permanence may be the very reason you are using a database cache backend,
so any potential speed improvements it would give may not be worth worrying
about :)

## Future Work

MySQL 5.6 ships with a `memcached` interface plugin for `InnoDB`, avoiding
MySQL protocol overhead and SQL parsing whilst remaining persistent.
I haven’t tried it out yet, but it can probably be used directly with Django’s
`PyLibMCCache` or `MemcachedCache` backends, although with a little setup to
create the table and configure the plugin. Maybe **django-mysql** will provide
helpers for the setup process in the future, and I can benchmark it against
`MySQLCache`.

In `MySQLCache` I’ve also considered adding operations beyond Django’s basic
API that can be efficiently supported due to the rows being stored in a table.
For example, since keys are stored in order in the primary key BTree index, it
is quite efficient to search for keys with a given prefix. Additionally, with
MariaDB’s dynamic columns, hashes, lists, or sets could potentially be
supported, making it a bit like Redis!

If you think of something, [open an issue on GitHub]
(https://github.com/adamchainz/django-mysql/issues/new) and maybe send a pull
request!

## To use it...

If `MySQLCache` sounds appetising and is suitable for your project, you can
`pip install django-mysql`, follow the
[library installation instructions]
(http://django-mysql.readthedocs.org/en/latest/installation.html),
and follow the [cache setup guide]
(http://django-mysql.readthedocs.org/en/latest/cache.html) and you’ll be on
your way.

Thanks!
