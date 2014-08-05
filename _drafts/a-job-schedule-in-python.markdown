---
layout: post
title: A job schedule in Python
date: 2014-08-05 21:15:16 +0100
comments: true
categories:
---

I was recently tasked with keeping the various repeating jobs running for our
data scientists at YPlan. They have a number of relatively small nightly tasks
to be run, such as creating summary tables of the day's various activity logs,
or pulling in data from third party services.


Of course, the jobs were already running in a scattered way, and it was my task
to mostly bring them together under one consistent EC2 instance, configured
with Ansible. They were mostly being run by **cron**, but during the re-build,
I realized it just wasn't up to the task for even my handful of jobs.


CRON? Why? It's a staple of the unix ecosystem, relied upon for decades to keep
processes running nightly. What's wrong with it?


Unfortunately, it's just *too* simple. Its syntax for _when_ jobs run is
esoteric in the least (quick - what does `*/5 * 2 * *` mean again?), and it's
famously hard to get the environment to be the way you want it - that script
that runs from bash will probably take a few tries to get working via cron. And
on top of that, every job definition will need some log redirection, e.g. `2>&1
>>/var/log/something`, to get working, or else run it with a wrapper script
that does all that for you. By the time I'd thought it through, it was a
headache.


I searched for existing tools, and a few caught my eye:


* [**Crabd**] [1] - a wrapper around your cron jobs that also provides a
  consistent environment and logging, plus a dashboard that reports successful
  runs and failures. Unfortunately the installation instructions were too hard
  to follow, especially in Ansible code, so I never got around to booting it.

* [**Azkaban**] [2] - created at LinkedIn and designed for Hadoop jobs, this
  looked good as it offered a dashboard and execution history. Unfortunately it
  was even harder to install, and even configure - the only documented way is
  to upload a zipfile of job descriptions via the web interface, which makes
  them too hard to track in source control.

* Various other things that turned up when googling 'cron monitor' etc.


In the end though, I stumbled on the simple [**schedule**] [3] library (I
covered it better in my [last python post] [4]) and realized that it would do
everything I wanted, and no more. I could build something that it would be easy
to use to define jobs, track them in code, and rebuild at any time. So I typed
up a quick `jobs.py`:

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
tied into the existing code in the repository, for example the `logging`
configuration.

Of course, an infinite loop with sleeping is great, but how do you get it
started? And what if a job threw an exception, how would you restart it? This
is where I needed another tool that I've been using a long time -
[**Supervisord**] [5].


A quick supervisor conf (templated by Ansible) would do all I needed - keep
the `jobs.py` process running no matter what, and capture all its output to a
log file:

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


Of course, there are a few extensions - setting up logstash so that logs get
shipped properly, and also logging errors to our [**Sentry**] [6] server so
that failures are noticed quickly. It shouldn't actually be too hard to get
there with the ability to add in arbitrary Python code though!



[1]: https://github.com/grahambell/crab
[2]: http://azkaban.github.io/
[3]: https://github.com/dbader/schedule
[4]: {% post_url 2014-07-23-five-neat-little-python-libraries %}
[5]: http://supervisord.org/
[6]: http://getsentry.com/
