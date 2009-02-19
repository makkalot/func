%if 0%{?rhel} == 3
%define __python_ver 2.3
%endif
%define python python%{?__python_ver}
%define __python /usr/bin/%{python}

%{!?python_version: %define python_version %(%{__python} -c "from distutils.sysconfig import get_python_version; print get_python_version()")}
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)

Summary: Remote management framework
Name: func
Version: 0.24 
Release: 5%{?dist}
Source0: %{name}-%{version}.tar.gz
License: GPLv2+
Group: Applications/System
%if 0%{?rhel} == 3
Requires: %{python}
Requires: pyOpenSSL-py23
%else
Requires: python >= 2.3
Requires: pyOpenSSL
%endif
Requires: %{python}-simplejson
Requires: certmaster >= %{version}
Requires: logrotate
BuildRequires: %{python}-devel
%if %is_suse
BuildRequires: gettext-devel
%else
%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
%if 0%{?rhel} >= 5
BuildRequires: python-setuptools
%endif
%endif
%endif
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Url: https://fedorahosted.org/func/

%description
func is a remote api for mangement, configuration, and monitoring of systems.

%prep
%setup -q
%if 0%{?rhel} == 3
%patch0 -p1
%endif

%build
%{__python} setup.py build

%install
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --prefix=/usr --root=$RPM_BUILD_ROOT

%clean
rm -fr $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%if "%{python_version}" >= "2.5"
%{python_sitelib}/func*.egg-info
%endif
%{_bindir}/funcd
%{_bindir}/func
%{_bindir}/func-inventory
%{_bindir}/func-create-module
%{_bindir}/func-transmit
%{_bindir}/func-build-map
#%{_bindir}/update-func
/etc/init.d/funcd
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/minion-acl.d/
%dir /etc/func/modules/
%config(noreplace) /etc/func/minion.conf
%config(noreplace) /etc/func/async_methods.conf
%config(noreplace) /etc/logrotate.d/func_rotate
%config(noreplace) /etc/func/modules/Test.conf
%config(noreplace) /etc/func/modules/Bridge.conf
%config(noreplace) /etc/func/modules/Vlan.conf
%dir %{python_sitelib}/func
%dir %{python_sitelib}/func/minion
%dir %{python_sitelib}/func/overlord
%dir %{python_sitelib}/func/overlord/cmd_modules
%dir %{python_sitelib}/func/overlord/modules
%dir %{python_sitelib}/func/yaml
%{python_sitelib}/func/minion/*.py*
%{python_sitelib}/func/overlord/*.py*
%{python_sitelib}/func/overlord/cmd_modules/*.py*
%{python_sitelib}/func/overlord/modules/*.py*
%{python_sitelib}/func/yaml/*.py*
%{python_sitelib}/func/*.py*
%dir %{python_sitelib}/func/minion/modules
%{python_sitelib}/func/minion/modules/*.py*

# we need to make the spec and setup.py find modules
# in deep dirs automagically

%dir %{python_sitelib}/func/minion/modules/netapp
%dir %{python_sitelib}/func/minion/modules/netapp/vol
%{python_sitelib}/func/minion/modules/*/*.py*
%{python_sitelib}/func/minion/modules/*/*/*.py*

%dir /var/log/func
%dir /var/lib/func
%doc AUTHORS README LICENSE
%{_mandir}/man1/func.1.gz
%{_mandir}/man1/func-inventory.1.gz
%{_mandir}/man1/funcd.1.gz
%{_mandir}/man1/func-transmit.1.gz


%post
# for suse 
if [ -x /usr/lib/lsb/install_initd ]; then
  /usr/lib/lsb/install_initd /etc/init.d/funcd
# for red hat distros
elif [ -x /sbin/chkconfig ]; then
  /sbin/chkconfig --add funcd
# or, the old fashioned way
else
   for i in 2 3 4 5; do
        ln -sf /etc/init.d/funcd /etc/rc.d/rc${i}.d/S99funcd
   done
   for i in 1 6; do
        ln -sf /etc/init.d/funcd /etc/rc.d/rc${i}.d/k01funcd
   done
fi

# upgrade old installs if needed
#/usr/bin/update-func

exit 0

%preun
if [ "$1" = 0 ] ; then
  /etc/init.d/funcd stop  > /dev/null 2>&1
  if [ -x /usr/lib/lsb/remove_initd ]; then
    /usr/lib/lsb/remove_initd /etc/init.d/funcd
  elif [ -x /sbin/chkconfig ]; then
    /sbin/chkconfig --del funcd
  else
    rm -f /etc/rc.d/rc?.d/???funcd
  fi
fi



%changelog
* Wed Feb 18 2009 Adrian Likins <alikins@redhat.com> - 0.24-5
- remove version file

* Mon Jan 19 2009 Adrian Likins <alikins@redhat.com> - 0.24.4
- make inclusion of egginfo dependant on having python >= 2.5
- remove need for patch on rhel3+python2.4 cases (distutils should
  do all the /usr/bin/python renaming now)
- minor reformatting changes

* Tue Jan 06 2009 Greg Swift <gregswift@gmail.com> - 0.24-3
- Fixed spec because it was only building in rhel3

* Wed Dec 31 2008 Greg Swift <gregswift@gmail.com> - 0.24-2
- Patched SPEC to build on rhel3 with python2.3
- Added Patch0 to handle python2.3 if on rhel3

* Wed Dec 17 2008 Adrian Likins <alikins@redhat.com> - 0.24-1
- require certmaster 0.24 

* Mon Dec 8 2008 Adrian Likins <alikins@redhat.com> - 0.24-1
- claim ownership of all dirs bz#474644
- add dep on logrotate

* Fri Jul 18 2008 Adrian Likins <alikins@redhat.com> - 0.23-2
- remove requirement for pyyaml, add python-simplejson

* Fri Jul 11 2008 Michael DeHaan <mdehaan@redhat.com> - 0.23-1
- (for ssalevan) adding in mapping/delegation tools

* Mon Jul 07 2008 Michael DeHaan <mdehaan@redhat.com> - 0.22-1
- packaged func-transmit script

* Wed Jul 02 2008 Michael DeHaan <mdehaan@redhat.com> - 0.21-1
- new release, upstream changes

* Mon Jun 30 2008 Michael DeHaan <mdehaan@redhat.com> - 0.20-1
- new release, upstream changes

* Fri Jun 28 2008 Adrian Likins <alikins@redhat.com> - 0.18-2
- fix fedora bug #441283 - typo in postinstall scriptlet
  (the init.d symlinks for runlevels 1 and 6 were created wrong)


* Mon Mar 03 2008 Adrian Likins <alikins@redhat.com> - 0.18-1
- split off certmaster

* Fri Feb 8 2008 Michael DeHaan <mdehaan@redhat.com> - 0.17-1
- bugfix release

* Mon Feb 4 2008 Michael DeHaan <mdehaan@redhat.com> - 0.16-1
- bump version for release
- fixing versions in previous changelogs

* Mon Feb 4 2008 Adrian Likins <alikins@redhat.com> - 0.15-1
- catch some deeper minion modules as well

* Sun Jan 13 2008 Steve 'Ashcrow' Milner <smilner@redhat.como> - 0.14-6
- Added in func-create-module for scripts.

* Tue Dec 18 2007 Adrian Likins <alikins@redhat.com> - 0.14-5
- add /var/lib/ dirs to spec file

* Thu Dec 13 2007 Eli Criffield <elicriffield@gmail.com> - 0.14-4
- changes for suse integration 

* Tue Dec 11 2007 Michael DeHaan <mdehaan@redhat.com> - 0.14-2
- python egg section added for F9 and later

* Tue Dec 11 2007 Michael DeHaan <mdehaan@redhat.com> - 0.14-1
- new release to mirrors

* Fri Oct 26 2007 Michael DeHaan <mdehaan@redhat.com> - 0.13-3
- Misc fixes per Fedora package-review

* Wed Oct 24 2007 Michael DeHaan <mdehaan@redhat.com> - 0.13-2
- packaged func-inventory and associated manpage
- release bump for Fedora submission
