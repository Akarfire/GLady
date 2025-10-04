#from Core import GLadyCore

#
class ControlServer:

    def __init__(self, core):

        self.core = core
        self.core.logger.log("Control Server initialized")