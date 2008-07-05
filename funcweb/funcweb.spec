
%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define is_suse %(test -e /etc/SuSE-release && echo 1 || echo 0)

%define version 0.1
Summary: Web GUI for FUNC API
Name: funcweb
Version: %{version}
Release: 1
License: GPLv2+
Group: Applications/System
Source0: funcweb-%{version}.tar.gz 
Requires: python >= 2.3
Requires: func >= 0.20
Requires: certmaster >= 0.1
Requires: mod_ssl >= 2.0
BuildRequires: httpd >= 2.0
BuildRequires: python-devel
BuildRequires: TurboGears >= 1.0
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

FuncWeb is the Web GUI management tool for commandline based tool func.

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
%{python_sitelib}/funcweb*egg-info
%dir %{python_sitelib}/funcweb*egg-info
%{python_sitelib}/funcweb*egg-info/*
%endif
#%{_bindir}/funcd

%dir %{python_sitelib}/funcweb/
%dir %{python_sitelib}/funcweb/config
%dir %{python_sitelib}/funcweb/templates
%dir %{python_sitelib}/funcweb/tests
%dir %{python_sitelib}/funcweb/static
%dir %{python_sitelib}/funcweb/static/css
%dir %{python_sitelib}/funcweb/static/images
%dir %{python_sitelib}/funcweb/static/javascript
%dir %{python_sitelib}/funcweb/identity
%config(noreplace) %{_sysconfdir}/httpd/conf.d/funcweb.conf

%{python_sitelib}/funcweb/*.py*
%{python_sitelib}/funcweb/config/*.py*
%{python_sitelib}/funcweb/config/*.cfg
%{python_sitelib}/funcweb/templates/*.py*
%{python_sitelib}/funcweb/templates/*.kid
%{python_sitelib}/funcweb/templates/*.html
%{python_sitelib}/funcweb/tests/*.py*
%{python_sitelib}/funcweb/static/css/*.css
%{python_sitelib}/funcweb/static/images/*.png
%{python_sitelib}/funcweb/static/images/*.ico
%{python_sitelib}/funcweb/static/images/*.gif
%{python_sitelib}/funcweb/static/javascript/*.js
%{python_sitelib}/funcweb/identity/*.py*

/usr/bin/start-funcweb
/usr/config/prod.cfg
%doc README

%post
%preun
%changelog
* Sat Jul 05 2008 Denis Kurov <makkalot@gmail.com> - 0.1
- package funcweb with new dynamic widget stuff

