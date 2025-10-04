from Source.Core.Core import GLadyCore


# Submodule of GLady Core, responsible for locating, loading/unloading and registering plugins
class PluginManager:

    def __init__(self, core):

        # All located plugins are assigned unique names and put into a Plugins Table
        self.pluginsTable : dict = dict()
        self.core : GLadyCore = core