---
title:  "Why you need a NAS: your easy private home server"
description: "Setting up a home server is probably the ultimate tool to stay as private as possible, but if you don't have the technical skills, or the time, then the next best thing is a NAS: it's not just for storage, it's for everything! "
author: nick
image: /images/posts/nas/default.jpg
tags:
  - Privacy

date: 2023-02-07

---

It's a well known fact that using cloud storage services from Google, Apple, Microsoft, or any big tech company can be a gamble with your privacy. And to avoid that, the easiest solution is to build your own home server, and host everything directly from the comfort of your house. But a lot of people might not have the technical skills, the inclination, or the time to make that jump, it's like building your own PC: even if you know how, it doesn't mean you want to.

Thankfully, there's a pretty easy solution: a NAS. These things might have initially been designed for file storage, but they've now matured into full blown home servers, with easy graphical interfaces and one click installable solutions that let you replicate virtually everything a home server could do, but without sinking so much time into learning how to actually do it.

So, let's take a look a why you should have a NAS at home, and, of course, if you want a video version of all of that text, well, you're welcome:

<aside>
{% assign id = "LBtEJ-iQbeg" %}
{% include youtube.html id=id %}
</aside>

## What's a NAS

<figure markdown="1">

![Tuner](/images/posts/nas/mynas.png)


<figcaption>This is a pretty big NAS. Smaller ones are of course available</figcaption>
</figure>


NAS stands for Network Attached Storage, but basically what it is is a computer in a small enclosure whose space is mainly taken by plenty of hard drives so you have all the storage space you want. They run specific operating systems designed to make them as easy to use as possible, with package libraries to add features, and easy to understand Graphical user interfaces to let you configure things even if you don't know anything about servers.

Think of it as a home server without the hassle of setting it up yourself, opening ports, using the command line to install things. It just takes care of all of that for you. By default, it only does file storage locally, but it's very easy to expand that, and add new features.

To write this article, and make the accompanying video, I used a Synology NAS, because they were kind enough to provide me with their DS1522+ NAS and a bunch of drives to slot in in order to make this video. Synology is one of the biggest NAS manufacturers, and they run their own NAS operating system called Diskstation manager. It uses Linux, but the OS that runs on top of it isn't open source. It has plenty of one click installable packages to extend the functionality beyond just file storage, and some of these are open source.

Of course, if what you want is more of a do it yourself approach, you could grab any old computer, attach drives to it, and install another NAS operating system, like TrueNAS or FreeNAS, but you'll need to ensure hardware compatibility, their interfaces are arguably not as simple to use as Synology's, and the package library might not be as complete.

Still, of course, everything I'll show here will also be possible on other NAS operating systems, using different packages, and their own interfaces. The goal here is to show what is possible with one of these devices, whatever the OS or manufacturer you pick.

## Setting things up


<figure markdown="1">

![Tuner](/images/posts/nas/slottingdrive.png)


<figcaption>Slot some drives in, and you're ready to go</figcaption>
</figure>

Let's see how you actually setup one of these things. First, you need to slot your drives in, so here are a bunch of 4TB drives that I'll insert one by one into the NAS. Pretty easy, you just remove the drive bay, you slot the drive in there, and you screw it in so it doesn't move, and you just pop that back in.

Once that's done, you plug your NAS, and then you connect it to your router or internet provider box, and you boot it up. To access the interface here, Synology just has a simple URL, but other NAS will also be accessible in the same fashion through a web browser.

You go through a first run setup to install the OS on the device, and let it reboot, and then you'll need to create a storage pool to actually make use of these drives. That's where the NAS operating system will really make a difference compared to running your own server: you'll be able to create a RAID array graphically, so the data is replicated onto multiple drives, and one drive failing won't take down all your files. That's something that requires a bit more knowledge on a Linux server that you'd set up manually, for example.


<figure markdown="1">

![Tuner](/images/posts/nas/firstrun.png)


<figcaption>Synology's DiskStation Manager has a very simple first run wizard</figcaption>
</figure>

And basically, once that's done, if all you need is file storage, then you got it. Here, on my Fedora laptop, I can just open the file manager, and I'll automatically see my NAS available. Clicking on it asks me to enter the password I setup during the first run install of the OS, and then I'm good to go, I can create a shared folder, and I can transfer files to it manually, copy paste anything, it's there as additional storage that I can use whenever I want.

I also have access to the OS interface, that basically is a grid of icons, straight from my webbrowser on my local network. Here it includes a nice set of utilities for managing resource usage, file storage, search, logs, settings, but also the Package Center, which will let me install whatever other applications to extend the features of the NAS.

## File storage at home


<figure markdown="1">

![Tuner](/images/posts/nas/storage.png)


<figcaption>That's a lot of terabytes</figcaption>
</figure>

Because of course, that's not all you might want to do with your files. For example, how do you share that file storage with others outside of your local network, or how do you access it when you're not home?

Well, I can quickly enable my NAS to be accessible from outside my local network. In the OS, I can just go to "external access", and create a domain name in a few clicks, using Synology as the provider, but I could have picked from a selection of other providers. I can also get a certificate so the connection uses HTTPS and is more secure.

It's not exactly a piece of cake, and you'll need to read a few tutorials for this kind of stuff, but it's still much easier than doing it using the command line on a regular server. And once that's done, I can use that domain name to access my NAS interface from anywhere in any web browser. Pretty cool.


<figure markdown="1">

![Tuner](/images/posts/nas/external.png)


<figcaption>Setting up external storage accessible from anywhere only took a couple of clicks</figcaption>
</figure>

And then, that's where the package manager becomes useful. For example, I can just install the webdav server package, which will let me access the storage on my NAS from anywhere on any network. In one click, it's added to my list of applications. I can just open it, enable HTTPS access, and that's it. 

Now, in my file manager, my webdav storage appears automatically, or I can just type dav:// then the domain name I just set up, and boom, I login with my NAS user, and my storage is mounted in my file manager, so I can access it from anywhere.

And if I want to auto sync files, I can use Synology Drive, which is basically exactly like Google Drive, but stored privately at home, and they have clients for every operating system, including Linux, and smartphones.

## Backups


<figure markdown="1">

![Tuner](/images/posts/nas/backup.png)


<figcaption>My laptop, and my desktop are now backed up to my NAS</figcaption>
</figure>

Next, let's talk Backups! Yeah, backups ARE cool, I swear. You need them. A good backup strategy is to have a local copy of your files on your computer, then a backup of that at home, and another backup of that outside of your home. Backup solutions are a dime a dozen, and you can just automate that with Synology Drive, or any other backup app for any other NAS.

For example, I could backup the content of cloud storage accounts, like Google Workspace, or Microsoft 365, although since a NAS can replace all of these cloud storage solutions, that's not something I consider super useful for me personally.

But you also have stuff like Active backup for business, which lets you, well, backup another NAS, multiple PCs, servers and even virtual machines to your NAS. Other NAS operating systems will also have packages to backup anything you want.

## Photo Collection


<figure markdown="1">

![Tuner](/images/posts/nas/photos.png)


<figcaption>Why bother with Google photos when you can store everything at home and still access it from anywhere?</figcaption>
</figure>

Now there's a thing everyone uses cloud storage for, but that a NAS will do better and more privately, and that's photo storage. Here again, let's take a look at the package center, where there's a neat little app called Synology Photos.

I can install it in one click again, and then access it from the operating system directly. And there we go, I have an online photo library, where I can add photos manually and even have face recognition if I want, that's running locally on my NAS, so everything is private. But if you have to manually upload everything, it kinda sucks. Fortunately, you can auto sync from your phone to your NAS!

I can install the Synology Photos app on my phone, and auto upload anything from there, photos and videos, and also view all these with the albums I configured, the face recognition if I have that enabled, and more. So, basically, it's Google or iCloud Photos, but stored at home, privately and securely, and you can still access it from anywhere.

## Media server

<figure markdown="1">

![Tuner](/images/posts/nas/plex.png)

<figcaption>Yes, I ripped these legally</figcaption>
</figure>

But we're just getting started. A NAS can also be used as a media server, to store your movies and TV shows that you have ripped totally legally from DVDs and Blu-Rays you absolutely own, and then to stream these to any device you want in your home, or outside of your home. For example, I can install Plex in one click, from the Package Center. I could also install JellyFin using the Docker app and its docker image.

Once it's installed, I can just configure it like any other Plex Server, by logging in to my account, or creating one, then creating a media library using folders I created in the Files app of my NAS, to keep things orderly, and that's it! Now I can run the Plex app from my smartTV or computer, connect to the server, and access all that media easily, and stream it like it was a streaming service, that I own.

Plex can also handle music, if you have a local music collection, but if you're more of an itunes person, there's an iTunes server app you can install on Synology's Nas, to be accessible by a large variety of music players, including on Linux.

## Productivity


<figure markdown="1">

![Tuner](/images/posts/nas/productivity.png)


<figcaption>Does this look like Google Docs to you?</figcaption>
</figure>


A NAS can also be a complete replacement for a Google Workspace, or Office 365 account. Here, for example, I can install Note Station for notes, or Synology Contacts and Calendars to have my own online solution to store all of that, and they have Synology office which is an office suite, integrated with your file storage, that lets you create and edit text files, spreadsheets, or presentations, straight from your NAS. It supports collaborative editing and it's compatible with Microsoft office formats, and it looks just like Google Docs, so it should be familiar.

On other NAS operating systems, you could also install stuff like Collabora, or OnlyOffice if you prefer. Basically, your NAS can become your full replacement for a Microsoft 365 account, or a Google account: you get all the same features and applications, but hosted at home, without giving your data to anyone.

Or, if you prefer a fully open source solution, you could also use your NAS to install Nextcloud, through a Docker image for example, and you'll get your own Nextcloud server, fully ready, with tons of storage accessible from anywhere.

## The rest

And that only covers the basics. Your NAS can also be used to host your own website, or even multiple websites on the same NAS. It can run an antivirus for you, if you plan to let windows users access your file storage, or to send them files from it that you might have gotten off the internet. YOu can even setup your own DNS server if you want. You can run a chat server, a VPN, basically anything a regular server can do, you'll find a one click installable package for it on your NAS operating system.

**That's the real draw of a NAS: it's a home server, but simplified. Not everything is foolproof, but it's always easier than setting up your own home server with, let's say Ubuntu server, and then configuring and installing everything manually**

## Price

<figure markdown="1">

![Tuner](/images/posts/nas/price.png)


<figcaption>A NAS doesn't have to cost you a lot of money</figcaption>
</figure>

Of course, we have to talk about the price, because you're buying a computer, and some drives. So obviously, you'll pay more in one go than with just a monthly cloud storage payment. But if you start adding things up, it makes total sense: you can have a small NAS for around 150 bucks, and a 2TB hard drive for another 50 dollars. That's 200 bucks, which is less than 2 years of monthly Google payments for 2TB. So if you plan to store stuff for 2 years or more, a NAS really makes sense, and when you want to add more storage, you can just slot in another drive without increasing any monthly payment.

And that's not counting the privacy advantages: whether you use a Synology Nas or any other system, you're storing stuff at home, without any data being sent to anyone, and you have full control over the hardware. So, if you don't feel like using the cloud, and you don't feel like you have the technical know how to run your own home server and install everything manually, then you definitely should get a NAS. It's more money upfront than cloud storage, but the advantages are absolutely worth it.

Hopefully, this showed you a couple of things you can do with these little devices. Most of my experience was using a Synology NAS, but any other NAS with any other operating syste will have the same capabilities. The packages you install might be different, and have more or less features, but the general feature set will be the same!
