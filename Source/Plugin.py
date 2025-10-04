from Core.Core import GLadyCore

# Base class for all GLady plugins
# A non-mandatory module, that is responsible for a specific GLady function.
class Plugin:

    def __init__(self, core):
        self.core : GLadyCore = core

        self.pluginName : str = "plugin"

    # Called when the plugin is loaded by the Plugin Manager
    def _load(self):
        None

    # Called when the plugin is unloaded (generally, before program's shutdown)
    def _unload(self):
        None

    # Called when the plugin has received an event from the communication bus
    def _received_event(self):
        None


