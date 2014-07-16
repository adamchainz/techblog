---
layout: post
title: "Installing and Removing R Packages With Ansible"
date: 2014-07-16 21:25:16 +0100
categories:
---

R is a bit funny because CRAN is only usable within R scripts (it appears, I
didn't have too long to research it). Hence you have to use a little R code to
install/remove packages.


A quick google gave me a [blog post by Svend Vanderveken](http://svendvanderveken.wordpress.com/2014/02/25/snippet-to-install-r-packages-with-ansible/),
but as the author points out, it reports 'changed' even when the package is
already installed. This is not great - we all know that an alarm that is always
going off is quickly ignored. Thankfully, it's not hard to fix that, using a
couple lesser-known Ansible features `changed_when` and `failed_when`, and a bit
of extra **R** code:


```yaml
- name: r - packages
  command: >
    Rscript --slave --no-save --no-restore-history -e "if (! ('{{ item }}' %in% installed.packages()[,'Package'])) { install.packages(pkgs='{{ item }}', repos=c('http://ftp.heanet.ie/mirrors/cran.r-project.org/')); print('Added'); } else { print('Already installed'); }"
  register: r_result
  failed_when: r_result.rc != 0
  changed_when: r_result.stdout.find("Added") != -1
  with_items:
    - getopt
```

Since it's hard to read as a one liner here's that **R** code expanded:

```r
if (! ('{{ item }}' %in% installed.packages()[,'Package'])) {
    install.packages(pkgs='{{ item }}', repos=c('http://ftp.heanet.ie/mirrors/cran.r-project.org/'));
    print('Added');
} else {
    print('Already installed');
}
```

So the task will report changed only if the package is not installed already :)


Whilst we're at it, here's code for removing R packages:

```yaml
- name: r - remove packages
  command: >
    /usr/bin/Rscript --slave --no-save --no-restore-history -e "if (! ('{{ item }}' %in% installed.packages()[,'Package'])) { print('Not installed'); } else { remove.packages(pkgs='{{ item }}'); print('Removed'); }"
  register: r_result
  failed_when: r_result.rc != 0
  changed_when: r_result.stdout.find("Removed") != -1
  with_items:
    - getopt
```


Expanded again for readability:


```r
if (! ('{{ item }}' %in% installed.packages()[,'Package'])) {
    print('Not installed');
} else {
    remove.packages(pkgs='{{ item }}');
    print('Removed');
}
```

Of course, what we'd really like to see is an **R** package module, but I'm not
very experienced with R so I don't know how easy it would be to make this
cross-platform compatible.


One last hint! Don't use R packages if you don't have to. In general, OS
packages will be faster to install so you'll get your provisioning done much
quicker - this certainly stands for `numpy` in Python. So, whilst in this
example I've used `getopt`, I've actually ended up using the `apt` action to
install `r-cran-getopt`.
