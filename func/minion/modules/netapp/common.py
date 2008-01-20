import subprocess 

SSH = '/usr/bin/ssh'

def ssh(user, host, command):
    cmd = subprocess.Popen([SSH, "%s@%s" % (user, host), command], 
                           executable=SSH,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           shell=False)

    (out, err) = cmd.communicate()
    return out
