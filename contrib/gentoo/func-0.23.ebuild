# Gentoo Portage ebuild for func, by Luca Lesinigo
# Distributed under the terms of the GNU General Public License v2
#
# this is pretty rough at the moment. it needs a look by someone who actually
# knows how to write ebuilds. But it's a start - it Works For Me :)
#
# Known todo list:
# - check for correct use of NEED_PYTHON and RDEPEND=dev-lang/python
# - check for correct usage of USE flags
# - write metadata.xml for local flags
# - patch init script for dependencies
#   \-> currently only hald if USE=hal
# - split overlord and minion setups (is this actually useful?)
#   \-> on minion could delete func/overlord directory and func scripts
# - provide config step to for cert request on the minion?
NEED_PYTHON=2.3

inherit distutils

DESRIPTION="Fedora Unified Network Controller allows for running commands on remote systems in a secure way"
HOMEPAGE="https://fedorahosted.org/func/"
SRC_URI="http://people.fedoraproject.org/~mdehaan/files/func/${P}.tar.gz"

LICENSE="GPLv2"
SLOT="0"
KEYWORDS="~x86 ~amd64 ~hppa"
IUSE="hal iptables nagios smart snmp"

RDEPEND="app-crypt/certmaster
         >=dev-lang/python-2.3
         sys-process/psmisc
         hal?      ( sys-apps/hal )
         iptables? ( net-firewall/iptables )
         nagios?   ( net-analyzer/nagios-plugins )
         smart?    ( sys-apps/smartmontools )
         snmp?     ( net-analyzer/net-snmp )"

PYTHON_MODNAME="func"

src_install() {
	distutils_src_install
	newinitd "${FILESDIR}"/funcd-init.d funcd
	# TODO: patch init script to depend on hald if USE=hal

	cd ${D}/usr/lib*/python*/site-packages/func
	# modules with external deps
	use hal      || rm -f  minion/modules/hardware.py
	use iptables || rm -fr minion/modules/iptables
	use nagios   || rm -f  minion/modules/nagios-check.py
	use smart    || rm -f  minion/modules/smart.py
	use snmp     || rm -f  minion/modules/snmp.py
	# non working modules
	rm -f  minion/modules/service.py # TODO: implement gentoo support
	rm -f  minion/modules/virt.py    # TODO: look in app-emulation/libvirt
	rm -f  minion/modules/rpms.py    # what about app-arch/rpm ?
	rm -f  minion/modules/yumcmd.py  # what about sys-apps/yum ?
	# non tested modules
	rm -f  minion/modules/jboss.py
	rm -fr minion/modules/netapp
}

