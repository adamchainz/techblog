---
layout: post
title: "Validating Ansible changes"
date: 2014-10-31 15:30:00 +0100
comments: true
tags: [ansible]
---

![Engine X] ({{ site.baseurl }}/assets/2014-10-31-engine.jpg)

If you're using ansible to set a configuration file for a program, one of the
most important things you can add is a validation step to ensure that you don't
hit reboot and the program refuses to launch - service down!

Some programs make this easy, like `nginx`, with a validation comand, such as:

```sh
nginx -t
```

It will read the configuration file (and all those included via e.g. `conf.d`)
and die with an easy to read error message on any problems. In ansible you can
add this as a step after templating the configuration, for example:

```yaml
- name: copy in nginx conf
  template: src=nginx.conf.j2
            dest=/etc/nginx/nginx.conf

- name: validate nginx conf
  command: nginx -t
  changed_when: false
```

Ansible will pick up on command failure and stop the play on that host,
outputting what nginx says. All you need to do then is panic, rewrite the file,
and rerun the playbook (maybe with `--start-at-task "copy in nginx conf"` to
skip the bits you've just finished). At least it's much less panic than
rebooting nginx in an invalidate state and having the service down for users!

An important line there is the `changed_when: false` line. Typically ansible
assumes that a `command` changes the state of the host, but `changed_when`
lets you set a Jinja2 conditional to specify a different condition. This stops
false alarms from runs that change nothing on the host, which is good for
idempotency.

The only sad thing about this technique is that many programs do not have any
configuration check that you can run in ansible before doing the big
user-facing reboot. For example, if deploying a django app, you won't know your
it is bad until the last second. It shouldn't be too hard to code a check
script though - e.g. import the settings, check for database connectivity,
page templates can be read from disk, etc. A few broad strokes would prevent
many problems that deploying new app configuration tends to present.
