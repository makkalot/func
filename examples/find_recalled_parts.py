#!/usr/bin/python
# find all parts that need to be recalled
# (C) Michael DeHaan, 2007 <mdehaan@redhat.com>
# ===============================================

import func.overlord.client as fc

bad = open("./part_data.txt").read().split()

info = fc.Client("*").hardware.info()

for (host,details) in info.iteritems():

    if type(details) != dict:
        print "%s had an error : %s" % (host,str(details))
        break

    for device in details["devices"]:
        for bad_value in bad:
           if device["Description"].find(bad_value) != -1:
              print "%s has flagged part: %s " % (host, device["Description"])
              break
  

