from turbogears import controllers, expose, flash
# from model import *
# import logging
# log = logging.getLogger("funcweb.controllers")

class Root(controllers.RootController):
    @expose(template="funcweb.templates.welcome")
    def index(self):
        import time
        # log.debug("Happy TurboGears Controller Responding For Duty")
        flash("Your application is now running")
        return dict(now=time.ctime())
