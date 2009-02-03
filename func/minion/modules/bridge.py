#!/usr/bin/python
#
# Copyright 2008, Stone-IT
# Jasper Capel <capel@stone-it.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301  USA

"""
Func module for bridge management
"""

__author__ = "Jasper Capel <capel@stone-it.com>"
__version__ = "0.0.3"
__api_version__ = "0.0.2"

import func_module
import os, re
from certmaster.config import BaseConfig, Option, ListOption


class Bridge(func_module.FuncModule):
    version = __version__
    api_version = __api_version__
    description = "Func module for Bridge management"

    class Config(BaseConfig):
        ignorebridges = ListOption()
        brctl = Option("/usr/sbin/brctl")
        ip = Option("/sbin/ip")
        ifup = Option("/sbin/ifup")
        ifdown = Option("/sbin/ifdown")

    def list(self, listvif=True):
        """
        List bridges.

        Returns a dictionary. Elements look like this:
        key: bridgename, value: [ interface1, interface2, ..., interfaceN ]

        Keyword arguments:
        listvif -- Boolean: when False, xen-style virtual interfaces (vifX.Y) will be omitted from the listing
        """

        retlist = {}

        command = self.options.brctl + " show"

        fp = os.popen(command)

        vifpattern = re.compile('vif[0-9]+\.[0-9]+')

        # Read output, discard the first line (header):
        # Example output:
        # bridge name   bridge id       STP enabled interfaces
        # mgmtbr        8000.feffffffffff   no      vif12.0
        #                                           vif11.0
        # netsbr        8000.feffffffffff   no      pbond1
        #                                           vif0.2

        lines = fp.readlines()[1:]
        fp.close()

        curbr = ""
        for line in lines:
            elements = line.split()

            if len(elements) > 1:
                # Line containing a new bridge name + interface
                curbr = elements[0]
                if not curbr in self.options.ignorebridges:
                    if len(elements) == 3:
                        # This is a bridge without connected devices
                        retlist[elements[0]] = [ ]
                    elif len(elements) == 4:
                        # This is a bridge with one or more devices attached to
                        # it.
                        if vifpattern.match(elements[3]) and listvif == False:
                            # Omit this interface from the listing
                            retlist[elements[0]] = [ ]
                        else:
                            retlist[elements[0]] = [ elements[3] ]

            elif len(elements) == 1:
                # Dictionary key containing interface name should already
                # exist, append the interface.
                if not curbr in self.options.ignorebridges:
                    if not vifpattern.match(elements[0]) and listvif == True:
                        retlist[curbr].append(elements[0])
    
        return retlist

    def list_permanent(self):
        """
        List bridges which are configured to be enabled at boot time (in other words, for which an ifcfg-file exists)

        Returns a list of permanent bridges (bridges configured to be enabled at boot-time:
        key: bridgename, value: [ interface1, interface2, ..., interfaceN ]
        """

        retlist = {}
        ifpattern = re.compile('ifcfg-([a-z0-9]+)')
        # RHEL treats this value as case-sensitive, so so will we.
        brpattern = re.compile('TYPE=Bridge')
        brifpattern = re.compile('BRIDGE=([a-zA-Z0-9]+)')
        devpattern = re.compile('DEVICE=([a-zA-Z0-9\.]+)')
        nwscriptdir = "/etc/sysconfig/network-scripts"

        # Pass one: find bridges
        for item in os.listdir(nwscriptdir):
            match = ifpattern.match(item)
            if match:
                filename = "%s/%s" % (nwscriptdir, item)
                fp = open(filename, "r")
                lines = fp.readlines()
                fp.close()
                bridge = False
                ifname = ""
                for line in lines:
                    if brpattern.match(line):
                        bridge = True
                    devmatch = devpattern.match(line)
                    if devmatch:
                        ifname = devmatch.group(1)
                if bridge == True:
                    # Create empty interface list for bridge
                    retlist[ifname] = []

        # Pass two: match interface to bridge
        for item in os.listdir(nwscriptdir):
            match = ifpattern.match(item)
            if match:
                filename = "%s/%s" % (nwscriptdir, item)
                fp = open(filename, "r")
                lines = fp.readlines()
                fp.close()
                ifname = ""
                brname = ""
                for line in lines:
                    devmatch = devpattern.match(line)
                    if devmatch:
                        ifname = devmatch.group(1)
                    brmatch = brifpattern.match(line)
                    if brmatch:
                        brname = brmatch.group(1)
                if brname != "":
                    # Interface belongs to bridge
                    if brname in retlist:
                        # Just to be sure... if it doesn't match this interface
                        # is orphaned.
                        retlist[brname].append(ifname)
        return retlist
    
    def add_bridge(self, brname):
        """
        Creates a bridge

        Keyword arguments:
        brname -- Name for this bridge (string, ex: "br0")
        """

        if brname not in self.options.ignorebridges:
            brlist = self.list()
            if brname not in brlist:
                exitcode = os.spawnv(os.P_WAIT, self.options.brctl, [ self.options.brctl, "addbr", brname ] )
                if exitcode == 0:
                    os.spawnv(os.P_WAIT, self.options.brctl, [ self.options.brctl, "setfd", brname, "0" ] )
            else:
                # Bridge already exists, return 0 anyway.
                exitcode = 0
        else:
            exitcode = -1

        return exitcode

    def add_bridge_permanent(self, brname, ipaddr=None, netmask=None, gateway=None):
        """
        Creates a permanent bridge (this creates an ifcfg-file)

        Keyword arguments:
        brname -- Name for this bridge (string, ex: "br0")
        ipaddr -- IP address for this bridge (string)
        netmask -- Netmask for this bridge (string)
        gateway -- Gateway address for this bridge (string)
        """
        
        if brname not in self.options.ignorebridges:
            filename = "/etc/sysconfig/network-scripts/ifcfg-%s" % brname
            fp = open(filename, "w")
            filelines = [ "DEVICE=%s\n" % brname, "TYPE=Bridge\n", "ONBOOT=yes\n", "DELAY=0\n" ]
            if ipaddr != None:
                filelines.append("IPADDR=%s\n" % ipaddr)
            if netmask != None:
                filelines.append("NETMASK=%s\n" % netmask)
            if gateway != None:
                filelines.append("GATEWAY=%s\n" % gateway)
            fp.writelines(filelines)
            fp.close()
            exitcode = os.spawnv(os.P_WAIT, self.options.ifup, [ self.options.ifup, brname ] )
        else:
            exitcode = -1
        return exitcode


    def add_interface(self, brname, ifname):
        """
        Adds an interface to a bridge

        Keyword arguments:
        brname -- Bridge name (string, ex: "br0")
        ifname -- Interface to add to bridge (string, ex: "eth3")
        """

        if brname not in self.options.ignorebridges:
            brlist = self.list()
            if ifname not in brlist[brname]:
                exitcode = os.spawnv(os.P_WAIT, self.options.brctl, [ self.options.brctl, "addif", brname, ifname ] )
            else:
                # Interface is already a member of this bridge, return 0
                # anyway.
                exitcode = 0
        else:
            exitcode = -1

        return exitcode

    def add_interface_permanent(self, brname, ifname):
        """
        Permanently adds an interface to a bridge.
        Both interface and bridge must have a ifcfg-file we can write to.

        Keyword arguments:
        brname -- Bridge name (string, ex: "br0")
        ifname -- Interface name (string, ex: "eth2")
        """

        brfilename = "/etc/sysconfig/network-scripts/ifcfg-%s" % brname
        iffilename = "/etc/sysconfig/network-scripts/ifcfg-%s" % ifname
        if os.path.exists(brfilename) and os.path.exists(iffilename):
            # Read all lines first, then we append a BRIDGE= line.
            fp = open(iffilename, "r")
            lines = fp.readlines()
            fp.close()
            pattern = re.compile("BRIDGE=(.*)")
            exitcode = 0
            for line in lines:
                if pattern.match(line) != None:
                    # This interface is configured to bridge already, leave it
                    # alone.
                    exitcode = 1
                    break
            if exitcode == 0:
                # Try change on live interface
                if self.add_interface(brname, ifname) == 0:
                    # Change succeeded, write to ifcfg-file
                    # Reopen file for writing
                    fp = open(iffilename, "w")
                    lines.append("BRIDGE=%s\n" % brname)
                    fp.writelines(lines)
                    fp.close()
                else:
                    exitcode = 2
        else:
            exitcode = -1

        return exitcode

    def delete_bridge(self, brname):
        """
        Deletes a bridge

        Keyword arguments:
        brname -- Bridge name (string, ex: "br0")
        """
        if brname not in self.options.ignorebridges:
            # This needs some more error checking. :)
            self.down_bridge(brname)
            exitcode = os.spawnv(os.P_WAIT, self.options.brctl, [ self.options.brctl, "delbr", brname ] )
        else:
            exitcode = -1

        return exitcode

    def delete_bridge_permanent(self, brname):
        """
        Permanently deletes a bridge. This bridge must be configured through an ifcfg-file.

        Keyword arguments:
        brname -- Bridge name (ex: br0)
        """
        filename = "/etc/sysconfig/network-scripts/ifcfg-%s" % brname
        if brname not in self.options.ignorebridges:
            returncode = self.delete_bridge(brname)
            if os.path.exists(filename):
                os.remove(filename)
        else:
            returncode = -1
        return returncode
    
    def delete_interface(self, brname, ifname):
        """
        Deletes an interface from a bridge

        Keyword arguments:
        brname -- Bridge name (ex: br0)
        ifname -- Interface to remove (ex: eth2)
        """
        if brname not in self.options.ignorebridges:
            exitcode = os.spawnv(os.P_WAIT, self.options.brctl, [ self.options.brctl, "delif", brname, ifname ] )
        else:
            exitcode = -1

        return exitcode

    def delete_interface_permanent(self, brname, ifname):
        """
        Permanently deletes interface from bridge (interface must have an ifcfg-file)

        Keyword arguments:
        brname -- Bridge name (ex: br0)
        ifname -- Interface to remove (ex: eth2)
        """
        iffilename = "/etc/sysconfig/network-scripts/ifcfg-%s" % ifname

        if brname in self.options.ignorebridges:
            exitcode = -1
        elif os.path.exists(iffilename):
            # This only works if the interface itself is permanent
            fp = open(iffilename, "r")
            lines = fp.readlines()
            fp.close()
            pattern = re.compile("BRIDGE=(.*)")
            exitcode = 1
            for line in lines:
                if pattern.match(line):
                    lines.remove(line)
                    exitcode = 0
            if exitcode == 0:
                # Try change live
                trychange = self.delete_interface(brname, ifname)
                if trychange == 0:
                    # Change succeeded, write new interface file.
                    fp = open(iffilename, "w")
                    fp.writelines(lines)
                    fp.close()
                else:
                    exitcode = trychange
        else:
            exitcode = 2
        return exitcode

    def delete_all_interfaces(self, brname):
        """
        Deletes all interfaces from a bridge

        Keyword arguments:
        brname -- Bridge name (ex: "br0")
        """

        if brname not in self.options.ignorebridges:
            bridgelist = self.list()
            if brname in bridgelist:
                # Does this bridge exist?
                exitcode = 0
                interfaces = bridgelist[brname]
                for interface in interfaces:
                    childexitcode = self.delete_interface(brname, interface)
                    if exitcode == 0 and childexitcode != 0:
                        exitcode = childexitcode
            else:
                exitcode = 1
        else:
            exitcode = -1
        return exitcode

    def delete_all_interfaces_permanent(self, brname):
        """
        Permanently deletes all interfaces from a bridge
        
        Keyword arguments:
        brname -- Bridge name (string, ex: "br0")
        """
        if brname not in self.options.ignorebridges:
            bridgelist = self.list_permanent()
            if brname in bridgelist:
                exitcode = 0
                interfaces = bridgelist[brname]
                for interface in interfaces:
                    childexitcode = self.delete_interface_permanent(brname, interface)
                    if exitcode == 0 and childexitcode != 0:
                        exitcode = childexitcode
                # Now that the startup-config is gone, remove all interfaces
                # from this bridge in the running configuration
                if exitcode == 0:
                    exitcode = self.delete_all_interfaces(brname)
            else:
                exitcode = 1
        else:
            exitcode = -1
        return exitcode

    def make_it_so(self, newconfig):
        """
        Applies supplied configuration to system

        Keyword arguments;
        newconfig -- Configuration (dictionary, ex: {"br0": ["eth1", "eth2"]})
        """

        # The false argument is to make sure we don't get the VIFs in the
        # listing.
        currentconfig = self.list(False)

        # First, delete all bridges / bridge interfaces not present in new
        # configuration.
        for bridge, interfaces in currentconfig.iteritems():
            if bridge not in newconfig:
                self.delete_all_interfaces(bridge)
                self.delete_bridge(bridge)

            else:
                for interface in interfaces:
                    if interface not in newconfig[bridge]:
                        self.delete_interface(bridge, interface)

        # Now, check for bridges / interfaces we need to add.
        for bridge, interfaces in newconfig.iteritems():
            if bridge not in currentconfig:
                # Create this bridge
                self.add_bridge(bridge)
                for interface in interfaces:
                    # Add all the interfaces to the bridge
                    self.add_interface(bridge, interface)
            else:
                for interface in interfaces:
                    if interface not in currentconfig[bridge]:
                        self.add_interface(bridge, interface)

        return self.list()

    def write(self):
        """
        Applies running configuration to startup configuration
        """

        # The false argument is to make sure we don't get the VIFs in the
        # listing.
        newconfig = self.list(False)
        currentconfig = self.list_permanent()

        # First, delete all bridges / bridge interfaces not present in new
        # configuration.
        for bridge, interfaces in currentconfig.iteritems():
            if bridge not in newconfig:
                self.delete_all_interfaces_permanent(bridge)
                self.delete_bridge_permanent(bridge)

            else:
                for interface in interfaces:
                    if interface not in newconfig[bridge]:
                        self.delete_interface_permanent(bridge, interface)

        # Now, check for bridges / interfaces we need to add.
        for bridge, interfaces in newconfig.iteritems():
            if bridge not in currentconfig:
                # Create this bridge
                self.add_bridge_permanent(bridge)
                for interface in interfaces:
                    # Add all the interfaces to the bridge
                    self.add_interface_permanent(bridge, interface)
            else:
                for interface in interfaces:
                    if interface not in currentconfig[bridge]:
                        self.add_interface_permanent(bridge, interface)

        return self.list_permanent()

    def add_promisc_bridge(self, brname, ifname):
        """
        Creates a new bridge, attaches an interface to it and sets
        the MAC address of the connected interface to FE:FF:FF:FF:FF:FF so
        traffic can flow freely through the bridge. This seems to be required
        for use with xen.

        Keyword arguments:
        brname -- Bridge name (string, ex: "br0")
        ifname -- Interface name (string, ex: "eth2")
        """

        addbrret = self.add_bridge(brname)
        addifret = self.add_interface(brname,ifname)
        # Set the MAC address of the interface we're adding to the bridge to
        # FE:FF:FF:FF:FF:FF. This is consistent with the behaviour of the
        # Xen network-bridge script.
        setaddrret = os.spawnv(os.P_WAIT, self.options.ip, [ self.options.ip, "link", "set", ifname, "address", "fe:ff:ff:ff:ff:ff" ])
        if addbrret or addifret or setaddrret:
            return -1
        else:
            return 0

    def updown_bridge(self, brname, up):
        """
        Marks a bridge and all it's connected interfaces up or down (used internally)

        Keyword arguments:
        brname -- Bridge name (string, ex: "br0")
        up -- Whether to mark this bridge up. (Boolean, ex: false, when false, it marks everything as down)
        """

        if up:
            updown = "up"
        else:
            updown = "down"

        bridges = self.list()
        if not brname in bridges:
            # Bridge doesn't exist, or should be ignored.
            return -1

        interfaces = [ brname ]
        for bridgemember in bridges[brname]:
            interfaces.append(bridgemember)

        exitcode = 0

        for ifname in interfaces:
            retcode = os.spawnv(os.P_WAIT, self.options.ip, [self.options.ip, "link", "set", ifname, updown ] )
            if retcode != 0:
                exitcode = retcode

        return exitcode

    def up_bridge(self, brname):
        """
        Marks a bridge and all it's connected interfaces up
        """

        return self.updown_bridge(brname, 1)

    def down_bridge(self, brname):
        """
        Marks a bridge and all it's connected interfaces down
        """

        return self.updown_bridge(brname, 0)

