---
title:  "8 Areas where Linux is Better than Windows"
description: "We're not the best at everything, but we're still better in a lot of ways"
author: nick
image: /images/posts/8-areas/8-areas-cover.jpg
tags:
  - Linux
  - Article ported from the old site
  - Windows
---

After a little bit of exploration, and a few videos on the various strengths of Linux, I decided to take a look at the areas where Linux is, in my opinion, better than Windows, and most specifically, Windows 10.

Windows 10 has been criticized a lot recently. Botched updates, weird design, messy store, and incoherent interfaces are nominated by quite a few people as areas where the system needs to improve. These areas, and some others, are where Linux shines in comparison.


<p align="center"><iframe style="width:75%;height:300px;" src="https://www.youtube.com/embed/LEnJcB03Bb4" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></p>


## Updating your system: easier when it's all in one place

Nowadays, Windows manages app updates in the Windows Store, and OS updates in the settings. While this is an improvement from older versions of the system, it's still confusing. You have to check two different places to see what can or can't be updated. Compare this to most Linux distros, where you have a one stop shop to manage everything: your package manager.

![AppCenter](/images/posts/8-areas/eos-appcenter.png)

Depending on the distro, you can have a nice separation between OS updates, and app updates, like on elementary OS, or they can be thrown all in one place, like in pamac on Manjaro, but with only one click, your can make sure that your whole system is up to date. Deepin is an exception here (and I'm sure there are others), putting system updates in its right-side-sliding control panel, and app updates in the Deepin Store, but generally, it's all managed in the same place.

With flatpaks and snaps, you can get a bit more fragmentation. If your distro ships with support for these formats out of the box, then it's all ok, but if not, you might still have to rely on the command line to update flatpaks. Snaps are updated automatically, so you don't even have to open an app to make sure everything is up to the latest version.

On Windows, even if app updates are managed through the Windows Store, this marketplace is still pretty understocked, and you'll probably have to install stuff from the internet with a regular installer. This makes updating these apps more of a pain, since each app can have its own update mechanism, or none at all.

![Windows Store](/images/posts/8-areas/windows-store.png)

Some angry comment suggested I willfully ignored Chocolatey, a package manager for Windows of sorts, but let's be honest: how many "regular" users know about this thing, and will be willing to go through its obscure installation instructions to get it running ?

So, advantage Linux on that one, it might not be perfect yet, but it's still better than the Microsoft alternative.

## The Package Manager : a One Stop Shop

It might seem redundant, but it's not. On Windows, you can manage your apps from one place, if you decide to only install apps from the store. That means you'll miss out on most of the great Windows programs available out there, and most people won't do that. So you still have to search for a program online, download its installer, run it, etc...

![Store](/images/posts/8-areas/store.png)

Again, you could use Chocolatey, and if you're stuck on Windows, I recommend you do so, but this is not something most users are aware of.

On Linux, everything you can install is in the package manager. This has its advantages and drawbacks, namely the fact that if it's not in there, then it's going to be more of a pain to install it. Sometimes you can add a repo, which can be easy or not, depending on your distro and your knowledge of Linux, but most distros ship with a GUI for that kind of operation.

Sometimes, you need to download an AppImage, or go with Flatpak to install the app you want, or you might even have to compile it.

But if you picked your distro carefully, and are ok with going with the app versions available in its repos, you won't need to look anywhere else in most cases. Users of Arch or Arch based distros are even more in luck, with the AUR (Arch User Repository), which contains virtually everything you'd ever want to run, and a lot more you don't.

Again, Linux's way is far from perfect, with repos not being up to date everywhere, and some apps not being distributed there, but it's still better to have 90% of what you need in your package manager, and hunt for the remaining 10%, than to have 10% available and be forced to manage everything else manually.

## Security: Marketshare Makes You Vulnerable

Windows is the most used OS on the planet, on the desktop at least. This means it's a much more interesting target for hackers and pirates of all sorts than Linux, with its 2-3% marketshare.

So, obviously, Windows is more subject to malware, ransomware, spyware, and all other evil-wares. The fact that you need to hunt down and install most programs manually is also a security issue: these installers can download and install crap from anywhere without you knowing, where on Linux, packages from your repos are carefully vetted and monitored.

![Micro Torrent](/images/posts/8-areas/microtorrent.png)

It also defaults to ask you for a root password, when Windows users only have to click "Yes" to give the necessary rights to a program to install itself. You can avoid these issues on Windows by running anti-malware and antivirus software, but this will eat up your precious CPU cycles and RAM, when on Linux, the only reason you'd want to run this is if you're planning to exchange files with a windows user.

The open source nature of Linux also means that, while anyone can look at its code and find vulnerabilities to use them for malicious purposes, anyone can also look at the code to find these vulnerabilities and fix thel before they're used. On Windows, the only people who can look at the code are Microsoft's employees, and if someone finds a vulnerability, there's no guarantee they'll report it, or that it will be fixed.

## Privacy: Windows 10 likes Data

Apart from Ubuntu which asks the user for telemetry data, I know of no Linux distro that collects personal information. No email addresses, passwords, names, phone numbers, etc.

![Ubuntu Data Collection](/images/posts/8-areas/ubuntudata.png)

WIndows 10, on the other hand, asks for a lot. First, it really insists that you create a Microsoft account when you set up your PC, with all the data you'll need to input for that to work. Then, it bombards you with screen after screen asking for your permission to collect handwriting data, speech data, information about your computer (which you can't even fully disable), and more.

![Windows 10 Data Collection](/images/posts/8-areas/windowsdata.png)

At least, you're informed it's taking place, and you can disable most (but not all) of it, but these things are all checked by default, and an unwary user will then transmit a bunch of stuff to Microsoft every time they use their computer.

I find this unsavory, and frankly unacceptable. Linux gets the point on that one too.

## Disk Space: Less Relevant Today, but Still

Nowadays, a Linux install rarely goes over 10Gb before you've added your programs and files. A Windows 10 install goes to 15Gb, and can grow to a lot more than this after updates.

Each major update creates a Windows.old folder, which basically stores the entire older version of Windows. It can be auto deleted, but in the meantime, it doubles the space the OS uses.

These days, storage space doesn't come at a premium, so it's less of an issue than in the past, but I like to think that my OS is what allows me to store the files I create and need, and should be as lightweight as possible.

Customization: As Long as You Want it In Black

Most, if not all Linux distros can be tweaked. The global theme, the icons, the fonts, the extensions, even the desktop environments can be changed a lot. You can set up your computer any way you want it, to suit any workflow.

![Windows 10 Customization](/images/posts/8-areas/colorchoice.png)

On Windows, you can move the taskbar around, and set a dark theme, or select an accent color. Don't like the icons, the fonts, or the fact that the taskbar hasn't substantially evolved in the last 20 years ? Too bad. You might want to install other programs, third party stuff to add more functionnality, but that comes with its own set of problems, namely possible breakage with updates, imperfect workflow integration, and duplicate features.

On this one, Linux takes the cake.

## UX Consistency: If it Looks the Same, You Already Know How to Use it

Hey, many people seem to not care about this, and are OK with every program looking different and behaving differently. I'm not, and most UX experts agree on that one. If programs are all completely different, then users need to learn each program's subtelties before being able to use them.

On Windows 10, you have many, many different app styles. You have the apps that look like they were migrated straight from Windows 98, with menubars, older icons, and table view everywhere. The disk manager or Notepad are prime examples. You then have WIndows 7 style apps, like the file manager, with a ribbon interface, a newer, 3D, glossy set of icons. And you have Windows 8 / Windows 10 style apps, mostly referred to as UWP apps, with burger menus, pivot tabs, and a semi transparent user interface designed as an hybrid between touch and mouse input.

![Windows 10 Incoherences](/images/posts/8-areas/incoherence.png)

These styles don't mesh. At all. You end up having to re-learn everything every time you're faced with an app you never used before. Microsoft is working on this, bringing updated versions of its apps with the "fluent" design language, but it's still not there yet.

On Linux, you can get to the same point, if you mix and match apps from different desktop environments. KDE apps don't look like GNOME apps, that's true, and elementary apps, while not that different from GNOME apps design-wise, are still not totally conforming to the same UI conventions.

If you stick to a specific DE's apps, though, you get consistency. More consistency than on any other platform, in fact, Mac OS X included.

<p align="center"><iframe width="840" height="472" src="https://www.youtube.com/embed/CJyzR-deHtM" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></p>

Apps looks and behave the same, and generally are easy to pick up (apart from some more technical and advanced applications, like big photo managers, video editing software, etc.).

So again, Linux is not perfect, and it's more than likely you'll need to use an app that's not from your favorite DE (I use Kdenlive on GNOME, for example, and there are others, like GIMP, or LibreOffice), but it's still better by default than what you get on Windows 10.

## You Only Get One First Impression

Once you start up your new OS for the first time, you quickly get a feel for it. Is it bloated or lean ? Are there tons of icons on your desktop and on your menu, or does it seem well made and coherent ?

Most users booting up a Windows machine will get a horrfying experience, not because of Windows, but because of manufacturers. They tend to add a whole software "suite" or bloatware and crapware, like DVD creation software, Control Centers, Photo Managers, AntiVirus software, and other terrible stuff.

![Windows 10 Ads Menu](/images/posts/8-areas/menuads.png)

You often can spend hours uninstalling these, since Windows blocks you from uninstalling more than one non-UWP app at a time. Some of these programs are even very hard to uninstall, requiring multiple reboots and leaving files everywhere.

On most Linux distros, you get what you need, and little more. Sure, you might not have need of some of what is shipping by default. I know I removed a bunch of stuff from my base Manjaro install. In as amny clicks as programs I wanted gone, it took about 5 minutes in total. This is also because Linux is not yet a major player in the "I'm shipping preinstalled on a PC" space. Linux computer manufacturers do exist, and make pretty good hardware (hello, Purism, System76, I'm available for any hardware review you'd like :D ), they don't represent much of the worldwide PC market.

So, in the end, Linux has a few strong points over Windows 10. It's leaner, more coherent by default, and more respecting of your privacy. Its package managers, while not perfect, re still ahead of the Windows app situation, and out of the box, a Linux distro is sure to use less space, and be a lot less bloated than a default OEM install.

And that's what I'm trying to underline in this (very) long article: Linux is far from perfect. Windows is ahead in a lot of other areas, namely games (even though we're getting there), thirs party, proprietary app support, driver support, availability, and others. But Linux does shine brighter in other areas, and I feel it's important to celebrate that.
