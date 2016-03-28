---
layout: post
title: "Python Under the Hood 1: Literal Dicts"
date: 2015-04-10 21:20:00 +0100
comments: true
---

**_Disclaimer:_** This is a quick investigation into how Python works "under
the hood", and not necessarily a great guide for optimization. Not many
programs are limited by the speed at which they can construct dictionaries!
However, hopefully by understanding this micro-level phenomenon, we can get an
angle on what affects macro-level performance.

When creating a dict in Python, there are two (easy) methods:

1. Using the literal syntax: `mydict = {'a': 1, 'b': 2}`
2. Using the constructor: `mydict = dict(a=1, b=2)`

Most of the time you see the former, but some coders prefer the latter since it
leads to a more consistent syntax with other instantiation calls (such as
`mydictsubclass(a=1)`), and also saves a couple of characters (quote marks)
for each key. Withholding judgment on style, which is faster?

Here's a pair of simple test functions:

```python
def with_literal():
    return {'a': 1, 'b': 2}


def with_constructor():
    return dict(a=1, b=2)
```

Now I can I time them with IPython `%timeit` magic: (Macbook Pro, 2.6GHz. Using
Python 2.7 but the numbers on 3.4 were very similar)

{% highlight ipython %}
In [2]: %timeit with_literal()
10000000 loops, best of 3: 194 ns per loop

In [3]: %timeit with_constructor()
1000000 loops, best of 3: 387 ns per loop
{% endhighlight %}

It appears that literals are nearly twice as fast for this two-item dictionary!

Let's try that again with nine keys (a CPython dict has a default size of 8
slots, so this will force it to expand once):

```python
def with_literal2():
    return {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5, 'f': 6, 'g': 7, 'h': 8, 'i': 9}


def with_constructor2():
    return dict(a=1, b=2, c=3, d=4, e=5, f=6, g=7, h=8, i=9)
```

Timing:

{% highlight ipython %}
In [4]: %timeit with_literal2()
1000000 loops, best of 3: 583 ns per loop

In [5]: %timeit with_constructor2()
1000000 loops, best of 3: 1.07 µs per loop
{% endhighlight %}

Again, around the literal method is around twice as fast! What's going on?

We can disassemble the functions to a text representation of the underlying
bytecode (what the Python VM actually executes) using the `dis` module:

{% highlight ipython %}
In [6]: import dis

In [7]: dis.dis(with_literal)
  2           0 BUILD_MAP                2
              3 LOAD_CONST               1 (1)
              6 LOAD_CONST               2 ('a')
              9 STORE_MAP
             10 LOAD_CONST               3 (2)
             13 LOAD_CONST               4 ('b')
             16 STORE_MAP
             17 RETURN_VALUE

In [8]: dis.dis(with_constructor)
  2           0 LOAD_GLOBAL              0 (dict)
              3 LOAD_CONST               1 ('a')
              6 LOAD_CONST               2 (1)
              9 LOAD_CONST               3 ('b')
             12 LOAD_CONST               4 (2)
             15 CALL_FUNCTION          512
             18 RETURN_VALUE
{% endhighlight %}

The clue is in the difference in codes. In `with_literal`, there are
specialized codes - `BUILD_MAP` and `STORE_MAP` - that construct the
dictionary directly. In `with_constructor`, a `LOAD_GLOBAL` is required to find
what the name `dict` actually refers to (which basically amounts to a
look-up in the globals dictionary), before the arguments are strung together
and passed to it with `LOAD_CONST` and `CALL_FUNCTION`.

The `LOAD_GLOBAL` gives your code some flexibility it probably doesn't need -
for example, the name `dict` in `globals()` could theoretically be swapped for
some other class that quacks the same way, like `OrderedDict`. Most Python
programs don't need this flexibility though (when they say `dict` they mean
`dict`), and thus the lookup is a bit of a waste.

Hold that dial though! Don't run away to refactor your projects *right now* to
replace calls to `dict` with literals - that's almost certainly a waste of
time! Don't even try and enforce a standard on other developers with the naïve
claim "it's faster, I read a blog post". We're still talking nanoseconds here,
most likely don't matter for you :)

The only lesson I've learnt here is that whilst the two syntaxes give the same
result, only one uses the more specialized bytecodes; thus there are real
tradeoffs like this (essentially speed for flexibility) inherent in Python.
Maybe there may be more obvious coding rules to adopt out there that we can
find through timing and disassembly - tune in next time.
