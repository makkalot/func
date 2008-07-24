"""
check checks to see how happy func is.
it provides sanity checks for basic user setup.

Copyright 2008, Red Hat, Inc
Michael DeHaan <mdehaan@redhat.com>

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""


import optparse
import os
import urllib2

from func.overlord import base_command
from func import utils
from func.minion import sub_process
from certmaster.config import read_config
from certmaster.commonconfig import MinionConfig


class CheckAction(base_command.BaseCommand):
    name = "check"
    usage = "check func for possible setup problems"
    summary = usage

    def addOptions(self):
        self.parser.add_option("-c", "--certmaster", action="store_true", help="check the certmaster configuration on this box")
        self.parser.add_option("-m", "--minion", action="store_true", help="check the minion configuration on this box")
        self.parser.add_option("-v", "--verbose", dest="verbose", action="store_true")

    def handleOptions(self, options):
        # FIXME: all through the code we have this constant in each
        # file, need to make this common.
        self.check_certmaster = options.certmaster
        self.check_minion     = options.minion
        self.verbose          = options.verbose

    def do(self, args):

        if not self.check_certmaster and not self.check_minion:
           print "* specify --certmaster, --minion, or both"
           return
        else:
           print "SCAN RESULTS:"

        hostname = utils.get_hostname()
        print "* FQDN is detected as %s, verify that is correct" % hostname
        self.check_iptables()

        if not os.getuid() == 0:
           print "* root is required to run these setup tests"
           return

        if self.check_minion:

           # check that funcd is running
           self.check_service("funcd")

           # check that the configured certmaster is reachable
           self.check_talk_to_certmaster()
           
        if self.check_certmaster:

           # check that certmasterd is running
           self.check_service("certmasterd")

           # see if we have any waiting CSRs
           # FIXME: TODO

           # see if we have signed any certs
           # FIXME: TODO

           self.server_spec = self.parentCommand.server_spec
           self.getOverlord()
           
           results = self.overlord_obj.test.add(1,2)
           hosts = results.keys()
           if len(hosts) == 0:
               print "* no systems have signed certs"
           else:
               failed = 0
               for x in hosts:
                   if results[x] != 3:
                       failed = failed+1 
               if failed != 0:
                   print "* unable to connect to %s registered minions from overlord" % failed
                   print "* run func '*' ping to check status"

           # see if any of our certs have expired

        # warn about iptables if running
        print "End of Report."

    def check_service(self, which):
        if os.path.exists("/etc/rc.d/init.d/%s" % which):
            rc = sub_process.call("/sbin/service %s status >/dev/null 2>/dev/null" % which, shell=True)
            if rc != 0:
                print "* service %s is not running" % which

    def check_iptables(self):
        if os.path.exists("/etc/rc.d/init.d/iptables"):
            rc = sub_process.call("/sbin/service iptables status >/dev/null 2>/dev/null", shell=True)
 
            if rc == 0:
              # FIXME: don't hardcode port
              print "* iptables may be running, ensure 51234 is unblocked"

    def check_talk_to_certmaster(self):
        config_file = '/etc/certmaster/minion.conf'
        minion_config = read_config(config_file, MinionConfig)
        cert_dir = minion_config.cert_dir
        # FIXME: don't hardcode port
        master_uri = "http://%s:51235/" % minion_config.certmaster
        print "* this minion is configured in /etc/certmaster/minion.conf to talk to host '%s' for certs, verify that is correct" % minion_config.certmaster
        # this will be a 501, unsupported GET, but we should be
        # able to tell if we can make contact
        connect_ok = True
        try:
            fd = urllib2.urlopen(master_uri)
            data = fd.read()
            fd.close()
        except urllib2.HTTPError:
            pass
        except:
            connect_ok = False
        if not connect_ok:
            print "cannot connect to certmaster at %s" % (master_uri)
