# Setup Guide

At this point GLady has no graphical user interface for configuration, so the process might be tricky, but it can be mostly avoided if you use default configuration. In this guide I will describe how to easily setup GLady and pair her with OBS Studio for:

* On-screen multi-chat for Youtube and Twitch (or any of them separately);
* Text To Speech message commands;
* Meme Effects message commands for showing funny pictures and playing funny sounds ;)

*Note: This guide assumes you have completed Installation guide from the README page/file and ran GLady at least once*.

---
### Step 1: Setup Chat Reading Plugins
GLady comes bundled with 2 live stream chat reading plugins: `TwitchChatReader` and `YouTubeChatReader`, that read Twitch and YT chats in real time. 

If you only need one of them, then you can disable the one you don't need by going to `GLady/Plugins/*PluginName*/plugin_info.txt` and changing `enabled = True` to `enabled = False`.

#### Setting up Twitch Chat Reader
`TwitchChatReader` requires a relatively complicated but a one-time setup. For it you will have to create a twitch bot account and put it's authentication data into `GLady/Private/Auth/TwitchAuthData.txt`.