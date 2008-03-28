#!/usr/bin/python
#
# Copyright 2008, Red Hat, Inc
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Library General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
# Copyright (c) 2007 Red Hat, inc 

import sys
import func.overlord.client as fc

if __name__ == '__main__':
    try:
        service = sys.argv[1]
    except Exception, ex:
        print "Usage: service_checker.py SERVICE"
        sys.exit(1)

    # Get the information from the systems
    info = fc.Overlord("*").service.status(service)
    for (host, details) in info.iteritems():
        status = "OFF"
        if details == 0:
            status = "ON"
        elif details == 3:
            status = "OFF"
        else:
            status = "ERR"
        print "%s: %s %s" % (host, service, status)
