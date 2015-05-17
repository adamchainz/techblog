---
layout: post
title: "Factory Boy Fun"
date: 2014-09-03 21:20:00 +0100
comments: true
categories: [django]
---

![Factory.]
({{ site.baseurl }}/assets/2014-09-03-factory.jpg)

I've recently been working on improving the test suite at YPlan. The biggest
change is moving towards dynamic fixtures for our Django models using
[“Factory Boy”][1]. This library is essentially a tool that lets you define
simple helper functions to generate random, sensible model instances quickly;
by using them in tests you can avoid the static JSON fixture files that Django
recommends you use in tests by default. Factories are also general purpose -
they just generate data and use it to create a model - and so they can be
re-used to fill your development database rather than dumping from production.

## The problem

Here's a typical test case:

```python
class MyTests(TestCase):
    fixtures = ['basic.json']
    def setUp(self):
        self.user = User.objects.create(
            username='adam',
            first_name='Adam',
            last_name='Johnson',
            email='adam@example.com'
        )

    # do some testing ...
```

We have test data in two places with different maintenance strategies - ouch.
Firstly, the 'basic.json' file contains JSON objects with data to be passed to
the model constructor; and secondly, the call to `User.objects.create` which
contains data in a different format.

Also, it's really hard to tell which bits of the data the test *depends* on,
since the fixtures are shared between tests, and to call `create` on a model
you need to fill in all of its non-nullable fields, e.g. most tests don't care
about an email, but they have to declare it anyway. This is just noise.

If you've created more than a handful of tests you may have started extracting
some of the basics into your own helper functions, e.g. adding a `create_user`
method to your `TestCase`:

```python
class MyTests(TestCase):
    fixtures = ['basic.json']
    def setUp(self):
        self.user = self.create_user('Adam', 'Johnson')

    # and some tests ...
```

The noise is cut down, and this also looks like we could extend it to cover
everything that the static fixtures are doing (e.g. a
`self.create_basic_fixtures()` call). But these functions are a lot of work to
create and maintain, and if you want lots of flexibility, you will end up doing
a lot of work. Work? We don't like work!

## A basic factory

**Factory boy** rescues us here with its factories. You define them as classes,
but they act more like functions since attempting to instantiate a factory
returns an instance of the model instead (through a little Metaclass magic).

I've used the convention of creating a `factories` module alongside `models`,
and importing that to call `factories.User()` to generate a user. This avoids
some of the smurfiness that the factory boy docs produce with `UserFactory()`
all over the place.

Here's a basic factory that generates `auth.User` instances:

```python
# app/factories.py
import datetime as dt
from random import randint
from django.template.defaultfilters import slugify
from factory import DjangoModelFactory, lazy_attribute


class User(DjangoModelFactory):
    class Meta:
        model = 'auth.User'
        django_get_or_create = ('username',)

    first_name = 'Adam'
    last_name = 'Johnson'
    username = lazy_attribute(lambda o: slugify(o.first_name + '.' + o.last_name))
    email = lazy_attribute(lambda o: o.username + "@example.com")

    @lazy_attribute
    def date_joined(self):
        return dt.datetime.now() - dt.timedelta(days=randint(5, 50)
    last_login = lazy_attribute(lambda o: o.date_joined + dt.timedelta(days=4))
```

Calling this as it stands (`factories.User()`) will perform the same task as
the previous `User.objects.create` call. However, it brings with it some
awesome bonuses.

Firstly, the `lazy_attribute` calls mean the username and email fields are
filled from the first and last names. A call specifying one field, e.g.
`factories.User(first_name='Johnny')`, will have its username and email set to
sensible values, reducing typing and noise in our test code.

Secondly, the factory's `Meta` has `django_get_or_create` set, which
means the factory will call the Django built-in `User.objects.get_or_create` to
make the model, yielding only one user per username. This gets more useful when
we call several different factories for models with foreign keys to
User and we want them to share.

Lastly, the `date_joined` and `last_login` fields are automatically filled in
with sensible random values - what we call fuzzy testing. Since tests shouldn't
depend on specific values they don't declare, this is a good extension of the
factory - BUT we can make it fuzzier still...

## Adding fuzz

<img src="{{ site.baseurl }}/assets/2014-09-03-fuzzy-camel.jpg"
     style="width: 70%; margin: 0 auto" alt="Fuzzy Camel">

Having a factory which by default always returns the 'adam' user *could* be
useful, but it's more likely that you want the factory to give a different user
each time. Thankfully, fuzziness is one of factory boy's strengths. This is
also a great way of adding value to your tests since you'll always
automatically be testing with a range of values, so the range of errors you may
catch has increased.

Let's update the factory to use random names:

```python
import faker

faker = faker.Factory.create()  # separate to a factory boy Factory

class User(DjangoModelFactory):
    # class Meta - as above

    first_name = lazy_attribute(lambda o: faker.first_name())
    last_name = lazy_attribute(lambda o: faker.last_name())
    # ... as above
```

Aha! What's this [**faker**] [2]? It's a brilliant little utility library for
generating fake data via a ton of helper functions. And again thanks to the
dependencies we set up with `lazy_attribute` above in other fields, we'll get a
complete `User` with everything filled in appropriately.

### Controlling the Randomness

A quick diversion on your test structure - using fuzziness is great, but if you
get a failure that only occurs with *specific* fuzzed values, you won't be able
to recreate it without control over the random number generator used in your
tests.

If you're using **nose**, you can add the [**nose-randomize**][3] plugin. It
will output the seed that is used to initialize the random number generator on
each run, as well as allowing you to control the seed by passing a
`--with-seed` flag when running the tests. As a bonus, it will also run your
tests in a random order, to prevent them from depending on each other!

## Even Better Lazy Attributes

Let's imagine extending the above `User` factory to allow us to create staff
members as well. The factory boy docs recommend sub-classing for this, where
we'd create a `StaffUser` factory that inherits from the `User` factory and
tweaks it appropriately. This can be useful, but since only a few attributes
need changing for staff, we can avoid creating (and having to think about)
another class and just improve the lazy attributes instead, so we can simply
call `factories.User(is_staff=True)`:

```python
class User(DjangoModelFactory):
    # Meta, first_name, last_name - as above...
    is_staff = False

    @lazy_attribute
    def email(self):
        domain = "myapp.com" if self.is_staff else "example.com"
        return o.username + "@" + domain
```

Also, let's quickly note just how awesome factory boy's lazy attributes are.
Functions decorated with `lazy_attribute` are not called with `self` as the
model, but instead an instance of `LazyStub`, which calculates *all* its
attributes on access. Therefore, we can add any dependencies we wish, apart
from circular ones. If, e.g. `email` is called first, it will first go and
calculate `is_staff` and `username` (which depends on `first_name`), before
completing. If you want to understand more, the [source] [4] is quite
instructive.

## Building versus Creating

At its core, factory boy is a tool for generating and passing a dict of
keyword-args to a function - and it also lets you choose which function.
Subclasses of `DjangoModelFactory` will by default call `Model.objects.create`
and give you back the resultant model. In Django world, `objects.create` calls
the model's `save()` to persist it to the database.

But actually, the factory comes with two methods - `create` and `build`.
`create` is the default (and short-cutted by calling the factory directly) that
calls `objects.create`, whilst `build` just instantiates the model and doesn't
call `save()`.

In some cases, just `build`ing the model will suffice for a test, and will save
us the overhead of DB access. In fact, it might be more useful for us to make
factories default to building - luckily there's a `Meta` attribute to do that:

```python
from factory import BUILD_STRATEGY


class User(DjangoModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
```

Now calling the factory with `factories.User()` will give us a user without an
`id`, i.e. not saved to the database, and you need to call
`factories.User.create()` to get an instance that has been saved.

Personally I prefer this as a default as it mirrors Django more closely and
you'll hopefully write faster tests since DB persistence is something you have
to request.

### Django gotcha

Djanger djanger! Watch out for Django's type coercion behaviour, which only
occurs on *load*. For example, if we have a DecimalField on our model called
`price` that the factory sets to an `int`, it won't be coerced to a `Decimal`
at any point:

```python
# app/models.py
class Product(Model):
    name = CharField(length=16)
    price = DecimalField(max_digits=10, decimal_places=2)

# app/factories.py
class Product(DjangoModelFactory):
    class Meta:
        model = 'app.Product'

    name = lazy_attribute(lambda o: "Book by " + faker.name())
    price = lazy_attribute(lambda o: randint(5, 100))
```

Calling `factories.Product()` returns a valid `models.Product` with a random
price, but that price will only be an `int`. This is a weakness of Django more
than anything else, so we'll have to be a bit more careful with our types here:

```python
from decimal import Decimal
#...
class Product(DjangoModelFactory):
    #...
    price = lazy_attribute(lambda o: Decimal(randint(5, 100)))
```

## One-to-many dependencies

<img src="{{ site.baseurl }}/assets/2014-09-03-yucca-tree.jpg"
     style="width: 70%; margin: 0 auto" alt="Tree of dependencies">

The **factory boy** docs are a bit thin on the ground for handling one-to-many
dependencies, although they go into depth on one-to-one and many-to-many
relationships. Thankfully the multi-purpose `post_generation` hook can be used
to solve the creation of many dependent objects, with a little extra code.

Here's an example:

```python
from factory import post_generation


class ProductGroup(DjangoModelFactory):
    class Meta:
        model = 'app.ProductGroup'

    name = lazy_attribute(lambda o: "Products from " + faker.company())

    @post_generation
    def products(self, create, count, **kwargs):
        if count is None:
            count = 3

        make_product = getattr(Product, 'create' if create else 'build')
        products = [make_product(group=self) for i in range(count)]

        if not create:
            # Fiddle with django internals so self.product_set.all() works with build()
            self._prefetched_objects_cache = {'product': products}


class Product(DjangoModelFactory):
    # as before
    group = SubFactory(ProductGroup)
```

We can now call `factories.ProductGroup()` to get a model instance back with
3 products in it, or we can call `factories.ProductGroup(products=5)` to get
one with 5. The post_generation hook actually allows you take an arbitrary
argument; here I've called it count and used a number, but anything goes.

A slight problem with the above setup is that you can't just generate a
`Product` by calling its factory now, without some mess building up; the
`SubFactory(ProductGroup)` will go create a `ProductGroup` which in turn will
generate 3 more `Product`s inside itself. In some cases this might not matter
- tests can just always create groups and if they need products directly,
access them via the group. However, for a one-to-many setup I was working on,
it was necessary to work both ways.

Fortunately, I figured a way with factory subclassing:

```python
class ProductGroup(DjangoModelFactory):
    # as above


class EmptyProductGroup(DjangoModelFactory):
    @post_generation
    def products(self, create, count, **kwargs):
        pass


class Product(DjangoModelFactory):
    # as before
    group = SubFactory(EmptyProductGroup)
```

It's pretty straightforward, although it does introduce an otherwise useless
“empty” factory.

## Conclusion

Factories cut down on two things: firstly, large numbers of objects being
created in tests that are useless for most of the test cases but still need to
be in the static fixtures; and secondly, code noise in dynamically generated
fixtures. They're helping me tend towards a negative line count on the code
base, and if I were to start a new Django project, I'd make this the only way
of adding fixtures to the tests.


[1]: http://factoryboy.readthedocs.org/
[2]: http://www.joke2k.net/faker/
[3]: https://github.com/nloadholtes/nose-randomize
[4]: https://github.com/rbarrois/factory_boy/blob/master/factory/containers.py#L35
