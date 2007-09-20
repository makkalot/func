#!/usr/bin/python

import sys
from distutils.core import setup, Extension
#from setuptools import setup,find_packages
import string
import glob

NAME = "func"
VERSION = open("version", "r+").read().split()[0]
SHORT_DESC = "%s remote configuration and management api" % NAME
LONG_DESC = """
A small pluggabe xml-rpc daemon used by %s to implement various web services hooks
""" % NAME


if __name__ == "__main__":
 
        manpath    = "share/man/man1/"
        etcpath    = "/etc/%s" % NAME
        etcpathdb  = "/etc/%s/db" % NAME
        wwwpath    = "/var/www/%s" % NAME
        initpath   = "/etc/init.d/"
        logpath    = "/var/log/%s/" % NAME
        logpathdb  = "/var/log/%s/db/" % NAME
	settingspath = "/var/lib/%s/" % NAME
        migraterepopath = "/var/lib/%s/db/" % NAME
	schemapath = "/usr/share/%s/db_schema/" % NAME
	upgradepath = schemapath + "upgrade/"
	puppetpath = "/usr/share/%s/puppet-config/" % NAME
	manifestpath = "/etc/puppet/manifests/"
	profiletemplatepath = "/usr/share/%s/profile-template/" % NAME
        profilespath    = "/var/lib/%s/profiles/" % NAME
        queuedprofilespath    = "/var/lib/%s/profiles/queued/" % NAME
        setup(
                name="%s" % NAME,
                version = VERSION,
                author = "Lots",
                author_email = "et-mgmt-tools@redhat.com",
                url = "https://hosted.fedoraproject.org/projects/func/",
                license = "GPL",
		scripts = ["scripts/funcd",
                ],
		# package_data = { '' : ['*.*'] },
                package_dir = {"%s" % NAME: "",
			       "%s/server" % NAME: "server",
			       "%s/server/modules" % NAME: "modules/",
			       "%s/client" % NAME: "client",
			       "%s/server/yaml" % NAME: "server/yaml/",
                },
		packages = ["%s" % NAME,
	        	    "%s/server" % NAME,
			    "%s/client" % NAME,
	        	    "%s/server/modules" % NAME,
	 	            "%s/server/yaml" % NAME,
                ],
                data_files = [(initpath, ["init-scripts/funcd"]),
                              (etcpath, ["settings",]),
			      (etcpathdb, []),
			      (logpath, []),
			      (logpathdb, []),
			      (migraterepopath, []),
			      (profilespath, []),
			      (queuedprofilespath, [])],
                description = SHORT_DESC,
                long_description = LONG_DESC
        )

