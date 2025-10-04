

# Base class for all GLady plugins
class Plugin:

    def __init__(self):
        None

    # Called when the plugin is loaded by the Plugin Manager
    def _load(self):
        None

    # Called when the plugin is unloaded (generally, before program's shutdown)
    def _unload(self):
        None

    # Called when the plugin has received an event from the communication bus
    def _received_event(self):
        None


