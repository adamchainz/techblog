---
layout: post
title: "Cleaning Up Nameless EC2 Instances with Ansible"
date: 2015-04-09 22:00:00 +0100
comments: true
categories:
---

![Anonymous Instances - AAaaahaaa]
({{ site.baseurl }}/assets/2015-04-09-anonymous-instances.jpg)


I gave a talk at the recent London Ansible Meetup on how I cleared up
unexplained nameless/'anonymous' EC2 instances from our AWS account at YPlan.
This is the blog post version of that talk, so you can follow along and stop
such instances appearing on your account and sapping money!

If you know what I'm talking and just want the code, you can head direct to the
bottom where there's a link to a gist.


## The Problem

I had a problem on EC2. Blank instances were appearing on the account! They
were totally 'anonymous' - no name, no tags, no CPU/network usage (not now, not
since they were launched). Whenever I spotted them on the console, they'd
normally been running for a couple weeks; though I probably look at the console
every day, it's very hard to notice blank rows!

I investigated where they were coming from. At first I suspected AWS might just
be padding out the bill, but digging further into the Cloudtrail logs, I
discovered that they had been launched by our Jenkins continuous delivery
server.

Our Jenkins build process at YPlan is uses an Ansible playbook to launch an
instance (using the **ec2** module), provision it with the latest code and
dependencies, and then freeze it as an Amazon Machine Image (AMI). The AMI is
what then gets tested and deployed (if you're interested, it's based upon some
code from Ansible's
[immutablish-deploys repo]
(https://github.com/ansible/immutablish-deploys/blob/master/build_ami.yml)
). I looked back through the build logs to the times the anonymous instances
had been started, and found that in each case Jenkins had launched them at the
start of the normal build process, but it had been cancelled immediately
afterwards. Cancelled builds are a regular occurence, when a developer knows
that the particular build is not going to be useful since it doesn't contain
all the necessary code, and they don't want it to block the next one.

So it turns out that on EC2, launching an instance and tagging it (which is
when it gets a name, since "Name" is just another tag) are separate actions. A
launch takes around 10-20 seconds to complete, and thus if you kill the process
creating the instance (Ansible's **ec2** module) right after it has sent the
launch request, you will be left with a blank, 'anonymous' instance.

## The Solution

The solution I settled on was simple - a sweeper process to regularly delete
any such blank instances. I'll walk you through creating that now.

Firstly, I on my Jenkins instance I already have a **"clean_resources"**
playbook set to run every 15 minutes, for cleaning up other cloud-cruft such as
old AMIs. I can just add another play:

{% raw %}
```yaml
- name: delete anonymous instances
  hosts: ec2
  gather_facts: false
  tasks:
    - name: delete anonymous instances
      ec2_sql: DELETE FROM ec2_instances
               WHERE length(tags) = 0 AND age > 30 minutes
```
{% endraw %}

Unfortunately, I'm stuck in DBA mode and have completely dreamt up the
**ec2_sql** module! It *does* look easy to use though, doesn't it?

It does clarify what we want though, so it'll work as a good framework for
creating the actual task. Here's a start with actual Ansible modules, ready to
terminate instances:

{% raw %}
```yaml
- name: delete anonymous instances
  hosts: ec2
  gather_facts: false
  tasks:
    - when: "True"  # length(tags) = 0 AND
                    # age > 30 minutes
      local_action: ec2 state=absent
                        instance_ids={{ ec2_id }}
```
{% endraw %}

Don't run that though! With the conditionals commented out it will just
terminate every instance on your account! We first need to convert the two
parts of the commented SQL 'WHERE' clause into actual Jinja2 code to make it
work. Let's step through that piece by piece.

**N.B.** Note we're using `local_action` with `ec2` to talk to EC2 from *this*
machine, rather than try form *that* machine. Thus in my case, this is run
directly on Jenkins.


### 1. Converting 'length(tags) = 0'

For the inventory I'm using the **ec2.py** script that comes with Ansible. It
gets all the instances from the EC2 API and returns them ready for Ansible,
with lots of `ec2_*` variables defined automatically. The tag variables all
start with `ec2_tag_`, like so:

```json
"ec2-54-75-123-123.eu-west-1.compute.amazonaws.com": {
    "ec2_architecture": "x86_64",
    "ec2_client_token": "",
    ...
    "ec2_tag_Name": "my_fancy_machine",
    "ec2_tag_tier": "web",
    ...
}
```

How can we test that *no* variables on the host have a given prefix? The
built-in Jinja2 filters, and Ansible extensions, don't seem to be of any help,
so we'll need to make our own.

The python code to filter strings to only those with a given prefix is easy -
in fact, it's a one-liner that we can try in 5 seconds on the REPL:

```python
In [1]: def filter_prefix(items, prefix):
   ...:     return [x for x in items if x.startswith(prefix)]

In [2]: var_names = ['ec2_architecture',
   ...:              'ec2_tag_Name',
   ...:              'ec2_tag_ansible_role']

In [3]: filter_prefix(var_names, 'ec2_tag_')
Out[3]: ['ec2_tag_Name', 'ec2_tag_ansible_role']
```

With that done, we just need to expose the `filter_prefix` function to
Ansible's Jinja2 system, so we can use it in templates, and therefore
conditionals.
[The docs](http://docs.ansible.com/developing_plugins.html#filter-plugins)
don't say too much on the topic, instead encouraging you to *use the source*,
but it's quite easy to follow if you know a little Python.

Ansible automatically discovers any filter modules in the folder
**filter_plugins** relative to your playbook; I'm saving mine as
**filter_plugins/my_plugins.py**. All we need for content is:

```python
def filter_prefix(items, prefix):
    return [x for x in items if x.startswith(prefix)]

class FilterModule(object):
    def filters(self):
        return {
            'filter_prefix': filter_prefix,
        }
```

Let's integrate it now with the task:

{% raw %}
```yaml
- name: delete anonymous instances
  hosts: ec2
  tasks:
    - when: >
        hostvars[inventory_hostname].keys()
          | filter_prefix('ec2_tag_')
          | length == 0

      local_action: ec2 state=absent
                        instance_ids={{ ec2_id }}
```
{% endraw %}

It's a slightly "wordy" pipeline to filter that number out, but it's relatively
straightforward:

* `hostvars[inventory_hostname]` is the dictionary of all variables assigned to
  this host
* `.keys()` gets just their names
* `| filter_prefix('ec2_tag_')` calls our plugin function to filter only those
  starting with `ec2_tag_`
* `| length` returns the length, which we can then test against 0

We're halfway!

### 2. Converting 'age > 30 minutes'

The reason we need to add this clause is the window between launching and
tagging. If the deletion task happens to run whilst a machine is launching, it
could terminate it immediately before it even had a chance to gain its tags!
We could set a time limit of 30 seconds to be quite strict, but since EC2
charges are rounded UP per hour, and the playbook is running every 15 minutes,
it doesn't make much difference to set our threshold to 30 minutes.

Looking again at the variables from **ec2.py**, we can see we have the
`ec2_launch_time`:

```json
"ec2-54-75-123-123.eu-west-1.compute.amazonaws.com": {
    ...
    "ec2_launch_time": "2014-11-15T11:25:57.000Z",
    ...
}
```

Since JSON has no native date/time format, it is stored as a string with an
AWS-specific formatting. Luckily, a little googling yields enough Stack
Overflow posts with code to convert the string into seconds-since-launch:

```python
from datetime import datetime
from time import strptime

def aws_age_seconds(ec2_launch_time):
    # Strip trailing subsecond part
    launch_time = ec2_launch_time[:-len('.000Z')]
    # Turn into datetime
    time_format = "%Y-%m-%dT%H:%M:%S"
    time_tuple = strptime(launch_time, time_format)
    time_dt = datetime(*time_tuple[:6])
    # Return difference in seconds
    diff = datetime.utcnow() - time_dt
    return seconds_diff.total_seconds()
```

To add this as a filter, it just needs to be copied again into the
**my_plugins** file and added into the dictionary returned by `filters()`.

So, to put it all together we have:

{% raw %}
```yaml
- name: delete anonymous instances
  hosts: ec2
  tasks:
    - when: >
        hostvars[inventory_hostname].keys()
          | filter_prefix('ec2_tag_')
          | length == 0
        and ec2_launch_time|aws_age_seconds > 1800
      local_action: ec2 state=absent
                        instance_ids={{ ec2_id }}
```
{% endraw %}

Looks quite neat!

## Conclusion

This task is not too complex but it shows you how sometimes you do *need* to
change something about Ansible. Thankfully it's quite easy most components can
be extended or swapped.

If you're on EC2 I hope you can use this code too to save yourself the grief
and bills of anonymous EC2 instances sitting around on your account. Our
Jenkins server has successfully run this task every 15 minutes for several
months now, so it should be fine!<sup>*</sup>

If you want the code in an easy to copy format, see
[my gist "my_filters.py"]
(https://gist.github.com/adamchainz/497d3b1e6b13d6b0c2e6).

Thanks!


<p style="font-size: 60%">
* Blog post has been adapted from production code and therefore may not be
representative of actual product. Suitability for your environment not
guaranteed. Produced in a facility handling nuts. Not intended for children
under the age of 5.
</p>
