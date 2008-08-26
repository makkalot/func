# -*- coding: utf-8 -*-
"""This module contains functions called from console script entry points."""

import os
import sys

from os.path import dirname, exists, join

import pkg_resources
pkg_resources.require("TurboGears")

import turbogears
import cherrypy
from certmaster import utils

cherrypy.lowercase_api = True

class ConfigurationError(Exception):
    pass

#that variable will help us to see when we are in PRODUCTION 
PRODUCTION_ENV = False

def start():
    """Start the CherryPy application server."""
    global PRODUCTION_ENV
    setupdir = dirname(dirname(__file__))
    curdir = os.getcwd()

    # First look on the command line for a desired config file,
    # if it's not on the command line, then look for 'setup.py'
    # in the current directory. If there, load configuration
    # from a file called 'dev.cfg'. If it's not there, the project
    # is probably installed and we'll look first for a file called
    # 'prod.cfg' in the current directory and then for a default
    # config file called 'default.cfg' packaged in the egg.
    if exists("/etc/funcweb/prod.cfg"):
        #we work with production settings now !
        PRODUCTION_ENV = True
        configfile = "/etc/funcweb/prod.cfg"
    
    elif len(sys.argv) > 1:
        configfile = sys.argv[1]
    elif exists(join(setupdir, "setup.py")):
        configfile = join(setupdir, "dev.cfg")
    elif exists(join(curdir, "prod.cfg")):
        configfile = join(curdir, "prod.cfg")
    else:
        try:
            configfile = pkg_resources.resource_filename(
              pkg_resources.Requirement.parse("funcweb"),
                "config/default.cfg")
        except pkg_resources.DistributionNotFound:
            raise ConfigurationError("Could not find default configuration.")

    turbogears.update_config(configfile=configfile,
        modulename="funcweb.config")

    from funcweb.controllers import Root
    
    if PRODUCTION_ENV:
        utils.daemonize("/var/run/funcwebd.pid")
    #then start the server
    try:
        turbogears.start_server(Root())
    except Exception,e:
        print "Debug information from cherrypy server ...: ",e
        #sys.exit(1)    
