---
layout: post
title: "Merging groups and hostvars in Ansible variables"
date: 2014-10-02 22:30:00 +0100
comments: true
---

![Tools of the trade.] ({{ site.baseurl }}/assets/2014-10-02-swords.jpg)

I was googling for information on creating round-robin DNS records in Route53
with Ansible and came across [this post by Daniel Hall] [1] who'd figured out a
way of merging the his host group list with their `hostvars` in Ansible. After
a bit of emailing with him I've figured a way to do it without having to add an
extra filter as he did originally - by digging more into Jinja2.

What's the problem?

*1.* A host group in ansible is a list of their addresses - e.g.
`["foo.example.com", "bar.example.com"]`

*2.* `hostvars` is a dictionary of all the known 'facts' for each system, e.g.:

```json
{
    "foo.example.com": {
        "ansible_default_ipv4": {
            "address": "192.168.1.7"
        }
    },
    ...
}
```

*3.* Given a host group, we want to create a single string that is the
comma-separated concatenation of all of their ip4 addresses from `hostvars`.

It uses a few of the lesser-used jinja2 features which I'll talk through.

Here's the example playbook (`test.yml`):

{% raw %}
```yaml
- hosts: all
  connection: local
  tasks:
    - debug:
        # Comma-separated string of all ip4 addresses of hosts
        msg: |
          {% set comma = joiner(",") %}
          {% for item in ['127.0.0.1', '127.0.0.1'] -%}
              {{ comma() }}{{ hostvars[item].ansible_default_ipv4.address }}
          {%- endfor %}
```
{% endraw %}

You can test it by running with:

```sh
ansible-playbook test.yml -i 127.0.0.1,
```

Yes, the way you test Ansible without an inventory file is a comma-separated
list of hosts - but the comma is needed for just one host.

It gives the output (cows disabled for conciseness):

```sh
PLAY [127.0.0.1] **************************************************************

GATHERING FACTS ***************************************************************
ok: [127.0.0.1]

TASK: [debug ] ****************************************************************
ok: [127.0.0.1] => {
    "msg": "192.168.1.7,192.168.1.7"
}

PLAY RECAP ********************************************************************
127.0.0.1                  : ok=2    changed=0    unreachable=0    failed=0
```


Success!

How does it work?

First thing to notice is the inner loop - {% raw %}`{% for item in ...`{% endraw %}. I'm looping on
an example array but you can easily replace this with a hosts list. At the end
of the loop declaration, a dash is added before the end of the tag - `-%}` -
this means jinja2 will collapse any whitespace it encounters in the loop.

Secondly, the ipv4 address is output with a simple lookup:
``hostvars[item].ansible_default_ipv4.address``. There are a lot of facts that
ansible gathers; add the task `debug: var=hostvars` to the playbook to see all
variables available.

Thirdly, there's this `joiner` thing being used. This is a template function in
Jinja2 precisely for the purpose of joining strings with separators. It outputs
the string you pass it on its 2nd+ calls. It's better documented [on Jinja2
  itself] [2].

Anyway, this was fun... especially since I didn't need to implement round-robin
DNS myself in the end! Also, there is maybe an easier way and I don't know it.
If you know, please tell me.


[1]: http://www.danielhall.me/2014/09/creating-rr-records-in-route53-with-ansible/
[2]: http://jinja.pocoo.org/docs/dev/templates/#joiner
