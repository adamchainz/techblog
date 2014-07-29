---
layout: post
title: "DevOps Exchange London: Continuous Delivery"
date: 2014-07-29 06:51:06 +0100
comments: true
categories:
---

Last Thursday (24th July 2014) I went to the DevOps Exchange London Meetup on
[Continuous Delivery] [1]; here is my quick review of the talks and what I
took away.

**Edit:** the [official blog post] [14] is online too now - if any of the below
talks sound enticing, you can watch them or read the slides there.


## 1. Snakes & Ladders - Continuous Delivery Edition

The first talk was given by **Nathan Fisher**, who used to work at
[ThoughtWorks][2] and is now at [Maxymiser][3]. He had a lot of experience to
share from consulting and helping organizations move over to a Continuous
Delivery pipeline.
As the title suggests, his talk used the ‘Snakes & Ladders’ board-game as an
analogy for the transition to CD, where ‘snakes’ are the issues that slow you
down, and ‘ladders’ are the easy wins on the way.
He talked on a number of topics, giving good rules of thumb backed up by
anecdotes from transitions he'd worked on before.

I took a few main points away. He suggested to focus on the people
first, rather than getting dug in with the technology; people often have
‘infatuation’ with existing structures/code/processes/etc., so even when a CD
pipeline would be a clear win, it's hard to get existing solutions thrown away.
He has also seen incredibly complex, multi-person software release processes
and suggested that before making any moves, a consultant should sit down with
each of the people involved at each stage whilst they complete a release.
Another point he emphasised was that manual QA can still be very important
for a CD pipeline, despite the general emphasis on automated testing;
whilst, say, Facebook can easily afford to find out a handful of features broke
on a deployment, a low traffic, high value website can't , and should have a
strong manual testing & QA process.

## 2. How to Choose Tools for DevOps and Continuous Delivery

The next talker was **Matthew Skelton**, who is clearly very experienced and
co-founded [Skelton Thatcher Consulting][4].
He told us how they had consulted with many large companies in nearly every
sector (tourism, gambling, finance, ...),
who have often been around since the dot-com-boom and therefore have 15 year
old software to rework.
He recommended the [Continuous Delivery Book][5] and explained how useful it
can be for planning - just print out the title page of each chapter and paste
them to a whiteboard, and you have a visualisation of the ideal pipeline which
you can rank the current process against.

His talk was structured around 4 main points:

1. Value Collaboration
2. Avoid Learning Mountain
3. Avoid ‘Singleton’ Tools
4. Conway's Law

Under **1**, he explained how important it is to get everyone on the same page,
and using the same tools, even if they aren't all using them at the same level.
He used this to fluidly transition to **2**, under which he showed how good
Git can be for this - by using a simple Web UI such as Github, everyone can
start to understand how Git works without any complex command-line invocations.
For example, a QA tester can look over the repository log and understand what
changes are being made without needing to even understand the code.

This transitioned into point **3**, where Matthew warned against using
‘Singleton Tools’, by which be meant those you can only use in a single
environment (production).
For example, *some* monitoring tools are expensively priced which stops them
being viable for every environment, including developer machines.
His experience indicated that such tools prevent vital inter-team collaboration
(back to point **1**),
whilst free open source tools such as the [ELK stack][6] are easy enough to
deploy everywhere and foster those links.
For example, if a developer works day-to-day with the logs in Kibana on his
local machine,
he'll feel comfortable helping a DevOps debug a production issue with the same
tool when it arises.
I found this very useful advice, and plan to try it myself soon.

His final point was to be on [Conway's Law][7] was unfortunately skipped due to
lack of time, but he recommended that we look it up.
For completeness, here it is:

> organizations which design systems ... are constrained to produce designs
> which are copies of the communication structures of these organizations

I'm sure Matthew would have enlightened us with some extra tales of when he'd
seen it rear its head in the real world.

## 3. The Need for Speed

The final talk was by **Steven Thair**, who has been working in IT for 25
years, and has now co-founded [DevOpsGuys][8].
His talk covered the evolution of the DevOps movement, starting with some
things I'd never heard of ([PRINCE][9] and [ITIL][10]), and describing how the
movement to cloud application hosting was changing things.

He talked us through how you could convince your boss to give you more money
and time to implement CD, by pointing to how speed is becoming a business
necessity.
He referred to a Harvard Business Review article titled [‘Accelerate!’][11],
where John Kotter argues that speed is becoming more critical for business
survival.
He also quoted Jack Welch:

> [for a business...] If the rate of change on the outside exceeds the rate of
> change on the inside, the end is near.

Steven also backed up the claim with some statistics on number of deployments
for some large internet companies:

* cars.com - 300 per year
* Flickr - 10+ per day
* Etsy - 50+ per day
* Amazon.com - incredibly, *every 11.6 seconds* (see [Hacker News][12])

He also finally talked about ‘Shadow IT’, where he noted how IT is becoming so
pervasive in companies that more and more ‘IT products’ are being created in
other departments - for example “Dave the Excel wizard who ended up creating
some HTMl templates.”
Gartner predicts that in 3 years, 35% of all IT output will be coming from outside the IT budget;
such statistics can be used to convince your head of IT to help you move to CD
and claim some of that budget back!

---

Of course, no meetup would be complete without a mingling session, and the
DevOps exchange delivered here too. Much pizza and beer was provided and there
were plenty of interesting people to talk to.

I'd like to say thanks to the organizers, speakers, and Moonfruit for hosting.
If you're interested, I'd recommend you join the meetup for next time on
[meetup.com][13] - I'll see you there!



[1]: http://www.meetup.com/DevOps-Exchange-London/events/194288152/
[2]: http://www.thoughtworks.com/
[3]: http://www.maxymiser.com/
[4]: http://skeltonthatcher.com/
[5]: http://www.amazon.co.uk/Continuous-Delivery-Deployment-Automation-Addison-Wesley/dp/0321601912
[6]: http://www.elasticsearch.org/overview/
[7]: https://en.wikipedia.org/wiki/Conway%27s_law
[8]: http://www.devopsguys.com/
[9]: https://en.wikipedia.org/wiki/PRINCE2
[10]: https://en.wikipedia.org/wiki/Information_Technology_Infrastructure_Library
[11]: http://hbr.org/2012/11/accelerate
[12]: https://news.ycombinator.com/item?id=2971521
[13]: http://www.meetup.com/DevOps-Exchange-London/
