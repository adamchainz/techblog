---
layout: post
title: "Factory Boy Fun"
date: 2014-09-02 12:40:00 +0100
comments: true
categories:
---

![Factory.]
({{ site.baseurl }}/assets/2014-09-02-factory.jpg)

I've recently been working on improving the test suite at YPlan. The biggest
change I'm making is to move towards dynamic fixtures for our Django models
using [“Factory Boy”][1]. Essentially, factory boy gives you easy helper
functions to generate model instances quickly, rather than using static fixture
json files as Django recommends by default. It's a lot easier and means you
don't have to maintain these models - as well as giving you the ability to
generate test data locally via e.g. a custom management command.

## A basic factory

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

First thing to note is that I don't bother with the convention in the factory
boy docs and just call the factories after the model they create. You can then
then just import the `factories` module and call it like e.g.
`factories.User()`.

The second thing is to make things dependent even if they aren't needed by the
factory definition as it stands. For example, the above factory will always
return the same user, with username adam, because the `first_name` attribute is
fixed. However, we can call it setting the `first_name` and get a different user
with e.g. `factories.User(first_name='Johnny')` - since `username` and `email`
are dependent, they'll be set accordingly, and via the `django_get_or_create`
in the factory's `Meta`, we'll get a different model.

## Adding fuzz

Now, having a factory that always runs `get_or_create` for the same values
*unless* you pass in a different `first_name` *could* be useful, but it's
passing up on one of the more useful features of factory boy - adding fuzziness
to the test data. This is a great way of adding value to your tests since by
automatically always testing with a range of values you increase the width of
your tests and the range of errors you may catch.

Let's update the factory to use a range of values:

```python
import faker

faker = faker.Factory.create()

class User(DjangoModelFactory):
    # class Meta - as above

    first_name = lazy_attribute(lambda o: faker.first_name())
    last_name = lazy_attribute(lambda o: faker.last_name())
    # ... as above
```

Aha! What's [**faker**] [2]? It's a brilliant little utility library for
generating fake data with a ton of helper functions for things you'd otherwise
end up writing yourself. And again thanks to the dependencies we set up
with `lazy_attribute` above, we'll get a complete `User` with the username and
email filled in appropriately.

### Test structure

A quick diversion on your test structure - using fuzziness is great, but if you
get a failure that only occurs on *specific* values in your model, you won't be
able to recreate it without adding some control for the random number
generator. If you're using **nose**, you can add the [**nose-randomize**][3]
plugin. It will output the seed that is used to initialize the random number
generator as well as allowing you to control the seed by passing a
`--with-seed` flag when running the tests. As a bonus, it will also run your
tests in a random order, to prevent them from depending on each other!

## Internal Dependencies

Let's imagine extending the above `User` factory to allow us to create staff
members as well. The factory boy docs recommend subclassing for this, i.e.
creating a `StaffUser` factory that inherits from the `User` factory and tweaks
it as appropriate. This would be good, but since only a few attributes need
change for staff, we can just add a bit to the lazy attributes instead, and
just call `factories.User(is_staff=True)`:

```python
class User(DjangoModelFactory):
    # Meta, first_name, last_name - as above...
    is_staff = False

    @lazy_attribute
    def email(self):
        domain = "myapp.com" if self.is_staff else "example.com"
        return o.username + "@" + domain
```

This is a neat little trick to avoid breaking Occam's Razor: **“Do not multiply
entities beyond necessity.”**

## Building versus Creating

Factory boy is, at its core, a tool for passing a dict of keyword-args to a
function - and it also lets you choose the function. Subclasses of
DjangoModelFactory will by default call `Model.objects.create` and give you
back the resultant model. In Django world, `objects.create` calls the model's
`.save()` to persist it to the database.

Factories have two methods - `create` and `build`. `create` is the default that
calls `objects.create`, whilst `build` just instantiates the model and doesn't
call `save()`. We can make our factory do this by setting the relevant factory
boy `Meta` attribute:

```python
from factory import BUILD_STRATEGY


class User(DjangoModelFactory):
    class Meta:
        strategy = BUILD_STRATEGY
```

Now calling the factory with `factories.User()` will give us a user without an
`id`, i.e. not saved to the database, and you need to call
`factories.User.create()` to get an instance that has been saved. I think this
is better and have it as the strategy for all factories; it mirrors Django
better and means that your default is to create unpersisted objects - you can
write faster tests that don't touch the db when required.

### Django gotcha

Djanger djanger! Watch out for Django's type coercion behaviour, which only
occurs on *load*. For example, if we have a DecimalField on our model called
`price` that the factory sets to an int, it won't be coerced to a `Decimal`
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

Call `factories.Product()` will return a valid `models.Product` with a random
price, but that price will be an `int`. This is a weakness of Django more than
anything else, but it's worth correcting in the factory rather than fiddling
around with the `Field` classes:

```python
from decimal import Decimal
#...
class Product(DjangoModelFactory):
    #...
    price = lazy_attribute(lambda o: Decimal(randint(5, 100)))
```


## One-to-many dependencies

The **factory boy** docs are a bit thin on the ground for handling one-to-many
dependencies, although they go into depth on one-to-one and many-to-many
relationships. Thankfully the multipurpose `post_generation` hook can be used
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
            self._prefetched_objects_cache = {'deal': deals}

class Product(DjangoModelFactory):
    # as before
    group = SubFactory(ProductGroup)
```

We can now call `factories.ProductGroup()` to get a model instance back with
3 products in it, or we can call `factories.ProductGroup(products=5)` will add
5. The post_generation hook actually allows you take an arbitrary argument;
here I've called it count and used a number, but in other situations you may
want to use e.g. a special string shorthand.

The only problem with these factories is that you can't just generate a
`Product` by calling its factory now, without some mess... The
`SubFactory(ProductGroup)` will go cause the `ProductGroup` to generate
3 more `Product`s inside itself. In some cases this mightn't matter - you'll
always be worried about generating `ProductGroup` instances as opposed to
`Products` alone, but for the case I was involved in, I had to come up with a
solution.

Expanding with this code gave me both `Product` and `ProductGroup` factories
that could be sensibly called:

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

The only problem with this solution is that it introudces an otherwise useless
subclass of the `ProductGroup` factory, which is a less than ideal. It's not
that unclear though, which is good


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
