---
layout: post
title: Don't use Cron
date: 2014-08-05 21:15:16 +0100
comments: true
categories:
---

![Clock clock clock clock clock clock clock clock]
({{ site.baseurl }}/assets/2014-08-06-portrait-of-time.jpg)


I was recently tasked with keeping the various repeating jobs running for our
data scientists at YPlan. They have a number of relatively small nightly tasks
to be run, such as creating summary tables of the day's various activity logs,
pulling in data from third party services, and so on.


The jobs were already running on a couple of brittle hand-configured EC2
instances via cron, and it was my job to bring them all together on one
instance configured using Ansible. During the re-build, I came to the
conclusion that cron, that unix staple, just wasn't cutting it for me, and I'd
have to find a replacement.


Cron? It's a staple of the unix ecosystem, relied upon for decades to keep
processes running to a schedule. What's wrong with it?


It's actually horrible to use. It's far *too* simple, its syntax for _when_
jobs run is esoteric to say the least (quick - what does `*/5 * 2 * *` mean
again?), and it's famously hard to get the environment to be the way you want
it - your script running perfectly fine in bash will probably take several
attempts to get working perfectly under the cron. And on top of that, every job
definition will need log redirection or a wrapper script to get working.


What I wanted was something straightforward and easy to integrate, that
could capture all the log output to a file (to be improved later with e.g.
[**logstash**] [7]). And it had to be easy to explain to my data scientists,
whose two common languages are python (yay!) and R (ok!).


I searched for existing tools and a few caught my eye:


* [**Crabd**] [1] - a wrapper around cron jobs that provides a consistent
  environment and log capture, plus a dashboard that reports successful runs
  and failures. Unfortunately the installation instructions were too hard to
  follow (copying files from elsewhere into the repo), especially in Ansible
  code, so I never got around to booting it.

* [**Azkaban**] [2] - created at LinkedIn and designed for Hadoop jobs, this
  looked good as it offered a dashboard and execution history. Unfortunately it
  was even harder to install, and then configure - the only documented way is
  to upload a zipfile of job descriptions via the web interface, which makes
  them too hard to track in source control.

* Various other things that turned up when googling 'cron monitor' etc.


In the end though, I stumbled on the simple [**schedule**] [3] library (as
covered in my [last python post] [4]) and realized that it
would do everything I wanted, and no more. It's based upon a similarly simple
**ruby library** [Clockwork] [8].

I downloaded the library and typed up a quick `jobs.py` (here I just have an
example job, but you get the idea):


```python
#!/usr/bin/env python
import schedule

from configuration import logging  # ensures that logging module is configured

logger = logging.getLogger('jobs')

def log_job(job_func):
    logger.info("Running `{}`".format(job_func.__name__))
    job_func()


def example():
    logger.info("I'm an example job!")

schedule.every(2).seconds.do(log_job, example)


def main():
    logger.info('Starting schedule loop')
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == '__main__':
    main()
```


The simple DSL syntax that **schedule** offers was nice and clear to me, and
because it was running in a python process I had all the flexibility of being
tied into the existing code in the repository, such as the `logging`
configuration.


With that all sorted, I had to think about keeping the jobs running, and
continuing should one through an exception or otherwise crash the python
interpreter. This is where I turned to another tool that I've been using for a
long time - [**Supervisord**] [5].


A quick supervisor job conf (templated by Ansible) would do all I wanted - keep
`jobs.py` running no matter what, and capture all its output to a log file:

{% highlight ini %}
{% raw %}
[program:jobs]
directory = {{ repo_path }}
user = {{ username }}
autorestart = true
environment = PYTHONPATH={{ repo_path }}:{{ libraries_path }}
command = {{ repo_path }}jobs.py
stdout_logfile = {{ repo_path }}jobs.out.log
redirect_stderr = True
{% endraw %}
{% endhighlight %}


The jobs themselves are mostly in python as scripts that can be run from the
command line, in which case I simply import the library and run its `main` on
schedule, e.g.:


```python
schedule.every().day.at("07:00").do(log_job, reports.dailystats.send)
```

There are some jobs implemented in **R** though - but use of the **sh** library
it is easy to run them as python functions:


```python
import sys
from sh import Rscript


def do_the_thing():
    Rscript('the_thing.R', _out=sys.stdout)
```


I need to get



[1]: https://github.com/grahambell/crab
[2]: http://azkaban.github.io/
[3]: https://github.com/dbader/schedule
[4]: {% post_url 2014-07-23-five-neat-little-python-libraries %}
[5]: http://supervisord.org/
[6]: http://getsentry.com/
[7]: http://logstash.net/
[8]: https://github.com/tomykaira/clockwork
