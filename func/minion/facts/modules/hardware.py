import fact_module
import sys
class HardwareFacts(fact_module.BaseFactModule):
    """
    Will give some basic info abouut hardware things
    """

    def __init__(self):
        sys.path.append("/usr/share/smolt/client")
        import smolt
        hardware = smolt.Hardware()
        self.host = hardware.host

    def run_level(self):
        """
        The runlevel of the system
        """
        return str(self.host.defaultRunlevel)

    #for easier acces be creful should be unique
    run_level.tag = "runlevel"

