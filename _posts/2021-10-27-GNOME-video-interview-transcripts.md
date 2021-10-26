---
title:  "Transcripts from the GNOME Theming Video"
description: "Some of the talks I had with various members of the community around GNOME and GTK have been really interesting, so here they are."
author: nick
image: /images/posts/itwtranscripts/note-taking.jpg
tags:
  - Linux
  - Open Source
  - Companion
  
hidden: true

---

I just published a video detailing the facts about GNOME's transition to become a platform, the move to libadwaita, and the impacts on GTK, on GNOME, on GTK-based desktops, and on theming. THis video was made thanks to a few questions I asked a bunch of people in the Linux community, including people working on GNOME, on elementary OS, on Fedora, or on the Yaru theme. Of course, I couldn't include all their answers in the video, so here are the transcripts of the conversations I had with them, so you can get more information.

But first, you should definitely watch the video!

<p align="center"><iframe style="width:75%;height:300px;" src="https://www.youtube.com/embed/w5TjoBxqBZw" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></p>


## Discussion with GNOME team members

The conversation started with GNOME team members, namely Alexander Mikhailenko, who also double-checked the answers with Chris Davies. Here are the questions and answers:



**The recent moves with the much improved GNOME Software and the use of libadwaita as the main "GNOME library" make me think that GNOME wants to be more than just a desktop, a collection of applications and panels, and lean more towards being a platform that developers intentionally target. Am I in the wrong?**

That's somewhat correct, though perspectives within GNOME can vary - I think most of us want GNOME to be a stable platform that developers can target, and to have a solid foundational experience for users out of the box.


**Are there other moves that we can expect to help solidify GNOME as a stable developer platform?**

Might be too broad - I mean there are so many different things people work on - e.g. Flatpak or Builder are huge steps in that direction, and those would be completely different people - so it's hard to answer as one person.


**Interoperability has long been a staple of Linux desktops. Is that focus towards being a more stable platform going to affect that interoperability with apps from other desktops, or is it going to help make it better?**

I think we can definitely work toward interoperability while still moving toward GNOME as a stable platform. For example, we can work on initiatives like a global dark style preference via cross-desktop components like the Freedesktop portals. It's not one or the other - a lot of what we need to do to have a stable platform for GNOME can lay the foundations for multiple stable platforms on a solid base.
This of course depends on what you call interoperability - for example, take GNOME and elementary. If you expect being able to run GNOME apps on elementary and the other way without breaking them - yes, it's getting better in this regard.
If you're expecting GNOME apps to look like elementary apps or the other way - then no - it doesn't work this way and I mean there's a good reason so many elementary apps are already hardcoding theme so it doesn't just fall apart on GNOME.


**GNOME will be moving all the "GNOME HIG related stuff" including the Adwaita theme, to libadwaita. What are the benefits of this move for Developers? for GNOME? For GNOME users?**

For app developers it means that you have a well defined target for developing apps. Historically this has been a bit all over the place. But here you have a single library - in line with the HIG, providing widgets implementing it, styles it mentions in one package. You don't need to think - ok HIG mentions this cool pattern, now how do I actually do that and find out that GTK has no widget for it, maybe there's a style class in Adwaita, though it seems broken in GTK4, but some another app implemented something similar 4 years ago, maybe you can copy-paste that and port it to GTK4 and whatever programming language you use if it's different - libadwaita avoids that kind of stuff.

For GNOME it means that we can iterate on the look and feel faster and in a more cohesive way. Previously when we wanted to change the look of GNOME, we had to change the default look of GTK - but we are not the only consumers of GTK. The same went for widgetry - when we wanted a new design pattern, often it needed to be implemented in GTK or someone else made a library for it. Thus, we had a conflict between the stability needs of GTK and the design goals we had for GNOME applications. GTK also moves very slowly - and for the past few years GTK3 has been frozen with no new features being added to it. Meanwhile, if GNOME needs some additions - well you can't have that.

For users it means multiple things. GTK4 itself is more neutral - e.g. right now elementary hacks around message dialog layouts to make them less GNOME-like and more elementary-like - I mean that's just not ok. Now we can put GNOME-specific widgets like that in libadwaita and leave GTK alone so it's more neutral. Inside GNOME you get better and more consistent apps. Look at Settings and how it has million different list row styles, sometimes different within the same page. This directly ties to what I've mentioned wrt developer experience - if apps are forced to do custom stuff, they will, and there will be no consistency whatsoever.


**We often hear that this move marks the death of theming on GNOME, that no themes will ever work again. Is there any truth to that, will it prevent users and distributions to apply themes to their GNOME desktop?**

Theming as we know it for GTK apps is not going to be supported by libadwaita. It's highly unlikely we'll have any API for loading arbitrary stylesheets. That said, there are things that we're having discussion about going forward. To be perfectly clear here: nothing is set in stone, so don't rely on anything happening, but: there have been talks of supporting different accent colors on a system level. We're also planning to work with Canonical on leveraging our planned recoloring support into an API for vendors to set specific colors. And - there are at least 2 more ways to sideload a theme anyway, they are just more clearly unsupported.



**The GNOME project has always been pretty clear about themes: they're not a supported feature since GTK3, and their current implementation is considered a hack. Can you explain the technical reason for that, in simple terms?**

This one is hard to answer concisely, since the length kinda shows the absurdity of the situation, so a wall of text:

Say you're a developer and need to know the current accent color - e.g. you want to draw a graph in that color. How would you do that?

You can check public colors themes expose - and get theme_selected_bg_color because it's blue in Adwaita. Then you try it on elementary and find out it's half-transparent there. Or that some theme doesn't even export it - after all it's not an API and there are 0 guarantees it's there. Or maybe it's exported but it's a bogus color that doesn't match anything in the UI at all.

Maybe you can render a widget and check its background color. Like a checkbox. Oh, but it's a gradient, not a flat color. Or maybe the whole thing is a png image. There's no way to check anything in that case.

Fine, let's draw a checkbox and pick pixels - it's getting ridiculous but maybe it works. So you get the right color on Adwaita and elementary, and... purple on Ubuntu and green on earlier versions of Ubuntu. Or maybe your theme has grey checkboxes - we used to have that in GNOME. So that's not reliable either.

But how would you actually do that then? Who knows.

Another example: you're developing a text editor and want to provide a light/dark switch that changes the UI and the editor colors. To switch the editor colors you need to know whether the UI is light or dark at the moment. And if you guess wrong you may get dark text on dark background, or the other way.

You might think - if I set light, why wouldn't it be light, but maybe you're using a theme that overrides light variant to be like dark, such as the ones Ubuntu and Pop expose in settings. So you have to check.

You can take an advantage of the fact their names both end with the word dark and check that, since we know the theme name. So you check the theme, but if it doesn't actually exist - the app can't know it doesn't exist, so you get light Adwaita and think it's dark - fail. Or maybe it does exist but it's called Something-midnight. That fails too.

So, again - how would you do that? Are apps not allowed to have features like that just because themes exist?

With libadwaita you can rely on things being there, documented and working as documented.


In other words, As Danielle put it earlier in a tweet, they are CSS frameworks more so than themes. Apps rely on them, and if they can't do that, they can't do very simple things.



**Other desktops manage to handle theming, seemingly without issues, for example KDE. What is the difference that prevents GTK or GNOME to follow in these footsteps?**

It breaks too - like last time I tried it I switched to a different theme and dark color scheme and got a dark on dark scrollbar in Konsole, light text on light toolbar, white on light orange Updates row in Discover, clipped titles in system settings. And another thing is - anything even remotely custom doesn't follow themes - for example, cards in Discover or system monitor, sidebar in system settings. It doesn't mean KDE is bad - but I think the claims that it doesn't break with theming are downplaying issues is well.



**What are the solutions that could be worked on to allow distributions and users to still retain some control over how GNOME looks? I'm thinking about the coloring API specifically.**

I think I've already answered it in 5.



**Developers can decide to stick to default Adwaita for their applications. Would a coloring API allow to bypass that, or would the colors set by the users or the distro be ignored in that case ?**

If an app wants to use certain colors, that's final - see 6. for what happens when it's not the case. Any settings or vendor API would only change defaults, which apps can then additionally override.

