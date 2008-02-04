##
## NetApp Filer 'common' Module
##
## Copyright 2008, Red Hat, Inc
## John Eckersberg <jeckersb@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

import re
import sub_process 

SSH = '/usr/bin/ssh'
SSH_USER = 'root'
SSH_OPTS = '-o forwardagent=no'
class GenericSSHError(Exception): pass
class NetappCommandError(Exception): pass

def ssh(host, cmdargs, input=None, user=SSH_USER):
    cmdline = [SSH, SSH_OPTS, "%s@%s" % (user, host)]
    cmdline.extend(cmdargs)

    cmd = sub_process.Popen(cmdline,
                           executable=SSH,
                           stdin=sub_process.PIPE,
                           stdout=sub_process.PIPE, 
                           stderr=sub_process.PIPE,
                           shell=False)

    (out, err) = cmd.communicate(input)

    if cmd.wait() != 0:
        raise GenericSSHError, err
    else:
        return out + err

def check_output(regex, output):
    #strip newlines
    output = output.replace('\n', ' ')
    if re.search(regex, output):
        return True
    else:
        raise NetappCommandError, output

