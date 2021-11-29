---
title:  "How I use elementary apps for work"
description: "I recently showcased 17 apps for elementary OS that you can install on other distros. Here is how I use some of the for my daily work."
author: nick
image: /images/posts/17apps/Splash.jpg
tags:
  - Linux
  - Open Source
  - Apps
  - Companion
date: 2021-10-26

---

I just published a video showcasing 17 applications that are designed for elementary OS, but can be installed on any other distribution, and I tend to use a lot of them daily, so here are my use cases for these wonderful apps (or programs if you hate the word apps).

But first, you should definitely watch the video!

<p align="center"><iframe style="width:75%;height:300px;" src="https://www.youtube.com/embed/pyg615mdZeQ" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></p>


## Clips, the clipboard manager


<figure class="half" markdown="1">

![Clips](/images/posts/17apps/clips.png)


<figcaption>Clips on my Fedora desktop</figcaption>
</figure>


Clips is that cute little clipboard manager that stores anything and everything. Of course, it's using  X.org, because it's insecurely getting access to virtually anything you copy from any other app, and it doesn't work on Wayland for now, but since I'm still stuck on the X.org side of Linux, thanks to my reliance on Nvidia GPUs, I can enjoy its benefits.


I only use Clips as a complete repository of everything I ever copied. If I remember copying something but can't be bothered to find the file back again, or the webpage, or the link, I just open Clips, and find it there, thanks to the handy search. It's super useful when writing the scripts for the Linux news videos, where I have to copy tons of links, but also for various research whenever I work on a video. Ever since I started using Epiphany, it's also become some kind of password manager, since Epiphany tends to really fail at filling in your login forms, even with the credentials stored in its password database. I should probably use a real password manager for this, though.



## Planner, the todo-list and project manager


<figure class="half" markdown="1">

![Planner](/images/posts/17apps/planner.png)


<figcaption>Planner on Fedora</figcaption>
</figure>

I've already talked a lot about Planner, but it's still my favorite application for managing tasks and projects, even though I don't use it as often. Nowadays, it's more for personal stuff. All the channel stuff lives in my Nextcloud instance, but for the work I do as a freelance for OpenFly, and for my personal tasks, I still rely on Planner. It's fast, it's beautiful, and reliable. I basically just keep it opened at all times, and write anything I need to do inside of it. I take a look at it every morning, and cross off whatever I feel like doing on that particular day.

It's a basic use case, and if it supported better caldav sync, I'd use it for the channel as well, but for now, it shows all completed tasks even though you don't want it to, and it groups all projects synced through Caldav in a "Caldav" category, which isn't super useful if you want to organize them with your other projects.


## Norka, the continuous text editor


<figure class="half" markdown="1">

![Norka](/images/posts/17apps/norka.png)


<figcaption>This script, being written in Norka</figcaption>
</figure>

Norka looks decidedly better on elementary OS than in GNOME, with the old style icons not doing it any favors on the latter, but it's still a super handy tool.

I use it to write my video scripts, in markdown. I save all files inside my Nextcloud / Notes folder, so these scripts are synced on all my devices. I'm starting to use it to write these articles as well, as I only apply simple markdown syntax and a few tags before pushing the article to my Github repo where Github pages and Jekyll do their magic and turn it into an article. Norka allows me to write without any distraction, which is what I'm asking of a text editor, and it supports the wonderful Solarized dark color scheme, so I'm happy with it.

## Resizer, the image resizing tool


<figure class="half" markdown="1">

![Resizer](/images/posts/17apps/resizer.png)


<figcaption>Resizer, doing what it does best</figcaption>
</figure>

Resizer is my go-to to resize images, whether it's to slot them in a Gitlab issue for my freelance work for OpenFly, or for one of these articles, that I promise I'll write more of as time goes by. It's a super useful tool, speedy, and reactive.

I wish it didn't add the new dimensions to the images and it just erased the original, but it still serves its purpose. It doesn't respect my dark theme on GNOME though, like a lot of these apps, which is too bad, but the future "dark style preference" portal should allow that to be solved.


## Optimizer, the image resizing tool


<figure class="half" markdown="1">

![Optimizer](/images/posts/17apps/optimizer.png)


<figcaption>Optimizer has alreaady optimized everything there is to optimize</figcaption>
</figure>


Obvious use case for that one as well, I guess. I use it mainly to reduce the file size of any image I'm going to use for articles on the OpenFly website, on Gitlab issues, or for these articles. It's super straightforward, you can put multiple images in it, and I honestly never could tell the difference between an unoptimized image, and one that it had handled. In the end, it's a great little utility, that I don't use everyday, but that comes in handy whenever I get one of these "File size must be under Whatever Mb" messages.

## Annotator, the screenshot annotation tool


<figure class="half" markdown="1">

![Annotator](/images/posts/17apps/annotator.png)


<figcaption>It has become one of my best allies in the freelance work I do</figcaption>
</figure>

Annotator is a newcomer to my app roster, but it has quickly risen to the rank of "this is the best thing I ever used".

See, my old day job now turned freelance work, has me reporting bugs a lot. And what better way to do that, other than a nice annotated screenshot. I used to use GIMP or Pinta to do that, but Annotator is much, much faster to open and to use, and it's been a HUGE time saver. I also use it to annoy our graphic designer, whenever he bothers sending us mockups and designs. I take immense pleasure in wrecking is work with crappy arrows and superimposed text. It's just delightful.

## Tuner, to relax


<figure class="half" markdown="1">

![Tuner](/images/posts/17apps/tuner.png)


<figcaption>A nice way to discover new music and not fiddle with playlists</figcaption>
</figure>

Tuner is my go-to app when I need to relax with music. See, I'm a Youtube Premium subscriber, so I got access to Youtube Music, which isn't bad per-se, but still makes me feel the need to fiddle with playlists, add or remove tracks. Basically it's not a passive listening experience on my desktop.

Tuner solves that: I don't decide the programmation or playlist, just the genre and the webradio. If I really LOVE a song, I can peek at the name and add it to my Youtube Music playlists, but if not, I can just let that play in the background and not worry about curating anything. It's great.


And that's about it! I also tend to use Mixer, Outliner and Minder from time to time, but not in any "officially part of my workflow" capacity. I love that these apps are available anywhere thanks to Flatpak, and I can keep the same workflow on my desktop and laptop, even though they're not both running elementary (only the laptop has that honor). 

I hope you found value in these as well!


