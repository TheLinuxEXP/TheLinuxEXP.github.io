---
title: "This website is back: a home for The Linux Experiment"
seo_title: A website for The Linux Experiment channel
focus_keyword: the linux experiment
description: "This website is back from the dead, and will be a home for The Linux Experiment content and extra things around the channel."
author: nick
image: /images/posts/plans-for-2027-the-linux-experiment/the-linux-experiment-website-capture.png
tags:
  - channel
date: 2026-10-18
last_modified_at: "2026-10-18 15:45:59 +0200"
---

This website hasn't been updated since 2023: the last real Linux-related article was about Plasma 5.27, so, yeah, that's a while back. Neither the codebase of the site, nor any articles have been changed since then, and I've always wanted to change that. Unfortunately, the previous structure of the website wasn't great for me personally.

So, here is what changed, and why this website is likely to get updated more often. I'll also cover a few changes and plans for the Linux Experiment, the [Youtube](/Going-Youtube-Full-Time/) channel that I run.

## Publishing Workflow

<figure markdown="1">

![A capture of all the files and folders of the Git repo for this website](/images/posts/plans-for-2027-the-linux-experiment/repo-for-the-website.webp)

<figcaption>This website is basically just a Git repo</figcaption>
</figure>

I'm a visual kind of guy. I like the command line as much as any Linux user, but when it comes to creating content, I like things to be as visual, GUI-driven as can be. And this website is basically a Git repo, meaning any article I publish is a markdown file that I need to write with the correct syntax, where I need to manually store images where I want them, name them properly, link to them properly in the markdown file, and then push to a repo so it can be visible online.

It's not complicated, but it's not efficient, and not visual either. It also meant yet another repo to update, where the codebase needed to be updated too, and I have not done that since the first article went live, simply because this is something that isn't interesting to me to handle.

When I'm done writing and the local website looks good enough, I can push in one click to the Github repo, and have the website be updated. That's it, simple, and efficient, and no need to rebuild an entire platform or to use something too heavy like Wordpress.

Now, the structure of the website is the exact same: it's still a static site, using Jekyll and Github pages. Each article is a markdown file, and the website is built from that. Where things have changed is that I now have an "admin" GUI to handle all the publishing.

## Using A.I.

And yes, I used A.I. to make that thing, which means I made nothing, I just asked for something to be made for me. It's a local thing that runs on my PC, and just gives me a visual way to write articles, slot in images that are automatically placed in the right folder, visualize the changes in real time, and push them to the actual website.

<figure markdown="1">

![A capture of the Admin graphical user interface I use for publishing to this website](/images/posts/plans-for-2027-the-linux-experiment/admin-gui.webp)

<figcaption>Basic, but gets the job done</figcaption>
</figure>

I'm not a big fan of A.I. (you can read my [Ethics](/Ethics) page to know more about my general stance on it), and I've made that clear repeatedly. I would never assume that what it writes is reliable enough to be published and open sourced, which is why my use of A.I. is limited to building tools that I can run on my own PC, and assess empirically: if they work for my own needs, I don't quite care if the code is trash, because in the end, it does what I need it to, and it saves me time, or makes a boring manual task a bit easier.

I would also never use it to generate text or images or videos, because at that point, well, what's the point?

So this little admin window I have is basically just a tool for me that lets me write more visually, set some stupid SEO related crap, and make sure that I can write without the previous blocker, which was the entire "update the website / publish that stuff" workflow.

<figure markdown="1">

![A capture of the "SEO" tab of the admin editor](/images/posts/plans-for-2027-the-linux-experiment/admin-seo.webp)

<figcaption>This stuff is boring, and this tool makes it easier</figcaption>
</figure>

I don't feel good about using A.I. for that, but in the end, it let me keep my own backend, update it to a reasonably working solution, and have a usable way of writing articles without starting from scratch.

## The end result

What does this mean? It means you'll now get an article per video. each new video I publish will have an article created automatically, where I'll write a short summary of the content (it will not be A.I. generated). Just to have a place I control, where I can replace the Youtube embed by something else if it ever comes to that.

This also means I'll write a few more articles here and there, with my thoughts on certain topics that wouldn't make sense as a video, maybe reviews for the games I played on Linux, maybe niche topics that would do terribly on Youtube and tank the channel, but would work in written form, that sort of stuff.

I could already do all of that, but the very idea of writing the thing in a text editor, manually adding links, copying images, pushing to git, checking that all is right, then fixing the mistakes and re-pushing, that stopped me in my tracks. I'm expecting the little GUI I have to be a big help to push me to write more.

It's also a more personal website, where I can talk about things that are fully unrelated to Linux. I already do a few things of that ilk in the Patroncast on Youtbe and Patreon (members only content), but for some things, a public outlet is interesting too.

## The ambition

There is no ambition for this website other than to be a blog and to list all the stuff I make. There's an RSS feed for people who want that, and that's about it. It's not monetized, there are no ads, and I don't think it will ever reach a point where it would make sense to have any ads anyway, it's just here to be a small home for my thoughts, videos, and links.

That's about it, no ambition, just a place I own outside of Youtube.
