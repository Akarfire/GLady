### Description

Implements time-based unique events (only one instance can exist at the same time). Can be useful in combination with other plugins, like `ObsWebsocket`.

---
### Options

* `UniqueEvents` : `dict` : Default Value :
```
{ 
	"ExampleUniqueEvent": {
		 "StartEventCall" : "$UniqueEventName$_Start",
		 "StartEventCustomData" : dict(),
		 "EndEventCall" : "$UniqueEventName$_End",
		 "EndEventCustomData" : dict()
		},
}
```
`UniqueEvents` option is a dictionary of all possible unique events and their configuration:
* `Key` - name of the unique event used to identify it;
* `StartEventCall` - normal event that is called when this unique event starts;
* `StartEventCustomData` - additional data that is bundled (added to `event.data`) with the normal event fired when this unique event starts. By default unique event's name is added to the `event.data`;
* `EndEventCall` - normal event that is called when this unique event ends;
* `EndEventCustomData` - additional data that is bundled (added to `event.data`) with the normal event fired when this unique event ends. By default unique event's name is added to the `event.data`.

---
### Event Processor Functions

* `StartUniqueEvent` (`UniqueEvent` : `string`, `Duration` : `float`, `CombineDuration` : `bool` = `True`) - starts the specified unique event with the specified duration. If unique event is already active and `CombineDuration` is set to `True` (it is so by default), then new duration will be added to existing one. Same arguments are looked up in `event.data`, but values obtained from there have lower priority than arguments that are specified in pipeline file.

* `StopUniqueEvent` (`UniqueEvent` : `string`) - forcefully ends the specified unique event. Same argument is looked up in `event.data`, but value obtained from there has lower priority than the argument.

* `StopAllUniqueEvents`() - forcefully ends all unique events.

---
### Generated Events

Events specified in `Options/UniqueEvents/StartEventCall` and `Options/UniqueEvents/EndEventCall` are called when corresponding unique events start and end.