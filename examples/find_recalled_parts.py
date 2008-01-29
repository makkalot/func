#!/usr/bin/python
# find all parts that need to be recalled
# (C) Michael DeHaan, 2007 <mdehaan@redhat.com>
# ===============================================

import func.overlord.client as fc
import func.utils as utils

bad = open("./part_data.txt").read().split()

info = fc.Client("*").hardware.hal_info()

for (host,details) in info.iteritems():

    if utils.is_error(details):
        print "%s had an error : %s" % (host,details[1:3])
        break

    for (device, full_output) in details.iteritems():
        for bad_value in bad:
             if full_output.find(bad_value) != -1:
                print "%s has flagged part: %s, matched %s" % (host, device, bad_value)
                break


