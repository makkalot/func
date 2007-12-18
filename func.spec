
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)

Summary: Remote config, monitoring, and management api
Name: func
Source1: version
Version: %(echo `awk '{ print $1 }' %{SOURCE1}`)
Release: %(echo `awk '{ print $2 }' %{SOURCE1}`)%{?dist}
Source0: %{name}-%{version}.tar.gz
License: GPLv2+
Group: Applications/System
Requires: python >= 2.3
Requires: pyOpenSSL
BuildRequires: python-devel
%if %is_suse
BuildRequires: gettext-devel
%else
%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
BuildRequires: python-setuptools
%endif
%endif
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Url: https://hosted.fedoraproject.org/projects/func/

%description

func is a remote api for mangement, configation, and monitoring of systems.

%prep
%setup -q

%build
%{__python} setup.py build

%install
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --prefix=/usr --root=$RPM_BUILD_ROOT

%clean
rm -fr $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%if 0%{?fedora} > 8
%{python_sitearch}/func*.egg-info
%endif
%{_bindir}/funcd
%{_bindir}/func
%{_bindir}/certmaster
%{_bindir}/certmaster-ca
%{_bindir}/func-inventory
/etc/init.d/funcd
/etc/init.d/certmaster
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/minion-acl.d/
%dir %{_sysconfdir}/pki/%{name}
%dir /etc/func/modules/
%config(noreplace) /etc/func/minion.conf
%config(noreplace) /etc/func/certmaster.conf
%config(noreplace) /etc/logrotate.d/func_rotate
%dir %{python_sitelib}/func
%dir %{python_sitelib}/func/minion
%dir %{python_sitelib}/func/overlord
%dir %{python_sitelib}/func/overlord/cmd_modules
%{python_sitelib}/func/minion/*.py*
%{python_sitelib}/func/overlord/*.py*
%{python_sitelib}/func/overlord/cmd_modules/*.py*
%{python_sitelib}/func/*.py*
%dir %{python_sitelib}/func/minion/modules
%{python_sitelib}/func/minion/modules/*.py*
%dir /var/log/func
%dir /var/lib/func
%dir /var/lib/func/certmaster
%doc AUTHORS README LICENSE
%{_mandir}/man1/func.1.gz
%{_mandir}/man1/func-inventory.1.gz
%{_mandir}/man1/funcd.1.gz
%{_mandir}/man1/certmaster.1.gz
%{_mandir}/man1/certmaster-ca.1.gz


%post
# for suse 
if [ -x /usr/lib/lsb/install_initd ]; then
  /usr/lib/lsb/install_initd /etc/init.d/funcd
  /usr/lib/lsb/install_initd /etc/init.d/certmaster
# for red hat distros
elif [ -x /sbin/chkconfig ]; then
  /sbin/chkconfig --add funcd
  /sbin/chkconfig --add certmaster
# or, the old fashioned way
else
   for i in 2 3 4 5; do
        ln -sf /etc/init.d/funcd /etc/rc.d/rc${i}.d/S99funcd
        ln -sf /etc/init.d/certmaster /etc/rc.d/rc${i}.d/S99certmaster
   done
   for i in 1 6; do
        ln -sf /etc/init.d/funcd /etc/rc.d/rc${i}.d/S99funcd
        ln -sf /etc/init.d/certmaster /etc/rc.d/rc${i}.d/S99certmaster
   done
fi
exit 0

%preun
if [ "$1" = 0 ] ; then
  /etc/init.d/funcd stop  > /dev/null 2>&1
  /etc/init.d/certmaster stop  > /dev/null 2>&1
  if [ -x /usr/lib/lsb/remove_initd ]; then
    /usr/lib/lsb/remove_initd /etc/init.d/funcd
    /usr/lib/lsb/remove_initd /etc/init.d/certmaster
  elif [ -x /sbin/chkconfig ]; then
    /sbin/chkconfig --del funcd
    /sbin/chkconfig --del certmaster
  else
    rm -f /etc/rc.d/rc?.d/???funcd
    rm -f /etc/rc.d/rc?.d/???certmaster
  fi
fi


%changelog
* Tue Dec 18 2007 Adrian Likins <alikins@redhat.com> - 0.0.14-5
- add /var/lib/ dirs to spec file

* Thu Dec 13 2007 Eli Criffield <elicriffield@gmail.com> - 0.0.14-4
- changes for suse integration 

* Tue Dec 11 2007 Michael DeHaan <mdehaan@redhat.com> - 0.0.14-2
- python egg section added for F9 and later

* Tue Dec 11 2007 Michael DeHaan <mdehaan@redhat.com> - 0.0.14-1
- new release to mirrors

* Fri Oct 26 2007 Michael DeHaan <mdehaan@redhat.com> - 0.0.13-3
- Misc fixes per Fedora package-review

* Wed Oct 24 2007 Michael DeHaan <mdehaan@redhat.com> - 0.0.13-2
- packaged func-inventory and associated manpage
- release bump for Fedora submission

* Thu Oct 18 2007 Seth Vidal <skvidal at fedoraproject.org> - 0.0.12-1
- change out minion-acl.conf for minion-acl.d

* Mon Oct 8 2007 Adrian Likins <alikins@redhat.com> - 0.0.12-1
- add cmd_modules

* Fri Sep 28 2007 Adrian Likins <alikins@redhat.com> - 0.0.12-1
- remove rhpl deps

* Fri Sep 28 2007 Michael DeHaan <mdehaan@redhat.com> - 0.0.12-1
- bump version and get ready for first public release
- add BuildRequires python-devel
- add logrotate config

* Thu Sep 27 2007 Jesus Rodriguez <jesusr@redhat.com> - 0.0.11-7
- removed unnecessary yum-utils Require

* Wed Sep 26 2007 Jesus Rodriguez <jesusr@redhat.com> - 0.0.11-5
- fixed Requires to include pyOpenSSL for use by certmaster

* Tue Sep 25 2007 Michael DeHaan <mdehaan@redhat.com> - 0.0.11-4
- Added manpage documentation 
- Renamed minion config file

* Tue Sep 25 2007 Robin Norwood <rnorwood@redhat.com> - 0.0.11-3
- Change server -> minion and client -> overlord

* Thu Sep 20 2007 James Bowes <jbowes@redhat.com> - 0.0.11-2
- Clean up some speclint warnings

* Thu Sep 20 2007 Adrian Likins <alikins@redhat.com> - 0.0.11-1
- initial release (this one goes to .11)

