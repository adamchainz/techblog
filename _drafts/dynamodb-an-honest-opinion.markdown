---
layout: post
title: "DynamoDB: A Complete Review"
date: 2014-08-10 16:15:00 +0100
comments: true
categories:
---

![Dynamoooo dynamo. Dynamoooo dynamo.]
({{ site.baseurl }}/assets/2014-08-10-dynamo.jpg)

## Who am I, what is this


At Memrise, was looking at moving big logging table (>100GiB) away from main
MySQL DB. I was a one man team at the time and looked around for any
easy-to-setup DB, and lo and behold, AWS had an offering that would work. Let's
see what they have to say:

> [DynamoDB] [4] is a fast, fully managed NoSQL database as a service that
> makes it simple and cost-effective to store and retrieve any amount of data,
> and serve any level of request traffic. Its reliable throughput and single-
> digit millisecond latency make it a great fit for gaming, ad tech, mobile and
> many other applications.


We'll inspect these claims later.


During this time I also became the author of [DynamoDB Utils] [2] which
contains my parallelized backup and restore utilities `dynamodb-dumper` and
`dynamodb-loader`. They're the fastest and easiest to use single-machine tools
available, and as far as I'm aware in use by a couple big companies such as
[FILLMEIN][]. I had to build them because the AWS-provided backup process is so
frustrating.


I've since moved on from Memrise, and thus haven't used DynamoDB in a while. So
the dust has settled and I've come to a full, reasoned opinion, and thought I'd
write it up. This post is structured like the wild west - the good, the bad,
and the ugly.


## The good


I'll be brief on the good, because the AWS marketing speak is full of it.


The main good point is that DynamoDB is simple. You can throw JSON at it (and
you probably already know JSON),
there's a small learning curve of just hash/range attributes and types, and you
can do a limited set of query operations. There's a vague idea that your data
is sharded and you don't know how exactly, but that's fine, it's what you're paying for. It's really easy to get
going - you can indeed create a table in minutes
and start writing to it, and there is no ops work to do on the side. There are
no complicated details to worry about for concurrency - they have a simple
last-write-wins policy. (Although this isn't always great, as we'll see.)

So basically, you can learn everything about DynamoDB in an hour or so.

Secondly, it is also cheap. I compared the pricing to a MySQL instance dedicated to the
single log table, estimating reads and writes, and it came out less than half the
price. It also gets cheaper the bigger your scale! (Although some of these savings will
cost you back in dev time though, as we'll see.)


The last thing I'd note is that whilst DynamoDB is, of course, closed source,
there are quite a few open source projects around it.  An ecosystem is always
important as it means most of the simple problems will have been solved.


## The bad

No ability to add indexes to tables, you have to delete them and rebuild
them. This compounds with the AWS metaphor of release early, upgrade often,
which means that several features, such as global secondary indexes, which
have been released since the inception of DynamoDB, would be totally
unavailable without an upgrade.

No modifications is very painful - my experience is that no one can perfectly
predict their data access patterns up front, and adding indexes is a must. Any
such change must be done with either downtime for a full dump-n-load, or with
app-level logic to handle working with the two tables.

Additionally the index model is simple, it can only be done on one column, and
for more complex requirements you may end up *maintaining your own* indexes
in code as extra tables like [these guys did] [3].

* capacity unclear level. want to load a large amount of data? Sit there
  clicking and raising the capacity dialogue every 5 minutes to increase until
  you're at the level you want.
* 64KB limit on values
* boto api is rubbish and in two pieces. thnakfully there is PynamoDB to
  restore some sanity
* Unlike open source databases, or in fact, just any software you can install, DynamoDB isn't easily tested or benchmarked. You just have to kinda trust Amazon that everything's okay. There's a fantastic series of blogposts by Kyle Kingsbury entitled 'Call me maybe' which inspects the CAP tradeoffs of many distributed databases using his ‘jepsen’ utility to cause network partitions. Of course, no such post can ever exist for DynamoDB, and you have to take their word for it that it's alright. The closest post is on [Riak] [1]


## The ugly


Firstly, the syntax of the JSON used in the API is ugly. As a developer you'd
hope that you could just use a nice abstraction layer on top, which you mostly
can, but at some point it is inevitable that you will have to deal with the
underlying communication, which is exceedingly verbose.

As an example, I've gotten a query for a single item from the [API reference]
[972]. Here it is formatted as SQL:

[972]: http://docs.aws.amazon.com/amazondynamodb/latest/APIReference/API_GetItem.html


```sql
SELECT LastPostDateTime, Message, Tags
FROM Thread
WHERE ForumName = "Amazon DynamoDB" AND
      Subject = "How do I update multiple items?"
```

But the operation in DynamoDB looks like this (ignoring the headers):


```json
{
    "TableName": "Thread",
    "Key": {
        "ForumName": {
            "S": "Amazon DynamoDB"
        },
        "Subject": {
            "S": "How do I update multiple items?"
        }
    },
    "AttributesToGet": ["LastPostDateTime","Message","Tags"],
    "ConsistentRead": true,
    "ReturnConsumedCapacity": "TOTAL"
}
```

One specifically ugly bit is that you can't just use JSON strings, you have to
wrap them in objects to declare type like `{"S": "MyString"}`. Also this is
about the shortest operatiosn get - I was planning on showing a `Query`
operation, but it would take up half the post!

AWS consistently manage to use JSON like XML - API calls to CloudFormation are
even uglier and allow you to write 'function calls' in JSON as nested objects
with specific keys.


Secondly, the idea of accessing your database over HTTP isn't the most
appealing. I can understand it's best for marketing DynamoDB as interoperable
makes it quite easy to write a client in your language of choice, but there is
still an overhead for HTTP, even in the same data centre.

The next ugly bit was **DynamoDB Local**. This is the AWS-written mock tool that runs
locally so you can unittest against the same API. In short, it doesn't let you query against the same API.

I found it amazingly inconsistent, for example, error responses would be
completely different. Here's a code fragment around dealing with the response
that each gives for trying to create a table that already exists:

```python
try:
    return _Table.create(**self._creation_kwargs)
except JSONResponseError as e:
    # DynamoDB, DynamoDB Local
    msg = e.body.get('Message', e.body.get('message', ''))
    if (
        msg == 'Cannot create preexisting table' or  # DynamoDB
        msg.startswith('Attempt to change a resource')  # DynamoDB Local
    ):
        return _Table(**self._creation_kwargs)
    else:
        raise
```

They managed to not match on both keyname and textual content of the error.
It's also really ugly determining *what* the error was by parsing the string
content of the response!

There's even an open source local mock called [dynalite] [144] that has the
long list of mismatches and fixes them in its reimplementation. That this
exists reveals that DynamoDB is still very self-serve in, which is
disappointing.

[144]: https://github.com/mhart/dynalite

There were also some problems getting DynamoDB Local running and I had to
contact support, and find and [document a fix] [312] to a java path error I was
getting when launching it on OS X.

[312]: https://github.com/adamchainz/dynamodb_local_utils

* The backup process was ugly too, via AWS Data Pipeline (hence why I wrote `dynamodb-dumper`). I say *was*, because there is a new process that I haven't had a chance to try, although I had a click and the first thing it asks is for you to head off to another part of the AWS console to create some IAM roles. It's still on data pipeline.


## Conclusion

* DynamoDB was my first serious foray into ‘NoSQL’ databases. I didn't like it.



[1]: http://aphyr.com/posts/285-call-me-maybe-riak
[2]: https://github.com/adamchainz/dynamodb_utils
[3]: http://news.dice.com/2013/02/21/why-my-team-went-with-dynamodb-over-mongodb/
[4]: http://aws.amazon.com/dynamodb/
[5]: http://aws.amazon.com/blogs/aws/amazon-dynamodb-libraries-mappers-and-mock-implementations-galore/
