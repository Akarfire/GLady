#CoreModule

Submodule of GLady Core, responsible for enabling inter-plugin communication.

### Events

Inter-plugin communication is executed through Events - special messages, travelling over the communication bus from their sender to any recipient, willing to hear them. Senders and Recipients are plugins.

Events do not exist overtime, once fired, they are immediately processed (rerouted to recipients) .


**Event Structure**

* *EventName* - string value, containing a unique name of the given event;
* *Initiator* - plugin, that initiated the event (sender);
* *Tags* - a set of event tags, acting as event attributes that are used by the communication infrastructure (Communication Bus, Network Manager, etc).
* *Data* - a dictionary of named values, that carry some event-specific data.


### Networking

Every event, that is passing through the Communication Bus, if not specified otherwise (using tags), is also passed to the Network Manager for it to be transmitted to other GLady Core instances in the network.


### Plugin to Bus Interface

Each plugin can initiate an event, by calling:

```python
CommunicationBus.init_event(Event) # Event structure must be preinitialized
```

To change the way plugins listen to events, one can modify:

```python
Plugin.listeningConfiguration
```

which contains:

```python
useWhiteList : bool = False  
whiteList : set
  
useBlackList : bool = False  
blackList : set
  
blockListening : bool = False
```

* `whiteList`, if used, lists all types of events the plugin is listening to;
* `blackList`, if used, lists all events that will be ignored by the plugin;
* `blockListening`, if set to true, makes the plugin ignore ALL incoming events;

Plugins can specify the names of events they want to be listening to by calling:

```python
Plugin.listen_to(PluginName, EventName) # Configurng white/black list
Plugin.stop_listening_to(PluginName, EventName) # Configurng white/black list
```


### Plugins Receiving Events

When plugin receives an event, the following method is called:

```python
Plugin.received_event(Event);
```

 Inside this method, the plugin checks, whether the received event is mapped to any EPF, and if so, calls this EPF.


### Tags List

Here is the list of all possible event tags and their descriptions.

* *Local* - this event will not be routed through the network and thus, will only be received by the plugins registered on the same instance of GLady Core.

* *SpecificReceiver* - this event can only be received by a specified list of plugins. Names of the allowed receiver-plugins must be listed in event's data region under the name "SpecificReceiver_Names";

* *NetSpecific* - this event (if it is not local) will only be sent to specific network instances of GLady Core. The list of instance names must be listed in event's data region under the name "NetSpecific_Names"; 


#### Links
* [Plugin](Plugin.md);