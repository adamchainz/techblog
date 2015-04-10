---
layout: post
title: "Python Mini Speed Boost 1: Literal Dicts"
date: 2015-04-10 21:20:00 +0100
comments: true
---

This is a quick investigation into making Python faster for constructing dicts.

When creating a dict python, there are essentially two styles:

1. Use the literal syntax: `mydict = {'a': 1, 'b': 2}`
2. Use the constructor: `mydict = dict(a=1, b=2)`

Some people prefer the latter since it leads to a more consistent syntax with
other instantiation calls, and means you don't have to quote all the names. But
which is faster?

Here are two test functions embodying the formats:

```python
def with_literal():
    return {'a': 1, 'b': 2}


def with_constructor():
    return dict(a=1, b=2)
```

Now if I run them with IPython's easy `timeit` integration, I get these results
on my Macbook Pro:

{% highlight ipy %}
In [2]: %timeit with_literal()
The slowest run took 11.08 times longer than the fastest. This could mean that an intermediate result is being cached
10000000 loops, best of 3: 194 ns per loop

In [3]: %timeit with_constructor()
The slowest run took 20.95 times longer than the fastest. This could mean that an intermediate result is being cached
1000000 loops, best of 3: 387 ns per loop
{% endhighlight %}

Let's skip over the 'slowest run' warnings for now - they are likely due to
something less deterministic happening during the runs, such as the garbage
collector collecting.

But the result we have is that for a two-item dictionary, the literal is nearly
twice as fast! What's going on?

Well, we can disassemble the functions to see their underlying bytecode:

{% highlight ipy %}
In [4]: import dis

In [5]: dis.dis(with_literal)
  2           0 BUILD_MAP                2
              3 LOAD_CONST               1 (1)
              6 LOAD_CONST               2 ('a')
              9 STORE_MAP
             10 LOAD_CONST               3 (2)
             13 LOAD_CONST               4 ('b')
             16 STORE_MAP
             17 RETURN_VALUE

In [6]: dis.dis(with_constructor)
  2           0 LOAD_GLOBAL              0 (dict)
              3 LOAD_CONST               1 ('a')
              6 LOAD_CONST               2 (1)
              9 LOAD_CONST               3 ('b')
             12 LOAD_CONST               4 (2)
             15 CALL_FUNCTION          512
             18 RETURN_VALUE
{% endhighlight %}

SOME EXPLANATION REQUIRED.
