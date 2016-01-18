# centos/sclo spec file for php-pecl-apcu, from:
#
# remirepo spec file for php-pecl-apcu
# with SCL compatibility, from:
#
# Fedora spec file for php-pecl-apcu
#
# Copyright (c) 2013-2016 Remi Collet
# License: CC-BY-SA
# http://creativecommons.org/licenses/by-sa/4.0/
#
# Please, preserve the changelog entries
#
%if 0%{?scl:1}
%if "%{scl}" == "rh-php56"
%global sub_prefix sclo-php56-
%else
%global sub_prefix sclo-%{scl_prefix}
%endif
%endif

%{?scl:          %scl_package        php-pecl-apcu}
%{!?scl:         %global pkg_name    %{name}}
%{!?php_inidir:  %global php_inidir  %{_sysconfdir}/php.d}
%{!?php_incldir: %global php_incldir %{_includedir}/php}
%{!?__pecl:      %global __pecl      %{_bindir}/pecl}
%{!?__php:       %global __php       %{_bindir}/php}
%global pecl_name  apcu
%if "%{php_version}" < "5.6"
%global ini_name   %{pecl_name}.ini
%else
%global ini_name   40-%{pecl_name}.ini
%endif

Name:           %{?sub_prefix}php-pecl-apcu
Summary:        APC User Cache
Version:        4.0.10
Release:        1%{?dist}
Source0:        http://pecl.php.net/get/%{pecl_name}-%{version}.tgz
Source1:        %{pecl_name}.ini

License:        PHP
Group:          Development/Languages
URL:            http://pecl.php.net/package/APCu

BuildRequires:  %{?scl_prefix}php-devel
BuildRequires:  %{?scl_prefix}php-pear
BuildRequires:  pcre-devel

Requires:       %{?scl_prefix}php(zend-abi) = %{php_zend_api}
Requires:       %{?scl_prefix}php(api) = %{php_core_api}

Provides:       %{?scl_prefix}php-apcu = %{version}
Provides:       %{?scl_prefix}php-apcu%{?_isa} = %{version}
Provides:       %{?scl_prefix}php-pecl-apcu = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl-apcu%{?_isa} = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl(apcu) = %{version}
Provides:       %{?scl_prefix}php-pecl(apcu)%{?_isa} = %{version}
# Same provides than APC, this is a drop in replacement
Provides:       %{?scl_prefix}php-apc = %{version}
Provides:       %{?scl_prefix}php-apc%{?_isa} = %{version}
Provides:       %{?scl_prefix}php-pecl-apc = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl-apc%{?_isa} = %{version}-%{release}
Provides:       %{?scl_prefix}php-pecl(APC) = %{version}
Provides:       %{?scl_prefix}php-pecl(APC)%{?_isa} = %{version}

%if 0%{?fedora} < 20 && 0%{?rhel} < 7
# Filter shared private
%{?filter_provides_in: %filter_provides_in %{_libdir}/.*\.so$}
%{?filter_setup}
%endif


%description
APCu is userland caching: APC stripped of opcode caching in preparation
for the deployment of Zend OPcache as the primary solution to opcode
caching in future versions of PHP.

APCu has a revised and simplified codebase, by the time the PECL release
is available, every part of APCu being used will have received review and
where necessary or appropriate, changes.

Simplifying and documenting the API of APCu completely removes the barrier
to maintenance and development of APCu in the future, and additionally allows
us to make optimizations not possible previously because of APC's inherent
complexity.

APCu only supports userland caching (and dumping) of variables, providing an
upgrade path for the future. When O+ takes over, many will be tempted to use
3rd party solutions to userland caching, possibly even distributed solutions;
this would be a grave error. The tried and tested APC codebase provides far
superior support for local storage of PHP variables.

Package built for PHP %(%{__php} -r 'echo PHP_MAJOR_VERSION.".".PHP_MINOR_VERSION;')%{?scl: as Software Collection (%{scl} by %{?scl_vendor}%{!?scl_vendor:rh})}.


%package devel
Summary:       APCu developer files (header)
Group:         Development/Libraries
Requires:      %{name}%{?_isa} = %{version}-%{release}
Requires:      %{?scl_prefix}php-devel%{?_isa}
Provides:      %{?scl_prefix}php-pecl-apcu-devel = %{version}-%{release}
Provides:      %{?scl_prefix}php-pecl-apcu-devel%{?_isa} = %{version}-%{release}
Provides:      %{?scl_prefix}php-pecl-apc-devel = %{version}-%{release}
Provides:      %{?scl_prefix}php-pecl-apc-devel%{?_isa} = %{version}-%{release}

%description devel
These are the files needed to compile programs using APCu.


%prep
%setup -qc
mv %{pecl_name}-%{version} NTS

cd NTS

# Sanity check, really often broken
extver=$(sed -n '/#define PHP_APCU_VERSION/{s/.* "//;s/".*$//;p}' php_apc.h)
if test "x${extver}" != "x%{version}"; then
   : Error: Upstream extension version is ${extver}, expecting %{version}.
   exit 1
fi
cd ..


%build
cd NTS
%{_bindir}/phpize
%configure --with-php-config=%{_bindir}/php-config
make %{?_smp_mflags}


%install
# Install the NTS stuff
make -C NTS install INSTALL_ROOT=%{buildroot}
install -D -m 644 %{SOURCE1} %{buildroot}%{php_inidir}/%{ini_name}

# Install the package XML file
install -D -m 644 package.xml %{buildroot}%{pecl_xmldir}/%{name}.xml

# Test & Documentation
cd NTS
for i in $(grep 'role="test"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_testdir}/%{pecl_name}/$i
done
for i in apc.php $(grep 'role="doc"' ../package.xml | sed -e 's/^.*name="//;s/".*$//')
do install -Dpm 644 $i %{buildroot}%{pecl_docdir}/%{pecl_name}/$i
done


%check
cd NTS

# Check than both extensions are reported (BC mode)
%{_bindir}/php -n -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so -m | grep 'apcu'
%{_bindir}/php -n -d extension=%{buildroot}%{php_extdir}/%{pecl_name}.so -m | grep 'apc$'

# Upstream test suite for NTS extension
TEST_PHP_EXECUTABLE=%{_bindir}/php \
TEST_PHP_ARGS="-n -d extension_dir=$PWD/modules -d extension=%{pecl_name}.so" \
NO_INTERACTION=1 \
REPORT_EXIT_STATUS=1 \
%{_bindir}/php -n run-tests.php --show-diff


# when pear installed alone, after us
%triggerin -- %{?scl_prefix}php-pear
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

# posttrans as pear can be installed after us
%posttrans
if [ -x %{__pecl} ] ; then
    %{pecl_install} %{pecl_xmldir}/%{name}.xml >/dev/null || :
fi

%postun
if [ $1 -eq 0 -a -x %{__pecl} ] ; then
    %{pecl_uninstall} %{pecl_name} >/dev/null || :
fi


%files
%doc %{pecl_docdir}/%{pecl_name}
%{pecl_xmldir}/%{name}.xml

%config(noreplace) %{php_inidir}/%{ini_name}
%{php_extdir}/%{pecl_name}.so


%files devel
%doc %{pecl_testdir}/%{pecl_name}
%{php_incldir}/ext/%{pecl_name}


%changelog
* Mon Jan 18 2016 Remi Collet <remi@fedoraproject.org> - 4.0.10-1
- cleanup for SCLo build

* Mon Dec  7 2015 Remi Collet <remi@fedoraproject.org> - 4.0.10-1
- Update to 4.0.10 (stable)

* Fri Nov 20 2015 Remi Collet <remi@fedoraproject.org> - 4.0.8-1
- Update to 4.0.8 (stable)

* Fri Nov 20 2015 Remi Collet <remi@fedoraproject.org> - 4.0.8-0.1.20151120git0911f48
- test build for upcoming 4.0.8
- sources from github

* Fri Jun 19 2015 Remi Collet <remi@fedoraproject.org> - 4.0.7-3
- allow build against rh-php56 (as more-php56)

* Tue Jun  9 2015 Remi Collet <remi@fedoraproject.org> - 4.0.7-2
- upstream fix for the control panel
- drop runtime dependency on pear, new scriptlets

* Wed Dec 24 2014 Remi Collet <remi@fedoraproject.org> - 4.0.7-1.1
- Fedora 21 SCL mass rebuild

* Sat Oct 11 2014 Remi Collet <remi@fedoraproject.org> - 4.0.7-1
- Update to 4.0.7

* Sun Aug 24 2014 Remi Collet <remi@fedoraproject.org> - 4.0.6-2
- improve SCL stuff

* Thu Jun 12 2014 Remi Collet <remi@fedoraproject.org> - 4.0.6-1
- Update to 4.0.6 (beta)

* Wed Jun 11 2014 Remi Collet <remi@fedoraproject.org> - 4.0.5-1
- Update to 4.0.5 (beta)
- open https://github.com/krakjoe/apcu/pull/74 (PHP 5.4)

* Sun Jun  8 2014 Remi Collet <remi@fedoraproject.org> - 4.0.4-3
- add build patch for php 5.6.0beta4

* Wed Apr  9 2014 Remi Collet <remi@fedoraproject.org> - 4.0.4-2
- add numerical prefix to extension configuration file

* Sat Mar 01 2014 Remi Collet <remi@fedoraproject.org> - 4.0.4-1
- Update to 4.0.4 (beta)

* Mon Jan 27 2014 Remi Collet <remi@fedoraproject.org> - 4.0.3-1
- Update to 4.0.3 (beta)
- install doc in pecl doc_dir
- install tests in pecl test_dir (in devel)
- drop panel sub-package in SCL
- add SCL stuff

* Mon Sep 16 2013 Remi Collet <rcollet@redhat.com> - 4.0.2-2
- fix perm on config dir
- always provides php-pecl-apc-devel and apc-panel

* Mon Sep 16 2013 Remi Collet <remi@fedoraproject.org> - 4.0.2-1
- Update to 4.0.2

* Fri Aug 30 2013 Remi Collet <remi@fedoraproject.org> - 4.0.1-3
- rebuild to have NEVR > EPEL (or Fedora)

* Thu Jul  4 2013 Remi Collet <remi@fedoraproject.org> - 4.0.1-2
- obsoletes APC with php 5.5
- restore APC serializers ABI (patch merged upstream)

* Tue Apr 30 2013 Remi Collet <remi@fedoraproject.org> - 4.0.1-1
- Update to 4.0.1
- add missing scriptlet
- fix Conflicts

* Thu Apr 25 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-2
- fix segfault when used from command line

* Wed Mar 27 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-1
- first pecl release
- rename from php-apcu to php-pecl-apcu

* Tue Mar 26 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.4.git4322fad
- new snapshot (test before release)

* Mon Mar 25 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.3.git647cb2b
- new snapshot with our pull request
- allow to run test suite simultaneously on 32/64 arch
- build warning free

* Mon Mar 25 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.2.git6d20302
- new snapshot with full APC compatibility

* Sat Mar 23 2013 Remi Collet <remi@fedoraproject.org> - 4.0.0-0.1.git44e8dd4
- initial package, version 4.0.0