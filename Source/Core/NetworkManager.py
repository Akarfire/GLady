

# Submodule of GLady Core, responsible for enabling network communication with other GLady Core instances in the network.
class NetworkManager:

    def __init__(self, core):
        self.core = core

        self.core.logger.log("Network Manager initialized")