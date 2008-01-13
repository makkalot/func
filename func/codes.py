"""
func

Copyright 2007, Red Hat, Inc
See AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import exceptions


class FuncException(exceptions.Exception):
    pass


class InvalidMethodException(FuncException):
    pass

# FIXME: more sub-exceptions maybe
