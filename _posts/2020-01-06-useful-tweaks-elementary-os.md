---
title:  "Useful Tweaks For elementary OS"
description: "Since I got a bunch of questions on how to add certain features to elementary OS, here are some easy, useful tweaks you can apply."
author: nick
image: /images/posts/tweaks-eos/tweaks.jpg
tags:
  - Personal
  - Article ported from the old site

---
Since I got a few questions on how I got some features on elementary OS that are not shipped as standard, I thought I'd give a small rundown of the tweaks I applied. There are 3 main tweaks I added to my default install.


### Notification icons
<figure markdown="1">

![Notification Tray](/images/posts/tweaks-eos/notifs.png)

<figcaption>I mean, this looks super old, and these icons are not needed there, but since some programs insist you use them...</figcaption>
</figure>

The first tweak is indicators. By default, elementary OS doesn't support notification icons for apps using an outdated way of displaying them, like Steam, OBS, or pCloud. 

Still, the "modern, approved way" is not used by many apps, so in the meantime, it's easier to add back that support. The way to do this is pretty simple.: you have to install two deb packages, called wingpanel-indicator-ayatana, and indicator-application. These packages need patches to work correctly, and are not included in the main elementary OS or Ubuntu repositories. 

Fortunately, there are pre-built and patched packages available through both links below:

[https://github.com/mdh34/elementary-indicators/releases](https://github.com/mdh34/elementary-indicators/releases)

[https://launchpad.net/~elementary-os/+archive/ubuntu/stable/+files/wingpanel-indicator-ayatana_2.0.3+r27+pkg17~ubuntu0.4.1.1_amd64.deb](https://launchpad.net/~elementary-os/+archive/ubuntu/stable/+files/wingpanel-indicator-ayatana_2.0.3+r27+pkg17~ubuntu0.4.1.1_amd64.deb)

To install these, either download them and install them through the command line, or just install [Eddy](https://appcenter.elementary.io/com.github.donadigo.eddy/) from the AppCenter, and open them with it. Once that's done, just logout and log back in, and your apps using indicators should be displayed in the top panel.

I personally don't like using these indicators, and I'd much rather have icons in my dock to access these options instead of having these icons, but unfortunately, some of these programs don't work that way.

### A native looking Firefox
<figure markdown="1">

![Firefox](/images/posts/tweaks-eos/firefox.png)

<figcaption>Yep, this is Firefox, not Epiphany</figcaption>
</figure>

My Firefox looks like Epiphany, and that's because I installed a custom UserChrome.css file to it, which is a simple CSS file that changes the look of the interface. This file hasn't been created by me, but by Harvey Cabaguio.

To enable this theme, you first need to tell Firefox to accept these userchrome.css tweaks, so in your Firefox address bar, type about:config.

Look for toolkit.legacyUserProfileCustomizations.stylesheets, and double click that line to enable it.

<figure markdown="1">

![Firefox Profile](/images/posts/tweaks-eos/firefoxprofile.png)

<figcaption>Yep, this is Firefox, not Epiphany</figcaption>
</figure>


Then, you'll need to put the tweaked files in your Firefox profile. In the address bar, type about:support, and look for the button called "Open Directory", in the Application Basics > Profile Directory segment.

In that folder, create a folder called "chrome". In that folder, paste the userChrome.css you downloaded from the link below:

[https://github.com/harveycabaguio/firefox-elementary-theme/archive/master.zip](https://github.com/harveycabaguio/firefox-elementary-theme/archive/master.zip)

Don't forget to completely quit Firefox and restart it for the tweaks to be taken into account.

I haven't noticed any issues with these tweaks, but keep in mind that as Firefox is updated, it might break and cause Firefox to crash or stop working altogether. You can still right click on the toolbar, and select Customize, to change the position of various elements and make it look even more native if you like.

### elementary Tweaks
<figure markdown="1">

![elementary Tweaks](/images/posts/tweaks-eos/elementary-tweaks.png)

<figcaption>elementary tweaks is easy to install, if you feel you need some of these features </figcaption>
</figure>

Much like GNOME Tweaks, this program allows you to change a few more options in pantheon, elementary OS' desktop environment. It installs as a panel in the system settings, which makes it nicer to use than to have a separate application, and it enables all kinds of customisations.

The main ones? Dark mode system-wide, changing the them and icons (althouygh on elementary OS, unless you downloaded a theme specifically made for elementary, you're going to have issues), adding back some windows buttons if you feel you need them, or disabling the single click behavior in the file manager.

Personally, I only use it to make the max volume higher than 100% on my Huawei Matebook 13, since it's a bit too quiet, and reducing the duration of animations, to give a snappier feel to the OS.

To install it, just type these commands in a terminal:

Add support for PPAs to your elementary OS:

    sudo apt install software-properties-common


Add the elementary-tweaks PPA:

    sudo add-apt-repository ppa:philip.scott/elementary-tweaks


Install elementary tweaks:

    sudo apt install elementary-tweaks


You'll then find a new panel in your system settings, called "Tweaks".


And there you go, the three main tweaks I added to elementary OS to make it nicer to use. They're not really needed, but they still bring some quality of life improvements, for those that would be lost without these few features and enhancements.

If you want to learn more about elementary OS, you can also watch my latest video on their latest release, elementary OS 5.1 Hera:

<p align="center" ><iframe width="560" height="315" src="https://www.youtube.com/embed/rpjyCeUhQlM" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></p>


