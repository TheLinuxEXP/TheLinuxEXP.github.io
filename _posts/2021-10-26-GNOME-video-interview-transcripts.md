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
date: 2021-10-26
---

I just published a video detailing the facts about GNOME's transition to become a platform, the move to libadwaita, and the impacts on GTK, on GNOME, on GTK-based desktops, and on theming. This video was made thanks to a few questions I asked a bunch of people in the Linux community, including people working on GNOME, on elementary OS, on Fedora, or on the Yaru theme. Of course, I couldn't include all their answers in the video, so here are the transcripts of the conversations I had with them, so you can get more information.

But first, you should definitely watch the video!

<p align="center"><iframe style="width:75%;height:300px;" src="https://www.youtube.com/embed/Pdx_MwcMtnM" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></p>

Also to note: I wanted to get even more viewpoints, from people who had been critical of this move to libadwaita, including Jeremy Soller, from System76 and PopOS, and Joshua Strobl, who works on Solus, but they declined to comment, as they felt they had already stated their views. I respect that 100%, but I just wanted to mention it here, to fend off the "why didn't you talk to X" comments :) 

## Discussion with GNOME team members


<figure class="half" markdown="1">

![Alexander Mikhaylenko](/images/posts/itwtranscripts/AM.png)
![Chris Davis](/images/posts/itwtranscripts/chrisdavis.png)

<figcaption>Alexander Mikhaylenko (no pic available AFAIK) and Chris Davis, the GNOME contributors who answered my questions</figcaption>
</figure>

The conversation started with GNOME team members, namely Alexander Mikhaylenko, who also double-checked the answers with Chris Davis. Here are the questions and answers:


**The recent moves with the much improved GNOME Software and the use of libadwaita as the main "GNOME library" make me think that GNOME wants to be more than just a desktop, a collection of applications and panels, and lean more towards being a platform that developers intentionally target. Am I in the wrong?**

That's somewhat correct, though perspectives within GNOME can vary - I think most of us want GNOME to be a stable platform that developers can target, and to have a solid foundational experience for users out of the box.


**Are there other moves that we can expect to help solidify GNOME as a stable developer platform?**

Might be too broad - I mean there are so many different things people work on - e.g. Flatpak or Builder are huge steps in that direction, and those would be completely different people - so it's hard to answer as one person.


**Interoperability has long been a staple of Linux desktops. Is that focus towards being a more stable platform going to affect that interoperability with apps from other desktops, or is it going to help make it better?**

I think we can definitely work toward interoperability while still moving toward GNOME as a stable platform. For example, we can work on initiatives like a global dark style preference via cross-desktop components like the Freedesktop portals. It's not one or the other - a lot of what we need to do to have a stable platform for GNOME can lay the foundations for multiple stable platforms on a solid base.


This of course depends on what you call interoperability - for example, take GNOME and elementary. If you expect being able to run GNOME apps on elementary and the other way without breaking them - yes, it's getting better in this regard.
If you're expecting GNOME apps to look like elementary apps or the other way - then no - it doesn't work this way and I mean there's a good reason so many elementary apps are already hardcoding theme so it doesn't just fall apart on GNOME.


**GNOME will be moving all the "GNOME HIG related stuff" including the Adwaita theme, to libadwaita. What are the benefits of this move for Developers? for GNOME? For GNOME users?**

For app developers it means that you have a well defined target for developing apps. Historically this has been a bit all over the place. But here you have a single library - in line with the HIG, providing widgets implementing it, styles it mentions in one package.

You don't need to think - ok HIG mentions this cool pattern, now how do I actually do that and find out that GTK has no widget for it, maybe there's a style class in Adwaita, though it seems broken in GTK4, but some another app implemented something similar 4 years ago, maybe you can copy-paste that and port it to GTK4 and whatever programming language you use if it's different - libadwaita avoids that kind of stuff.

For GNOME it means that we can iterate on the look and feel faster and in a more cohesive way. Previously when we wanted to change the look of GNOME, we had to change the default look of GTK - but we are not the only consumers of GTK.

The same went for widgetry - when we wanted a new design pattern, often it needed to be implemented in GTK or someone else made a library for it. Thus, we had a conflict between the stability needs of GTK and the design goals we had for GNOME applications. GTK also moves very slowly - and for the past few years GTK3 has been frozen with no new features being added to it. Meanwhile, if GNOME needs some additions - well you can't have that.

For users it means multiple things. GTK4 itself is more neutral - e.g. right now elementary hacks around message dialog layouts to make them less GNOME-like and more elementary-like - I mean that's just not ok.

Now we can put GNOME-specific widgets like that in libadwaita and leave GTK alone so it's more neutral. Inside GNOME you get better and more consistent apps. Look at Settings and how it has million different list row styles, sometimes different within the same page. This directly ties to what I've mentioned wrt developer experience - if apps are forced to do custom stuff, they will, and there will be no consistency whatsoever.


**We often hear that this move marks the death of theming on GNOME, that no themes will ever work again. Is there any truth to that, will it prevent users and distributions to apply themes to their GNOME desktop?**

Theming as we know it for GTK apps is not going to be supported by libadwaita. It's highly unlikely we'll have any API for loading arbitrary stylesheets.

That said, there are things that we're having discussion about going forward. To be perfectly clear here: nothing is set in stone, so don't rely on anything happening, but: there have been talks of supporting different accent colors on a system level.

We're also planning to work with Canonical on leveraging our planned recoloring support into an API for vendors to set specific colors. And - there are at least 2 more ways to sideload a theme anyway, they are just more clearly unsupported.


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

It breaks too - like last time I tried it I switched to a different theme and dark color scheme and got a dark on dark scrollbar in Konsole, light text on light toolbar, white on light orange Updates row in Discover, clipped titles in system settings.

And another thing is - anything even remotely custom doesn't follow themes - for example, cards in Discover or system monitor, sidebar in system settings. It doesn't mean KDE is bad - but I think the claims that it doesn't break with theming are downplaying issues is well.


**What are the solutions that could be worked on to allow distributions and users to still retain some control over how GNOME looks? I'm thinking about the coloring API specifically.**

I think I've already answered it in 5.


**Developers can decide to stick to default Adwaita for their applications. Would a coloring API allow to bypass that, or would the colors set by the users or the distro be ignored in that case ?**

If an app wants to use certain colors, that's final - see 6. for what happens when it's not the case. Any settings or vendor API would only change defaults, which apps can then additionally override.


## Conversation with an anonymous Yaru Contributor


<figure markdown="1">

![The Yaru Theme](/images/posts/itwtranscripts/yaru.jpg)

<figcaption>The recently-ditched Yaru mixed theme</figcaption>
</figure>

I then got a bit of information from someone working on the Yaru theme, but this person preferred staying anonymous, so I won't provide their name here, as in the video. Here is what we talked about:

**GNOME decided to split all the HIG-related stuff from GTK into libadwaita. We often hear that this means the end of distro and user theming. What are the impacts for Ubuntu and Yaru?**

I've had chance to play and mess around with the widget-set provided by libadwaita, it's a wonderful addition to GTK4. It really makes it very easy for app-developers to build with GTK. The thing about it being end of distro and user theming is a conclusion derived on the current state of libadwaita.

It's in alpha state and many of the features are being actively worked and developed. Currently the main priority/focus of libadwaita is to land proper support for universal dark preference for GNOME 42. I can't say what ubuntu-desktop will do regarding this but I can confidently share that Yaru is 100% compatible with libadwaita/GTK4 especially now that we dropped the mixed-theme.

Yaru is 100% compatible with libadwaita/GTK4 beacuse for every minor change made on libadwaita's master branch an automatic pull-request is generated to Yaru which we review and apply on Yaru's master branch.


**Is theming the default desktop important for a distribution? Is it just an aesthetic or a branding issue? Are there other advantages?**

This seems to be a question for ubuntu-desktop team people, since they may have better analysis and statistics to back the claims.


**The GNOME team has talked about a coloring API, that would let users or distributions change various colors of the Adwaita theme, while retaining the look of the controls, and making sure that developers can avoid bug reports related to themes. Would that solution be satisfactory for the yaru team?**

Currently the coloring API is built around the choice of an app-developer. There's no option provided for distributions and will be offered in the future. The look provided by libdwaita is actually pretty similiar to Yaru-1.0 (Yaru shipped in ubuntu 18.10 and 19.04 orignally was a flat-theme before the re-base to Adwaita during 19.10).

With GTK-3 we have quite a number of tweaks on top of Adwaita to make it look Yaru. With libadwaita we essentially just recolor controls as everything else is very very very close to Yaru's POV as most things Yaru did are already present in upstream

**If this coloring API could be satisfactory, how has the work on it progressed so far?**

I've seen Marco Trevinho from ubuntu-desktop team and Alexander and Chris from GNOME involved with the discussions of API for accents and palettes on libadwaita's matrix channel. Just search Trevinho/ubuntu/yaru on [https://matrix.to/#/#libadwaita:gnome.org?via=gnome.org](Matrix) for exact discussions and re-coloring per app-basis.

## Conversation with Fedora


<figure markdown="1">

![Christian Schaller](/images/posts/itwtranscripts/schaller.png)

<figcaption>Christian Schaller, Director for Desktop at Red Hat</figcaption>
</figure>

I also neeeded the point of view from someone who worked on a distro that shipped GNOME in an unmodified way, and so Fedora came to mind. Christian Schaller, the Director for Desktop at Red hat, agreed to answer my questions:


**It looks, to me at least, that GNOME wants to be more than just a desktop that you can stack on a top of a distribution. It feels like GNOME is working towards being a complete platform, that developers target intentionally, and that doesn't get modified as much as it can be right now.  Maybe something more akin to how elementary OS works, where you can't really ship Pantheon any other way than how it is on elementary OS. Do you share that opinion? Is that something that could impact Fedora and/or other distributions?**


So first question about GNOME wanting to be more than a desktop you stack on top of a distribution, I think that is true in the sense that it has been a long held belief in the GNOME community that you can not make a great desktop if you theat your desktop operating system as a layer cake.

If you read my blog post from 2014 when we where kicking of the Fedora Workstation effort I actually [https://blogs.gnome.org/uraeus/2014/04/16/preparing-the-ground-for-the-fedora-workstation/](talk a lot about this) and I also mention this talk done all the way back in 2001 by Jim Gettys, a talk which I think influenced the thinking about these issues ever since.
 
 So can this be a challenge for distributions? It definitely can be as it means that the desktop will have expectations on your system as a whole and if you want to go a different way it might take quite a bit of work. In Fedora we do relatively few downstream changes to GNOME, instead we focus on getting our features and enhancements upstreamed right away and at the same time we take part in the upstream discussions about the pathway to take to try to keep upstream from at least not taking decisions that are directly adverse to our needs, but at the same time allow the upstream to retain its independence.
 

**GNOME decided to split all the HIG-related stuff from GTK into libadwaita. We often hear that this means the end of distro and user theming. What are the impacts for Fedora? For distributions that ship a customized version of GNOME?**


As for libadwaita, as I said in the previous answer we as a policy in Fedora try not to modify the upstream project greatly, so it is not impacting us a lot. I  would also say that the whole issue has been blown far out of proportions. The desktop linux space is not a homogenous space today where you can change a theme and expect every application to abide by it. libadwaita is a tool for applications developers to assert more control over the experience their end users experience with their application and to allow for the implementation of a well working dark-style which has become so popular.

**Is theming the default desktop important for a distribution? Is it just an aesthetic or a branding issue? Are there other advantages?**


As for theming and branding and its importance for a distribution. This is a good question and one that we have discussed in Fedora many times. In a situation where you have multiple distributions sharing a desktop solution the question of how do you make your option stand out comes up a lot. So for instance if someone posts a screenshot of their linux system online there line of thought that we should try to come up with ways to ensure that users right away recognize that as 'our' system and theming for instance is a tempting path to go down to do that (or creating your own desktop completely). We do some branding in Fedora, most notably our custom background images and a fedora logo in the about screen. Other distributions go a lot further. We have decided to focus our diversification on being the technology leader, with projects such as PipeWire, Wayland and Bolt, instead of spending a lot of time on trying to colour the UI Fedora blue.


**The GNOME team has talked about a coloring API, that would let users or distributions change various colors of the Adwaita theme, while retaining the look of the controls, and making sure that developers can avoid bug reports related to themes. Would that solution be satisfactory for distributions?**


We are probably not the best OS to ask about the coloring API since we as mentioned doesn't do a lot of custom theming, but in general I have to say that the right approach to these things if you are a distribution to be actively involved both on the design and code side upstream yourself. For instance in Fedora Workstation we have Allan Day involved as our upstream designer who then keeps an eye out for important changes being discussed. And when there are things coming up where we are worried about a change impacting us negatively we ensure to have both Allan active representing our needs in the design discussion, but also offer to help on the coding side to adjust the solution to also work for us. The one thing that never works in open source is to sit back and expect other people to do your work for you.

**Did you, or any other distribution, offer to discuss another solution with GNOME? Something like "validated themes"? Something else?**


As mentioned we have Allan Day constantly engaged upstream to talk to other parts of the design team and ensure our needs are met. One has to remember that a lot of major changes in GNOME is driven by one distribution or other, who has a feature/they want/need and then provide the engineering resources to do so. So usually the discussion we have is not with 'GNOME', but with other stakeholders about how their needs and requirements can be resolved without hurting our needs and requirements. And usually people are amendable to such discussions, especially if you are willing to work with them to make the needed adjustments, what tends to fall down is if you just try to put more work onto someone else for a feature they are not personally or their employer isn't especially interested in. This is especially true for something net new like libadwaita, where from what I understand the two main authors have been very open to accommodating requests for things like the coloring API, but also made it clear that they don't have the bandwidth to personally implement it, but patches are welcome.

## Discussion with elementary OS


<figure markdown="1">

![Cassidy Blaede](/images/posts/itwtranscripts/cassidy.png)

<figcaption>Cassidy Blaede, Co-Founder of elementary</figcaption>
</figure>

Since GNOME isn't the only one using GTK, I also wanted to talk to someone that worked on GTK based stuff, but not on GNOME. elementary OS was the obvious candidate, and Cassidy Blaede agreed to answer my questions:

**GNOME, much like elementary OS, seems to want to put more effort into becoming a more stable and reliable platform for application developers. This has led to the creation of libadwaita, which regroups all GNOME-HIG related elements into a single lib that developers can target. elementary OS uses GTK, how does that move impact elementary?**

This is a great move from our perspective, and is actually a solution we’ve been asking for for some time; we use GTK, but we don’t always use the same UI patterns or styling as GNOME. So in the past GTK may have forced GNOME-style dialogs or layouts that we had to work around, which we should see less of. By adding these GNOME-specific widgets and utilities to LibAdwaita rather than GTK, it keeps GTK itself more neutral and more flexible for desktops like elementary OS.

At the same time, there are some intriguing bits of LibAdwaita—especially around multi-touch gestures and animation—coming from its history as LibHandy, which we’re using heavily in elementary OS today. So I could see us using LibAdwaita in future elementary software, and because we’re in constant collaboration with GNOME contributors, that won’t be an issue for us; we will be able to use the bits that make sense while basically ignoring GNOME specific design bits.

All together, LibAdwaita is making it easier to make high quality GTK and GNOME apps without having to reinvent common patterns which is a boon to GNOME, elementary OS, and any desktop using GNOME or GTK.

**Is theming the desktop important for a distribution? Is it just an aesthetic or a branding issue? Are there other advantages?**

So before I really answer this, I think we need to clearly distinguish the parties involved in these discussions and decisions.

First, you have the people making the desktop (GNOME). GNOME is less like a traditional top-down software company and really more like a collective of people with overlapping ideals but often very different opinions! This is great for a diversity of thought but sometimes can be frustrating because there is not a singular person or vision you can point to for the ultimate direction of GNOME; you have to look at the direction as a whole, and understand that there are many, many people who are generally steering GNOME in the direction it is going.

Within that collective of people, you have progressive app developers who are longing for a better experience that has more modern patterns, easier ways to build apps, and modern features that many have gotten used to e.g. on popular mobile OSes. These folks are generally the ones behind the “Please Don’t Theme My App” initiative, and include folks working on pushing GNOME tech and design forward by working within the design team and on tools like LibHandy and LibAdwaita.

Then you have desktops or distros using GNOME downstream more as building blocks to make their own experiences; this probably includes Ubuntu, Pop!_OS, and many others. These projects have their own goals and don’t always work directly within the GNOME community to help steer GNOME, but may still contribute bits upstream like bug fixes and performance improvements. In my mind, the distinguishing characteristic of this group is that they use GNOME to build their own experience, but are also leaning heavily on the GNOME ecosystem rather than building their own ecosystem.

Then you have desktops like elementary OS where we are using some GNOME components, but largely building our own experience and ecosystem in parallel. We often work within upstream projects but aren’t directly steering GNOME (other than occasionally via design influence 😉). We ensure compatibility between our ecosystems by heavily leaning on FreeDesktop standards and being in constant communication and collaboration with GNOME and shared upstream projects.

Last but not least, you have the actual users of the software whose opinions and wants are as diverse as the people within the GNOME community itself.

Each of these groups probably has a different outlook on “theming,” but I can answer from the perspective of the progressive GNOME folks and elementary-like ecosystems, plus users (based on years of research and user studies).

For both the progressive GNOME folks and elementary, we largely see traditional theming as we know it on Linux desktops as a legacy implementation that is unique to “desktop Linux” for the worse. It is unlike any mainstream platform and makes it difficult for app developers to design and develop innovative, modern experiences. This is why elementary OS and GNOME 3 have never officially supported arbitrary theming via switching out the system stylesheet. There is absolutely an aesthetic and branding aspect (it’s good for screenshots of elementary OS to be recognizable as elementary OS, for example), but more important is avoiding breakage for both app developers and end users. With elementary OS, for example, we often see people who switch out their system stylesheet get upset when there is poor contrast, broken widgets, or feature (like the dark style or accent color preferences) that no longer work for them. We also see third-party apps that are doing interesting custom widgets (some of the most innovative and unique apps) completely break because some unsupported stylesheet doesn’t support the variables or style classes they depend on to make it easier to make their app.

However, for users, there are three main aspects to “theming,” and this is backed up by my years-long research and studies (like [https://blog.elementary.io/user-interface-study-findings/](this post) ): first, aesthetics or as I like to call it "making it your own." This is the same reason we have wallpapers on every modern OS (and look at early versions of iOS to see the opposite end of this line of thinking). People want to make their computer feel like theirs, just like they might want to decorate their physical desk with their own style to make it more pleasing for them. The second major aspect is accessibility which encompasses contrast and light/dark style preferences; some people have an easier time using their computer if it temporarily or permanently looks different than the defaults. Lastly, there's the "familiarity" aspect which often overlaps with the previous two, but can also include things like a theme to make the OS look more like Windows or macOS.

From the elementary perspective (and seemingly the progressive GNOME perspective with recent developments), we're tackling the first two aspects differently than just arbitrary themes; we've added a dark style preference and app API to address the aesthetic and accessibility needs for a dark interface while ensuring it's well supported by apps. We've even had success moving this under the FreeDesktop banner via a Portal API and now future GNOME versions will be shipping a compatible API as well (which gives us hope for third-party apps like Firefox and Chrome supporting it on Linux, too). We've also added ten new accent colors to elementary OS and a refreshed stylesheet that uses them throughout the OS in places like highlighted text, selected options, suggested actions, focus glows, and even accented text like in the Date & Time indicator. As a result, you can keep the default stylesheet and still make elementary OS feel very personalized while also ensuring it passes accessibility standards for contrast, and without breaking third-party apps. In fact, these new features are made possible because of the default stylesheet. So for us, we're happy to talk to users to discover how and why they are leaning on theming, and address those directly in the system stylesheet. Of course with open source software people will always be able to go and change how it looks and works, but we're focused on making the default experience adress the majority of those cases while also avoiding breakage.

The last perspective is the downstream GNOME-based distro perspective, and is one I'm less qualified to answer (because I don't share the opinions), but I can share my understanding from interacting with those folks and having previously worked at System76 on Pop!_OS. From my understanding, the biggest reason they want GNOME and GTK to officially support arbitrary theming is for their own vendor differentiation; Pop!_OS should look different from Zorin, should look different from Ubuntu, etc. They see the aesthetic of the software as part of their brand identity and one potential reason a user or customer might choose them over something else. I always draw parallels with the Android ecosystem here, though, because I think we're seeing the same thing play out. Early versions of Android were heavily skinned inside and out by OEMs differentiating their offerings. In some cases, it was because stock Android was subjectively ugly or incomplete, as well. But as Android as an ecosystem grew, OEMs (often via their agreements with Google) stopped modifying the toolkit and core styling of Android itself so it interfered less with third-party apps, but still differentiated their offerings with their first-party apps (often forks of the AOSP apps) and their "System UI" changes (much like changes to GNOME Shell on a GNOME-based OS). As a result, we now have a diverse ecosystem of devices with different experiences, and some greatly prefer one brand over another for their unique approach to the experience. But at for users, an app that works on one phone will work the same way as an app on a phone from a competing company. These OEMs are using Android to create a device and experience, but are all participating in the Google Play/Android ecosystem. But then you also have companies like Amazon who are using the Android platform to build their own separate Kindle/Fire ecosystem, and not participating in the larger ecosystem. Both approaches are valid and have benefits, but you kind of have to pick one or the other. And then on top of either ecosystem, you end up with users who root and install custom modules to customize how the OS looks and works themselves.

Wow, that's quite an answer. To summarize my thoughts on this original question, I personally think theming at a user level will always have a place for the tinkerers and experimentors; I even got my start in OS design by hacking on Windows 98 and Windows XP to swap out custom styles! But I think a successful modern ecosystem needs to make some guarantees to users and app developers about how the platform looks and works, and the current state of swapping out entire stylesheets from under apps is not sustainable. This is why platforms like GNOME and elementary OS are adding well-defined features like dark style APIs and accent colors, and why there is interest within the GNOME community in developing a well-defined theming API. I think that's the best way forward for all parties.

**elementary OS already has a similar "platform library", with Granite. Will Granite be interoperable with libadwaita, will both libraries be able to benefit from each other's work, or will they just be separate?**

I don't expect to see much change in how we approach Granite; it exists primarily as a way to abstract common patterns in real world use in elementary apps into reusable widgets and utilities. If LibAdwaita implements something similar to an existing pattern but it's better in some way, we could switch to that and deprecate our own Granite implementation, as we've done in the past when things have been added to GTK or LibHandy. Granite and LibHandy are currently perfectly interoperable, and we expect the same to be true with LibAdwaita, again, because we're in constant collaboration with the folks working on it.

**Have you had talks about this with GNOME developers, to see if development efforts can be combined?**

Yes, we’re in constant communication with folks working on GNOME and are always finding ways we can work together. And GNOME contributors are excellent about reaching out and getting our opinions on things when they're being worked on, as well, like with the new LibAdwaita tabs or the new dark style Portal API. Even though elementary OS is downstream of many GNOME components, I do feel like we're often a proving ground of new widgets, designs, or APIs that then make their way back up into GNOME while also handling more use cases--and when that happens, we're happy to deprecate our implementation. I think this approach is more productive overall than if we were to solely work within GNOME to implement our ideas, as we often update apps and widgets faster than would be possible in GNOME, or ship a certain pattern that GNOME designers aren't convinced of just yet as a way to prove it in action.

**Developers will have to decide between the GNOME platform, the elementary platform, or the KDE platform. Could that make the Linux app development situation more complicated than it already is?**

We already see this today, and LibAdwaita doesn’t change that. A GNOME app doesn’t look at home on elementary OS because we have different Human Interface Guidelines and conventions, and that has always been the case. Just like a KDE app doesn’t look at home on GNOME, and it’s not realistic to expect it to.

But this is also not unexpected from the status quo; we have popular apps like Spotify, Discord, Chrome, Steam, etc. that don’t really feel native in any desktop environment, but the important thing to users is that they can use these apps. With cross-desktop standards that GNOME, elementary, KDE, and others are working on together, it means we can have our own implementations while ensuring compatibility. It’s the whole reason you can even install a KDE app on GNOME or elementary OS and it correctly gets a launcher icon, is managed by the window manager, and can integrate with the desktop in places like the sound menu; we have FreeDesktop.org standards and efforts like Flatpak where we are all working together.

Of course from the elementary perspective we hope our platform is an attractive target for indie developers, and we work hard on our documentation, Human Interface Guidelines, platform features, and app monetization model to ensure that. At the same time, an app built for elementary OS and distributed on AppCenter is also trivially installable on any modern Linux-based OS, ultimately increasing the size and diversity of the "desktop Linux ecosystem" if you want to look at it that way. So I don't see it as in conflict with GNOME; we have differing visions for our platforms, but work together when it benefits us all.

**If app developers decide to force the use of Adwaita in their applications, could this lead to less consistency overall? With desktops made of apps themed by the distribution, apps built for elementary OS, apps built for GNOME, all with their own HIG, theme, and look and feel?**

I think my answer here is partially covered in the above answer as well. But more specifically, I don't believe surface-level consistency is a worthwhile ultimate goal; if I was shipping an Android app, I would design and write it using native Android patterns and tech. If I were shipping an iOS app, I would do so with native iOS tooling and patterns. I wouldn't expect my Android app to look "consistent" on iOS, and vice versa. In the same way, I don't expect a KDE or GNOME app to be "consistent" on elementary OS; even if it were using the same colors on the surface, the way those platforms look and work are just different. (As an example, dialogs in all three platforms look very differnet from one another, including where the suggested button is placed. Should apps adapt for every possible platform, or should they just use the conventions of the platform they were actually built for? And none of that is solved with, theming but requires code changes from the developer themselves.) However, it's a pretty cool result of our collaboration and standards that you can use those apps on elementary OS, and that is worthwhile.

**elementary OS has always been focused on the user experience. Could that move in favor of app developers result in a less coherent experience for users, with desktops made of apps themed by the distribution, apps built for elementary OS, apps built for GNOME, all with their own HIG, theme, and look and feel?**

I think this is also pretty well covered earlier, but yes, it can and has resulted in a less consistent experience on a surface level. But that's not new, and not solved by anything to do with theming; it's a result of having different interoperable platforms. The only way to solve this is to make "desktop Linux" a singular platform with a single set of Human Interface Guidelines and a single toolkit and a single stylesheet and a single desktop and... yeah, I don't think we want that, either!
