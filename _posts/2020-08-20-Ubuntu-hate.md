---
title:  "Why is Ubuntu Getting so Much Hate?"
description: "Ubuntu is the 'big dog' of Linux distros, and as such, people love to hate on Ubuntu, sometimes just because everyone does it. Let's see if it's deserved."
author: nick
image: /images/posts/ubuntuhate/header.jpg
tags:
  - Linux
  - Ubuntu
  - Video Companion

hidden: true
---


<figure markdown="1">

![Ubuntu 20.04](/images/posts/ubuntuhate/header.jpeg)

<figcaption>Ubuntu 20.04 is a fantastic distro, and Amazon-free as well!</figcaption>
</figure>

Ubuntu is the biggest distro out there. It had a transformative impact on the Linux desktop, helping to move it from "hobbyist project" to something that can, and is used by millions. From its inception in 2004 until today, Ubuntu has been working on the Linux desktop, with more or less success depending on the initiatives they took. And still, this distro, and its associated company, Canonical, are being criticized, dismissed and are generally getting a lot of hate lately. Let's see why!

If you want to see a video form of that article, here it is, if not, read on!

<p align="center"><iframe style="width:75%;height:300px;" src="https://www.youtube.com/embed/WpRi6nCuTcA" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></p>


### Data collection
Ok, the first thing that comes often first is the fact that Ubuntu spies on its users. This complaint usually is linked to 2 Ubuntu features: the Amazon web app, and the opt-out system information.
Ubuntu introduced an integration with Amazon when they started shipping Unity as a default desktop environment, and later, they added a reporting tool that collects sytem information and sends it back to Ubuntu to check on what their users are actually using hardware wise.

THe Amazon thing was bad. It sent unencrypted search requests to Amazon, for anything the users were looking for in the Unity dash, and it generally returned very bad results. Ubuntu actually enabled users to disable that feature a little later, and in the end, that Amazon integration turned into an affiliate link in the dash, that could be removed easily, and not used. Still, the community generally resented the distro for adding this by default.

<figure markdown="1">

![Amazon](/images/posts/ubuntuhate/amazon.png)

<figcaption>The Amazon webapp, before it got the boot</figcaption>
</figure>

I can understand that, since no one really wants ads in their software, but the goal here was monetization. Ubuntu is backed by Canonical, a company that, at the time, depended largely on Mark Shuttleworth for revenue. If that company wanted to keep existing for a bit longer, they needed to earn some money. This is probably not the happiest move they've made, but since this has been removed entirely from the current versions of the distro, I don't think people should hold that against them anymore.

Then there's the data collection. Ubuntu asks their users if they want to DISABLE the data collection after install, meaning that it's turned on by default. THis created outrage in the Linux community, arguing that Ubuntu had become spyware. Now, this is complete nonsense.

<figure markdown="1">

![Data Collection](/images/posts/ubuntuhate/datacol.png)

<figcaption>The data collection tool shows up at first boot.</figcaption>
</figure>

First, Ubuntu gives users an example of the data they collect: it's just hardware configs, nothing personal is sent or kept. It's less info than what the Steam user survey collects, and the goal here is to help Ubuntu tailor the experience for their users, looking at what hardware they use. SUre, it would have been better to make that data collection opt-in instead of opt-out, but that's what KDE Plasma has done, and they still took a lot of flak for it, even though it's entirely DISABLED by default.

The linux community is very privacy sensitive, and they don't take too kindly on any form of data collection, voluntary or not. I still feel the outrage has been overblown on this one, but to each their own.

### Unity and Mir

The second thing that often gets brought up is that Ubuntu tries to reinvent the wheel. Most projects that are cited here are Mir and Unity. Mir was a new display server that Ubuntu pushed when they were working on their new Unity desktop, to try and have a coherent solution for mobile devices and desktops at the same time, to work towards device convergence.

These plans failed, and Mir was then limited to Ubuntu Touch, which became a community project.

Unity was a desktop environment that shipped a new shell combined with GNOME applications, at the point where GNOME 3 was released.

For both these projects, Ubuntu took some flak, the community accusing them of reinventing the wheel, splitting the community's efforts for development, and just wanting to do their own things.

While these are valid criticisms, you have to remember that the competing projects, at that time, were far from ready. Ubuntu should have gone with Wayland instead of inventing Mir is a phrase we often read nowadays, and still, Wayland at the time just wasn't suited for what Ubuntu wanted to do. Wayland is just a protocol, and its implementation at the time, Weston was severely lacking. Mir was supposed to allow a less modular design, with more stuff relegated to the display server instead of the client, to guarantee more performance on ARM environments, which was where Mir would run as well: on smartphones and IoT devices. Wayland didn't meet these criteria.

Unity, on the other hand, was created because GNOME 3, at the time, was such a huge departure from what users were used to. GNOME 3 did away with most, if not all the conventions for what a desktop was in the minds of users. No menu bars, no task bar, no application list, no regular menu. Instead, they pushed the activities concept, did away with the minimize button, they genreally invented a whole new vision for the desktop.

<figure markdown="1">

![Unity](/images/posts/ubuntuhate/unity.png)

<figcaption>Unity got a few good ideas from Mac OS X.</figcaption>
</figure>

Ubuntu didn't want to break all of their user's workflow, and so they worked on something that users would be more familiar with, and added their own spin on things, with the dash, allowing users to search through the entire system, a dock, and a global menu bar.

THese two projects are often criticized as unnecessary, and as having hurt the development of competing initiatives. The problem here is that Ubuntu has a vision that differed from what the other projects had in mind, and these couldn't be reconciled, so they had to go their own way, or ditch what they felt the desktop should look like, or their plans for convergence. 

Problem is, these 2 projects were basically abandoned later, or at least transfered to the community. Mir, because Canonical just didn't achieve its vision for convergence, and Unity, because GNOME 3 got to the point where it actually became usable by anyone, and maintaining a whole separate desktop environment meant for convergence, when the convergence thing was dead in the water didn't make much sense.

Funny enough, they got some backlash for abandoning Unity as well, since people had started growing fond of the desktop environment.

In the end, I don't think we should criticize distros or projects for inventing new ways of doing the same thing. This is the strength of free software;: teams iterate on the same concept with different visions, that's how we get so much choice in terms of apps, of desktop environments, and distributions.

### Snaps

Snaps are another controversial point, that I would tend to put in the "they invented another way to do things instead of contributing to an already existing model" locker.

Snaps are a way of packaging and distributing software. They are generally criticized for being slow to load, creating new mount points in the disk utility, yes, really, and for being proprietary.

While snaps are indeed pretty slow to load, don't always respect the user's theme, and do use mount points to mount the snaps and allow the apps to run, the proprietary part is complete bogus.

Snaps themselves are completely open source, as is the way of creating them, running them. What is proprietary, however, is the snap store, the place where applications are distributed.


<figure markdown="1">

![Snap Store](/images/posts/ubuntuhate/snapcraft.png)

<figcaption>The Snap Store itself is the only proprietary component of Snaps.</figcaption>
</figure>

There is a good reason for this, though: Ubuntu doesn't want multiple store and repos popping up, to keep the snap store consistent for companies that would like to distribute their apps there. Snaps, just like flatpaks, try to solve the app distribution problem on Linux: with these formats, you can package your app once, and it will run anywhere. Companies that make software might want to distribute their apps on Linux, but if their app is displayed next to a lot of copycat applications that are left unchecked, or if their application get repackaged by other users, then they're just not going to go for it.

The snap store is a way to alleviate these concerns, and that's why most corporate software is available as snaps, instead of flatpaks, which is the community's choice for open source applications.

Now snaps can be criticized for a lot of things, and I generally agree that I'd rather use regular packages that are smaller, faster, and better integrated, than snaps or even flatpaks. You just have to remember that the decision to use snaps by Ubuntu is more than just a statement that they don't want to use other people's stuff. Snaps can also implement server side stuff, like Nextcloud, when flatpaks can't, or just don't at the moment.

### Other reasons

There are other reasons, less often expressed, for the hate Ubuntu receives. Ubuntu is popular. People that might not have heard of Linux might know about Ubuntu. Anyone that works in IT has heard about it, and probably not of Manjaro, or even Arch. Ubuntu is the big dog these days, and people don't like that.

The Linux community tends to like being edgy users, that use stuff that normies don't know about, or wouldn't use. Ubuntu has crossed that threshold for some time now. Ubuntu also is very noob friendly. They ship drivers by default, even proprietary ones, they tend to provide utilities for most beginners to get around to use their system and not have to discover everything by themselves. This is actually what made them that big in the beginning: they took the Linux desktop and tweaked it in a way that made users that didn't know anything about Linux capable of using it.

THis is also resented by a fringe of the Linux community that feels Linux is a "hacker" system, something for technical people, and they don't want to use a "noob friendly" system. THe "start with ubuntu the move to arch" meme is still alive, and still complete BS. Ubuntu is a perfectly fine distro for beginners, and technical users as well.

The corporate backing is probably the last reason Ubuntu gets so much hate. Ubuntu is backed by Canonical, and as such, is not a purely community ran distro. Some people don't like that, they don't want companies intervening in the open source community, they dislike anything corporate. That's a valid point of view, but that's also a bit short sighted: when your distro reaches mass appeal, and starts making a bit of money, off of donations, or contracts with institutions to provide support for them, then they NEED a structure to handle that.

Let's not forget that Red Hat is behind Fedora, that Manjaro has also a company now, as does SUSE, or elementary OS. Most distros that want to achieve financial stability do.


So these are the main reasons why Ubuntu is getting so much hate online. As always, haters are more vocal than people who happily enjoy using it, and that's why we see more negativity than positive feedback.

Everyone is entitled to their opinion, and if you don't like Ubuntu, fine, it's your choice, and you don't have to use it. I just don't think we should take away what Ubuntu and Canonical have achieved for the Linux desktop, which is working towards making it more mainstream, more usable, and generally a lot better. They might have made some missteps along the way, but that's unavoidable when you want to make something bigger and better for everyone. 

Ubuntu is the base for a lot of user-focused distros, and there is a reason for that.
