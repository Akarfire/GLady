import socket

#
class ControlServer:

    def __init__(self, core):

        self.core = core
        self.core.logger.log("Control Server initialized")

    def update(self, delta_time : float):
        None