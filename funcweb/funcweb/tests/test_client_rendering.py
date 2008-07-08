from funcweb.widget_validation import WidgetSchemaFactory
from funcweb.widget_automation import WidgetListFactory,RemoteFormAutomation,RemoteFormFactory
from func.overlord.client import Overlord, Minions
import socket
import func.utils

class TestClientWidgetRender(object):
    minion = None

    def test_all_minions(self):
        minions =Minions("*").get_all_hosts()
        for m in minions:
            self.minion = m
            self.remote_widget_render()

    def remote_widget_render(self):
        print "\n******testing minion : %s**********"%(self.minion)
        fc = Overlord(self.minion)
        modules = fc.system.list_modules()
        display_modules={}
        
        print "Getting the modules that has exported arguments"
        for module in modules.itervalues():
            for mod in module:
                #if it is not empty
                exported_methods = getattr(fc,mod).get_method_args()[self.minion]
                if exported_methods:
                    print "%s will be rendered"%(mod)
                    display_modules[mod]=exported_methods

        #do the rendering work here
        for module,exp_meths in display_modules.iteritems():
            for method_name,other_options in exp_meths.iteritems():
                minion_arguments = other_options['args']
                if minion_arguments:
                    wlist_object = WidgetListFactory(minion_arguments,minion=self.minion,module=module,method=method_name)
                    wlist_object = wlist_object.get_widgetlist_object()
                    #print wlist_object
                    wf = WidgetSchemaFactory(minion_arguments)
                    schema_man=wf.get_ready_schema()
                    minion_form = RemoteFormAutomation(wlist_object,schema_man)
                    print "%s.%s.%s rendered"%(self.minion,module,method_name)



