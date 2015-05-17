---
layout: post
title: Time to Move on From Cron
date: 2014-08-16 18:00:00 +0100
comments: true
tags: [python]
---

![Clock clock clock clock clock clock clock clock clock clock clock clock clock]
({{ site.baseurl }}/assets/2014-08-06-portrait-of-time.jpg)


I was recently tasked with keeping the various repeating jobs running for our
data scientists at [YPlan] [13]. They have a number of nightly or weekly jobs
to be run, such as creating summary tables of the day's various activity logs,
pulling in data from third party services, and so on.


The jobs were already running on a couple of brittle hand-configured EC2
instances via cron, and it was my job to bring them all together on one
instance configured using Ansible. During the re-build, I came to the
conclusion that cron, the unix staple, just wasn't cutting it, and I'd have to
find a replacement.


But, not use cron? Why not? It has been relied upon by sysadmins for decades to
keep such jobs running to schedule. What's wrong with it?


Well, let's be honest... it's *horrible* to use. The syntax for _when_ jobs run
is esoteric (quick - what does `*/5 * 2 * *` mean again?), and it's famously
hard to match environment between your shell and it. Logging is normally a
matter of redirecting into files with `2>&1 >>myfile.log`, and often you end up
prefacing every job with a `cd` into its directory. I know when I've used cron
in the past I've ended up writing a wrapper script to do the working
directory/environment/logging stuff and then put the wrapper script around each
job in the crontab... by which time, I could've investigated and used a better
tool.


> **Exhibit A:** the internet is abound in crontab testing webtools to turn to
> in frustration when you realize you've already spent an hour debugging why
> that job didn't run when you said it should. ([CRON tester] [9])
> <img src="{{ site.baseurl }}/assets/2014-08-06-cron-tester.png" class='screenshot' alt='CRON tester'>


A job scheduler should be easily integrated with the rest of your code, and
simple enough to read when the jobs run. I'd been blessed prior to this that
the main job scheduler I'd been working with was the one built in to the
[celery task queue] [10]. I've also recently wrestled with `launchctl`, the
convoluted XML-based Mac OS X scheduler which is worse than cron.


For my data scientists though, celery would have been overkill and too much to
explain, so I set out looking for a simple job scheduler that was still better
than cron. Because most of the data science code is already in Python, finding
a library that would do it was my first idea. Through my googling, I came
across the simple [**schedule**] [3] library (as I mentioned in my [last python
post] [4]) and realized that it would do everything I wanted - and no more.
It's based upon a similarly simple **ruby library** [Clockwork] [8], which was
dreamt up by [Adam Wiggins] [11], another cron-hater.


I installed the library and within minutes had a `jobs.py` script ready to
run (here gutted to just an example job, but you get the idea):


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
configuration. The `log_job` helper I added was there because, to begin with,
most of the jobs gave no output when run.


With that all sorted, I had to think about keeping the jobs running, and
continuing should one through an exception or otherwise crash the python
interpreter. This is where I turned to another tool that I've been using for a
long time - [**Supervisord**] [5].

Supervisor is just focused around keeping processes running, according to the
specification you give it. I typed up this simple supervisor configuration
(templated by Ansible) which keeps `jobs.py` running no matter what, and
captures all its output to a log file (to be replaced by [**logstash**] [7]
soon):


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


The jobs themselves are mostly python scripts that can be run from the
command line, in which case to run them as jobs I simply import the module and
run its `main` on schedule, e.g.:


```python
schedule.every().day.at("07:00").do(log_job, database.rebuild_summary_tables.main)
```

There are some jobs implemented in **R** though - but use of the **sh** library
it is easy to run them as easily as python functions:


```python
import sys
from sh import Rscript
from configuration import sh_file_logger


def process_stats():
    Rscript('process_stats.R', _out=sh_file_logger)
```

Here, the `sh_file_logger` is a special file-like-logger-wrapper, based on
[this recipe] [12], that replaces `stdout` so the R script's output is directed
through the python logging module, keeping all the logs in the same place.


In conclusion, the data scientists are happy and so am I. Jobs are running and
logged properly, and the syntax is straightforward so it's simple for any team
member to add a new one, without having to understand any more.


Next time you're looking at scheduling a few jobs on a single machine, don't
automatically turn to cron. There are much more sensible alternatives out
there!


[1]: https://github.com/grahambell/crab
[2]: http://azkaban.github.io/
[3]: https://github.com/dbader/schedule
[4]: {% post_url 2014-07-23-five-neat-little-python-libraries %}
[5]: http://supervisord.org/
[6]: http://getsentry.com/
[7]: http://logstash.net/
[8]: https://github.com/tomykaira/clockwork
[9]: http://cron.schlitt.info/
[10]: http://www.celeryproject.org/
[11]: http://adam.herokuapp.com/past/2010/6/30/replace_cron_with_clockwork/
[12]: http://plumberjack.blogspot.co.uk/2009/09/how-to-treat-logger-like-output-stream.html
[13]: http://yplanapp.com/
