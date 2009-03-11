# our modules
import func_module

# =================================

from func.minion.facts import minion_query
class FactsModule(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Has some useful about Facts module"
    
    def list_fact_modules(self):
        """
        List facts that are availible in that system
        """
        return minion_query.load_facts_modules().keys()
    
    def list_fact_methods(self):
        """
        List facts that are availible in that system
        """
        return minion_query.load_fact_methods().keys()

    def show_fact_module(self,module_name):
        """
        Show some info about fact module
        """
        
        for name,module in minion_query.load_facts_modules().iteritems():
            if name == module_name:
                return {
                        'name':name,
                        'description':getattr(module,"description",""),
                        'version':getattr(module,"version","")
                        }
        return {}

    def show_fact_method(self,method_name):
        """
        Display info about fact method
        """
        
        for name,method in minion_query.load_fact_methods().iteritems():
            if name == method_name:
                return {
                        'name':name,
                        'description':getattr(method,"description",""),
                        'tag':getattr(method,"tag",""),
                        'usage':getattr(method,"usage","")
                        }
        return {}

    def call_fact(self,method_name):
        """
        Sometimes we may need to get some of the facts live 
        """
        for name,method in minion_query.load_fact_methods().iteritems():
            if name == method_name:
                return method() 
        return {}



