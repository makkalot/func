import fact_module
import sys
class HardwareFacts(fact_module.BaseFactModule):
    """
    Will give some basic info abouut hardware things
    """
    version = "0.0.1"
    description = "A modules that supplies hardware facts"

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
    run_level.description = "Shows the runlevel of the system"
    run_level.usage = "Can be used with all keywords"

    def os_name(self):
        """
        Gives back the os name of the system
        """
        return str(self.host.os)
    
    #for easier acces be creful should be unique
    os_name.tag = "os"
    os_name.description = "Shows the os of the system"
    os_name.usage = "Can be used with all keywords better with string related"

    
    def cpu_vendor(self):
        """
        The cpu vendor easy one
        """
        return str(self.host.cpuVendor)

    cpu_vendor.tag = "cpuvendor"
    cpu_vendor.description = "Shows the cpu_vendor of the system"
    cpu_vendor.usage = "Can be used with all keywords better with string related"

    
    def cpu_model(self):
        """
        Cpu model
        """
        return str(self.host.cpuModel)
 
    cpu_model.tag = "cpumodel"
    cpu_model.description = "Shows the cpu_model of the system"
    cpu_model.usage = "Can be used with all keywords better with string related"

    def kernel_version(self):
        """
        Kernel version
        """
        return str(self.host.kernelVersion)
    
    kernel_version.tag = "kernel"
    kernel_version.description = "Shows the kernel version of the system"
    kernel_version.usage = "Can be used with all keywords"



