# Contains per-plugin configurable event listening settings
class PluginListeningData:

    def __init__(self):
        self.useWhiteList : bool = False
        self.whiteList : set = set()

        self.useBlackList : bool = False
        self.blackList : set = set()

        self.blockListening : bool = False