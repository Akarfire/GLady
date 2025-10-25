#CoreModule 

Submodule of GLady Core, responsible for creating and writing execution logs.

### Interface

Main function of this module. Writes `message` into the log as a new line (and prints it into the console, if `should_print` is set true):

```python
Logger.log(message, message_type = 0, should_print = True)
```

Message type modifies the way the message is displayed:

* **0** - Normal message;
* **1** - Error message.

Before logging, this function always adds a time stamp to the beginning of the message.