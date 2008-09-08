#
# Copyright 2008 
# Luca Foppiano <lfoppiano@byte-code.com>
# Simone Pucci <spucci@byte-code.com>
# Byte-code srl www.byte-code.com
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


import func_module
from func.minion import sub_process
from func.minion import codes
import process
import networktest
import command
from func import logger

class JBoss(func_module.FuncModule):
    version = "0.0.1"
    api_version = "0.0.1"
    description = "JBoss monitoring and control module"

    def status(self):
        """
            Get jboss information
            (instance name, ports, bind address, pid)
        """  
        processo = process.ProcessModule()
        results = processo.info("ax") 
		
	logging = logger.Logger().logger
        output = []
        for items in results:
            if "-Dprogram.name=run.sh" in items:
                for item in items:
                    if "java" in item:
                        java = True

                if java == True:
                    if items.__contains__("-c"):
                        instance = items[items.index("-c")+1]
                    else:
                        instance = ""

                    if items.__contains__("-b"):
                        address = items[items.index("-b")+1]
                    else:
                        address = ""

                    output.append((int(items[0]),instance,address,[]))

        # Retrieve information about network (netstat -tupln)

	net_status = networktest.NetworkTest()
	results = net_status.netstat("-tupln")

        for string in results:#netstat_list:
            address = None
            port = None
            pid = None

            try:
                address_port = string.split()[3]
                pid_name = string.split()[6]
            except:
                address_port = None
                pid_name = None
	    
            if address_port != None:
                try:
                    address = address_port.split(":")[0]
                    port =  int(address_port.split(":")[1])
                except:
                    address = None
                    port = None

            if pid_name != None:
                try:
                    pid = int(pid_name.split("/")[0])
                except:
                    pid = None
            
            if pid != None:
                for data in output:
                    if data[0] == pid:
                        #verify address
                        if address != None:
                            if data[2] == address:
                                data[3].append(port)

        return output


    def check(self, status=None):
        """
            Check if jboss instances works, controls:
                * check if instance listen on ports

            Return values:
                - instance up but not listen = (-1, instances with problem)
                - OK = (0, [])                
        """     
        if(status == None):
            data = self.status()
        else:
            data = status

        result = []
        code = 0
        for item in data:
            if len(item[3]) == 0:
                code = -1
                result.append(item)
        
        return (code, result)


    def search_by_port(self, port, status=None):
        """
            Search instance by listening port
        """
        if(status == None):
            data = self.status()
        else:
            data = status
	
	port = int(port)	
        founded = []

        for item in data:
            for ports in item[3]:
                if port == ports:
                    founded.append(item)
        
        return founded


    def search_by_instance(self, instance, status=None):
        """
            Search instance by instance name
        """
        if(status == None):
            data = self.status()
        else:
            data = status

        founded = []

        for item in data:
            if item[1] == instance:
                founded.append(item)
        
        return founded

    def search_by_address(self, address, status=None):
        """
            Search instance by bind address
        """
        if(status == None):
            data = self.status()
        else:
            data = status

        founded = []

        for item in data:
            if item[2] == address:
                founded.append(item)
        
        return founded

    def register_method_args(self):
        """
        Implementin the method argument getter part
        """

        return {
                'status':{
                    'args':{},
                    'description':"Get jboss information"
                    },
                'check':{
                    'args':{
                        'status':{
                            'type':'string',
                            'optional':True,
                            'description':"The status of instance to check (optional)"
                            }
                        },
                    'description':"Check if jboss instances works"
                    },
                'search_by_port':{
                    'args':{
                        'port':{
                            'type':'int',
                            'optional':False,
                            'min':0,
                            'max':65535,
                            'description':'The port to search for'
                            },
                        'status':{
                            'type':'string',
                            'optional':True,
                            'description':"The status of instance to check (optional)"
                            }
                        },
                    'description':"Search instance by listening port"
                    },
                'search_by_instance':{
                    'args':{
                        'instance':{
                            'type':'string',
                            'optional':False,
                            'description':"The name of the instance"
                            },
                        'status':{
                            'type':'string',
                            'optional':True,
                            'description':"The status of the instance to search (optional)"
                            }
                        },
                    'description':"Search instance by instance name"
                    },
                'search_by_address':{
                    'args':{
                        'address':{
                            'type':'string',
                            'optional':False,
                            'description':"The bind adress to check"
                            },
                        'status':{
                            'type':'string',
                            'optional':True,
                            'description':"The status of the instance to search (optional)"
                            }
                        },
                    'description':"Search instance by bind address"

                    }
                }

'''
    def start(self, address="127.0.0.1", instance="default"):
        """
            Start a jboss instance, you must specify couple 
	    address/instance_name. ATM __call__() in server.py 
	    doesn't support keywords.
        """
	# TODO: move outside this two variables
        jboss_path="/var/lib/jboss-4.2.2.GA"
        jboss_run_path=jboss_path+"/bin/run.sh"
        status=self.status()
		
        if len(self.search_by_address(address=address, status=status)) != 0:
            return (-1,"Another instances listening on this address, ")

       	if len(self.search_by_instance(instance=instance, status=status)) != 0:
            return (-1,"This instances is just instanced")

        launcher ="sh "+str(jboss_run_path)+" -c "+instance+" -b "+address

	comm = command.Command()
	comm.run(launcher)
        
	return "OK, instance "+ instance +"started on address "+address


    def stop(self, address="127.0.0.1"):
        """
            Stop a jboss instance, It suppose you are using 
	    use standard JNDI port 1099. 
 	    By default stop che localhost bind instance
            TODO: give more flexibility
        """
        jboss_path="/var/lib/jboss-4.2.2.GA"
        jboss_sd_path=jboss_path+"/bin/shutdown.sh"
        data = self.search_by_address(address)

        if len(data) == 0:
            return (-1, "Istance on "+ address +" not running")
    
	launcher ="sh "+str(jboss_sd_path)+" -s jnp://"+address+":1099"

        comm = command.Command()
	comm.run(launcher)

        return "OK, stopped instance listening address "+address
 
   def version(self):
        """
            Return jboss version
            TODO: implementation, is necessary to 
		find a way to get jboss version (maybe
		by parse log files)
        """

	return "version"

'''
