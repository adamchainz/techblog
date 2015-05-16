---
layout: post
title: "Building a better DatabaseCache for Django on MySQL"
date: 2015-05-16 17:00:00 +0100
comments: true
categories:
---

I recently released version 0.1.10 of my library
**[django-mysql](https://github.com/adamchainz/django-mysql)**, for which the
main new feature was a backend for Django’s cache framework called
`MySQLCache`. This post covers some of the inspiration and improvements it has,
as well as a basic benchmark against Django’s built-in `DatabaseCache`.

**TL;DR** - it’s better than **DatabaseCache**, and if you’re using MySQL,
please try it out by following the instructions linked at the end.

## Why bother?

Django’s cache framework provides a generic API for key-value storage, and gets
used for a variety of caching tasks. It ships with multiple backends for
popular technologies, including Redis and Memcached, as well as a basic
cross-RDBMS `DatabaseCache`. The `DatabaseCache` is recommended only for
smaller environments, and has a number of race condition problems. Naturally
Redis and Memcached are more popular, being specifically designed to fit
key-value storage; or you could even say Django’s cache framework is
specifically designed to fit them.

If they work so well, why would anyone bother using `DatabaseCache`, and why
would I care about improving on it? Well, I have a few reasons:

* **Persistent data.** Memcache makes no persistence promises, with new keys
  overwriting old ones whenever necessary. Redis can run in a persistent mode,
  but is designed to be in-memory, and thus most apps tend to rely on their
  RDBMS for actually persistent data. If you have key-value cache-like data,
  but without without which your site goes down, it’s much better to keep it in
  your source-of-truth disk-backed data store along with all your user records,
  rather than an ephemeral memory store.

  What kind of persistent data am I talking about? At YPlan we are using the
  rather excellent [Whoosh](https://pythonhosted.org/Whoosh/quickstart.html) to
  power our search feature, which requires a few MB of files on disk. We
  rebuild this regularly from the database in a **Celery** task, store this in
  a `MySQLCache` key, and the webservers pull it via cron. If we were putting
  this in Memcached and the key was bumped before all the webservers pulled it,
  they would start serving out-of-date search results (or none at all). The
  persistence demand is greater than plain old caching.

  Another example would be counters. Whilst Memcached counters may be mostly
  reliable and useful for things like rate-limiting, if a key is ever bumped,
  you could lose count. If you are in advertising this could be a particularly
  costly loss of clicks!

* **Large[r] data.** Memcache has a hard upper limit of 1MB for a value, for
  which the recommended solution is to compress and split your values - but
  then you have to deal with lost keys. Redis has a limit of 512MB, and MySQL
  can reach 1GB.

* **Fewer moving pieces.** If you can get away with just a database server, and
  not a database server *and* a memcached server, it’s easier to build and
  maintain your system. Adding more servers and libraries always increases the
  complexity of your system, and the number of potential problems.

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
  several GBs of per-customer data that our recommendation system produces with
  great success.

## Development

When we first set up the Whoosh storage in cache, we used ``DatabaseCache``
since we knew we wanted the persistence. Unfortunately when I read the source
I realized it wouldn’t be very efficient or fast, due to its design which
caters to every database backend.

I created `MySQLCache` to correct as many problems as I could see for MySQL.
My full list of improvements includes:

* **Using ``BLOB`` for value storage**

  `DatabaseCache` uses a `TEXT` column with base64 encoding - I guess because
  not every RDBMS has a binary data type. Unfortunately this increases the size
  of every value by 33% owing to the unused bits, wasting network packets and
  disk space. `MySQLCache` uses MySQL’s binary data type `BLOB` to avoid wasted
  bits.

* **`SELECT COUNT(*)` on cull**

  On every set() operation, `DatabaseCache` does a cull check to see if needs
  to remove any keys to remain under its specified max size. Unfortunately the
  only way it can do this is to run `SELECT COUNT(*)`, which will cause a table
  scan on most database backends, especially on MySQL+InnoDB, as I’ve [written
  about being slow before]
  ({% post_url 2014-07-16-extending-djangos-queryset-to-return-approximate-counts %}).
  With `MySQLCache` the cull-check behaviour becomes probabilistic, by default
  performing the `cull()` check on only 1% of `set()` operations - making 99%
  of your write operations faster at the sacrifice of going somewhat over the
  specified maximum number of items. You can also disable the cull-on-set
  behaviour by setting the probability to 0 and perform it yourself in a
  background task so it never affects your end users.

* **Making use of MySQL’s upsert syntax.**

  This is an operation missing from many RDBMS’s, which included PostgreSQL up
  until a couple of weeks ago. An upsert allows a single statement to perform
  either an `UPDATE` of existing data or an `INSERT` to create new data,
  race-condition free - for a longer explanation, see the [PostgreSQL wiki
  page]
  (https://wiki.postgresql.org/wiki/UPSERT#UPSERT_as_implemented_in_practice).
  MySQL’s has had the `INSERT ON DUPLICATE KEY UPDATE` statement for some time,
  allowiing `MySQLCache` to implement the `add()`, `set()`, and `incr()`
  operations each with single queries. This avoids the race conditions that
  `DatabaseCache` is open to - the kind of unexpected behaviour that crops up
  only when you have enough visitors to your site acting on the same thing
  concurrently.

* **The `*_many` operations all use single queries, rather than one per key.**

  It seems that `DatabaseCache` avoids creating multi-row queries because the
  syntax varies more by RDBMS. It didn’t take much to support it in MySQL,
  though users have to be aware of the protocol packet size limit in MySQL -
  `max_allowed_packet` - which can easily be hit when setting or getting
  multiple large values.

* **Automatic compression with `zlib`.**

  A feature copied from `pylibmc`, which is a fast memcached client library.
  Even relatively values of a few KB benefit from the smaller network and
  storage size. `MySQLCache` also provides capacity for tuning the `zlib`
  compression level, or adding custom compression schemes.

## Benchmark

I’ve created and run a simple benchmark, [available on GitHub]
(https://github.com/adamchainz/django-mysql-benchmark-cache). It tests the
configured backends with 1000 repeats of operations such as `set()`,
`set_many()`, and `get()` with randomly sized values. It’s not a perfect load
simulator but it gives an idea of which can be faster. It runs `MySQLCache`
with `MySQL`’s two most popular storage engines - the non-transactional
`MyISAM` and the default, transactional `InnoDB`.

I ran it locally with MariaDB (MySQL fork) version 10.0.17 and memcached
version 1.4.22 on my Macbook Pro. The results are, in seconds per
1000-operation benchmark:

| Cache Alias         | set benchmark | set_many benchmark | get benchmark | get_many benchmark | delete benchmark | incr benchmark |
|---------------------|---------------|--------------------|---------------|--------------------|------------------|----------------|
| `DatabaseCache`     |         1.023 |             42.193 |         0.237 |              8.621 |            6.216 |          1.084 |
| `MySQLCache_MyISAM` |         0.329 |              6.080 |         0.311 |              1.949 |            0.639 |          0.195 |
| `MySQLCache_Innodb` |         0.629 |              6.392 |         0.213 |              1.168 |            0.619 |          0.344 |
| `MemcachedCache`    |         0.102 |              1.460 |         0.089 |              1.308 |            1.068 |          0.082 |
| `PyLibMCCache`      |         0.075 |              2.218 |         0.061 |              0.488 |            1.725 |          0.057 |


MySQLCache clearly isn’t as fast as Memcached, but it *is* writing to disk.
Thankfully it is quite a bit faster than `DatabaseCache`, especially on the
`*_many` operations. I suspect the performance gap gets much bigger at tens of
thousands or hundreds of thousands of keys, owing to the `SELECT COUNT(*)`
behaviour - I just didn’t have the patience to keep running the benchmark.

As for the storage engines, `MyISAM` is faster than `InnoDB` for `set()` but
slower for `get()` - not a great trade-off for most applications of caching
where reads are much more common. Also its non-transactionality can lead to
misunderstanding when everyone only knows `InnoDB`.

I would have liked to benchmark the `MEMORY` storage engine, which avoids
writing to disk, but it can’t store `BLOB` columns (large binary data). There
is [a patch in the MySQL fork **Percona Server**]
(https://www.percona.com/doc/percona-server/5.5/flexibility/improved_memory_engine.html)
to enable this, but I didn’t have time to try it and I guess most project can’t
switch MySQL version so easily. Of course, as stated, the permanence may be the
very reason you are using a database cache backend, so any potential speed
improvements may be moot :)

## Possible Extensions

MySQL 5.6 ships with a `memcached` interface plugin direct to `InnoDB`,
avoiding protocol overhead and SQL parsing. I haven’t tried it yet, but it can
probably be used with Django’s `PyLibMCCache` or `MemcachedCache` backends
directly, and it would circumvent much of the overhead that `MySQLCache` also
has, whilst remaining a transactional on-disk table. This is an interesting
alternative, though it does require a bit more setup.

In `MySQLCache` I’ve also considered some of the other operations an
in-database cache can efficiently support beyond Django’s basic API. For
example, since keys are stored in order in BTree indexes, it makes it quite
efficient to search for keys with a given prefix.

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
