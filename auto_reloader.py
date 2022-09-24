from messages import SayText2
import os
import time
from commands.server import ServerCommand
from listeners.tick import GameThread
from plugins.manager import plugin_manager
import plugins

KNOWN_FILES = []
HAD_FIRST_ITERATION = False
IGNORED_FILES = ['auto_reloader', '__pycache__']


class PluginFile:
    def __init__(self, path):
        self.path = path
        self.last_modified = os.path.getmtime(path)

    def modified(self):
        if os.path.getmtime(self.path) != self.last_modified:
            self.last_modified = os.path.getmtime(self.path)
            return True
        return False


def reload_plugin(plugin_name):
    plugin_manager.reload(plugin_name=plugin_name)


def load_plugin(plugin_name):
    plugin_manager.load(plugin_name=plugin_name)


def is_plugin_known(file_path):
    found = None
    for i in range(len(KNOWN_FILES)):
        if KNOWN_FILES[i].path == file_path:
            found = KNOWN_FILES[i]
    return found


def get_plugin_list():
    return [item for item in os.listdir(plugins.manager.PLUGIN_PATH) if os.path.isdir(
        os.path.join(plugins.manager.PLUGIN_PATH, item)) and item not in IGNORED_FILES]


def check_plugins():
    global HAD_FIRST_ITERATION
    global KNOWN_FILES

    for plugin_name in get_plugin_list():
        plugin_file_path = os.path.join(
            plugins.manager.PLUGIN_PATH, plugin_name, plugin_name + ".py")
        if not HAD_FIRST_ITERATION:
            KNOWN_FILES.append(PluginFile(plugin_file_path))
            continue
        found_plugin = is_plugin_known(plugin_file_path)
        if not found_plugin:
            SayText2("New plugin detected: " + plugin_name).send()
            KNOWN_FILES.append(PluginFile(plugin_file_path))
            load_plugin(plugin_name)
        if found_plugin.modified():
            SayText2("Plugin modified: " + plugin_name).send()
            reload_plugin(plugin_name)
    if not HAD_FIRST_ITERATION:
        HAD_FIRST_ITERATION = True


def main_loop():
    while True:
        print("Auto Reloader: Checking for changes...")
        check_plugins()
        time.sleep(5)


def load():
    thread = GameThread(target=main_loop)
    thread.daemon = True
    thread.start()


def unload():
    pass
