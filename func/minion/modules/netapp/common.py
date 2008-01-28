import re
import subprocess 

SSH = '/usr/bin/ssh'
SSH_USER = 'root'
class GenericSSHError(Exception): pass
class NetappCommandError(Exception): pass
class NetappMissingParam(Exception): pass
class NetappNotImplementedError(Exception): pass

def ssh(host, cmdargs, input=None, user=SSH_USER):
    cmdline = [SSH, "-o forwardagent=no", "%s@%s" % (user, host)]
    cmdline.extend(cmdargs)

    cmd = subprocess.Popen(cmdline,
                           executable=SSH,
                           stdin=subprocess.PIPE,
                           stdout=subprocess.PIPE, 
                           stderr=subprocess.PIPE,
                           shell=False)

    (out, err) = cmd.communicate(input)
    
    if cmd.wait() != 0:
        raise GenericSSHError, err
    else:
        return out + err

def param_check(args, required):
    for r in required:
        if not args.has_key(r):
            raise NetappMissingParam, r

def check_output(regex, output):
    #strip newlines
    output = output.replace('\n', ' ')
    if re.search(regex, output):
        return True
    else:
        raise NetappCommandError, output

