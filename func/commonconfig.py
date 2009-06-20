
"""
func

Copyright 2007, Red Hat, Inc
see AUTHORS

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""


from certmaster.config import BaseConfig, BoolOption, Option, IntOption, FloatOption

FUNCD_CONFIG_FILE="/etc/func/minion.conf"
OVERLORD_CONFIG_FILE="/etc/func/overlord.conf"

class FuncdConfig(BaseConfig):
    log_level = Option('INFO')
    acl_dir = Option('/etc/func/minion-acl.d')
    certmaster_overrides_acls = BoolOption(True)

    listen_addr = Option('')
    listen_port = IntOption('51234')
    minion_name = Option('')

class OverlordConfig(BaseConfig):
    socket_timeout = FloatOption(0)
    backend = Option('conf')
    group_db = Option('')


