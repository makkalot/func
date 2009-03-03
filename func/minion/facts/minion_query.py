class FactsMinion(object):
    """
    That class wil be responsible for
    de-seriaqlization of the query by converting
    it to a Q structure and calling the facts modules
    """
    pass

FACTS_MODULES = "func/minion/facts/modules/"
from func.module_loader import load_modules
from func.minion.facts.modules import fact_module
def load_facts_modules():
    """
    loads the facts modules same way we do with
    minion modules ,keeps the refernces globally
    """
    return load_modules(path=FACTS_MODULES,main_class=fact_module.BaseFactModule)

