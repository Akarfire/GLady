import sys
import os
import importlib.util
from pathlib import Path
import random

from Plugin import Plugin

# Data class, containing info about a plugin that is being loaded
class PluginLoadingInfo:

    def __init__(self):
        self.directory : str = ""
        self.name : str = ""
        self.version : str = ""
        self.code_file : str = ""
        self.dependencies : list = []


# Submodule of GLady Core, responsible for locating, loading/unloading and registering plugins
class PluginManager:

    def __init__(self, core):

        # All located plugins are assigned unique names and put into a Plugins Table
        self.pluginsTable : dict = dict()
        self.core = core

        self.dir = "Plugins"

        self.core.logger.log("Plugin Manager initialized")

        self.core.logger.log(" ")
        self.core.logger.log("LOADING PLUGINS")
        self.core.logger.log(" ")

        # Loads plugins
        self.__load_plugins()

        self.core.logger.log(" ")
        self.core.logger.log("PLUGIN LOADING COMPLETE")
        self.core.logger.log(" ")
        
        # Requests
        
        self.core.controlServer.register_request("Plugins", self.request_plugins)


    # Loads plugin's code module
    @staticmethod
    def __load_plugin_module(path):

        name = os.path.split(path)[-1].replace(".py", '')
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)

        return module


    # Locates and loads all the plugins
    def __load_plugins(self):
        
        # Loading code modules in "Plugins" folder
        Path(self.dir).mkdir(parents=True, exist_ok=True)

        plugins_info : list[PluginLoadingInfo] = []
        
        # Scanning "Plugins/" directory for plugin folders
        for directory in os.listdir(self.dir):
            if '.' not in directory:

                files = os.listdir(self.dir + "/" + directory)

                # Looking for the "plugin_info.txt" file

                if "plugin_info.txt" in files:
                    info = PluginLoadingInfo()
                    info.directory = self.dir + "/" + directory

                    info_file = open(self.dir + "/" + directory + "/plugin_info.txt")
                    lines = info_file.readlines()

                    # Parsing info file
                    for line in lines:

                        line = line.replace('\n', '')

                        # Ignore empty and comment lines
                        if line.startswith('#') or len(line) == line.count(' '): continue

                        # Name line
                        if line.startswith('name'):
                            info.name = str(eval(line.split('=')[1]))

                        # Version line
                        if line.startswith('version'):
                            info.version = line.split('=')[1].replace(' ', '')

                        # Code file
                        if line.startswith('code_file'):
                            info.code_file = str(eval(line.split('=')[1]))

                        # Dependencies
                        if line.startswith('dependencies'):
                            dependency_list = [i.replace(' ', '') for i in line.split('=')[1].split(',')]
                            for dep in dependency_list:
                                if dep != "":
                                    info.dependencies.append(dep)

                    if info.code_file != "":
                        plugins_info.append(info)

                    info_file.close()

        # TO DO: Dependency sorting
        
        # Loading plugins
        loaded_plugins = set()

        for plugin_info in plugins_info:

            # Checking if all the dependencies have been loaded successfully
            dependency_fault = False
            for dependency in plugin_info.dependencies:
                if dependency not in loaded_plugins:

                    self.core.logger.log(f"Missing dependency: '{dependency}'!", message_type=1)

                    dependency_fault = True
                    break

            if dependency_fault:
                self.core.logger.log(f"Plugin {plugin_info.name} failed to load: Dependency Fault!", message_type=1)

            # Loading code module
            try:
                self.__load_plugin_module(f"{plugin_info.directory}/{plugin_info.code_file}")

                # When code module is loading, plugin class is appended to the end of Plugin.pluginList
                plugin = Plugin.pluginList[-1]

                # Instancing plugin class
                inst = plugin(self.core)

                # Caching plugin directory
                inst.directory = plugin_info.directory

                # Creating a unique name for the plugin
                unique_name = plugin_info.name
                if unique_name in self.pluginsTable:
                    unique_name = unique_name + "_" + str(random.randint(10000, 99999))

                inst.pluginName = unique_name
                self.pluginsTable[unique_name] = inst

                inst.load()

                loaded_plugins.add(plugin_info.name)
                self.core.logger.log(f"PLUGIN {inst.pluginName} loaded")

            except Exception as e:
                self.core.logger.log(f"PLUGIN {plugin_info.directory} failed to load: {e}", message_type=1)


    # Updates all plugins
    def update_plugins(self, delta_time : float):
        for plugin in self.pluginsTable.values():
            try:
                plugin.update(delta_time)

            except Exception as e:
                self.core.logger.log(f"Failed to update plugin {plugin.pluginName} : {str(e)}\nThis plugin will be unloaded!", message_type=1)

                # Unload problematic plugins
                self.runtime_unload_plugin(plugin.pluginName)


    # Unloads all plugins before program shutdown
    def unload_plugins(self):
        for plugin in self.pluginsTable.values():
            try:
                plugin.unload()

            except Exception as e:
                self.core.logger.log(f"Failed to unload plugin {plugin.pluginName} : {str(e)}", message_type=1)


    # Unloads a plugin during runtime
    def runtime_unload_plugin(self, plugin_name : str):

        if plugin_name in self.pluginsTable:

            try:
                self.pluginsTable[plugin_name].unload()

                self.pluginsTable.pop(plugin_name)

                self.core.logger.log(f"PLUGIN {plugin_name} unloaded!")

            except Exception as e:
                self.core.logger.log(f"Failed to unload plugin {plugin_name} : {str(e)}", message_type=1)

            # TO DO: maybe actually unload the code module (not sure how to do it yet)
            
    # Requests
    
    def request_plugins(self, data):
        return { "Plugins:" : list(self.pluginsTable.keys())}