import sys
import os
import importlib.util
from pathlib import Path
import random

from Source.Plugin import Plugin


# Submodule of GLady Core, responsible for locating, loading/unloading and registering plugins
class PluginManager:

    def __init__(self, core):

        # All located plugins are assigned unique names and put into a Plugins Table
        self.pluginsTable : dict = dict()
        self.core = core

        self.dir = "../Plugins"

        self.core.logger.log("Plugin Manager initialized")

        self.core.logger.log(" ")
        self.core.logger.log("LOADING PLUGINS")
        self.core.logger.log(" ")

        # Loads plugins
        self.__load_plugins()

        self.core.logger.log(" ")
        self.core.logger.log("PLUGIN LOADING COMPLETE")
        self.core.logger.log(" ")


    def __load_plugin_module(self, path):

        name = os.path.split(path)[-1].replace(".py", '')
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)

        return module


    def __load_plugins(self):

        # Loading code modules in "Plugins" folder
        Path(self.dir).mkdir(parents=True, exist_ok=True)

        plugin_directories = []

        # Scanning "Plugins/" directory for plugin folders
        for directory in os.listdir(self.dir):
            if '.' not in directory:

                files = os.listdir(self.dir + "/" + directory)

                # Looking for the "plugin.py file"

                if "plugin.py" in files:
                    plugin_directories.append(self.dir + "/" + directory)

        # TO DO: Dependency sorting

        # Loading plugins
        for plugin_dir in plugin_directories:

            # Loading code module
            try:
                self.__load_plugin_module(f"{plugin_dir}/plugin.py")

                # When code module is loading, plugin class is appended to the end of Plugin.pluginList
                plugin = Plugin.pluginList[-1]

                # Instancing plugin class
                inst = plugin(self.core)

                # Caching plugin directory
                inst.directory = plugin_dir

                # Creating a unique name for the plugin
                unique_name = inst.pluginName
                if unique_name in self.pluginsTable:
                    unique_name = unique_name + "_" + str(random.randint(10000, 99999))

                inst.pluginName = unique_name
                self.pluginsTable[unique_name] = inst

                inst.load()

                self.core.logger.log(f"PLUGIN {inst.pluginName} loaded")

            except Exception as e:
                self.core.logger.log(f"PLUGIN {plugin_dir} failed to load: {e}", message_type=1)


    def delete_plugin(self, plugin_name : str):

        if plugin_name in self.pluginsTable:

            self.pluginsTable[plugin_name].unload()
            self.pluginsTable.pop(plugin_name)

            self.core.logger.log(f"PLUGIN {plugin_name} deleted")

            # TO DO: maybe actually unload the code module (not sure how to do it yet)