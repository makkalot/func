# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("funcweb", "release.py"))

packages=find_packages()
package_data = find_package_data(where='funcweb',
    package='funcweb')
if os.path.isdir('locales'):
    packages.append('locales')
    package_data.update(find_package_data(where='locales',
        exclude=('*.po',), only_in_packages=False))

#adding to the virtual part of the apache
etcpath    = "/etc/httpd/conf.d"
#having a manual part for funcweb may add more things there in the future
self_etcpath    = "/etc/funcweb"
#the init path for starting and stoping the server !
initpath = "/etc/init.d"
#the log path
logpath = "/var/log/funcweb"
rotpath = "/etc/logrotate.d"
#the pam path
pampath = "/etc/pam.d/"

#the setup part
setup(
    name="funcweb",
    version=version,
    description=description,
    author=author,
    author_email=email,
    url=url,
    license=license,
    install_requires=[
        "TurboGears >= 1.0.4.2",
    ],
    zip_safe=False,
    packages=packages,
    package_data=package_data,
    keywords=[
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop

        # if this has widgets, uncomment the next line
        # 'turbogears.widgets',

        # if this has a tg-admin command, uncomment the next line
        # 'turbogears.command',

        # if this has identity providers, uncomment the next line
        # 'turbogears.identity.provider',

        # If this is a template plugin, uncomment the next line
        # 'python.templating.engines',

        # If this is a full application, uncomment the next line
        # 'turbogears.app',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        # if this is an application that you'll distribute through
        # the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Applications',

        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Widgets',
    ],
    test_suite='nose.collector',
    entry_points = {
        'console_scripts': [
            'funcwebd = funcweb.commands:start',
            ],

        'turbogears.identity.provider' : [
            'pam = funcweb.identity.pamprovider:PAMIdentityProvider'
        ],

        'turbogears.visit.manager' : [
            'funcvisit = funcweb.identity.visit:FuncWebVisitManager'
        ],
    },
    # Uncomment next line and create a default.cfg file in your project dir
    # if you want to package a default configuration in your egg.
    data_files = [
            (etcpath,['etc/funcweb.conf']),
            (self_etcpath,['etc/prod.cfg']),
            (initpath,['init-scripts/funcwebd']),
            (logpath,[]),
            (rotpath,['etc/funcweb_rotate']),
            (pampath,['etc/pam.d/funcweb'])
            ],
    )
