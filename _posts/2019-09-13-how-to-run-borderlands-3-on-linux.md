---
title:  "How to Run Borderlands 3 on Linux"
description: "Here is how I got Borderlands 3 to start on Linux, with a few caveats..."
author: nick
image: /images/posts/bdl3/bdl3.png
tags:
  - Linux
  - Gaming
  - Article ported from the old site

---

![Borderlands 3](/images/posts/bdl3/bdl3.png)


After spending most of the afternoon on trying to get Borderlands 3 running on Linux, I managed to get it in a playable state, with a few workarounds.

Disclaimer:

- This might not work on your machine

- You need the necessary vulkan and lib32-vulkan libs installed on your machine

- Your machine needs to work with DXVK

- Online works

- Gameplay works

- Menus work

Here's a quick video recap of every step you need to follow:

<p align="center"> <iframe width="560" height="315" src="https://www.youtube.com/embed/IvmTAR3I8Ww" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></p>

And if you'd prefer reading through everything, here are the details:

### Lutris and Epic Games Store

First thing to do is installing Lutris. Find it in your package manager, or grab it from Lutris.net. That step is easy enough :)

<figure markdown="1">

![Lutris](/images/posts/bdl3/lutris.png)

<figcaption>Lutris will let you install the Epic Games Store in one click.</figcaption>
</figure>

Second step is installing the Epic Games Store (yuck, I know).

Click the little "search" icon in the top bar, and type "epic games". Select the Epic Games Store, and click the install button on the right side of the screen.

Once the install is done (it might take a while), start the Store from Lutris, and log in or, more likely, create an account (yuck, I know).

Now, buy / install Borderlands 3. you can refund items on the EGS for 14 days after purchase, as long as you haven't played them more than 2 hours, largely enough to see if it works for you.

### Setting things up

Don't start the game yet !

Close the Epic Games Launcher, and right click on its icon on Lutris, then select "Configure".

Open the "Runner options" tab, and disable Esync.

![Esync](/images/posts/bdl3/esync.png)

Then make sure the other settings are displayed as follow:

![Settings](/images/posts/bdl3/settings.png)


### Running the game

Easy enough ! Open the EGS from Lutris, and launch Borderlands 3. You'll see a whole lot of nothing, black screen, with a "compiling shaders" in the bottom left corner. Wait a bit, and you should get the menu.

If you've done the steps details in the Edit listed on top of the article, everything should work now !

On my Ryzen 5, RTX2060, 16Gb of RAM, I can play at 1440p on a mix of High and Ultra settings maintaining a steady 60fps, once the shaders are correctly cached.

When I get to a new map, it takes 10-20s for the framerate to stabilize, but it seems to do the same thing for my friends playing on Windows.

Online does work as well, but you'll bit a wall whenever the game tries to play a video in-game. Let's fix this!


### Get the videos to play:

Now, there is a solution to get all mp4 videos playing in-game, and at character creation. Here are the steps to follow onces you've installed the game:

First, install the mf-install and mf-installcab scripts. These will get you all the required dlls and codecs.

To do so, head to these links:

[https://github.com/z0z0z/mf-install](https://github.com/z0z0z/mf-install)

[https://github.com/z0z0z/mf-installcab](https://github.com/z0z0z/mf-installcab)

Download both files, and extract them.

Once you're done, you're going to open a terminal, and get into the directory where you extracted the files.

For example, for me it was:

```
cd Downloads/mf-install
```

Once you're inside this directory, type:

```
WINEPREFIX="/PATH/TO/THE/PREFIX/WHERE/YOU/INSTALLED/THE/GAME" ./install-mf.sh
```

To get the prefix path, you can open Lutris, right click on the Epic Games Store, and select "Browse Files". Go up in the folder structure until you see a "drive_c" folder. The directory containing this drive_c folder is the path to the prefix.

Repeat the same operations for mf-installcab with:

```
WINEPREFIX="/PATH/TO/THE/PREFIX/WHERE/YOU/INSTALLED/THE/GAME" ./install-mf-64.sh
```

I had to right click on the script file, open the properties, and enable exeuting the script in the "Permissions" tab.

Then, in the folder where you've extracted the mf-installcab files, copy the mfplat.dll file, and paste it into the Borederlands3 folder where your Borderlands3.exe file is located.

Then, you'll need a COLORCNV.dll file. I got one frome here: [https://www.dllme.com/dll/files/colorcnv_dll.html](https://www.dllme.com/dll/files/colorcnv_dll.html)

Copy that file in your wine prefix, in the windows/system32 directory.

You'll need to register it in the windows registry as well, so on Lutris, right click the Epic Games Store, and select Wine Registry.


Go to HKEY_CLASSES_ROOT\CLSID

In CLSID create a key named {98230571-0087-4204-b020-3282538e57d3}

Inside this key {98230571-0087-4204-b020-3282538e57d3} double click (Default) and type in Color Converter DMO.

Create another key in {98230571-0087-4204-b020-3282538e57d3} called InprocServer32

Inside InprocServer32, double click (Default) and type in C:\windows\system32\COLORCNV.dll

Create a String called ThreadingModel, double click it and type in Both

And you're done ! Now, videos should play in-game, and you won't get stuck during quests, or need to download previous file saves, you can create your own characters !
