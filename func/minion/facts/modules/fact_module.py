from func import logger
from func.utils import is_public_valid_method

class BaseFactModule(object):
    """
    The base fact module  which is clever
    enough to register the facts it is kind
    of FuncModule but registers modules with 
    different convention and style ..
    """
    version = "0.0.0"
    description = "Base module of all facts"



    def __init__(self):
        self.__init_log()
    
    def __init_log(self):
        log = logger.Logger()
        self.logger = log.logger
    
    def register_facts(self,fact_callers,module_name,abort_on_conflict=False):
        # a dictionary to catch the conflicts
        conflicts = {}
        for attr in dir(self):
            if self.__is_public_valid_method(attr):
                fact_method = getattr(self, attr)
                fact_callers["%s.%s"%(module_name,attr)] = fact_method
                if hasattr(fact_method,"tag"):
                    method_tag = getattr(fact_method,"tag")
                    if fact_callers.has_key(method_tag):
                        self.logger.info("Facts has registered the tag : %s before, it was overriden"%method_tag)
                        if abort_on_conflict:
                            if not conflicts.has_key(method_tag):
                                conflicts[method_tag] = []
                            conflicts[method_tag].append(getattr(fact_method,"__name__","default"))
                            if getattr(fact_callers[method_tag],"__name__","default") not in conflicts[method_tag]:
                                conflicts[method_tag].append(getattr(fact_callers[method_tag],"__name__","default"))

                    fact_callers[method_tag] = fact_method

        #if there is conflict show it
        if abort_on_conflict:
            return conflicts
                        
    def __is_public_valid_method(self,attr):
        return is_public_valid_method(self, attr, blacklist=['register_facts'])

