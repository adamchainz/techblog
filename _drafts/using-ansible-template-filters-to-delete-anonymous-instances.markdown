---
layout: post
title: "Using Ansible Template Filters to Delete Anonymous Instances"
date: 2015-03-30 20:10:00 +0100
comments: true
categories:
---

![Anonymous Instances - AAaaahaaa]
({{ site.baseurl }}/assets/anonymous-instances.jpg)


This is the blog post of a talk I gave at the London Ansible Meetup last week.


## The Problem

I had a problem on EC2. Blank instances were appearing on the account! They
were totally 'anonymous' - no name, no tags, no CPU/network usage (not now, not
since they were launched). And when I spotted them on the console, they'd
normally been running for a couple weeks - even though I probably look at the
console every day, it's very hard to notice blank rows!


I had to investigate where they were coming from. At first I suspected AWS
might just be padding out the bill, but digging further into the logs, I
discovered that they had been launched by Jenkins.


Our build process at **YPlan** is based around using an Ansible playbook to
provision a machine with the latest code and dependencies, then freeze
it as an AMI (Amazon Machine Image). The AMI is what then gets tested and
deployed.
Looking through the build logs I found the anonymous instances were being
launched by Jenkins at the start of a build, but then the build was getting
cancelled immediately by a developer - normally because they knew that the next
build would be more useful and they didn't want to wait.

It so turns out that launching an instance and tagging it (when it gets a name)
are separate actions with the EC2 API, with the first taking about 10 seconds
to complete. Therefore if you kill Ansible's **ec2** module after it has
sent the launch request, you will be left with a blank, anonymous instance.

## The Solution

I realized what I needed quickly - a little *more* Ansible code to clean up the
mess my Ansible code was leaving behind. I drafted a task to be run every 15
minutes in our tidy-up playbook (we already had one as our cloud can get quite
messy), using the fantastic **ec2_sql** module:

{% raw %}
```yaml
- name: delete anonymous instances
  ec2_sql:
    sql: DELETE FROM ec2_instances
         WHERE length(tags) = 0 AND age > 30 minutes
```
{% endraw %}

Unfortunately, I'd simply dreamt up the **ec2_sql** module and its ease of use.
It was going to take a little more work to make Ansible do this clean up. Well,
at least the SQL statement helped serve as an expression of what I wanted...

I sketched a real task like this, using the `ec2` module with `local_action`
to initiate instance termination from the machine running the playbook:

{% raw %}
```yaml
- name: delete anonymous instances
  hosts: ec2
  tasks:
    - when: "True"  # length(tags) = 0 AND
                    # age > 30 minutes
      local_action: ec2 state=absent
                        instance_ids={{ ec2_id }}
```
{% endraw %}

Don't run the above directly! In its current state it will delete *every* EC2
instance. I'll step you through how I converted the two-part 'WHERE' clause
in the comment into actual Jinja2 filters to make it work.


### length(tags) = 0

For the inventory we're using the **ec2.py** script bundled with Ansible. It
gets
all your instances from the API and returns them ready for SSH, with lots of
`ec2_*` variables automatically retrieved. The tag variables all start with
`ec2_tag_`, like so:

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

How can we test for *no* variables on a host with a given prefix? Well, I
couldn't find an easy way using the built-in Ansible Jinja2 filters, so I
found I needed to make my own.

The python code to filter those strings with a prefix is easy - in fact, it's a
one-liner that I first tried out in the REPL:

```python
In [1]: def filter_prefix(items, prefix):
   ...:     return [x for x in items
                    if x.startswith(prefix)]

In [2]: var_names = ['ec2_architecture',
   ...:              'ec2_tag_Name',
   ...:              'ec2_tag_ansible_role']

In [3]: filter_prefix(var_names, 'ec2_tag_')
Out[3]: ['ec2_tag_Name', 'ec2_tag_ansible_role']
```

Given this, we just need to expose that function to Ansible's Jinja2 system so
we can use it in templates, and therefore conditionals.
[The docs](http://docs.ansible.com/developing_plugins.html#filter-plugins)
don't say too much on the topic, instead encouraging you to *use the source*,
but it's not hard to follow. Ansible automatically discovers any filter modules
in the folder **filter_plugins** relative to your playbook automatically, so I
put mine at **filter_plugins/my_plugins.py**, with the contents:

```python
def filter_prefix(items, prefix):
    return [x for x in items if x.startswith(prefix)]

class FilterModule(object):
    def filters(self):
        return {
            'filter_prefix': filter_prefix,
        }
```

So now let's integrate it with the task to delete those instances with 0 tags!

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

It's a bit of a mouthful for all the filtering - it's certainly not SQL! But
it's a simple pipeline:

* `hostvars[inventory_hostname]` is the dictionary of all variables assigned to
  this host.
* `.keys()` gets just their names
* `| filter_prefix('ec2_tag_')` calls the plugin function to filter only those
  starting with `ec2_tag_`
* `| length` returns the length, which is then tested to be 0.

Or in plain english:

> When the count of the host's variables that are prefixed `ec2_tag_` is 0,
> tell ec2 to terminate it.

## age > 30 minutes

Unfortunately we can't just run the playbook as above - since the insatnce
launch takes about 10 seconds to return, we could terminate a fresh one before
it even had a chance to be tagged. Hence, I added the second condition to
filter those instances that have been around for more than 30 minutes (it won't
cost any more than, say, 10 minutes - EC2 charges per hour rounded *up*).

If we look again at the variables we have from **ec2.py**, we'll find the
`ec2_launch_time`:

```json
"ec2-54-75-123-123.eu-west-1.compute.amazonaws.com": {
    ...
    "ec2_launch_time": "2014-11-15T11:25:57.000Z",
    ...
}
```

Since JSON has no datetime native format, it is just set as a string of the
format of Amazon's choosing. Luckily a little googling lead me to a couple
Stack Overflow posts that I could combine into this date-parsing code to count
how many seconds have passed since the launch:

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

To add this as a filter, I just needed to add another entry into the `dict`
returned by `filters()` to the function.

The final playbook to delete the untagged instances older than 30 minutes thus
came out as:

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


And it's been working ever since!*

<p style="font-size: 60%">
* Blog post has been adapted from production code and therefore may not be
representative of actual product. Suitability for your environment not
guaranteed. Produced in a facility handling nuts. Not intended for children
under the age of 5.
</p>
