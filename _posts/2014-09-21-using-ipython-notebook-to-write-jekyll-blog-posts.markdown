---
layout: post
title: "Using IPython Notebook to Write Jekyll Blog Posts"
date: 2014-09-21 11:00:00 +0100
comments: true
categories:
---

![Yup, that's a Python]({{ site.baseurl }}/assets/2014-09-21-python.jpg "Skin of Huge Python - Palawan")

My [last blog post] [last] was written in IPython notebook, and my blog is in Jekyll. Here's how I hooked the two up.

[last]: {{ site.baseurl }}{% post_url 2014-09-20-python-concepts-part-none %}

First, I started by writing the first draft of the post in IPython notebook. You can do that by firing up the notebook server with:

```sh
$ ipython notebook
```

This lets you use the web interface to write up your post. Sections may be code, which is run by IPython and its output sent back, or markdown. It looks a bit like this:

<img src="{{ site.baseurl }}/assets/2014-09-21-ipython-notebook.png" class='screenshot' alt='IPython Notebook Interface'>

Once I had a bit of a notebook, I wanted to convert it to jekylly markdown. There's an ipython command for this - having saved the notebook, run:

```sh
ipython nbconvert --to markdown my-notebook.ipynb
```

This would probably work well for most posts. However, since I was trying to write a follow-along interactive session, I wanted the IPython `In [1]:` and `Out[1]:` prompts left in and highlighted correctly, which isn't what `nbconvert` does.

How should I solve this, but hack away?

The first thing I discovered is that `.ipynb` files are stored in the `json` format, something like this:

```json
{
 "metadata": {
  "name": "",
  "signature": "sha256:117cbff7008b2c2ea7334c76ccadd48a900275c02cd438d7ffd76c030fb87e0b"
 },
 "nbformat": 3,
 "nbformat_minor": 0,
 "worksheets": [
  {
   "cells": [
    {
     "cell_type": "markdown",
     "metadata": {},
     "source": [
      "---\n",
      "layout: post\n",
      "title: \"Python Concepts: Part None\"\n",
      //etc.
```

Brilliant. I can get at the cells in the notebook easily, and I can already see that for markdown cells the text is stored line-by-line in a list called `source` - won't be hard to convert that at all. The next step was to fire up IPython and load that json:

{% highlight ipy %}
In [1]: import json
{% endhighlight %}

{% highlight ipy %}
In [2]: nb = json.load(open('2014-09-20-python-concepts-part-none.ipynb'))
{% endhighlight %}

{% highlight ipy %}
In [3]: nb['worksheets'][0]['cells'][4]
Out[3]: {u'cell_type': u'markdown',
 u'metadata': {},
 u'source': [u"Aha, we get some output. `print` turns its input into a string so it can be output - and the `str`ing output of `None` is `'None'`. Let's check that `str`ing representation:"]}
{% endhighlight %}

That worked well. After a little more inspection I figured out how the notebook stored code with `input` and `output` as well as the different `output_type` options, for example:

{% highlight ipy %}
In [4]: nb['worksheets'][0]['cells'][3]
Out[4]: {u'cell_type': u'code',
 u'collapsed': False,
 u'input': [u'print None'],
 u'language': u'python',
 u'metadata': {},
 u'outputs': [{u'output_type': u'stream',
   u'stream': u'stdout',
   u'text': [u'None\n']}],
 u'prompt_number': 2}
{% endhighlight %}

Within a few minutes I had my first version of `ipynb_to_jekyll.py` ready from running little snippets in the shell to figure how it should work, then copy-pasting them into a longer script. The full script is available on my [github repo of useful scripts] (https://github.com/adamchainz/chainz-scripts/blob/master/ipynb_to_jekyll.py).

Running `ipynb_to_jekyll.py some-notebook.ipynb` creates/overwrites the relevant `some-notebook.markdown` file. I put everything in the notebook, including the jekyll YAML header (which is valid markdown too), and then just run this to create the post.

I had to tweak Jekyll here too. By default, it converts everything in your `_drafts` and `_posts` folders into posts - regardless of extension. So by putting the `.ipynb` file in there ready for converting, it generated gobbledegook json posts. Luckily, you can just edit `config.yml` to set:

```yaml
exclude:          ['*.ipynb']
```

And it forgets about them.

The next thing was highlighting. Jekyll is using Pygments' `pygmentize` command to add syntax highlighting to code blocks, and IPython's `nbconvert` library contains some extra lexers for properly highlighting the IPython prompts:

{% highlight ipy %}
In [5]: "Like this"
Out[5]: 'Like this'
{% endhighlight %}

However, `pygmentize` can't actually see them by default. A little google gave me [this package] (https://bitbucket.org/sanguineturtle/pygments-ipython-console/), but it was a little out of date, so I [forked and updated it](https://bitbucket.org/AdamChainz/pygments-ipython-console). And now, my code is highlighted correctly!

The last thing to figure out was auto-rebuilding. Great that I could convert, but I wanted to hit save in the notebook editor and see it appear as a post seconds later. Luckily there is a great utility [`fswatch`](https://github.com/emcrisostomo/fswatch) that can help us set up a pipeline:

```sh
fswatch -e 'checkpoint' -i '\.ipynb$' -e '.*' . | xargs -n1 ipynb_to_jekyll.py
```

A quick walk through the arguments:

1. `fswatch` watches for filesystem changes and outputs them on stdout. The final argument for it, `.`, just means watch the current folder.
2. `-e 'checkpoint'` means exclude files matching the regex `'checkpoint'` - IPython notebook writes checkpoint `ipynb` files that I don't want to be turned into posts.
3. `-i '\.ipynb$'` means include only files matching with `.ipynb` as their extension
4. A fallback `-e '.*'` is required to make it ignore any other filesystem changes.
5. `xargs` is a utility that takes input, rewrites it to commands. `fswatch` just pipes a list of filenames into it, the command we want to run is the last argument, `ipynb_to_jekyll.py`.
6. `-n1` means run as soon as you know about one argument - i.e. immediately on filesystem change. By default, `xargs` tries to gather up to 5000 filenames before running the command, but that would be useless here as I'd have to hit save 5000 times before the post was created :)

So now I have three terminal tabs open for just a simple blogpost:

1. `jekyll serve --watch --drafts` to get jekyll to auto-convert posts to html and serve them locally.
2. `ipython notebook` to open the notebook editor.
3. The above `fswatch` pipe to auto-convert notebooks to posts.

A bit complex, but it works! Maybe I'll simplify it one day with an overarching runner such as **Grunt** - but then again, if it ain't broke...

