#Plugin

A non-mandatory module, that is responsible for a specific GLady function.

### Plugin Structure

#### Info
* *Plugin Name* - name of a specific plugin, doesn't have, but is welcomed to be unique;
* *Dependency List* - list of plugin (names), that are required for this plugin to function properly;
* *Event Processor Functions (EPFs)* - dictionary of functions that can be used to process incoming events;
* *Event Mapping* - dictionary that maps event types to EPFs;


### Plugin File Structure

Each plugin has it's own directory, which is located inside of GLady's *"Plugins"* folder.

Plugin's directory contains:

* Main *.py* file that contains plugin's class;
* *plugin_info.txt* with plugin's meta data;
* *Config* folder with plugin's configuration files:
	* *Options.txt* that contains general plugin options;
	* *EventMapping.txt* that specifies mapping of incoming (received) events to corresponding Event Processor Functions (EPFs);


**Example of a main *.py* plugin file:

```python
import Plugin as PluginAPI

class SamplePlugin(PluginAPI.Plugin):

    def __init__(self, core):
        super().__init__(core)
        # Registering event processor function for later mapping configuration

        self.eventProcessorFunctions["SampleEventProcessorFunction"] = self.sample_event_processor_function

        #...

    # Called when the plugin is loaded by the Plugin Manager
    def load(self):
        super().load()

    # Called when the plugin is unloaded (generally: right before program's shutdown)
    def unload(self):
        super().unload()

    # Example event processor function
    def sample_event_processor_function(self, event : PluginAPI.Event):
        # Some event processing logic
```


**Contents of the *plugin_info.txt* file:

```
# Plugin info file for "Sample Plugin Gen 2.0"

name = "SamplePlugin"
version = 0.1

description = "This plugin is a base for creating other plugins, copy and paste this plugin's folder and start editing it to create your own plugin!"


code_file = "plugin.py"
dependencies = SampleDependencyPlugin, ...
```

* *name* - name of this plugin;
* *version* - version of this plugin;
* *description* - description of this plugin;
* *code_file* - relative path to the main .py file;
* *dependencies* - list of other plugins that are required by this plugin;


### Plugin Configuration

#NeedsWriting


### Mapping and EPFs

#NeedsWriting


### Methods

``` python
init_plugin()
``` 
This method is called by the plugin manager once the plugin has been initialized. Guaranteed to be called after all the plugins from the Dependency List have been initialized (initPlugin was called on them);


```python
received_event(Event)
```
This method is called by the Communication Bus when the plugin hears of an event. Inside this method, the plugin checks, whether the received event is mapped to any EPF, and if so, calls this EPF.


``` python
load()
``` 
This method is called after all the plugins have been initialized;


``` python
unload()
```
This method is called when the plugin is unloaded (application is closing or plugin is disabled).


### Plugin to Communication Bus Interface

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

