#
# Copyright 2008
# Steve 'Ashcrow' Milner <smilner@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""
Django control module.

See http://www.djangoproject.com/ for more information about Django.
"""

import exceptions
import os
import sys
import types

import func_module
import sub_process


class Django(func_module.FuncModule):

    version = "0.0.1"
    api_version = "0.0.1"
    description = "Django control module."

    def _verify_path(self, project_path):
        """
        Verifies the project path exists and is readable.

        project_path is the path to the Django project.
        """
        # Verify path exists
        if not os.access(project_path, os.F_OK):
            raise exceptions.OSError(
                "Path %s doesn't exist." % project_path)
        # .. and that we can read it
        if not os.access(project_path, os.R_OK):
            raise exceptions.OSError(
                "Path %s is not readable." % project_path)
        return True

    def _get_settings(self, project_path):
        """
        Gets the settings object.

        project_path is the path to the Django project.
        """

        self._verify_path(project_path)
        # Append the settings to the path
        sys.path.append(project_path)
        import settings
        del sys.path[-1]
        return settings

    def settings(self, project_path):
        """
        Simple gets the settings for a specific application.

        project_path is the path to the Django project.
        """
        self._verify_path(project_path)
        settings = self._get_settings(project_path)
        items = {}
        # for each item in settings attempt to append the setting to items
        for item in dir(settings):
            # ... assuming it isn't _*
            if item[1] != '_':
                setting = getattr(settings, item)
                # See if we can directly append
                if type(setting) in [types.TupleType,
                                     types.StringType,
                                     types.DictType,
                                     types.ListType]:
                    items[item] = setting
                else:
                    # Else force it to a string
                    items[item] = str(setting)
        # Remove the settings from the path
        return items

    def setting(self, project_path, a_setting):
        """
        Returns a single setting.

        project_path is the path to the Django project.
        """
        items = self.settings(project_path)
        return items[a_setting]

    def manage(self, project_path, command):
        """
        Executes django-admin.py adding the path and settings
        variables for a command.

        project_path is the path to the Django project.
        command is the command to run.
        """
        self._verify_path(project_path)
        settings = self._get_settings(project_path)

        command = "django-admin.py %s --pythonpath=%s --settings=settings" % (
                      command, project_path)
        cmdref = sub_process.Popen(command.split(), stdout=sub_process.PIPE,
                                   stderr=sub_process.PIPE, shell=False,
                                   close_fds=True)
        data = cmdref.communicate()
        return (cmdref.returncode, data[0], data[1])

    def environment(self, project_path):
        """
        Gets the environment information that the project is running on.

        project_path is the path to the Django project.
        """
        self._verify_path(project_path)
        import platform
        from django import get_version

        return {'django_version': get_version(),
                'uname': platform.uname(),
                'dist': platform.dist(),
                'python_version': platform.python_version()}
