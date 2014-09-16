---
layout: post
title: "A N00b's Guide to Python Part None"
date: 2014-09-16 22:05:00 +0100
comments: true
categories:
---

Welcome Python beginner. Let's learn about a simple concept - `None`. What is `None`? It's the python equivalent of nothing, not even zero (that is a number, which is something!). You may also know this idea as `null`.

I'm working in IPython, if you want to follow along. It's a better (like 100x better) python interpreter. If you already have python installed, you can just `pip install ipython` to get it, and type `ipython` to run it.

Let's start by getting a `None`:

{% highlight python %}
In [1]: None
{% endhighlight %}

Woah, why isn't there any output? Let's try `print`ing it to the screen:

{% highlight python %}
In [2]: print None
Out [2]: None

{% endhighlight %}

Okay, that's better. `print` gives you human output to the screen of what's happening. IPython doesn't show any output if a statement is `None`, which is wise, because it means nothing. But printing it lets us know that what we tried to print was `None`, rather than something. In fact, what `print` does is just output the `str`ing representation of what you give it:

{% highlight python %}
In [3]: str(None)
Out [3]: 'None'
{% endhighlight %}

Aha, that's definitely a `str`ing since it has 'quote marks' around it. If we print the `str`ing, they won't display though:

{% highlight python %}
In [4]: print str(None)
Out [4]: None

{% endhighlight %}

Brilliant.

This `None` thing is interesting. Let's ask IPython more about it:

{% highlight python %}
In [5]: None?
{% endhighlight %}

    Type:        NoneType
    String form: None
    Namespace:   Python builtin
    Docstring:   <no docstring>

Aha, so its type is **"NoneType"**. Sounds like things in Python have types. That **String Form** there - we've already encountered that. **Namespace** is Python builtin - sensible, since I told you it was part of python and we haven't done anything to include any other spaces of names. But it has no docstring, which isn't a prescription, but something that documents what you're looking at.

Does anything else have a docstring?

{% highlight python %}
In [6]: str?
{% endhighlight %}

    Type:        type
    String form: <type 'str'>
    Namespace:   Python builtin
    Docstring:
    str(object='') -> string

    Return a nice string representation of the object.
    If the argument is a string, the return value is the same object.

Wow, looks like `str` has a **docstring**, that tells us it can take any object and turn it into a *nice string representation*. We've already seen it do that, and it sure was nice!

But its **type** is **type** ?

Hmm, we already saw the type of `None` is `NoneType`. Does that mean we can get that type and make more `None` objects?

{% highlight python %}
In [7]: type(None)
Out [7]: NoneType
{% endhighlight %}

{% highlight python %}
In [8]: none_type = type(None)
{% endhighlight %}

{% highlight python %}
In [9]: none_type()
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mTypeError\x1b[0m                                 Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-9-bd46beb9df28>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mnone_type\x1b[0m\x1b[0;34m(\x1b[0m\x1b[0;34m)\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u"\x1b[0;31mTypeError\x1b[0m: cannot create 'NoneType' instances"]
{% endhighlight %}

Oh dear. We have a handle on the `NoneType` type, but we can't make any more of it. Does that mean there is only one `None`?

{% highlight python %}
In [10]: a = None
{% endhighlight %}

{% highlight python %}
In [11]: b = None
{% endhighlight %}

{% highlight python %}
In [12]: a == b
Out [12]: True
{% endhighlight %}

Well, they're equal, that's a start. But can we check that `a` and `b` are *exactly* the same thing?

{% highlight python %}
In [13]: a is b
Out [13]: True
{% endhighlight %}

Yes indeed they are. So there is only ever one `None`, and we can't make any more of it - that's useful to know (write it down in your copy book now).

I wonder if `None` can be checked against:

{% highlight python %}
In [14]: if None:

    print "Yes, none."
{% endhighlight %}

Oh, nothing happened. Let's see what happens if we go the other way:

{% highlight python %}
In [15]: if not None:

    print "Yes, not none."
Out [15]: Yes, not none.

{% endhighlight %}

Aha! So `None` is never `True`, and always `False`. Let's just check that:

{% highlight python %}
In [16]: None == True
Out [16]: False
{% endhighlight %}

{% highlight python %}
In [17]: None == False
Out [17]: False
{% endhighlight %}

But `is` `None` ever the same thing as `True` or `False`?

{% highlight python %}
In [18]: None is True
Out [18]: False
{% endhighlight %}

{% highlight python %}
In [19]: None is False
Out [19]: False
{% endhighlight %}

Clearly not. In fact, `is` *only* checks if two objects are exactly the same object, and for `None`, `True`, and `False`, we know they are builtins. Let's just quickly check for `True`:

{% highlight python %}
In [20]: True?
{% endhighlight %}

    Type:        bool
    String form: True
    Namespace:   Python builtin
    Docstring:
    bool(x) -> bool

    Returns True when the argument x is true, False otherwise.
    The builtins True and False are the only two instances of the class bool.
    The class bool is a subclass of the class int, and cannot be subclassed.

Exactly. But we've discovered the `type` of both `True` and `False` - it's `bool`! Let's do as it says and make a `bool` out of `None`:

{% highlight python %}
In [21]: bool(None)
Out [21]: False
{% endhighlight %}

That explains why testing it with `if` worked like it did - `None` gets turned into `False` when we try test it as a `bool`ean.

Let's try doing some more day-to-day things with `None`.

{% highlight python %}
In [22]: None + None
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mTypeError\x1b[0m                                 Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-22-28a1675638b9>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mNone\x1b[0m \x1b[0;34m+\x1b[0m \x1b[0mNone\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u"\x1b[0;31mTypeError\x1b[0m: unsupported operand type(s) for +: 'NoneType' and 'NoneType'"]
{% endhighlight %}

{% highlight python %}
In [23]: None - None
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mTypeError\x1b[0m                                 Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-23-7c914bd3dc48>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mNone\x1b[0m \x1b[0;34m-\x1b[0m \x1b[0mNone\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u"\x1b[0;31mTypeError\x1b[0m: unsupported operand type(s) for -: 'NoneType' and 'NoneType'"]
{% endhighlight %}

{% highlight python %}
In [24]: None + 0
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mTypeError\x1b[0m                                 Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-24-0587a0ddb24e>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mNone\x1b[0m \x1b[0;34m+\x1b[0m \x1b[0;36m0\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u"\x1b[0;31mTypeError\x1b[0m: unsupported operand type(s) for +: 'NoneType' and 'int'"]
{% endhighlight %}

Makes sense. `None` really is absolutely nothing, and it would appear there is nothing we can do with it.

Let's check its `dir`ectory of methods though - maybe it has something it hasn't told us yet.

{% highlight python %}
In [25]: dir(None)
Out [25]: ['__class__',
 '__delattr__',
 '__doc__',
 '__format__',
 '__getattribute__',
 '__hash__',
 '__init__',
 '__new__',
 '__reduce__',
 '__reduce_ex__',
 '__repr__',
 '__setattr__',
 '__sizeof__',
 '__str__',
 '__subclasshook__']
{% endhighlight %}

Wow, that's a lot of things! How many things?

{% highlight python %}
In [26]: len(dir(None))
Out [26]: 15
{% endhighlight %}

Wow, **15** things that `None` can do!

Let's try from the top...

{% highlight python %}
In [27]: None.__class__
Out [27]: NoneType
{% endhighlight %}

`NoneType` again? I thought we already got that guy with `type`! Is that the same `NoneType` really?

{% highlight python %}
In [28]: type(None) is None.__class__
Out [28]: True
{% endhighlight %}

Okay, that's boring.

Let's check the next one - `__delattr__`.

{% highlight python %}
In [29]: None.__delattr__
Out [29]: <method-wrapper '__delattr__' of NoneType object at 0x10b8b77d8>
{% endhighlight %}

Okay, it's a method-wrapper. Guess that means it's like a method. Let's try calling it.

{% highlight python %}
In [30]: None.__delattr__()
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mTypeError\x1b[0m                                 Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-30-c029fddc3dab>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mNone\x1b[0m\x1b[0;34m.\x1b[0m\x1b[0m__delattr__\x1b[0m\x1b[0;34m(\x1b[0m\x1b[0;34m)\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u'\x1b[0;31mTypeError\x1b[0m: expected 1 arguments, got 0']
{% endhighlight %}

Okay, you want an argument? I'll give you an argument!

{% highlight python %}
In [31]: None.__delattr__("argument")
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mAttributeError\x1b[0m                            Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-31-2426153cd4f8>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mNone\x1b[0m\x1b[0;34m.\x1b[0m\x1b[0m__delattr__\x1b[0m\x1b[0;34m(\x1b[0m\x1b[0;34m"argument"\x1b[0m\x1b[0;34m)\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u"\x1b[0;31mAttributeError\x1b[0m: 'NoneType' object has no attribute 'argument'"]
{% endhighlight %}

Oh, you want an argument that's the name of an *attribute*? Why didn't you say? We already know the name of an attribute that we don't need - `__class__` is something we can get by calling `type` - so let's get rid of that and save some space:

{% highlight python %}
In [32]: None.__delattr__("__class__")
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mTypeError\x1b[0m                                 Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-32-16c650f8235a>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mNone\x1b[0m\x1b[0;34m.\x1b[0m\x1b[0m__delattr__\x1b[0m\x1b[0;34m(\x1b[0m\x1b[0;34m"__class__"\x1b[0m\x1b[0;34m)\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u"\x1b[0;31mTypeError\x1b[0m: can't delete __class__ attribute"]
{% endhighlight %}

Well that's annoying, but I guess it's okay for python to have some protection over such built-in features. For all we know, `type` might actually just simply return the `__class__` attribute of the `None` object, right?

I give up, let's try the next one.

{% highlight python %}
In [33]: None.__doc__
{% endhighlight %}

Oh great. I guess we kind of knew that one from the question we asked IPython earlier though, where it told us there was no "docstring" - this is where it is stored I guess. Let's give it a check though by looking for the `str` docstring in the same place:

{% highlight python %}
In [34]: str.__doc__
Out [34]: "str(object='') -> string\n\nReturn a nice string representation of the object.\nIf the argument is a string, the return value is the same object."
{% endhighlight %}

Yup, that's the string, although the new-line characters have been displayed as `\\n`. Next!

{% highlight python %}
In [35]: None.__format__
Out [35]: <function __format__>
{% endhighlight %}

{% highlight python %}
In [36]: None.__format__()
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mTypeError\x1b[0m                                 Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-36-b3b553b690f4>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mNone\x1b[0m\x1b[0;34m.\x1b[0m\x1b[0m__format__\x1b[0m\x1b[0;34m(\x1b[0m\x1b[0;34m)\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u'\x1b[0;31mTypeError\x1b[0m: __format__() takes exactly 1 argument (0 given)']
{% endhighlight %}

{% highlight python %}
In [37]: None.__format__(None)
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mTypeError\x1b[0m                                 Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-37-85c2a0b25bf2>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mNone\x1b[0m\x1b[0;34m.\x1b[0m\x1b[0m__format__\x1b[0m\x1b[0;34m(\x1b[0m\x1b[0mNone\x1b[0m\x1b[0;34m)\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u'\x1b[0;31mTypeError\x1b[0m: argument to __format__ must be unicode or str']
{% endhighlight %}

Okay, let's pass in an empty str.

{% highlight python %}
In [38]: None.__format__("")
Out [38]: 'None'
{% endhighlight %}


{% highlight python %}
In [39]: None.__getattribute__()
[u'\x1b[0;31m---------------------------------------------------------------------------\x1b[0m\n\x1b[0;31mTypeError\x1b[0m                                 Traceback (most recent call last)', u'\x1b[0;32m<ipython-input-39-5ae801cbefcc>\x1b[0m in \x1b[0;36m<module>\x1b[0;34m()\x1b[0m\n\x1b[0;32m----> 1\x1b[0;31m \x1b[0mNone\x1b[0m\x1b[0;34m.\x1b[0m\x1b[0m__getattribute__\x1b[0m\x1b[0;34m(\x1b[0m\x1b[0;34m)\x1b[0m\x1b[0;34m\x1b[0m\x1b[0m\n\x1b[0m', u'\x1b[0;31mTypeError\x1b[0m: expected 1 arguments, got 0']
{% endhighlight %}

Let's try giving it the name of an attribute...

{% highlight python %}
In [40]: None.__getattribute__("__class__")
Out [40]: NoneType
{% endhighlight %}

Wow, we just discovered that the 'dot' operator really just calls the `__getattribute__` method of the object! So you can get any attribute that way? Let's try getting them all!

{% highlight python %}
In [41]: for name in dir(None):

    print name, None.__getattribute__(name)
Out [41]: __class__ <type 'NoneType'>
__delattr__ <method-wrapper '__delattr__' of NoneType object at 0x10b8b77d8>
__doc__ None
__format__ <built-in method __format__ of NoneType object at 0x10b8b77d8>
__getattribute__ <method-wrapper '__getattribute__' of NoneType object at 0x10b8b77d8>
__hash__ <method-wrapper '__hash__' of NoneType object at 0x10b8b77d8>
__init__ <method-wrapper '__init__' of NoneType object at 0x10b8b77d8>
__new__ <built-in method __new__ of type object at 0x10b8bda60>
__reduce__ <built-in method __reduce__ of NoneType object at 0x10b8b77d8>
__reduce_ex__ <built-in method __reduce_ex__ of NoneType object at 0x10b8b77d8>
__repr__ <method-wrapper '__repr__' of NoneType object at 0x10b8b77d8>
__setattr__ <method-wrapper '__setattr__' of NoneType object at 0x10b8b77d8>
__sizeof__ <built-in method __sizeof__ of NoneType object at 0x10b8b77d8>
__str__ <method-wrapper '__str__' of NoneType object at 0x10b8b77d8>
__subclasshook__ <built-in method __subclasshook__ of type object at 0x10b8b7988>

{% endhighlight %}

Wow, that saved some work, checking what they are and where they are from! Most seem to be part of the `NoneType` object, but some are from `object` or `type`. Weird!

Wait, is `None` and `object` ?

{% highlight python %}
In [42]: isinstance(None, object)
Out [42]: True
{% endhighlight %}

Apparently so! What else is an `object`?

{% highlight python %}
In [43]: isinstance(object, object)
Out [43]: True
{% endhighlight %}

{% highlight python %}
In [44]: isinstance(type(None), object)
Out [44]: True
{% endhighlight %}

{% highlight python %}
In [45]: isinstance(type, object)
Out [45]: True
{% endhighlight %}

Well, I heard python is object-oriented, but it seems oriented towards making *everything* an object.

So what does that mean? Does object have some stuff on it that you can do anywhere or something?

{% highlight python %}
In [46]: dir(object)
Out [46]: ['__class__',
 '__delattr__',
 '__doc__',
 '__format__',
 '__getattribute__',
 '__hash__',
 '__init__',
 '__new__',
 '__reduce__',
 '__reduce_ex__',
 '__repr__',
 '__setattr__',
 '__sizeof__',
 '__str__',
 '__subclasshook__']
{% endhighlight %}

{% highlight python %}
In [47]: len(dir(object))
Out [47]: 15
{% endhighlight %}

Holy smokes, that's like the same list that `None` has! Wait, is it exactly the same list?

{% highlight python %}
In [48]: dir(object) == dir(None)
Out [48]: True
{% endhighlight %}

Yes indeed! Aww wait, we learnt nothing interesting about `None` - it only has all the same things that every other `object` has, i.e. everything else... :( So it really *doesn't* do anything interesting.

Well, this sucks, and we've run out of time. Guess we'll have to call it a day and hopefully next time using `True` and `False` will impart more wisdom to us!
