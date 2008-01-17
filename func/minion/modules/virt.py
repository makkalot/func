"""
Virt management features

Copyright 2007, Red Hat, Inc
Michael DeHaan <mdehaan@redhat.com>

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

# warning: virt management is rather complicated
# to see a simple example of func, look at the
# service control module.  API docs on how
# to use this to come.

# other modules
import os
import sub_process
import libvirt

# our modules
import codes
import func_module

VIRT_STATE_NAME_MAP = {
   0 : "running",
   1 : "running",
   2 : "running",
   3 : "paused",
   4 : "shutdown",
   5 : "shutdown",
   6 : "crashed"
}

class FuncLibvirtConnection(object):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Virtualization items through func."

    def __init__(self):

        cmd = sub_process.Popen("uname -r", shell=True, stdout=sub_process.PIPE)
        output = cmd.communicate()[0]

        if output.find("xen") != -1:
            conn = libvirt.open(None)
        else:
            conn = libvirt.open("qemu:///system")

        if not conn:
            raise codes.FuncException("hypervisor connection failure")

        self.conn = conn

    def find_vm(self, vmid):
        """
        Extra bonus feature: vmid = -1 returns a list of everything
        """
        conn = self.conn

        vms = []

        # this block of code borrowed from virt-manager:
        # get working domain's name
        ids = conn.listDomainsID();
        for id in ids:
            vm = conn.lookupByID(id)
            vms.append(vm)
        # get defined domain
        names = conn.listDefinedDomains()
        for name in names:
            vm = conn.lookupByName(name)
            vms.append(vm)

        if vmid == -1:
            return vms

        for vm in vms:
            if vm.name() == vmid:
                return vm

        raise codes.FuncException("virtual machine %s not found" % vmid)

    def shutdown(self, vmid):
        return self.find_vm(vmid).shutdown()

    def pause(self, vmid):
        return self.suspend(self.conn,vmid)

    def unpause(self, vmid):
        return self.resume(self.conn,vmid)

    def suspend(self, vmid):
        return self.find_vm(vmid).suspend()

    def resume(self, vmid):
        return self.find_vm(vmid).resume()

    def create(self, vmid):
        return self.find_vm(vmid).create()

    def destroy(self, vmid):
        return self.find_vm(vmid).destroy()

    def undefine(self, vmid):
        return self.find_vm(vmid).undefine()

    def get_status2(self, vm):
        state = vm.info()[0]
        # print "DEBUG: state: %s" % state
        return VIRT_STATE_NAME_MAP.get(state,"unknown")

    def get_status(self, vmid):
        state = self.find_vm(vmid).info()[0]
        return VIRT_STATE_NAME_MAP.get(state,"unknown")



class Virt(func_module.FuncModule):

    def __get_conn(self):
        self.conn = FuncLibvirtConnection()
        return self.conn

    def state(self):
        vms = self.list_vms()
        state = []
        for vm in vms:
            state_blurb = self.conn.get_status(vm)
            state.append("%s %s" % (vm,state_blurb))
        return state


    def info(self):
        vms = self.list_vms()
        info = dict()
        for vm in vms:
            data = self.conn.find_vm(vm).info()
            # libvirt returns maxMem, memory, and cpuTime as long()'s, which
            # xmlrpclib tries to convert to regular int's during serialization.
            # This throws exceptions, so convert them to strings here and
            # assume the other end of the xmlrpc connection can figure things
            # out or doesn't care.
            info[vm] = {
                "state"     : VIRT_STATE_NAME_MAP.get(data[0],"unknown"),
                "maxMem"    : str(data[1]),
                "memory"    : str(data[2]),
                "nrVirtCpu" : data[3],
                "cpuTime"   : str(data[4])
            }
        return info


    def list_vms(self):
        self.conn = self.__get_conn()
        vms = self.conn.find_vm(-1)
        results = []
        for x in vms:
            try:
                results.append(x.name())
            except:
                pass
        return results

    def install(self, server_name, target_name, system=False):

        """
        Install a new virt system by way of a named cobbler profile.
        """

        # Example:
        # install("bootserver.example.org", "fc7webserver", True)

        conn = self.__get_conn()

        if conn is None:
            raise codes.FuncException("no connection")

        if not os.path.exists("/usr/bin/koan"):
            raise codes.FuncException("no /usr/bin/koan")
        target = "profile"
        if system:
            target = "system"

        # TODO: FUTURE: set --virt-path in cobbler or here
        koan_args = [
            "/usr/bin/koan",
            "--virt",
            "--virt-graphics",  # enable VNC
            "--%s=%s" % (target, target_name),
            "--server=%s" % server_name
        ]

        rc = sub_process.call(koan_args,shell=False)
        if rc == 0:
            return 0
        else:
            raise codes.FuncException("koan returned %d" % rc)


    def shutdown(self, vmid):
        """
        Make the machine with the given vmid stop running.
        Whatever that takes.
        """
        self.__get_conn()
        self.conn.shutdown(vmid)
        return 0


    def pause(self, vmid):

        """
        Pause the machine with the given vmid.
        """
        self.__get_conn()
        self.conn.suspend(vmid)
        return 0


    def unpause(self, vmid):

        """
        Unpause the machine with the given vmid.
        """

        self.__get_conn()
        self.conn.resume(vmid)
        return 0


    def create(self, vmid):

        """
        Start the machine via the given mac address.
        """
        self.__get_conn()
        self.conn.create(vmid)
        return 0


    def destroy(self, vmid):

        """
        Pull the virtual power from the virtual domain, giving it virtually no
        time to virtually shut down.
        """
        self.__get_conn()
        self.conn.destroy(vmid)
        return 0


    def undefine(self, vmid):

        """
        Stop a domain, and then wipe it from the face of the earth.
        by deleting the disk image and it's configuration file.
        """

        self.__get_conn()
        self.conn.undefine(vmid)
        return 0


    def get_status(self, vmid):

        """
        Return a state suitable for server consumption.  Aka, codes.py values, not XM output.
        """

        self.__get_conn()
        return self.conn.get_status(vmid)
