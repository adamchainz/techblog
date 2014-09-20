---
layout: post
title: "Python Concepts: Part None"
date: 2014-09-22 17:30:00 +0100
comments: true
categories:
---

![Space. The closest thing to a picture of nothing that's not blank.]({{ site.baseurl }}/assets/2014-09-17-big-dipper.jpg)

<p class='message'>
    <strong>Disclaimer:</strong> even though this post covers nothing, it does so in a fairly technical manner, so it's probably not appropriate for complete newbies. You'll need a little programming experience to understand what I'm blabbing on about.
</p>

Let's learn about nothing. More particularly, let's learnt about python's concept of representing nothing, `None`. This is the most nothingest concept of nothing as well - for example, zero is nothing, but it's also a number, so it still has some information. Other names for nothing from other programming languages include `null`, `nil`, or `Nothing`.

I'm writing this post in **IPython**. If you want to follow along at home, get your IPython console started by typing `ipython` at the command prompt. Didn't work? [Install it](http://ipython.org/install.html). Bam.

Now, let's start. Let's see what happens if ask for nothing:

{% highlight ipy %}
In [1]: None
{% endhighlight %}

No output - makes sense. Let's try outputting it to screen though:

{% highlight ipy %}
In [2]: print None
None

{% endhighlight %}

Aha, we get some output. `print` turns its input into a string so it can be output - and the `str`ing output of `None` is `'None'`. Let's check that `str`ing representation:

{% highlight ipy %}
In [3]: str(None)
Out[3]: 'None'
{% endhighlight %}

Now, since we didn't use print, the output comes from the IPython prompt, with an "Out" marker to indicate that. IPython takes the expression you typed in, evaluates it, and displays the result as a prompt - unless the result is `None`, when it displays nothing! And you guessed it, input 1 evaluated to `None`, and so did input 2 (`print` actually can't even return anything).

So if we print again, there is no output prompt, since the print statement evaluates to nothing. Let's try `print`ing the `str`ing of `None`:

{% highlight ipy %}
In [4]: print str(None)
None

{% endhighlight %}

Brilliant.

Anyway, the string `"None"` is *something*, and we're here to investigate nothing. Let's use an IPython feature to find out more about it:

{% highlight ipy %}
In [5]: None?
{% endhighlight %}

{% highlight ipy %}
Type:        NoneType
String form: None
Namespace:   Python builtin
Docstring:   <no docstring>
{% endhighlight %}

Intriguing. `None` has a type - the `NoneType`. In fact, every object in python has a type, which is like a `class` in other languages, except it extends to builtin things as well.

The **String Form** there - that's what you get when you pass `None` to `str` as we've seen.

**Namespace** is 'Python builtin' - which means, surprise surprise, it's built-in to Python.

There's no **docstring** - this is a way of adding documentation to objects in Python for users to access. Let's check for a docstring on another object we know about:

{% highlight ipy %}
In [6]: str?
{% endhighlight %}

{% highlight ipy %}
Type:        type
String form: <type 'str'>
Namespace:   Python builtin
Docstring:
str(object='') -> string

Return a nice string representation of the object.
If the argument is a string, the return value is the same object.
{% endhighlight %}

Ah, `str`'s docstring is much more instructive - and it tells us how to do what we did on line 3!

But its **type** is **type**? This means we can make fresh `str` objects by calling the type:

{% highlight ipy %}
In [7]: str()
Out[7]: ''
{% endhighlight %}

And tada, a blank `str`ing appears.

Can we do that with the `NoneType` I wonder?

{% highlight ipy %}
In [8]: NoneType()
---------------------------------------------------------------------------
NameError                                 Traceback (most recent call last)
<ipython-input-8-49f3f437d859> in <module>()
----> 1 NoneType()

NameError: name 'NoneType' is not defined
{% endhighlight %}

Uh-oh. Looks like we don't actually have `NoneType` available in our current namespace - just `None`. But luckily, we can ask for the type of `None`, store it in a variable, and call that:

{% highlight ipy %}
In [9]: type(None)
Out[9]: NoneType
{% endhighlight %}

{% highlight ipy %}
In [10]: local_none_type = type(None)
{% endhighlight %}

{% highlight ipy %}
In [11]: local_none_type()
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-11-ae31f43f07b8> in <module>()
----> 1 local_none_type()

TypeError: cannot create 'NoneType' instances
{% endhighlight %}

Dang. We can have a handle on the `NoneType` type, but we can't make any more of it. This is actually a special rule for the `NoneType`... Does it mean there is only ever one `None`?

{% highlight ipy %}
In [12]: a = None
{% endhighlight %}

{% highlight ipy %}
In [13]: b = None
{% endhighlight %}

{% highlight ipy %}
In [14]: a == b
Out[14]: True
{% endhighlight %}

Well, they're equal, that's a start. But can we check that `a` and `b` are *exactly* the same thing?

{% highlight ipy %}
In [15]: a is b
Out[15]: True
{% endhighlight %}

Yes indeed they are. So there is only ever one `None`, and we can never make any more of it. That's useful to know - write it down in your copy book now.


---

Let's have a break with a quote on nothing:

![Marcus Aurelius]({{ site.baseurl }}/assets/2014-09-17-marcus-aurelius.png)

> Nothing proceeds from nothingness, as also nothing passes away into non-existence.
> 
> -- Marcus Aurelius, Meditations, IV, 4

---

Let's continue; I wonder if `None` can be checked against:

{% highlight ipy %}
In [16]: if None: print "Yes, none."
{% endhighlight %}

Oh, nothing happened. Let's see what happens if we go the other way:

{% highlight ipy %}
In [17]: if not None: print "Yes, not none."
Yes, not none.

{% endhighlight %}

Aha! So `None` is never `True`, and always `False`? Let's just check that by turning it into a `bool`ean:

{% highlight ipy %}
In [18]: bool(None)
Out[18]: False
{% endhighlight %}

Exactly.

That explains why our `if` statement worked that way - `None` gets turned into `False` when we test it as a `bool`ean.

Let's try doing some more day-to-day things with `None`.

{% highlight ipy %}
In [19]: None + None
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-19-28a1675638b9> in <module>()
----> 1 None + None

TypeError: unsupported operand type(s) for +: 'NoneType' and 'NoneType'
{% endhighlight %}

{% highlight ipy %}
In [20]: None - None
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-20-7c914bd3dc48> in <module>()
----> 1 None - None

TypeError: unsupported operand type(s) for -: 'NoneType' and 'NoneType'
{% endhighlight %}

{% highlight ipy %}
In [21]: None + 0
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-21-0587a0ddb24e> in <module>()
----> 1 None + 0

TypeError: unsupported operand type(s) for +: 'NoneType' and 'int'
{% endhighlight %}

So, you can't really do anything. Makes sense that you do (nearly) nothing with nothing.

Let's check its `dir`ectory of methods though - maybe it has something it hasn't told us yet.

{% highlight ipy %}
In [22]: dir(None)
Out[22]: ['__class__',
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

{% highlight ipy %}
In [23]: len(dir(None))
Out[23]: 15
{% endhighlight %}

Wow, there are actually **15** things that `None` can do!?

Let's try from the top...

{% highlight ipy %}
In [24]: None.__class__
Out[24]: NoneType
{% endhighlight %}

`NoneType` again? I thought we already got that guy with `type`! Is that the same `NoneType` really?

{% highlight ipy %}
In [25]: type(None) is None.__class__
Out[25]: True
{% endhighlight %}

Okay, that's boring - just another way to get ahold of that `__class__` it looks like.

Let's check the next one - `__delattr__`.

{% highlight ipy %}
In [26]: None.__delattr__
Out[26]: <method-wrapper '__delattr__' of NoneType object at 0x10c00d7d8>
{% endhighlight %}

Okay, it's a method-wrapper. Guess that means it's like a method. Let's try calling it.

{% highlight ipy %}
In [27]: None.__delattr__()
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-27-c029fddc3dab> in <module>()
----> 1 None.__delattr__()

TypeError: expected 1 arguments, got 0
{% endhighlight %}

Okay, you want an argument? I'll give you an argument!

{% highlight ipy %}
In [28]: None.__delattr__("argument")
---------------------------------------------------------------------------
AttributeError                            Traceback (most recent call last)
<ipython-input-28-2426153cd4f8> in <module>()
----> 1 None.__delattr__("argument")

AttributeError: 'NoneType' object has no attribute 'argument'
{% endhighlight %}

Oh, you want an argument that's the name of an *attribute*? Why didn't you say? We already know the name of an attribute that we don't need - `__class__` is something we can get by calling `type` - so let's try saving some space by getting rid of that:

{% highlight ipy %}
In [29]: None.__delattr__("__class__")
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-29-16c650f8235a> in <module>()
----> 1 None.__delattr__("__class__")

TypeError: can't delete __class__ attribute
{% endhighlight %}

Well that's annoying, but I guess it's okay for python to have some protection over such built-in features. For all we know, `type` might need the `__class__` attribute to be there to work, right?

I give up, let's try the next one.

{% highlight ipy %}
In [30]: None.__doc__
{% endhighlight %}

Oh great, nothing. This is actually the attribute that stores an object's docstring though - and as we saw earlier, `None` has no docstring.

Let's check by getting the `str` docstring in the same way:

{% highlight ipy %}
In [31]: str.__doc__
Out[31]: "str(object='') -> string\n\nReturn a nice string representation of the object.\nIf the argument is a string, the return value is the same object."
{% endhighlight %}

Yup, that's the string, although the new-line characters have been displayed as `\\n`. Next!

{% highlight ipy %}
In [32]: None.__format__
Out[32]: <function __format__>
{% endhighlight %}

{% highlight ipy %}
In [33]: None.__format__()
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-33-b3b553b690f4> in <module>()
----> 1 None.__format__()

TypeError: __format__() takes exactly 1 argument (0 given)
{% endhighlight %}

{% highlight ipy %}
In [34]: None.__format__(None)
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-34-85c2a0b25bf2> in <module>()
----> 1 None.__format__(None)

TypeError: argument to __format__ must be unicode or str
{% endhighlight %}

Okay, let's pass in an empty str.

{% highlight ipy %}
In [35]: None.__format__("")
Out[35]: 'None'
{% endhighlight %}


{% highlight ipy %}
In [36]: None.__getattribute__()
---------------------------------------------------------------------------
TypeError                                 Traceback (most recent call last)
<ipython-input-36-5ae801cbefcc> in <module>()
----> 1 None.__getattribute__()

TypeError: expected 1 arguments, got 0
{% endhighlight %}

Let's try giving it the name of an attribute...

{% highlight ipy %}
In [37]: None.__getattribute__("__class__")
Out[37]: NoneType
{% endhighlight %}

Wow, we just discovered that the 'dot' operator really just calls the `__getattribute__` method of the object! So you can get any attribute that way? Let's try getting them all!

{% highlight ipy %}
In [38]: for name in dir(None):
    print name, " -> ", None.__getattribute__(name)
__class__  ->  <type 'NoneType'>
__delattr__  ->  <method-wrapper '__delattr__' of NoneType object at 0x10c00d7d8>
__doc__  ->  None
__format__  ->  <built-in method __format__ of NoneType object at 0x10c00d7d8>
__getattribute__  ->  <method-wrapper '__getattribute__' of NoneType object at 0x10c00d7d8>
__hash__  ->  <method-wrapper '__hash__' of NoneType object at 0x10c00d7d8>
__init__  ->  <method-wrapper '__init__' of NoneType object at 0x10c00d7d8>
__new__  ->  <built-in method __new__ of type object at 0x10c013a60>
__reduce__  ->  <built-in method __reduce__ of NoneType object at 0x10c00d7d8>
__reduce_ex__  ->  <built-in method __reduce_ex__ of NoneType object at 0x10c00d7d8>
__repr__  ->  <method-wrapper '__repr__' of NoneType object at 0x10c00d7d8>
__setattr__  ->  <method-wrapper '__setattr__' of NoneType object at 0x10c00d7d8>
__sizeof__  ->  <built-in method __sizeof__ of NoneType object at 0x10c00d7d8>
__str__  ->  <method-wrapper '__str__' of NoneType object at 0x10c00d7d8>
__subclasshook__  ->  <built-in method __subclasshook__ of type object at 0x10c00d988>

{% endhighlight %}

Wow, that saved some work, checking what they are and where they are from! Most seem to be part of the `NoneType` object, but some are from `object` or `type`. Weird!

Wait, is `None` an `object` ?

{% highlight ipy %}
In [39]: isinstance(None, object)
Out[39]: True
{% endhighlight %}

Apparently so! What else is an `object`?

{% highlight ipy %}
In [40]: isinstance(object, object)
Out[40]: True
{% endhighlight %}

{% highlight ipy %}
In [41]: isinstance(type(None), object)
Out[41]: True
{% endhighlight %}

{% highlight ipy %}
In [42]: isinstance(type, object)
Out[42]: True
{% endhighlight %}

Well, I heard python is object-oriented, but it seems oriented towards making *everything* an object.

So what does that mean? Does object have some stuff on it that you can do anywhere or something?

{% highlight ipy %}
In [43]: dir(object)
Out[43]: ['__class__',
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

{% highlight ipy %}
In [44]: len(dir(object))
Out[44]: 15
{% endhighlight %}

Holy smokes, that's like the same list that `None` has! Wait, is it exactly the same list?

{% highlight ipy %}
In [45]: dir(object) == dir(None)
Out[45]: True
{% endhighlight %}

Yes indeed! Aww wait, this means we learnt nothing interesting about `None` - it only has all the attributes that every other `object` has.  So maybe it really doesn't do anything!

But we've learnt some valuable lessons:

1. There is only one `None`
2. The type of `None` is `NoneType`
3. Most types let you create more objects of their type, but not `None`
4. `None` does nothing interesting
5. If you turn `None` into a `str`ing, it becomes `'None'`. If you turn `None` into a `bool`ean, it becomes `False`.

---

That's all we have time for in this blog post! Next time: `True` and `False` enter the picture in full focus.

