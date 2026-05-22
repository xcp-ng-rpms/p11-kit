%global package_speccommit 216d3fad39b70c3121a56d18a284d756f236aad4
%global usver 0.24.1
%global xsver 4
%global xsrel %{xsver}%{?xscount}%{?xshash}

%if 0%{?xenserver} < 9
# need to set explicitly for xs8 for parallel build
%global _smp_build_ncpus %(nproc)
%endif

%bcond_with doc

# This spec file has been automatically updated
Version:        0.24.1
Release: %{?xsrel}~XCPNG2698.8%{?dist}
Name:           p11-kit
Summary:        Library for loading and sharing PKCS#11 modules

%bcond_with bash_completion

License:        BSD
URL:            http://p11-glue.freedesktop.org/p11-kit.html
Source0: p11-kit-0.24.1.tar.xz
Source3: trust-extract-compat
Source4: p11-kit-client.service

BuildRequires:  gcc
BuildRequires:  libtasn1-devel >= 2.3
BuildRequires:  libffi-devel
BuildRequires:  gettext
%if %{with doc}
BuildRequires:  gtk-doc
%endif
BuildRequires:  meson
BuildRequires:  systemd-devel
BuildRequires:  bash-completion
BuildRequires:  libtasn1-tools
BuildRequires:  cmake
# Work around for https://bugzilla.redhat.com/show_bug.cgi?id=1497147
# Remove this once it is fixed
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  gnupg2
BuildRequires:  /usr/bin/xsltproc

%description
p11-kit provides a way to load and enumerate PKCS#11 modules, as well
as a standard configuration setup for installing PKCS#11 modules in
such a way that they're discoverable.


%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package trust
Summary:            System trust module from %{name}
Requires:           %{name}%{?_isa} = %{version}-%{release}
Conflicts:          nss < 3.14.3-9

%description trust
The %{name}-trust package contains a system trust PKCS#11 module which
contains certificate anchors and black lists.


%package server
Summary:        Server and client commands for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description server
The %{name}-server package contains command line tools that enable to
export PKCS#11 modules through a Unix domain socket.  Note that this
feature is still experimental.


%prep

%autosetup -p1

%build
# These paths are the source paths that  come from the plan here:
# https://fedoraproject.org/wiki/Features/SharedSystemCertificates:SubTasks
%if %{with bash_completion}
%define bashopt -Dbash_completion=enabled
%else
%define bashopt -Dbash_completion=disabled
%endif

%if %{with doc}
%meson -Dgtk_doc=true -Dman=true -Dtrust_paths=%{_sysconfdir}/pki/ca-trust/source:%{_datadir}/pki/ca-trust-source %{bashopt}
%else
%meson -Dgtk_doc=false -Dman=false -Dtrust_paths=%{_sysconfdir}/pki/ca-trust/source:%{_datadir}/pki/ca-trust-source %{bashopt}
%endif
%meson_build

%install
%meson_install
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pkcs11/modules
install -p -m 755 %{SOURCE3} $RPM_BUILD_ROOT%{_libexecdir}/p11-kit/

# Install the example conf with %%doc instead
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}
mv $RPM_BUILD_ROOT%{_sysconfdir}/pkcs11/pkcs11.conf.example $RPM_BUILD_ROOT%{_docdir}/%{name}/pkcs11.conf.example
mkdir -p $RPM_BUILD_ROOT%{_userunitdir}
install -p -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_userunitdir}
%find_lang %{name}

ln -s pkcs11/p11-kit-trust.so $RPM_BUILD_ROOT%{_libdir}/libnssckbi.so

%check
%meson_test

%files -f %{name}.lang
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc AUTHORS NEWS README
%{_docdir}/%{name}/pkcs11.conf.example
%dir %{_sysconfdir}/pkcs11
%dir %{_sysconfdir}/pkcs11/modules
%dir %{_datadir}/p11-kit
%dir %{_datadir}/p11-kit/modules
%dir %{_libexecdir}/p11-kit
%{_bindir}/p11-kit
%{_libdir}/libp11-kit.so.*
%{_libdir}/p11-kit-proxy.so
%{_libexecdir}/p11-kit/p11-kit-remote
%if %{with doc}
%{_mandir}/man1/trust.1.gz
%{_mandir}/man8/p11-kit.8.gz
%{_mandir}/man5/pkcs11.conf.5.gz
%endif
%if %{with bash_completion}
%{_datadir}/bash-completion/completions/p11-kit
%endif

%files devel
%{_includedir}/p11-kit-1/
%{_libdir}/libp11-kit.so
%{_libdir}/pkgconfig/p11-kit-1.pc
%if %{with doc}
%doc %{_datadir}/gtk-doc/
%endif

%files trust
%{_bindir}/trust
%dir %{_libdir}/pkcs11
%{_libdir}/libnssckbi.so
%{_libdir}/pkcs11/p11-kit-trust.so
%{_datadir}/p11-kit/modules/p11-kit-trust.module
%{_libexecdir}/p11-kit/trust-extract-compat
%if %{with bash_completion}
%{_datadir}/bash-completion/completions/trust
%endif

%files server
%{_libdir}/pkcs11/p11-kit-client.so
%{_userunitdir}/p11-kit-client.service
%{_libexecdir}/p11-kit/p11-kit-server
%{_userunitdir}/p11-kit-server.service
%{_userunitdir}/p11-kit-server.socket


%changelog
* Tue Nov 11 2025 Lin Liu <lin.liu01@citrix.com> - 0.24.1-4
- CP-310102: Rebuild to support building gnutls

* Tue Jan 14 2025 Alex Brett <alex.brett@cloud.com> - 0.24.1-3
- CP-53127: Remove dependency on alternatives

* Mon May 13 2024 Lin Liu <lin.liu@citrix.com> - 0.24.1-2
- Rebuild with libffi-3.4.4

* Thu Jun 29 2023 Lin Liu <lin.liu@citrix.com> - 0.24.1-1
- First imported release

