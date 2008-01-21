import subprocess 

SSH = '/usr/bin/ssh'

class GenericSSHException(Exception): pass

def ssh(user, host, command):
    cmd = subprocess.Popen([SSH, "%s@%s" % (user, host), command], 
                           executable=SSH,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           shell=False)

    (out, err) = cmd.communicate()

    if err:
        raise GenericSSHException, err
    else:
        return out
