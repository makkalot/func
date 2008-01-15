## -*- coding: utf-8 -*-
##
## Process lister (control TBA)
##
## Copyright 2007, Red Hat, Inc
## Michael DeHaan <mdehaan@redhat.com>
##
## This software may be freely redistributed under the terms of the GNU
## general public license.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
##

# other modules
import sub_process
import codes

# our modules
from modules import func_module

# =================================

class ProcessModule(func_module.FuncModule):
    def __init__(self):
        self.methods = {
            "info"    : self.info,
            "kill"    : self.kill,
            "pkill"   : self.pkill,
            "mem"     : self.mem
        }
        func_module.FuncModule.__init__(self)

    def info(self, flags="-auxh"):
        """
        Returns a struct of hardware information.  By default, this pulls down
        all of the devices.  If you don't care about them, set with_devices to
        False.
        """

        flags.replace(";", "") # prevent stupidity

        cmd = sub_process.Popen(["/bin/ps", flags], executable="/bin/ps", 
                                stdout=sub_process.PIPE, 
                                stderr=sub_process.PIPE,
                                shell=False)

        data, error = cmd.communicate()

        # We can get warnings for odd formatting. warnings != errors.
        if error and error[:7] != "Warning":
            raise codes.FuncException(error.split('\n')[0])

        results = []
        for x in data.split("\n"):
            tokens = x.split()
            results.append(tokens)

        return results

    def mem(self):
        """
        Returns a list of per-program memory usage.

             Private  +  Shared   =  RAM used     Program

           [["39.4 MiB", "10.3 MiB", "49.8 MiB",  "Xorg"],
            ["42.2 MiB", "12.4 MiB", "54.6 MiB",  "nautilus"],
            ["52.3 MiB", "10.8 MiB", "63.0 MiB",  "liferea-bin"]
            ["171.6 MiB", "11.9 MiB", "183.5 MiB", "firefox-bin"]]

        Taken from the ps_mem.py script written by Pádraig Brady.
        http://www.pixelbeat.org/scripts/ps_mem.py
        """
        import os
        our_pid=os.getpid()
        results = []
        have_smaps=0
        have_pss=0

        def kernel_ver():
            """ (major,minor,release) """
            kv=open("/proc/sys/kernel/osrelease").readline().split(".")[:3]
            for char in "-_":
                kv[2]=kv[2].split(char)[0]
            return (int(kv[0]), int(kv[1]), int(kv[2]))

        kv=kernel_ver()

        def getMemStats(pid):
            """ return Rss,Pss,Shared (note Private = Rss-Shared) """
            Shared_lines=[]
            Pss_lines=[]
            pagesize=os.sysconf("SC_PAGE_SIZE")/1024 #KiB
            Rss=int(open("/proc/"+str(pid)+"/statm").readline().split()[1])*pagesize
            if os.path.exists("/proc/"+str(pid)+"/smaps"): #stat
                global have_smaps
                have_smaps=1
                for line in open("/proc/"+str(pid)+"/smaps").readlines(): #open
                    #Note in smaps Shared+Private = Rss above
                    #The Rss in smaps includes video card mem etc.
                    if line.startswith("Shared"):
                        Shared_lines.append(line)
                    elif line.startswith("Pss"):
                        global have_pss
                        have_pss=1
                        Pss_lines.append(line)
                Shared=sum([int(line.split()[1]) for line in Shared_lines])
                Pss=sum([int(line.split()[1]) for line in Pss_lines])
            elif (2,6,1) <= kv <= (2,6,9):
                Pss=0
                Shared=0 #lots of overestimation, but what can we do?
            else:
                Pss=0
                Shared=int(open("/proc/"+str(pid)+"/statm").readline().split()[2])*pagesize
            return (Rss, Pss, Shared)

        cmds={}
        shareds={}
        count={}
        for pid in os.listdir("/proc/"):
            try:
                pid = int(pid) #note Thread IDs not listed in /proc/
                if pid ==our_pid: continue
            except:
                continue
            cmd = file("/proc/%d/status" % pid).readline()[6:-1]
            try:
                exe = os.path.basename(os.path.realpath("/proc/%d/exe" % pid))
                if exe.startswith(cmd):
                    cmd=exe #show non truncated version
                    #Note because we show the non truncated name
                    #one can have separated programs as follows:
                    #584.0 KiB + 1.0 MiB = 1.6 MiB mozilla-thunder (exe -> bash)
                    #56.0 MiB + 22.2 MiB = 78.2 MiB mozilla-thunderbird-bin
            except:
                #permission denied or
                #kernel threads don't have exe links or
                #process gone
                continue
            try:
                rss, pss, shared = getMemStats(pid)
                private = rss-shared
                #Note shared is always a subset of rss (trs is not always)
            except:
                continue #process gone
            if shareds.get(cmd):
                if pss: #add shared portion of PSS together
                    shareds[cmd]+=pss-private
                elif shareds[cmd] < shared: #just take largest shared val
                    shareds[cmd]=shared
            else:
                if pss:
                    shareds[cmd]=pss-private
                else:
                    shareds[cmd]=shared
            cmds[cmd]=cmds.setdefault(cmd,0)+private
            if count.has_key(cmd):
               count[cmd] += 1
            else:
               count[cmd] = 1

        #Add max shared mem for each program
        total=0
        for cmd in cmds.keys():
            cmds[cmd]=cmds[cmd]+shareds[cmd]
            total+=cmds[cmd] #valid if PSS available

        sort_list = cmds.items()
        sort_list.sort(lambda x,y:cmp(x[1],y[1]))
        sort_list=filter(lambda x:x[1],sort_list) #get rid of zero sized processes

        #The following matches "du -h" output
        def human(num, power="Ki"):
            powers=["Ki","Mi","Gi","Ti"]
            while num >= 1000: #4 digits
                num /= 1024.0
                power=powers[powers.index(power)+1]
            return "%.1f %s" % (num,power)

        def cmd_with_count(cmd, count):
            if count>1:
               return "%s (%u)" % (cmd, count)
            else:
               return cmd

        for cmd in sort_list:
            results.append([
                "%sB" % human(cmd[1]-shareds[cmd[0]]),
                "%sB" % human(shareds[cmd[0]]),
                "%sB" % human(cmd[1]),
                "%s" % cmd_with_count(cmd[0], count[cmd[0]])
            ])
        if have_pss:
            results.append(["", "", "", "%sB" % human(total)])

        return results

    def kill(self,pid,signal="TERM"):
        if pid == "0":
            raise codes.FuncException("Killing pid group 0 not permitted")
        if signal == "":
            # this is default /bin/kill behaviour, 
            # it claims, but enfore it anyway
            signal = "-TERM"
        if signal[0] != "-":
            signal = "-%s" % signal
        rc = sub_process.call(["/bin/kill",signal, pid], 
                              executable="/bin/kill", shell=False)
        print rc
        return rc

    def pkill(self,name,level=""):
        # example killall("thunderbird","-9")
        rc = sub_process.call(["/usr/bin/pkill", name, level], 
                              executable="/usr/bin/pkill", shell=False)
        return rc

methods = ProcessModule()
register_rpc = methods.register_rpc
