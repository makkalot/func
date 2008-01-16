##
## Hardware profiler plugin
## requires the "smolt" client package be installed
## but also relies on lspci for some things
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

# our modules
import sub_process
import func_module

# =================================

class HardwareModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Hardware profiler."

    def hal_info(self):
        """
        Returns the output of lshal, but split up into seperate devices
        for easier parsing.  Each device is a entry in the return hash.
        """

        cmd = sub_process.Popen(["/usr/bin/lshal"],shell=False,stdout=sub_process.PIPE)
        data = cmd.communicate()[0]

        data = data.split("\n")

        results = {}
        current = ""
        label = data[0]
        for d in data:
            if d == '':
                results[label] = current
                current = ""
                label = ""
            else:
                if label == "":
                    label = d
                current = current + d

        return results

    def inventory(self):
        data = hw_info(with_devices=True)
        # remove bogomips because it keeps changing for laptops
        # and makes inventory tracking noisy
        if data.has_key("bogomips"):
            del data["bogomips"]
        return data

    def info(self,with_devices=True):
        """
        Returns a struct of hardware information.  By default, this pulls down
        all of the devices.  If you don't care about them, set with_devices to
        False.
        """
        return hw_info(with_devices)

# =================================

def hw_info(with_devices=True):

    # this may fail if smolt is not installed.  That's ok.  hal_info will
    # still work.

    # hack: smolt is not installed in site-packages
    sys.path.append("/usr/share/smolt/client")
    import smolt

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
