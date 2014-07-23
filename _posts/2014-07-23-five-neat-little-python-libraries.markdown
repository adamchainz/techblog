---
layout: post
title: "Five Neat Little Python Libraries"
date: 2014-07-16 21:25:16 +0100
categories:
---

Here are some great little Python libraries that have made my life (well, at
least the coding part) a little bit nicer and easier. They mostly add neat
syntax and a few things that you always wanted to do, but never knew.


## 1. Unipath

**What?**

It's an “object-oriented alternative to os/os.path/shutil”.

**How?**

From the README:

```pycon
>>> p = Path("/usr/lib/python2.5/gopherlib.py")
Path("/usr/lib/python2.5")
>>> p.name
Path("gopherlib.py")
>>> p.ext
'.py'
```

Basically, if you're fiddling around a lot with `os.path` and other
file-manipulation functions, you're missing out on this much nicer, arguably
more pythonic, way of doing things.

**Where?**

* `pip install Unipath`
* [Documentation on Github Readme](https://github.com/mikeorr/Unipath#readme)
* [Source on Github mikeorr/Unipath](https://github.com/mikeorr/Unipath)


## 2. sh

**What?**

Similar to `Unipath`, but for replacing `subprocess`. Call any program as if it
were a function, and get return values in a sane manner.

**How?**

Using a bit of python magic, the module lets you import any program as if it
were a function:

```pycon
>>> from sh import ls
>>> ls("-l")
total 16437
drwxrwxr-x+ 53 root  admin     1802  5 Jul 15:54 Applications
drwxr-xr-x+ 65 root  wheel     2210 25 Apr 09:24 Library
drwxr-xr-x@  2 root  wheel       68 25 Aug  2013 Network
<clipped>
```

Argument passing can also be done with keyword-args:

```pycon
>>> from sh import curl
>>> curl("https://duckduckgo.com/", silent=True).split()[:2]
[u'<!DOCTYPE', u'html>']
```

From that you might surmise that the return of any shell command is a `unicode`
object - but it's not! It's a `sh.RunningCommand` that wraps around the
result to expose the `stdout` by default, but lets you get at other attributes
easily too...

```pycon
>>> from sh import curl
>>> result = curl("https://www.duckduckgo.com/", silent=True)
>>> type(result)
sh.RunningCommand
>>> result.stderr.splitlines()[-5:]
['< Location: https://duckduckgo.com/',
 '< Expires: Wed, 16 Jul 2014 21:24:58 GMT',
 '< Cache-Control: max-age=1',
 '< ',
 '* Connection #0 to host www.duckduckgo.com left intact']
 ```

I'm sure you can see how much easier this makes subprocess interaction. Maybe
you'll find yourself forgoing bash for Python soon :)

**Where?**

* `pip install sh`
* [Documentation on Github Sphinx Pages](http://amoffat.github.io/sh/)
* [Source on Github amoffat/sh](https://github.com/amoffat/sh)


## 3. schedule

**What?**

A mini-library with easy syntax for scheduling recurring jobs and running a job
loop that executes them. For when cron isn't enough (environment issues,
logging, etc.), but anything much bigger is overkill.

**How?**

From the README:

```python
import schedule
import time

def job():
    print("I'm working...")

schedule.every(10).minutes.do(job)
schedule.every().hour.do(job)
schedule.every().day.at("10:30").do(job)
schedule.every().monday.do(job)
schedule.every().wednesday.at("13:15").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

It's inspired by a Ruby module, as you might be able to tell from the DSL
syntax (don't let anyone ever tell you again that Python can't do DSLs!). If
you do use it to replace cron, use something like
[supervisord](http://supervisord.org/) to keep your schedule program running in
case of failure.

**Where?**

* `pip install schedule`
* Readme says "(coming soon)" - but the
  [FAQ](https://github.com/dbader/schedule/blob/master/FAQ.rst#faq) explains
  nearly everything
* [Source on Github dbader/schedule](https://github.com/dbader/schedule)


## 4. Delorean

**What?**

"Time Travel Made Easy." Simplifies a lot of `datetime` interactions that
become painful when you're doing a lot of them.

**How?**

```python
>>> from delorean import Delorean
>>> Delorean()  # defaults to now, in UTC
Delorean(datetime=2014-07-16 22:04:51.206981+00:00, timezone=UTC)
>>> Delorean().date
datetime.date(2014, 7, 16)
>>> Delorean().next_tuesday().date
datetime.date(2014, 7, 22)
>>> import delorean
>>> from delorean import stops
>>> for stop in stops(freq=delorean.HOURLY, count=3):
...    print stop.datetime
...
2014-07-16 22:10:00+00:00
2014-07-16 23:10:00+00:00
2014-07-17 00:10:00+00:00
```

Delorean wraps a couple of useful date and time libraries - `pytz` and
`dateutil` - to provide this functionality. And it has an awesome name.

**Where?**

* `pip install delorean`
* [Documentation on Read the Docs](http://delorean.readthedocs.org/en/latest/)
* [Source on Github myusuf3/delorean](https://github.com/myusuf3/delorean/)


## 5. schema

**What?**

"Schema validation just got Pythonic."

**How?**

```pycon
>>> from schema import Schema, And, Use, Optional
>>> person_schema = Schema({
...     'name': str,
...     'age':  And(Use(int),
...                 lambda n: 18 <= n <= 99),
...     Optional('sex'): And(str,
...                          Use(str.lower),
...                          lambda s: s in ('male', 'female'))
... })
>>> sue = {'name': 'Sue', 'age': '28', 'sex': 'FEMALE'}
>>> sue_validated = person_schema.validate(sue)
>>> sue_validated['age']
28
>>> jim = {'name': 'jim', 'age': 22, 'sex': 'yes please'}
>>> person_schema.validate(jim)
Traceback (most recent call last):
 yada yada yada
SchemaError: <lambda>('yes please') should evaluate to True
```

Brilliant for validating API responses, user input, JSON stuffed in a database,
or whatever. Also great for unittests, where validating all the values output
by the code might be impossible, but you can at least check for their type and
existence.

**Where?**

* `pip install schema`
* [Documentation on Github Readme](https://github.com/halst/schema#schema-validation-just-got-pythonic)
* [Source on Github halst/schema](https://github.com/halst/schema)


## 6. Bonus!! django-unchained

**What??**

We've all heard of django for web app development; now there's the awesome
**Django Unchained** library to take it to the next level. You'll have to
`pip install django-unchained` to find out what it's all about.

---

...and that's the end of the presentation for today. Thanks for reading!
