---
layout: post
title: "Cleaning Up Nameless EC2 Instances with Ansible"
date: 2015-04-09 22:00:00 +0100
comments: true
tags: [ansible, aws]
---

![Anonymous Instances - AAaaahaaa]
({{ site.baseurl }}/assets/2015-04-09-anonymous-instances.jpg)


I gave a talk at the recent London Ansible Meetup on how I cleared up
unexplained nameless/'anonymous' EC2 instances from our AWS account at YPlan.
This is the blog post version of that talk, so you can follow along and stop
such instances appearing on your account and sapping money!

If you know what I'm talking about and just want the code, scroll direct to the
end.


## The Problem

Blank instances were appearing on our EC2 account! They were totally
'anonymous' - no name, no tags, no CPU/network usage (not now, not since they
were launched). Whenever I spotted them on the console, they'd normally been
running for a couple weeks - though I probably look at the console every day,
it's very hard to notice blank rows!

I investigated where they were coming from. At first I suspected AWS might just
be padding out the bill sneakily, but digging further into the Cloudtrail logs,
I discovered that they had been launched by our Jenkins continuous delivery
server.

Our Jenkins build process at YPlan uses an Ansible playbook to launch an
instance (using the **ec2** module), provision it with the latest code and
dependencies, and then freeze it as an Amazon Machine Image (AMI). The AMI is
what then gets used for testing and deployment (if you're interested, it's
based upon some code from Ansible's [immutablish-deploys repo]
(https://github.com/ansible/immutablish-deploys/blob/master/build_ami.yml)
).

I looked back through the build logs to the times the anonymous instances
had been started, and found that in each case Jenkins had launched them at the
start of the normal build process, but it had been cancelled immediately
afterwards. Cancelled builds are a regular occurence, when a developer knows
that the particular version is not going to be useful since it doesn't contain
all the necessary code, and they don't want it to block the next one.

So it turns out that on EC2, launching an instance and tagging it (which is
when it gets a name, since "Name" is a tag) are separate actions. A launch
takes around 10-20 seconds to complete, and thus if you kill the process
creating the instance (Ansible's **ec2** module) right after it has sent the
launch request, you will be left with a blank, 'anonymous' instance.

## The Solution

The solution to this problem is quite simple  - a second 'cleanup' Ansible task
run periodically to delete any blank instances. On our Jenkins server we have
a **"clean_resources"** play that gets run every 15 minutes to clean up other
cloud-cruft such as old AMIs, so I can just add a play to that.

Here's a first draft of such a play:

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

It does clarify what we want though, so it'll work well as a framework for
creating the actual play. Here's a start with the real Ansible ec2 module,
ready to terminate instances:

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

With all the conditionals left in comments though this will just terminate
every instance on the account! We first need to convert the two parts of the
commented SQL 'WHERE' clause into actual Jinja2 code to make it work :)

Let's do that one part at a time.

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

Looking good! ALl we need to do now is give the `filter_prefix` function to
Ansible's Jinja2 system so it can be used in templates, and therefore the
`when` conditional.
[The docs](http://docs.ansible.com/developing_plugins.html#filter-plugins)
don't say too much about making your own template filters, instead encouraging
you to *use the source*, but it's quite easy to follow if you know a little
Python.

Ansible automatically discovers any filter modules in the folder
**filter_plugins** relative to your playbook, therefore I'm saving mine as
**filter_plugins/my_plugins.py** next to **clean_resources.yml**. The only code
we need for this to be picked up as a Jinja2 filter module is:

```python
def filter_prefix(items, prefix):
    return [x for x in items if x.startswith(prefix)]

class FilterModule(object):
    def filters(self):
        return {
            'filter_prefix': filter_prefix,
        }
```

And we can integrate this in the task now :

{% raw %}
```yaml
- name: delete anonymous instances
  hosts: ec2
  gather_facts: false
  tasks:
    - when: >
        hostvars[inventory_hostname].keys()
          | filter_prefix('ec2_tag_')
          | length == 0
      # AND age > 30 minutes
      local_action: ec2 state=absent
                        instance_ids={{ ec2_id }}
```
{% endraw %}

It's a slightly "wordy" pipeline, but it's relatively straightforward to
follow:

* `hostvars[inventory_hostname]` is the dictionary of all variables assigned to
  the current host
* `.keys()` gets the names of the variables as a list
* `| filter_prefix('ec2_tag_')` calls our plugin function to filter only those
  starting with `ec2_tag_`. Note the Jinja2 syntax - the item on the left of
  the filter becomes our function's first argument `items`, and the argument in
  brackets becomes the second argument `prefix`
* `| length` returns the length of the filtered list, which we can then compare
  with 0

Nice!

### 2. Converting 'age > 30 minutes'

We need this second clause because of the ten second window between launching
and tagging. If our deletion task happens to run whilst a machine is being
created, it *could* terminate it before it even gets a first chance to be
tagged!

I've settled to delete untagged instances older than 30 minutes. In principle
a smaller timeout like 30 seconds would do, but since the playbook is run every
15 minutes, and EC2 instance charges are rounded UP to the next whole hour, we
wouldn't save anything.

Looking again at the variables from **ec2.py**, we can see we also have
`ec2_launch_time`:

```json
"ec2-54-75-123-123.eu-west-1.compute.amazonaws.com": {
    ...
    "ec2_launch_time": "2014-11-15T11:25:57.000Z",
    ...
}
```

Since JSON has no native date/time format, it is stored as a string with an
AWS-specific format, which makes it hard to compare. Luckily, a little
googling yields enough Stack Overflow code snippets to convert this string into
a datetime and then the number of seconds that have passed since then:

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
**my_plugins.py** file and added into the dictionary returned by `filters()`.
We can then use it direct in our `when` condition, comparing it against 30
minutes, or rather 1800 seconds:

{% raw %}
```yaml
- name: delete anonymous instances
  hosts: ec2
  gather_facts: false
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

Thankfully it's a bit more self-explanatory than the first half!

## Conclusion

Whilst this play is not particularly complex, it does show that sometimes you
do *need* to change something about Ansible. Thankfully it's quite easy as most
components, such as Jinja2 here, can be extended or swapped.

If you're on EC2 I hope you can use this code too to save yourself the grief
and bills of the anonymous instances. Our Jenkins server has successfully run
this task every 15 minutes for a few months now, so it should be
fine for you!<sup>*</sup>

If you want the filters in an easy to copy format (including some tests), check
out [my gist "my_filters.py"]
(https://gist.github.com/adamchainz/497d3b1e6b13d6b0c2e6).

Thanks!


<p style="font-size: 60%">
* Blog post has been adapted from production code and therefore may not be
representative of actual product. Suitability for your environment not
guaranteed. Produced in a facility handling nuts. Not intended for children
under the age of 5.
</p>
