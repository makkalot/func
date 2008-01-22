import subprocess 

SSH = '/usr/bin/ssh'

class GenericSSHError(Exception): pass
class NetappCommandError(Exception): pass
class NetappNotImplementedError(Exception): pass

def ssh(user, host, command):
    cmd = subprocess.Popen([SSH, "%s@%s" % (user, host), command], 
                           executable=SSH,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           shell=False)

    (out, err) = cmd.communicate()
    if cmd.wait() != 0:
        raise GenericSSHError, err
    else:
        return out
