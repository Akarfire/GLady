#CoreModule

GLady's core is the mandatory module, that cannot be disabled, it is responsible for:

* Loading plugins;
* Processing inter-plugin communications;
* Processing network communication with other instances of GLady core;
* Receiving and rerouting commands from control servers;
* Handling execution logs.

### Sub modules

 * [Plugin Manager](Plugin%20Manager.md) - locates, loads/unloads and registers plugins;
 * [Communication Bus](Communication%20Bus.md) - enables inter-plugin communication through a centralized event system.
 * [Network Manager](Network%20Manager.md) - enables network communication with other GLady core instances in the network;
 * [Control Server](Control%20Server.md) - receives commands and sends feedback to control servers;
 * [Logger](Logger.md) - creates and writes execution logs;


### Program Loop Structure

#NeedsWriting

### Core Commands and Requests

#NeedsWriting
