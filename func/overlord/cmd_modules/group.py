"""
group func method invoker

Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

from func.overlord.groups import Groups
from func.overlord import base_command
from certmaster.config import read_config, BaseConfig, ListOption


class Group(base_command.BaseCommand):
    name = "group"
    usage = "group [--add_group] [--remove_group] [--list_group] [--list_all] [--add_host] [--remove_host] [--list_hosts] {--exclude}"
    summary = "allows a specific module and method to be called"
    def addOptions(self):
        
        self.parser.add_option("-v", "--verbose", dest="verbose",
                               default=self.verbose,
                               action="store_true")
        
        self.parser.add_option("--ag", "--add_group", 
                               dest="add_group",
                               action="store_true")
        
        self.parser.add_option("--lg", "--list_group", 
                               dest="list_group",
                               action="store_true")
        

        self.parser.add_option("--rg", "--remove_group", 
                               dest="remove_group",
                               action="store_true")
        
        self.parser.add_option("--la", "--list_all", 
                               dest="list_all",
                               action="store_true")
        
        self.parser.add_option("--ah", "--add_host", 
                               dest="add_host",
                               action="store_true")

        self.parser.add_option("--rh", "--remove_host", 
                               dest="remove_host",
                               action="store_true")

        self.parser.add_option("--lh", "--list_hosts", 
                               dest="list_hosts",
                               action="store_true")

        self.parser.add_option("--e", "--exclude", 
                               dest="exclude",
                               action="store",
                               type="string")


    def handleOptions(self, options):
        self.options = options
        self.verbose = options.verbose

        # I'm not really a fan of the "module methodname" approach
        # but we'll keep it for now -akl

    def parse(self, argv):
        self.argv = argv

        return base_command.BaseCommand.parse(self, argv)
        

    def do(self, args):

        #create a group object
        #it will get the internals from other places :)
        self.group = Groups()

        #for that one we dont need any args
        if self.options.list_all:
            self.group.show()

        else:
            #here we need to have args[0]
            if not args:
                self.outputUsage()
                return

            if self.options.add_group:
                self._add_gr(args[0])

            elif self.options.remove_group:
                self._rm_gr(args[0])

            elif self.options.list_group:
                self._ls_gr(args[0])

            elif self.options.add_host:
                self._add_host(args[0])

            elif self.options.remove_host:
                self._rm_host(args[0])

            elif self.options.list_hosts:
                self._ls_host(args[0])

            else:
                #no valid usage
                self.outputUsage()

    def _add_gr(self,args):
        """
        Add args a list of gorups
        """
        args = self._parse_args_list(args)
        for arg in args:
            res = self.group.add_group(arg,save=True)
            if not res[0]:
                print res[1]


    def _rm_gr(self,args):
        args = self._parse_args_list(args)
        for arg in args:
            self.group.remove_group_glob(arg)

    def _ls_gr(self,args):
        args = self._parse_args_list(args)
        print "GROUPS : "
        for arg in args:
            res=self.group.get_groups_glob(arg)
            if res :
                print "\t ",res


    def _add_host(self,args):
        args = self._parse_args_list(args)
        args = self._match_group_host(args)
        if self.options.exclude:
            exclude = self._parse_args_list(self.options.exclude)
            exclude = self._match_group_host(exclude)
            
            for g_i,g_e in zip(args.iteritems(),exclude.iteritems()):
                for host_include,host_exclude in zip(g_i[1],g_e[1]):
                    self.group.add_hosts_to_group_glob(g_i[0][1:],host_include,exclude_string=host_exclude)
        #user didnt enter the exclude option so go on normally
        else:
            for group,hosts in args.iteritems():
                for h in hosts:
                    #adding here
                    #sometimes we may have formats like that :
                    #@group1:one,two,three
                    if h.find(",") != -1:
                        for sub_host in h.split(","):
                            self.group.add_hosts_to_group_glob(group[1:],sub_host)
                    else:
                        self.group.add_hosts_to_group_glob(group[1:],h)



    def _rm_host(self,args):
        args = self._parse_args_list(args)
        args = self._match_group_host(args)
        if self.options.exclude:
            exclude = self._parse_args_list(self.options.exclude)
            exclude = self._match_group_host(exclude)
            for g_i,g_e in zip(args.iteritems(),exclude.iteritems()):
                for host_include,host_exclude in zip(g_i[1],g_e[1]):
                    self.group.remove_host_glob(g_i[0][1:],host_include,exclude_string=host_exclude)
        #user didnt enter the exclude option so go on normally
        else:
            for group,hosts in args.iteritems():
                for h in hosts:
                    #adding here
                    if h.find(",") != -1:
                        for sub_host in h.split(","):
                            self.group.remove_host_glob(group[1:],sub_host)
                    else:
                        self.group.remove_host_glob(group[1:],h)


    def _ls_host(self,args):
        if self.options.exclude:
            print self.group.get_hosts_glob(args,exclude_string=self.options.exclude)
        else:
            print self.group.get_hosts_glob(args)
    
    def _parse_args_list(self,args):
        """
        Parsing the args sometimes we separate em
        via ; or , so need to convert to a list
        """
        if args.find(";")!=-1:
            return args.split(";")
        elif args.find(",")!=-1:
            return args.split(";")
        return [args]

    def _match_group_host(self,args):
        """
        Returns a dictionary for 
        {group:hosts}
        """
        groups = {}
        for arg in args :
            if arg.find(":")!=-1:
                group,host = arg.split(":")
                if groups.has_key(group):
                    if not host in groups[group]:
                        groups[group].append(host)
                else:
                    groups[group]=[]
                    groups[group].append(host)
            else:
                group = arg
                if groups.has_key(group):
                    if not "*" in groups[group]:
                        groups[group].append("*")
                else:
                    groups[group]=[]
                    groups[group].append("*")
        return groups


