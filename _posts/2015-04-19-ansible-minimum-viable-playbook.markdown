---
layout: post
title: "An Ansible MVP (Minimum Viable Playbook) for Testing Tasks"
date: 2015-04-18 20:25:00 +0100
comments: true
categories: [ansible]
---

![MVPs are tiny.] ({{ site.baseurl }}/assets/2015-04-19-ansible-mvp.jpg)

I showed this briefly in my post on
[merging groups and hostvars]
({{ site.url }}{% post_url 2014-10-02-merging-groups-and-hostvars-in-ansible-variables %}),
but I thought it was worth writing a whole post on. The Minimum Viable Playbook
(MVP) is the shortest, most useful Ansible playbook I have. Whenever I need to
write some Ansible code and I'm not entirely sure I'm doing it right (which is
often), I implement it first in the MVP so I can test it quickly. Here's my
latest iteration:

{% raw %}
```yaml
- hosts: 127.0.0.1
  connection: local
  gather_facts: no
  vars:
    my_name: a_b_c
  tasks:
    - debug: msg={{ my_name|replace('_', '-') }}
```
{% endraw %}

I keep the MVP saved as `~/tmp/test.yml`, from which it can be run with:

```sh
$ ansible-playbook -i 127.0.0.1, ~/tmp/test.yml
```

(The `-i` argument allows you to specify the inventory as a comma-separated
string of hosts, but it looks a little weird with only one host. You can't
leave out the comma, otherwise it gets interpreted as a filename.)

The MVP runs in about 0.2 seconds giving me quick feedback:

```
PLAY [127.0.0.1] **************************************************************

TASK: [debug ] ****************************************************************
ok: [127.0.0.1] => {
    "msg": "a-b-c"
}

PLAY RECAP ********************************************************************
127.0.0.1                  : ok=1    changed=0    unreachable=0    failed=0
```

Here I was testing a rather trivial use of the `replace` filter, but since I
wasn't sure I remembered how it worked, it was faster to use the MVP than to
test the full task I was writing, or to go to the documentation. Running the
actual playbook would take minutes rather than seconds (even with `--start-at-
task`, since it relied on other tasks), and whilst going to the documentation
is normally fast (I use [Dash](https://kapeli.com/dash) for quick local look-
ups), but it can be tricky when the answer might be split between the Ansible
and Jinja 2 docs.

Two things make the MVP particularly fast:

1. When running tasks locally, Ansible always uses the *local* connection type,
   which means there is no SSH overhead.

2. I've disabled fact-gathering which means my tasks are executed immediately.
   This saves about a second per run, which isn't much but you do notice it.

Hope this helps you. If there's something I'm missing, please let me know!
