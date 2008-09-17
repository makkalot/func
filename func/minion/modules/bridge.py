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

import func_module
import os

class Bridge(func_module.FuncModule):
    version = "0.0.1"
    api_version = "0.0.1"
    description = "Func module for Bridge management"

    # A list of bridge names that should be ignored. You can use this if you
    # have bridges that should never be touched by func.
    # This should go the the module-specific configuration file in the future.
    # Will ignore virbr0 by default, as it's managed by libvirtd, it's probably
    # a bad idea to touch it.
    ignorebridges = [ "virbr0" ]
    brctl = "/usr/sbin/brctl"
    ip = "/sbin/ip"

    def list(self):
        # Returns a dictionary. Elements look like this:
        # key: bridgename, value: [ interface1, interface2, ..., interfacen ]

        retlist = {}

        command = self.brctl + " show"

        fp = os.popen(command)

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
                if not curbr in self.ignorebridges:
                    if len(elements) == 3:
                        # This is a bridge without connected devices
                        retlist[elements[0]] = [ ]
                    elif len(elements) == 4:
                        # This is a bridge with one or more devices attached to
                        # it.
                        retlist[elements[0]] = [ elements[3] ]

            elif len(elements) == 1:
                # Dictionary key containing interface name should already
                # exist, append the interface.
                if not curbr in self.ignorebridges:
                    retlist[curbr].append(elements[0])
    
        return retlist
    
    def add_bridge(self, brname):
        # Creates a bridge
        if brname not in self.ignorebridges:
            exitcode = os.spawnv(os.P_WAIT, self.brctl, [ self.brctl, "addbr", brname ] )
        else:
            exitcode = -1

        return exitcode

    def add_interface(self, brname, ifname):
        # Adds an interface to a bridge
        if brname not in self.ignorebridges:
            exitcode = os.spawnv(os.P_WAIT, self.brctl, [ self.brctl, "addif", brname, ifname ] )
        else:
            exitcode = -1

        return exitcode

    def delete_bridge(self, brname):
        # Deletes a bridge
        if brname not in self.ignorebridges:
            # This needs some more error checking. :)
            exitcode = os.spawnv(os.P_WAIT, self.brctl, [ self.brctl, "delbr", brname ] )
        else:
            exitcode = -1

        return exitcode
    
    def delete_interface(self, brname, ifname):
        # Deletes an interface from a bridge
        if brname not in self.ignorebridges:
            exitcode = os.spawnv(os.P_WAIT, self.brctl, [ self.brctl, "delif", brname, ifname ] )
        else:
            exitcode = -1

        return exitcode

    def add_promisc_bridge(self, brname, ifname):
        # Creates a new bridge brname, attaches interface ifname to it and sets
        # the MAC address of the connected interface to FE:FF:FF:FF:FF:FF so
        # traffic can flow freely through the bridge. This is required for use
        # with Xen.
        addbrret = self.add_bridge(brname)
        addifret = self.add_interface(brname,ifname)
        # Set the MAC address of the interface we're adding to the bridge to
        # FE:FF:FF:FF:FF:FF. This is consistent with the behaviour of the
        # Xen network-bridge script.
        setaddrret = os.spawnv(os.P_WAIT, self.ip, [ self.ip, "link", "set", ifname, "address", "fe:ff:ff:ff:ff:ff" ])
        if addbrret or addifret or setaddrret:
            return -1
        else:
            return 0

    def updown_bridge(self, brname, up):
        # Marks a bridge and all it's connected interfaces up or down (used
        # internally)

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
            retcode = os.spawnv(os.P_WAIT, self.ip, [self.ip, "link", "set", ifname, updown ] )
            if retcode != 0:
                exitcode = retcode

        return exitcode

    def up_bridge(self, brname):
        # Marks a bridge and all it's connected interfaces up
        return self.updown_bridge(brname, 1)

    def down_bridge(self, brname):
        # Marks a bridge and all it's connected interfaces down
        return self.updown_bridge(brname, 0)

