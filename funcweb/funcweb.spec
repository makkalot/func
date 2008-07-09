
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

#packages that are required
Requires: python >= 2.3
Requires: func >= 0.20
Requires: certmaster >= 0.1
Requires: mod_ssl >= 2.0
Requires: httpd >= 2.0
Requires: TurboGears >= 1.0.4.2

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
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: noarch
Url: https://hosted.fedoraproject.org/projects/func/
%description

Web interface for managing systems controlled by Func

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
%if 0%{?fedora} >= 8
%dir %{python_sitelib}/funcweb*egg-info
%{python_sitelib}/funcweb*egg-info/*
%endif

#creating the directory structure
%dir %{python_sitelib}/funcweb/
%dir %{python_sitelib}/funcweb/config
%dir %{python_sitelib}/funcweb/templates
%dir %{python_sitelib}/funcweb/tests
%dir %{python_sitelib}/funcweb/static
%dir %{python_sitelib}/funcweb/static/css
%dir %{python_sitelib}/funcweb/static/images
%dir %{python_sitelib}/funcweb/static/javascript
%dir %{python_sitelib}/funcweb/identity
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/httpd/conf.d/funcweb.conf
%config(noreplace) %{_sysconfdir}/%{name}/prod.cfg

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
%{python_sitelib}/funcweb/static/images/*.ico
%{python_sitelib}/funcweb/static/images/*.gif
%{python_sitelib}/funcweb/static/images/Makefile
%{python_sitelib}/funcweb/static/javascript/*.js
%{python_sitelib}/funcweb/static/javascript/Makefile
%{python_sitelib}/funcweb/identity/*.py*
%{python_sitelib}/funcweb/identity/Makefile
/usr/bin/funcwebd
%doc README

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
* Sat Jul 05 2008 Denis Kurov <makkalot@gmail.com> - 0.1
- The first RPM for funcweb with new dynamic widget stuff

