---
layout: post
title: "DynamoDB: An Honest Opinion"
date: 2014-08-10 16:15:00 +0100
comments: true
categories:
---

![Dynamoooo dynamo. Dynamoooo dynamo.]
({{ site.baseurl }}/assets/2014-08-10-dynamo.jpg)



## The good

* cheap, simple
* json with some types
* don't need large number of people to operate - not too much to understand
  about how it works, and you can scale a table up to very large throughput for
  relatively little money. I did a calculation and it cost less than half of a
  MySQL solution for our big logging table.

## The bad

* capacity unclear level. want to load a large amount of data? Sit there clicking and raising the capacity dialogue every 5 minutes to increase until you're at the level you want.
* 64KB limit on values
*


## The ugly

* AWS support for local is shockingly bad
    * reported error with dynamodb local, as I documented at [x]
    * you tend to have to parse what a boto exception is saying from its message field. I found that messages for the same error, e.g. 'table does not exist', were written differently between the real DynamoDB and DynamoDBLocal.
    * in fact, there are many known problems with DynamoDBLocal, and that's why multiple alternative local implementations exist:
        https://github.com/mhart/dynalite (see the huge bug list here)
        https://github.com/ananthakumaran/fake_dynamo
* The backup process was ugly too, via AWS Data Pipeline (hence why I wrote `dynamodb-dumper`). I say *was*, because there is a new process that I haven't had a chance to try, although I had a click and the first thing it asks is for you to head off to another part of the AWS console to create some IAM roles.


## My refined opinion on ‘NoSQL’

