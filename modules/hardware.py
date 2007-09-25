#!/usr/bin/python

## 
## Hardware profiler plugin
## requires the "smolt" client package be installed
##
## Copyright 2007, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##


# other modules
import sys
# hack: smolt is not installed in site-packages
sys.path.append("/usr/share/smolt/client")
import smolt

# our modules
from modules import func_module

# =================================

class HardwareModule(func_module.FuncModule):
    def __init__(self):
        self.methods = {
            "info": self.info
        }
        func_module.FuncModule.__init__(self)

    def info(self,with_devices=True):
        """
        Returns a struct of hardware information.  By default, this pulls down
        all of the devices.  If you don't care about them, set with_devices to
        False.
        """
        return hw_info(with_devices)

# =================================

def hw_info(with_devices=True):

    hardware = smolt.Hardware()
    host = hardware.host

    # NOTE: casting is needed because these are DBusStrings, not real strings
    data = {
        'os'              : str(host.os),
        'defaultRunlevel' : str(host.defaultRunlevel),
        'bogomips'        : str(host.bogomips),
        'cpuVendor'       : str(host.cpuVendor),
        'cpuModel'        : str(host.cpuModel),
        'numCpus'         : str(host.numCpus),
        'cpuSpeed'        : str(host.cpuSpeed),
        'systemMemory'    : str(host.systemMemory),  
        'systemSwap'      : str(host.systemSwap),
        'kernelVersion'   : str(host.kernelVersion),
        'language'        : str(host.language),
        'platform'        : str(host.platform),
        'systemVendor'    : str(host.systemVendor),
        'systemModel'     : str(host.systemModel),
        'formfactor'      : str(host.formfactor), 
        'selinux_enabled' : str(host.selinux_enabled),
        'selinux_enforce' : str(host.selinux_enforce)
    }

    # if no hardware info requested, just return the above bits
    if not with_devices:
        return data
    
    collection = data["devices"] = []

    for item in hardware.deviceIter():

        (VendorID,DeviceID,SubsysVendorID,SubsysDeviceID,Bus,Driver,Type,Description) = item

        collection.append({
            "VendorID"       : str(VendorID),
            "DeviceID"       : str(DeviceID),
            "SubsysVendorID" : str(SubsysVendorID),
            "Bus"            : str(Bus),
            "Driver"         : str(Driver),
            "Type"           : str(Type),
            "Description"    : str(Description) 
        })

    return data

methods = HardwareModule()
register_rpc = methods.register_rpc



