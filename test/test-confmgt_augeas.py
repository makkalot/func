#!/usr/bin/env python


import sys
import func.overlord.client as fc
c = fc.Client("*")

print c.configmgt_augeas.getenv('AUGEAS_ROOT')

def chroottest():
    envdict={}
    print 'Get the env. variable AUGEAS_ROOT'
    for host,envlist in c.confmgt_augeas.getenv('AUGEAS_ROOT').iteritems():  
        print "Host: "+host
        augroot=envlist.get('AUGEAS_ROOT')
        print 'AUGEAS_ROOT: '+augroot
        envdict[host]=augroot
        if augroot == '/' or augroot == '(none)':
            print "The node "+host+" is not chrooted with AUGEAS_ROOT"
            print "You should consider setting this variable"
            print "before launching this test."
            sys.exit()
    print
    
    print 'Prepare the test environment'
    for host in envdict:
        augroot=envdict[host]
        client = fc.Client(host)
        print client.command.run('mkdir -p '+augroot+'/etc/ssh')
        print client.command.run('cp /etc/hosts '+augroot+'/etc')
        print client.command.run('cp -r /etc/ssh/* '+augroot+'/etc/ssh')
    print

chroottest()


def basictest():
    #print 'Backup sshd_config'
    #print c.confmgt_augeas.backup('/etc/ssh/sshd_config')
    #print

    print 'Delete the Parameter PermitRootLogin in sshd_config'
    print c.confmgt_augeas.rm('/etc/ssh/sshd_config','PermitRootLogin')
    print
    
    print 'Delete the Parameter Port in sshd_config with an Augeas-style path'
    print c.confmgt_augeas.rm('/etc/ssh/sshd_config/Port')
    print
    
    print 'Get sshd_config Port value.'
    print c.confmgt_augeas.get('/etc/ssh/sshd_config','Port')
    print
    
    print 'Set Port to 22 in sshd_config'
    print c.confmgt_augeas.set('/etc/ssh/sshd_config','Port','22')
    print
    
    print 'Get sshd_config Port value.'
    print c.confmgt_augeas.get('/etc/ssh/sshd_config','Port')
    print
    
    print 'Try to delete a non existant parameter in sshd_config'
    print c.confmgt_augeas.rm('/etc/ssh/sshd_config','Nawak')
    print
    
    print 'Try to delete a parameter in a non existant file.'
    print c.confmgt_augeas.rm('/etc/ssh/nimp','Nawak')
    print
    
    print 'Get sshd_config PermitRootLogin value.'
    print c.confmgt_augeas.get('/etc/ssh/sshd_config','PermitRootLogin')
    print
    
    print 'Set PermitRootLogin to yes in sshd_config'
    print c.confmgt_augeas.set('/etc/ssh/sshd_config','PermitRootLogin','yes')
    print
    
    print 'Set PermitRootLogin to no in sshd_config with an Augeas-style path.'
    print c.confmgt_augeas.set('/etc/ssh/sshd_config/PermitRootLogin','','no')
    print
    
    print 'Set PermitRootLogin to yes in sshd_config with an Augeas-style path.'
    print c.confmgt_augeas.set('/etc/ssh/sshd_config/PermitRootLogin','','yes')
    print
    
    print 'Get sshd_config PermitRootLogin value.'
    print c.confmgt_augeas.get('/etc/ssh/sshd_config','PermitRootLogin')
    print
    
    print 'Get sshd_config PermitRootLogin value with an Augeas-style path.'
    print c.confmgt_augeas.get('/etc/ssh/sshd_config/PermitRootLogin')
    print
    
    print 'Attempt to get a value for a non existant param in sshd_config'
    print c.confmgt_augeas.get('/etc/ssh/sshd_config','Nawak')
    print
    
    print 'Attempt to get a value for an empty param in sshd_config'
    print c.confmgt_augeas.get('/etc/ssh/sshd_config','Subsystem')
    print
    
    print 'Search for conf. entry in hosts file with canonical hostname = localhost' 
    print c.confmgt_augeas.match('/etc/hosts','canonical','localhost')
    print
    
    #print 'List all direct children of hosts (not very useful)'
    #print c.confmgt_augeas.ls('/etc/hosts/*')
    #print
    
    print 'List all direct children parameters of 1st hosts entry.'
    for host,paramlist in c.confmgt_augeas.ls('/etc/hosts/1').iteritems():
        print "Host: "+host
        if type(paramlist) == type({}):
            for node in paramlist['nodes']:
                print node[0]+" = "+node[1]
        else:
            print paramlist
    print
    
    print 'List all children nodes of 1st hosts entry.' 
    for host,paramlist in c.confmgt_augeas.printconf('/etc/hosts/1').iteritems():
        print "Host: "+host
        if type(paramlist) == type({}):
            for node in paramlist['nodes']:
                print node[0]+" = "+node[1]
        else:
            print paramlist
    print
    
    print 'Get values of 1st host entry.'
    print c.confmgt_augeas.get('/etc/hosts/','1')
    print
    
    print 'List all values for parameter of 1st fstab entry.' 
    minionDict=c.confmgt_augeas.ls('/etc/fstab/1')
    for host,entry in minionDict.iteritems():
        print "Host: "+host
        if type(entry) == type({}):
            print "Entry path: "+entry['path']
            for node in entry['nodes']:
                print node[0]+" = "+node[1]
        else:
            print entry
    print
    
    print 'Get ipaddr of /etc/hosts 1st entry.'
    print c.confmgt_augeas.get('/etc/hosts/1','ipaddr')
    print
    #
    #print 'List all direct children parameters of sshd_config' 
    #for host,paramlist in c.confmgt_augeas.ls('/etc/ssh/sshd_config').iteritems():
    #   print "Host: "+host
    #   for node in paramlist['nodes']:
    #       print node[0]+" = "+node[1]
    #print
    #
    print 'List all children nodes of sshd_config'
    for host,paramlist in c.confmgt_augeas.printconf('/etc/ssh/sshd_config').iteritems():
       print "Host: "+host
       for node in paramlist['nodes']:
           print node[0]+" = "+node[1]
    print
    
    print 'List all direct children of AcceptEnv entries in sshd_config'
    for host,paramlist in c.confmgt_augeas.ls('/etc/ssh/sshd_config/AcceptEnv').iteritems():
        print "Host: "+host
        if type(paramlist)==type({}):
            for node in paramlist['nodes']:
                print node[0]+" = "+node[1]
        else:
            print paramlist
    print
    
    print 'See all AcceptEnv entries in sshd_config'
    for host,paramlist in c.confmgt_augeas.printconf('/etc/ssh/sshd_config/AcceptEnv').iteritems():
        print "Host: "+host
        if type(paramlist)==type({}):
            for node in paramlist['nodes']:
                print node[0]+" = "+node[1]
        else:
            print paramlist
    print
    
    print 'Try to match PermitRootLogin yes in sshd_config'
    print c.confmgt_augeas.match('/etc/ssh/sshd_config','PermitRootLogin','yes')
    print
    
    print 'Try to match PermitRootLogin yes in sshd_config with an Augeas-style path'
    print c.confmgt_augeas.match('/etc/ssh/sshd_config/PermitRootLogin','','yes')
    print
    
    print 'Try to match PermitRootLogin yes in some config. files.'
    print c.confmgt_augeas.match('/etc/*/*','PermitRootLogin','yes')
    print
    
    print 'Try to match AcceptEnv in sshd_config'
    print c.confmgt_augeas.match('/etc/ssh/sshd_config','AcceptEnv')
    print
    
    print 'Try to match PermitRootLogin in sshd_config'
    print c.confmgt_augeas.match('/etc/ssh/sshd_config','PermitRootLogin')
    print
    
    print 'Try to match PermitRootLogin in sshd_config with an Augeas-style path.'
    print c.confmgt_augeas.match('/etc/ssh/sshd_config/PermitRootLogin')
    print
    
    print 'Try to match canonical entries in hosts file.'
    print c.confmgt_augeas.match('/etc/hosts','canonical')
    print
    
    print 'Try to match canonical entries in hosts file with an Augeas-style path.'
    print c.confmgt_augeas.match('/etc/hosts/*/canonical')
    print
    
    print 'Augeas metainformation.'
    print c.confmgt_augeas.ls('/','/augeas')
    print c.confmgt_augeas.get('/','save','/augeas')
    
    #Not supposed to work:
    print c.confmgt_augeas.set('/','save','backup','/augeas')
    print c.confmgt_augeas.set('/save','','backup','/augeas')
    
    print c.confmgt_augeas.get('/save','','/augeas')
    print c.confmgt_augeas.get('/files/etc/hosts/lens','info','/augeas')
    
    
    
    print 'Add a new variable FOO at the end of the last AcceptEnv line of sshd_config'
    print "And we don't want to do this twice."
    foomatch=c.confmgt_augeas.match('/etc/ssh/sshd_config','AcceptEnv/*','FOO')
    for host,matchlist in foomatch.iteritems():
        if not matchlist:
            client = fc.Client(host)
            print client.confmgt_augeas.set('/etc/ssh/sshd_config/AcceptEnv[last()]','10000','FOO')
    print
    
    
    print 'Change the (canonical) hostname associated to a specific IP in hosts file.'
    hostfile='/etc/hosts'
    ip='1.2.3.4'
    newCanonical='fozzie'
    #newCanonical='piggy'
    # We search which entry in /etc/hosts refers to the IP
    ipmatch = c.confmgt_augeas.match(hostfile,'ipaddr',ip)
    # for each minion concerned 
    for host,entry in ipmatch.iteritems():
        # The first and unique entry in the list, entry[0], is what we searched for 
        # We check that the target canonical hostname is not already set
        if (type(entry) == type([]) and entry):
            oldCanonical=c.confmgt_augeas.get(entry[0],'canonical')[host]['value']
            if oldCanonical != newCanonical:
                print c.confmgt_augeas.set(entry[0],'canonical',newCanonical)
            else:
                print 'Nothing to do'
        else:
            print repr(entry)+' - no match'
    print

basictest()

# Extended path syntax
def extendedtest():
    print 'Tests on extended paths'
    # not working:
    print c.confmgt_augeas.match('//error/descendant-or-self::*','/augeas')
    print 
    
    print c.confmgt_augeas.get('/etc/hosts/*[ipaddr = "127.0.0.1"]/canonical')
    print c.confmgt_augeas.get('/etc/hosts/*[ipaddr = "127.0.0.1"]/','canonical')
    print

    print c.confmgt_augeas.get("/etc//ipaddr[. = '127.0.0.1']")
    print

    print c.confmgt_augeas.match('/etc/hosts/*/ipaddr')
    print c.confmgt_augeas.match('/etc/hosts/*/','ipaddr')

    # not working:
    #print c.confmgt_augeas.printconf('/etc/hosts/*/','ipaddr')
    #print

    print c.confmgt_augeas.match('/etc/pam.d/*[.//module="pam_limits.so"]')
    print 

    # not working (wrong):
    print c.confmgt_augeas.match('/etc//1')

    # not working (wrong):
    print c.confmgt_augeas.match('/descendant-or-self::4')

extendedtest()
