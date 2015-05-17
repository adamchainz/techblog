---
layout: post
title: "Some Ansible Hints"
date: 2014-07-12 21:38:16 +0100
comments: true
categories: [ansible]
---

Three useful little tidbits for using Ansible that I've come across.


## 1. How to use with_items on lists of multiple types

With a little jinja-fu you can iterate a list of strings and dicts to template
the action in more elaborate ways than the typical use.


I was configuring the installation of some Python packages and wanted to fix
the version of Django, but not the version of `MySQL-python`, since any updates
to it are likely to be for security/compatability.  Typically, `with_items`
would be used to iterate over a list with dicts, like `{name: package1,
version: something}`, but it's tiresome to write when you often don't care
about one of the keys. Also, providing `version=""` won't work with the `pip`
module, since it would get converted to `pip install package==`, which pip
doesn't interpet as 'latest', so there would already have been a special case.
However with this little extra templating, I turned it into a nice readable
list:


{% highlight yaml %}
{% raw %}
---
- name: pip - install packages
  pip: name={{ item.name|default(item) }}
       {% if item.version|default('') > '' %}
         version={{ item.version }}
       {% else %}
         state=latest
       {% endif %}
  with_items:
    - MySQL-python
    - { name: Django, version: 1.6.5 }
{% endraw %}
{% endhighlight %}


I found this a good reminder that Ansible uses Jinja2 everywhere you could want
it to, and that Jinja2 can do a lot more than simple variable substitution.

**EDIT** This has been deemed bad practice and now fails on the latest Ansible
with this error:

{% highlight text %}
 ________________________________
< TASK: machine | pip - packages >
 --------------------------------
        \  ^___^
         \ (ooo)\_______
           (___)\       )\/\
                ||----w |
                ||     ||


fatal: [default] => A variable inserted a new parameter into the module args. Be sure to quote variables if they contain equal signs (for example: "{{var}}").
{% endhighlight %}

Guess it's just too clever!



## 2. Increase forks in .ansible.cfg

Although the default configuration is sensible, the 'forks' parameter may be
worth tweaking upwards - as the docs state, 5 is "very very conservative:". I
found that increasing it did sped things up drastically when I had to manage
more than a few hosts. My current `~/.ansible.cfg`:


{% highlight ini %}
[defaults]
forks = 25
{% endhighlight %}


(I manage my dotfiles using Ansible, but that's another post)


## 3. Use a different cow

Ansible will automatically use cowsay to brighten up the log output whilst
running if it is installed (on Mac, `brew install cowsay`). But you can
*also* change the cowfile it uses to further entertain yourself.

You can get the list of cowfiles installed with `cowsay -l`:

{% highlight text %}
Cow files in /usr/local/Cellar/cowsay/3.03/share/cows:
beavis.zen bong bud-frogs bunny cheese cower daemon default dragon
dragon-and-cow elephant elephant-in-snake eyes flaming-sheep ghostbusters
head-in hellokitty kiss kitty koala kosh luke-koala meow milk moofasa moose
mutilated ren satanic sheep skeleton small sodomized stegosaurus stimpy
supermilker surgery telebears three-eyes turkey turtle tux udder vader
vader-koala www
{% endhighlight %}

And you can choose which one will be used by setting the environment variable
in your shell startup file (.bash_profile, .zshrc, etc.):

{% highlight sh %}
export ANSIBLE_COW_SELECTION=three-eyes
{% endhighlight %}

I've opted for the subtly mutated three-eyed cow, which looks like this:

{% highlight text %}
 _________________
< GATHERING FACTS >
 -----------------
        \  ^___^
         \ (ooo)\_______
           (___)\       )\/\
                ||----w |
                ||     ||


ok: [127.0.0.1]
{% endhighlight %}

Some are incredibly impractical, as they take up a *lot* of screen estate, for
example, `dragon-and-cow`:

{% highlight text %}
 _________________
< GATHERING FACTS >
 -----------------
                       \                    ^    /^
                        \                  / \  // \
                         \   |\___/|      /   \//  .\
                          \  /O  O  \__  /    //  | \ \           *----*
                            /     /  \/_/    //   |  \  \          \   |
                            @___@`    \/_   //    |   \   \         \/\ \
                           0/0/|       \/_ //     |    \    \         \  \
                       0/0/0/0/|        \///      |     \     \       |  |
                    0/0/0/0/0/_|_ /   (  //       |      \     _\     |  /
                 0/0/0/0/0/0/`/,_ _ _/  ) ; -.    |    _ _\.-~       /   /
                             ,-}        _      *-.|.-~-.           .~    ~
            \     \__/        `/\      /                 ~-. _ .-~      /
             \____(oo)           *.   }            {                   /
             (    (--)          .----~-.\        \-`                 .~
             //__\\  \__ Ack!   ///.----..<        \             _ -~
            //    \\               ///-._ _ _ _ _ _ _{^ - - - - ~
{% endhighlight %}

I was also amused to see `cowsay` comes with Ren and Stimpy cowfiles, which
gives you an idea of its age.


---

Those are all the hints I have at the moment&mdash;tune in next time!
