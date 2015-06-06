---
layout: post
title: "Swapping decimal for cdecimal on Python 2"
date: 2015-06-06 09:20:00 +0100
tags: [python]
---

![cdecimal and decimal]
({{ site.baseurl }}/assets/2015-06-06-statues.jpg)


Python 3 includes a faster re-implementation of the `decimal` standard library,
called [cdecimal](http://www.bytereef.org/mpdecimal/doc/cdecimal/index.html).
How much faster?

> “Typical performance gains are between 30x for I/O heavy benchmarks and 80x
  for numerical programs”.

Nice! Thankfully we don't have to port all our code to Python 3 before we can
use it; it runs on Python 2 as well. You can install it either by downloading
via the external URL listed on its [official pip page]
(https://pypi.python.org/pypi/cdecimal), or if that annoys you as much as it
annoyed me, you can `pip install` it from the [`m3-cdecimal` pip upload]
(https://pypi.python.org/pypi/m3-cdecimal) with `pip install m3-cdecimal`.

If your code is quite simple, you might be able to just swap `from decimal
import Decimal` to `from cdecimal import Decimal` to get an instant speed
boost. Unfortunately, if any of your dependencies imports `decimal.Decimal`,
this might blow up in any of several ways.

A more all-encompassing solution is to swap the two in the module cache
`sys.modules`, right at the top - before any other imports - with this snippet:

```py
import sys
import cdecimal
# Ensure any import of decimal gets cdecimal instead.
sys.modules['decimal'] = cdecimal
```

As long as you get the first lines of every one of your entry points, this
should work really well.

Unfortunately, at YPlan we run our application via a third party monitoring
script, so we don't have control over the very first lines of Python that get
executed. It also turns out the script ends up importing some dependencies that
import `decimal`, which would require a lot of brittle monkey-patching of these
modules if we wanted to do the swap at our entry point(s).

At first I thought this meant we were out of options, but googling lead me to
find an [eleven year old blog post on patching Python's standard library]
(http://bob.ippoli.to/archives/2004/02/22/how-to-patch-pythons-standard-library-without-touching-vendor-files/) by Bob Ippolito that looked like what I wanted.
It covers fixing a buggy Python interpreter in an old version of Mac OS X, but
the main technique is still just as applicable, though something you'd rarely
use. This post is therefore a bit of a recycle of that one for the current
issue.

Python imports modules from a search path, and you might be familiar with
extending this via the `PYTHONPATH` environment variable. However, you can also
add to the search path by creating `.pth` files as noted in the [Python site
module docs]
(https://docs.python.org/2/library/site.html). These are read during
interpreter initialization and normally contain one directory per line to add
to the search path. The real magic of `.pth` files is this little extra,
which the manual explains with a single short sentence:

> Lines starting with import (followed by space or tab) are executed.

Since `import`ing a module allows arbitrary code execution, we can use this to
swap `decimal` and `cdecimal` for *all* code run on our python interpreter,
before any program code is executed. Using a `virtualenv` means our system
Python will be unaffected so we don't need to worry about breaking any OS
tools.

First, we need to create a `.pth` file in the default search path at e.g.
`/path/to/virtualenv/lib/python2.7/site-packages/my_patches.pth`, containing
the one-liner:

```py
import my_patches
```

This will then try to import the `my_patches` module, which we'll create at
`/path/to/virtualenv/lib/python2.7/site-packages/my_patches.py` with:

```py
import sys
import cdecimal
# Ensure any import of decimal gets cdecimal instead.
sys.modules['decimal'] = cdecimal
```

Then it's done! It's quite easy to test, for example using `ipython`:

```ipy
In [1]: import decimal, cdecimal

In [2]: decimal is cdecimal
Out[2]: True
```

You can also check other modules are importing `cdecimal`, e.g.
`simplejson.encoder` which does `from decimal import Decimal`:

```ipy
In [3]: import simplejson.encoder

In [4]: simplejson.encoder.Decimal is cdecimal.Decimal
Out[4]: True
```

Ta-daa! The only thing that remains is to benchmark and see if your code is
actually faster. Enjoy!
