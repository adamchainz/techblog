---
layout: post
title: "Making Ansible a Bit Faster"
date: 2015-05-18 22:00:00 +0100
comments: true
tags: [ansible]
---

![Jaguars are fast]
({{ site.baseurl }}/assets/2015-05-18-jaguar.jpg)


I recently reduced the YPlan build time by about 30% by tuning two Ansible
settings. They're not on by default, but work in most setups, so this will
make a nice short guide on going faster.

## 0. Profiling!

The first thing to do before trying to find any performance improvements is
always to gather some statistics! Googling "profile ansible" finds the
[Ansible Profiling](https://github.com/jlafon/ansible-profile) plugin, which
takes a mere three shell commands to install. There is also [an accompanying
blog post](http://jlafon.io/ansible-profiling.html) if you need more
instruction. It gives you output like this at the end of a playbook run:

```
PLAY RECAP ********************************************************************
task one --------------------------------------------------------------- 60.71s
task two --------------------------------------------------------------- 23.80s
somehost : ok=2  changed=2   unreachable=0    failed=0
```

I added this and ran a build first so that I had a record of the baseline I had
to improve upon.


## 1. SSH pipelining

SSH pipelining is an easy way of speeding up Ansible by “executing many ansible
modules without actual file transfer” (quote: [the docs]
(http://docs.ansible.com/intro_configuration.html#pipelining)). The boolean
flag defaults to off because some OS's have a `/etc/sudoers` config that
disallows it with `sudo` with the `requiretty` setting.

Fortunately the Ubuntu 14.04 EC@ base image that we use doesn't even mention
`requiretty`, so I was fine to just add the setting to `ansible.cfg`:

```ini
[ssh_connection]
pipelining = True
```

This made things much snappier, especially for runs of small jobs such as
copying files with the `copy` and `template` modules.


## 2. ControlPersist

`ControlPersist` is an SSH feature that keeps the connection to the server open
as a socket, ready to reuse between invocations. With this on, Ansible can
avoid reconnecting to hosts for each task. Ansible actually has it on by
default, with the sockets stored in the directory indicated by `control_path`.

Unfortunately, [as the docs indicate]
(http://docs.ansible.com/intro_configuration.html#control-path),
you can run into length problems when hostnames are quite long. Since we're
using the EC2 DNS names like
`ec2-123-123-123-123.eu-west-1.compute.amazonaws.com`, I feared it might not be
working for us.

I found it hard to determine if ControlPersist was working from Ansible's
output, even when using `-vvvv`. Instead I watched the control path directory
on the Jenkins server whilst it ran a build with:

```sh
watch /var/lib/jenkins/.ansible/cp/
```

The ControlPersist sockets didn't appear, indicating it wasn't working. Sad
face. Interpolating the full path for a control socket with the default
settings, it would come to:

```
/var/lib/jenkins/.ansible/cp/ansible-ssh-ec2-123-123-123-123.eu-west-1.compute.amazonaws.com-22-ubuntu
```

This is 102 characters, which is close to the suggested problem point of 108.
When I changed the setting to use `/tmp`, it worked and I saw the sockets
appearing:

```ini
[ssh_connection]
pipelining = True
control_path = /tmp/ansible-ssh-%%h-%%p-%%r
```

This took a further 10-20% off the run time. Yay!

## Further Speed Improvements

Since this, I've managed to make some more speed improvements by freezing some
configuration into a pre-built EC2 image, and using `async` to parallelize
tasks - there's a good blog post on this titled simply [“Speed up your Ansible
Playbooks”]
(http://acalustra.com/acelerate-your-ansible-playbooks-with-async-tasks.html).

Happy ansibling!
