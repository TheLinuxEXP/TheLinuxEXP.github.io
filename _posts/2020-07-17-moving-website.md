---
title:  "Moving the Website"
description: "If you had visited thelinuxexp.com before, you might have noticed the site has changed a bit..."
author: nick
image: /images/posts/movingsite/header.png
tags:
  - Personal

---
<figure markdown="1">

![The New Site](/images/posts/movingsite/header.png)

<figcaption>The new website, using elementary OS's blog template</figcaption>
</figure>

The website has changed! For those who follow me on Twitter, you might have picked up that I was moving the site to another solution. The original website, that I started at the end of 2019, was hosted and created with Wix. It was a simple solution: just select a basic template, add a few colors, and start writing, right? It took me a few hours to end up with something I liked, and I published 14 articles in total, some personal, some related to videos I had published, and some that were just random thoughts on various topics. The website had problems, though.

### Wix: not a great solution

<figure markdown="1">

![The Old Website](/images/posts/movingsite/oldsite.png)

<figcaption>The old website, made with Wix</figcaption>
</figure>


Wix might be fine if you don't have any time to start building your own website, or if you need to get something like an online shop running quickly. But for my use case, it was just overkill: my needs are super simple:
- Simple homepage to showcase the latest articles
- Ability to add images and youtube embeds
- Simple way of posting new articles
- Easy to tweak and customize to use the channel's colors

Wix provided all of that, but it also provided a ton of overhead. The website, while super simple, took ages to load: 13 seconds to just display the homepage, and almost 9 seconds to load the biggest article I've ever posted, with 149 different requests to load just that.

<figure markdown="1">

![So Many Requests](/images/posts/movingsite/somanyrequests.png)

<figcaption>The old website loaded articles around 10x slower than the new one</figcaption>
</figure>


The interface to manage the website is also a nightmare to use: it loads extremely slowly, accessing your posts is tedious, and it tends to keep the formatting of every text you'll copy and paste there, so you need to spend extra time to manage the various styles you want to use.

Wix wasn't working for me, and while it was easy to get started with it, it took too much willpower to actually fire up their editor and start writing there, which resulted in me not writing anymore, since I never had the courage to really use their image library, type in their slow CMS, and manage all the little details here and there.

### Moving to a static website

<figure markdown="1">

![elementary OS Blog](/images/posts/movingsite/eosblog.png)

<figcaption>>elementary OS's blog was exactly what I needed</figcaption>
</figure>

I fell in love with the elementary OS blog in the meantime; it's super fast, responsive, it adapts to your desktop's or phone's dark mode, and it just looks gorgeous. I decided to look into how they were doing things, and fortunately, Cassidy James and Daniel Fore are very open and have published a few tweets and articles about their blog that I read from end to end to try to figure out how to maybe replicate that kind of blog.

Turns out, it's super simple, and it's been made even easier by the fact that the elementary OS blog template is open source, and available from elementary's Github repo. I decided to grab it and see how I could get my own blog up and running using Github pages.

The setup was simple: just create your own Github repository, name it accordingly, and put the template in it. Once that's done, you just access the URL, which is your repository's name, and you're good to go!

I played with elementary's template to adapt it to the channel, and it was a breeze (even though it took me a while to remember a few bits of CSS, and to remove / tweak the various included blocks that I didn't need). Posting an article is super easy: I just create a new markdown file, add in some metadata at the beginning, and type my article's content in markdown. Then, I commit my changes, and push them to my Github repo, and the site updates a few minutes later. Super simple, and efficient, if you can handle 4 git commands.

The result is a slim, fast and super responsive website:
- It loads the homepage in 1.4 seconds
- The same article that I test-loaded in the old website? It now loads in 1.08 seconds
- This article only made 13 requests

Porting the 14 articles took me around 4 hours, to copy / past the content, and format it to markdown, as well as integrating the images and youtube embeds. The website set up in itself only took around 2 to 3 hours.

### Article writing workflow
Writing an article is pratty easy: I just fire up elementary Code, which has the local copy of my github repo opened as a folder. I create a new file or duplicate an already existing one in the "_posts" folder, and write whatever I want. I then format everything in markdown, adding header, images, links, and everything else.

<figure markdown="1">

![elementary Code](/images/posts/movingsite/code.png)

<figcaption>Writing this article in elementary Code</figcaption>
</figure>

For the images, I decided to store them in a folder in the github repo as well, and to make sure they're all relatively identical in terms of size, I use "Resizer", an elementary OS app that can be started from the right click menu in Files, and size them all to 720p in width. I then optimize them to reduce their weight, using "Image Optimizer", another elementary OS app that can be launched from the right click menu.

<figure markdown="1">

![Image Management tools](/images/posts/movingsite/tools.png)

<figcaption>These small tools are fantastic</figcaption>
</figure>

Once I'm done, I just open my terminal, and use git to add the files, commit the changes, and push them to the repo. After a short 2 minutes wait, the website is automatically refreshed and displays my new article!

### Some issues left
There are still a few issues I need to solve to make sure the website is perfect:
- Making the youtube embeds reponsive. For now, I use iframes, but that's a bit crappy: on desktop, they display fine, but on mobile, they have a fixed width, and that makes them overflow on the right side of the page. I'll need to look into how to integrate these better.
- Adding some kind of video carousel on the homepage for my latest videos: I'd like to display a small carousel of the most recent videos I uploaded to the channel, and to the gaming channel, and if at all possible, I'd like that carousel to be updated automatically, by pulling the latest videos from Youtube. My coding skills are not up to the task yet, so I'll need to look into that when I have some more free time.

And that's it for the new website! Now that publishing articles is a lot simpler, I'll probably write a lot more in here, either to add some content to an already published video, or just to ramble on some of the various topics and news in the Linux and open source world!

If you want to stay up to date with what I write here, you can subscribe to an RSS feed of all the articles by clicking the RSS button up in the header :)


