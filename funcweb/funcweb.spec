
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)

%define version 0.1
Summary: Web application for Func API
Name: funcweb
Source1: version
Version: %(echo `awk '{ print $1 }' %{SOURCE1}`)
Release: %(echo `awk '{ print $2 }' %{SOURCE1}`)%{?dist}
License: GPLv2+
Group: Applications/System
Source0: %{name}-%{version}.tar.gz 
Source2: %{name}.te

#packages that are required
Requires: python >= 2.3
Requires: func >= 0.20
Requires: certmaster >= 0.20
Requires: mod_ssl >= 2.0
Requires: httpd >= 2.0
Requires: TurboGears >= 1.0.4.2
Requires: pam
#a bug in Turbogears package that causes some problems if 
#bigger version than that one is installed on the system !
Requires: python-cherrypy < 3.0

#the build requires
BuildRequires: python-devel
BuildRequires: TurboGears >= 1.0.4.2
%if %is_suse
BuildRequires: gettext-devel
%else
%if 0%{?fedora} >= 8
BuildRequires: python-setuptools-devel
%else
BuildRequires: python-setuptools
%endif
%endif
# SELinux module
%if 0%{?fedora} == 5
BuildRequires: checkpolicy, selinux-policy >= 2.2.40, m4
%else
BuildRequires: checkpolicy, selinux-policy-devel
%endif
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Url: https://fedorahosted.org/func/ 
%description

Web interface for managing systems controlled by Func

%package    selinux
Summary:    SELinux support for FuncWeb
Group:      System Environment/Daemons
Requires:   %{name} = %{version}
Requires(post): policycoreutils, initscripts, %{name}
Requires(preun): policycoreutils, initscripts, %{name}
Requires(postun): policycoreutils

%description selinux
This package adds SELinux policy for FuncWeb

%prep
%setup -q
mkdir -p selinux
cp -p %{SOURCE2} selinux/

%build
%{__python} setup.py build

%install
test "x$RPM_BUILD_ROOT" != "x" && rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install --prefix=/usr --root=$RPM_BUILD_ROOT

#SELinux part
cd selinux/
make -f %{_datadir}/selinux/devel/Makefile
install -p -m 644 -D %{name}.pp $RPM_BUILD_ROOT%{_datadir}/selinux/packages/%{name}/%{name}.pp

%clean
rm -fr $RPM_BUILD_ROOT

%files
%defattr(-, root, root, -)
%dir %{python_sitelib}/funcweb*egg-info
%{python_sitelib}/funcweb*egg-info/*

#creating the directory structure
%dir %{python_sitelib}/funcweb/
%dir %{python_sitelib}/funcweb/config
%dir %{python_sitelib}/funcweb/templates
%dir %{python_sitelib}/funcweb/tests
%dir %{python_sitelib}/funcweb/static
%dir %{python_sitelib}/funcweb/static/css
%dir %{python_sitelib}/funcweb/static/images
%dir %{python_sitelib}/funcweb/static/images/imgs
%dir %{python_sitelib}/funcweb/static/javascript/ext
%dir %{python_sitelib}/funcweb/identity
%dir %{_sysconfdir}/%{name}
%dir /var/log/funcweb
%config(noreplace) %{_sysconfdir}/httpd/conf.d/funcweb.conf
%config(noreplace) %{_sysconfdir}/%{name}/prod.cfg
%config(noreplace) %{_sysconfdir}/pam.d/funcweb
%config(noreplace) /etc/logrotate.d/funcweb_rotate

#adding the server startup shutdown thing 
/etc/init.d/funcwebd

#the python files for funcweb
%{python_sitelib}/funcweb/*.py*
%{python_sitelib}/funcweb/Makefile
%{python_sitelib}/funcweb/config/*.py*
%{python_sitelib}/funcweb/config/*.cfg
%{python_sitelib}/funcweb/templates/*.py*
%{python_sitelib}/funcweb/templates/*.kid
%{python_sitelib}/funcweb/templates/*.html
%{python_sitelib}/funcweb/templates/Makefile
%{python_sitelib}/funcweb/tests/*.py*
%{python_sitelib}/funcweb/tests/Makefile
%{python_sitelib}/funcweb/static/css/*.css
%{python_sitelib}/funcweb/static/css/Makefile
%{python_sitelib}/funcweb/static/images/*.png
%{python_sitelib}/funcweb/static/images/*.jpg
%{python_sitelib}/funcweb/static/images/*.ico
%{python_sitelib}/funcweb/static/images/*.gif
%{python_sitelib}/funcweb/static/images/imgs/*.gif
%{python_sitelib}/funcweb/static/images/Makefile
%{python_sitelib}/funcweb/static/javascript/*.js
%{python_sitelib}/funcweb/static/javascript/ext/*.js
%{python_sitelib}/funcweb/static/javascript/Makefile
%{python_sitelib}/funcweb/identity/*.py*
%{python_sitelib}/funcweb/identity/Makefile
/usr/bin/funcwebd
%doc README

%files selinux
%defattr(-, root, root, -)
%{_datadir}/selinux/packages/%{name}/%{name}.pp

%post
# for suse 
if [ -x /usr/lib/lsb/install_initd ]; then
  /usr/lib/lsb/install_initd /etc/init.d/funcwebd
# for red hat distros
elif [ -x /sbin/chkconfig ]; then
  /sbin/chkconfig --add funcwebd
# or, the old fashioned way
else
   for i in 2 3 4 5; do
        ln -sf /etc/init.d/funcwebd /etc/rc.d/rc${i}.d/S99funcwebd
   done
   for i in 1 6; do
        ln -sf /etc/init.d/funcwebd /etc/rc.d/rc${i}.d/S99funcwebd
   done
fi

%post selinux
if [ "$1" -le "1" ]; then # Fist install
    semodule -i %{_datadir}/selinux/packages/%{name}/%{name}.pp 2>/dev/null || :
    semanage port -a -t funcweb_port_t -p tcp 51236 2>/dev/null || :
fi

%preun selinux
if [ "$1" -lt "1" ]; then # Final removal
    semanage port -d -t funcweb_port_t -p tcp 51236 2>/dev/null || :
    semodule -r funcweb 2>/dev/null || :
fi

%postun selinux
if [ "$1" -ge "1" ]; then # Upgrade
    # Replaces the module if it is already loaded
    semodule -i %{_datadir}/selinux/packages/%{name}/%{name}.pp 2>/dev/null || :
fi

#before uninstall the things 
%preun
if [ "$1" = 0 ] ; then
  /etc/init.d/funcwebd stop  > /dev/null 2>&1
  if [ -x /usr/lib/lsb/remove_initd ]; then
    /usr/lib/lsb/remove_initd /etc/init.d/funcwebd
  elif [ -x /sbin/chkconfig ]; then
    /sbin/chkconfig --del funcwebd
  else
    rm -f /etc/rc.d/rc?.d/???funcwebd
  fi
fi


%changelog
* Fri Jul 11 2008 Krzysztof A. Adamski <krzysztofa@gmail.com> - 0.1
- SELinux policy added

* Sat Jul 05 2008 Denis Kurov <makkalot@gmail.com> - 0.1
- The first RPM for funcweb with new dynamic widget stuff

