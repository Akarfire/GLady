from Core.Event import Event

# Submodule of GLady Core, responsible for enabling network communication with other GLady Core instances in the network.
class NetworkManager:

    def __init__(self, core):
        self.core = core

        self.core.logger.log("Network Manager initialized")

    # Routes local event to other GLady Core instances on the network
    def route_event_to_network(self, event: Event):
        None