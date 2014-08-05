---
layout: post
title: "Installing and Removing R Packages With Ansible"
date: 2014-07-19 10:10:00 +0100
categories:
---

I was asked by some of our Data Scientists to get a few R packages onto their
server, which I configured by Ansible. R seems to be bit funny compared to
other programming languages because it's package installation happens inside
R code, rather than with a dedicated commandline utility.


A quick google gave me a [blog post by Svend Vanderveken](http://svendvanderveken.wordpress.com/2014/02/25/snippet-to-install-r-packages-with-ansible/),
on how to install R packages with Ansible, but as the author points out, it
reports 'changed' even when the package is already installed. This is not great
- we all know that an alarm that always going off is quickly ignored.
Thankfully, it's not hard to fix that, using a couple of Ansible features
`changed_when` and `failed_when`, and a bit of extra **R** code:


```yaml
{% raw %}
- name: r - packages
  command: >
    Rscript --slave --no-save --no-restore-history -e "if (! ('{{ item }}' %in% installed.packages()[,'Package'])) { install.packages(pkgs='{{ item }}', repos=c('http://ftp.heanet.ie/mirrors/cran.r-project.org/')); print('Added'); } else { print('Already installed'); }"
  register: r_result
  failed_when: r_result.rc != 0 or r_result.stdout.find("had non-zero exit status") != -1
  changed_when: r_result.stdout.find("Added") != -1
  with_items:
    - getopt
{% endraw %}
```


Since it's hard to read as a one liner here's that **R** code expanded:


```r
{% raw %}
if (! ('{{ item }}' %in% installed.packages()[,'Package'])) {
    install.packages(pkgs='{{ item }}', repos=c('http://ftp.heanet.ie/mirrors/cran.r-project.org/'));
    print('Added');
} else {
    print('Already installed');
}
{% endraw %}
```

The R code will print out the status of the package, and then the Ansible code
checks to the output to only report changed if the package was not installed
already :)


Whilst we're at it, here's code for removing R packages:


```yaml
{% raw %}
- name: r - remove packages
  command: >
    /usr/bin/Rscript --slave --no-save --no-restore-history -e "if (! ('{{ item }}' %in% installed.packages()[,'Package'])) { print('Not installed'); } else { remove.packages(pkgs='{{ item }}'); print('Removed'); }"
  register: r_result
  failed_when: r_result.rc != 0
  changed_when: r_result.stdout.find("Removed") != -1
  with_items:
    - getopt
{% endraw %}
```


Expanded again for readability:


```r
{% raw %}
if (! ('{{ item }}' %in% installed.packages()[,'Package'])) {
    print('Not installed');
} else {
    remove.packages(pkgs='{{ item }}');
    print('Removed');
}
{% endraw %}
```


Of course, what we'd really like to see is an **R** package module, but I'm not
very experienced with R so I don't know how easy it would be to make this
cross-platform compatible.


One last hint! Don't use R packages if you don't have to. In general, OS
packages will be faster to install so you'll get your provisioning done much
quicker - this certainly stands for `numpy` in Python. So, whilst in this
example I've used `getopt`, I've actually ended up using the `apt` action to
install `r-cran-getopt`.
