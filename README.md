# GLady

GLady is a fully modular, highly customizable and locally-run system, designed to make live streams more entertaining by introducing various interactive elements available to viewers through chat commands.

**Status: Early Access / In Development**

---
### Features

#### Modularity & Customization

GLady is a completely modular system which can be extensively customized (More documentation on customization will be written in the future, right now it is not very user-friendly).

#### Plugin: On-Screen Chat

Mixed on-screen chat for YouTube and Twitch!
<p align="center">
	<img src="./GLady Documentation/Images/GLady_OnScreenChat.png">
</p>

#### Plugin: Message Commands

Create custom message commands in process them with various **plugins** like **Text To Speech** and **Meme Effects!**
<p align="center">
	<img src="./GLady Documentation/Images/GLady_TTS.png">
</p>
<p align="center">
	<img src="./GLady Documentation/Images/GLady_MemeEffects.png">
</p>

*NOTE: UI features are web-page based, so you can use them in `Browser Source` in OBS!*

---
### Installation

#### Installing GLady

1. Download a release or clone this repository onto your PC;
2. Run `Setup.bat`:
    * If you don't have python 3.12, the script will download an installer you will need to use (after installing python run `Setup.bat` again);
    * If/When you have python 3.12 installed, the script will do the rest automatically;
3. Run `RunGLady.bat` to run the app!

*NOTE: Every time you install a new plugin you need to run `Setup.bat` again!*

*NOTE: This guide is Windows only, if you want to run on Linux you will have to figure it out on your own (I didn't test whether it works or not)!*

#### Installing Plugins

To install a plugin, that is not included with GLady by default you just need to unpack the archive and paste the plugin folder in into the `Plugins` folder (plugin folder always contains a `plugin_info.txt` file).

---
### Roadmap
![](./GLady%20Documentation/Images/GLadyRoadMap.png)

---

### Documentation (WIP)

[Click Here](./GLady%20Documentation/G-Lady.md)