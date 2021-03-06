%bcond_with prepare_fastbuild
%bcond_with fastbuild
%bcond_with build_common_package

%define VERSION 4.10
%define RELEASE 1

%define _arc  %(getconf LONG_BIT)
%define _is64 %(if [ `getconf LONG_BIT` = "64" ] ; then  printf "64";  fi)

%define _cupsbindir /usr/lib/cups
%define _cupsbindir64 /usr/lib64/cups

%define _prefix	/usr/local
%define _bindir %{_prefix}/bin
%define _libdir /usr/lib%{_is64}
%define _ppddir /usr

%define CNBP_LIBS libcnbpcmcm libcnbpcnclapi libcnbpcnclbjcmd libcnbpcnclui libcnbpess libcnbpo
%define COM_LIBS libcnnet libcnbpcnclapi
%define PRINT_PKG_PROGRAM ppd cnijfilter

%define PKG %{MODEL}series

Summary: IJ Printer Driver Ver.%{VERSION} for Linux
Name: cnijfilter-%{PKG}
Version: %{VERSION}
Release: %{RELEASE}
License: See the LICENSE*.txt file.
Vendor: CANON INC.
Group: Applications/Publishing
Source0: cnijfilter-source-%{version}-%{release}.tar.gz
BuildRoot: %{_tmppath}/%{name}-root
#Requires:  cups popt
Requires: cnijfilter-common >= %{version} cups popt gtk2
#BuildRequires: gtk-devel cups-devel 

%if %{with build_common_package}
%package -n cnijfilter-common
Summary: IJ Printer Driver Ver.%{VERSION} for Linux
License: See the LICENSE*.txt file.
Vendor: CANON INC.
Group: Applications/Publishing
Requires:  cups popt
%endif


%description
IJ Printer Driver for Linux. 
This IJ Printer Driver provides printing functions for Canon Inkjet
printers operating under the CUPS (Common UNIX Printing System) environment.

%if %{with build_common_package}
%description -n cnijfilter-common
IJ Printer Driver for Linux. 
This IJ Printer Driver provides printing functions for Canon Inkjet
printers operating under the CUPS (Common UNIX Printing System) environment.
%endif


%prep
echo $RPM_BUILD_ROOT

%if %{with fastbuild}
%setup -T -D -n  cnijfilter-source-%{version}-%{RELEASE}
%else
%setup -q -n  cnijfilter-source-%{version}-%{RELEASE}
%endif

%if ! %{with prepare_fastbuild}

%if ! %{defined MODEL}
echo "#### Usage : rpmbuild -bb [spec file] --define=\"MODEL ipXXXX\" --define=\"MODEL_NUM YYY\" ####"
exit 1
%endif

%if ! %{defined MODEL_NUM}
echo "#### Usage : rpmbuild -bb [spec file] --define=\"MODEL ipXXXX\" --define=\"MODEL_NUM YYY\" ####"
exit 1
%endif

%endif


%build
%if %{with prepare_fastbuild}

pushd  ppd
    ./autogen.sh --prefix=/usr --program-suffix=CN_IJ_MODEL
popd
pushd cnijfilter
    ./autogen.sh --prefix=%{_prefix} --program-suffix=CN_IJ_MODEL --enable-libpath=%{_libdir}/bjlib --enable-binpath=%{_bindir}
popd

%else

%if %{with fastbuild}
	for prg_name in %{PRINT_PKG_PROGRAM};do
		pushd ${prg_name}
		find . -name Makefile -print > file_lists
		find . -name config.h -print >> file_lists
		for fn in `cat file_lists`; do
			if [ ! -f $fn.org ]; then
				cp $fn $fn.org
			fi
			sed -e s/CN_IJ_MODEL_NUM/%{MODEL_NUM}/g $fn.org | sed -e s/CN_IJ_MODEL/%{MODEL}/ > cn_ij_tmp; mv cn_ij_tmp $fn
		done
		make clean
		make
		popd
	done
%else
pushd  ppd
    ./autogen.sh --prefix=/usr --program-suffix=%{MODEL}
	make clean
	make
popd
pushd cnijfilter
    ./autogen.sh --prefix=%{_prefix} --program-suffix=%{MODEL} --enable-libpath=%{_libdir}/bjlib --enable-binpath=%{_bindir}
	make clean
	make
popd
%endif

%endif


%if %{with build_common_package}
pushd libs
    ./autogen.sh --prefix=%{_prefix} 
popd

pushd bscc2sts
    ./autogen.sh 
popd

pushd cnijnpr
    ./autogen.sh --prefix=%{_prefix} --enable-libpath=%{_libdir}/bjlib
popd

pushd cngpij
    ./autogen.sh --prefix=%{_prefix} --enable-progpath=%{_bindir}
popd

pushd cngpijmnt
    ./autogen.sh --prefix=%{_prefix} --enable-progpath=%{_bindir}
popd

pushd pstocanonij
    ./autogen.sh --prefix=/usr --enable-progpath=%{_bindir} 
popd

pushd backend
    ./autogen.sh --prefix=/usr
popd

pushd backendnet
    ./autogen.sh --prefix=%{_prefix} --enable-libpath=%{_libdir}/bjlib --enable-progpath=%{_bindir} LDFLAGS="-L../../com/libs_bin%{_arc}"
popd

pushd cmdtocanonij
    ./autogen.sh --prefix=/usr --datadir=/usr/local/share
popd

pushd cnijbe
    ./autogen.sh --prefix=/usr --enable-progpath=%{_bindir} 
popd

pushd lgmon2
    ./autogen.sh --prefix=%{_prefix} --enable-libpath=%{_libdir}/bjlib --enable-progpath=%{_bindir}  LDFLAGS="-L../../com/libs_bin%{_arc}"
popd

make
%endif


%install
# make and install files for printer packages
pushd  ppd
	make install DESTDIR=${RPM_BUILD_ROOT}
popd

pushd cnijfilter
    make install DESTDIR=${RPM_BUILD_ROOT}
popd

mkdir -p ${RPM_BUILD_ROOT}%{_libdir}/bjlib
install -c -m 644 %{MODEL_NUM}/database/*  		${RPM_BUILD_ROOT}%{_libdir}/bjlib
install -c -s -m 755 %{MODEL_NUM}/libs_bin%{_arc}/*.so.* 	${RPM_BUILD_ROOT}%{_libdir}


%if %{with build_common_package}
mkdir -p ${RPM_BUILD_ROOT}%{_bindir}
mkdir -p ${RPM_BUILD_ROOT}%{_cupsbindir}/filter
mkdir -p ${RPM_BUILD_ROOT}%{_cupsbindir}/backend
mkdir -p ${RPM_BUILD_ROOT}%{_cupsbindir64}/filter
mkdir -p ${RPM_BUILD_ROOT}%{_cupsbindir64}/backend
mkdir -p ${RPM_BUILD_ROOT}%{_prefix}/share/cups/model
mkdir -p ${RPM_BUILD_ROOT}/etc/udev/rules.d/

install -c -m 644 com/ini/cnnet.ini  		${RPM_BUILD_ROOT}%{_libdir}/bjlib

make install DESTDIR=${RPM_BUILD_ROOT}
install -c -s -m 755 com/libs_bin%{_arc}/*.so.* 	${RPM_BUILD_ROOT}%{_libdir}

install -c -m 755 ${RPM_BUILD_ROOT}%{_cupsbindir}/filter/pstocanonij	${RPM_BUILD_ROOT}%{_cupsbindir64}/filter/pstocanonij
install -c -m 755 ${RPM_BUILD_ROOT}%{_cupsbindir}/backend/cnijusb	${RPM_BUILD_ROOT}%{_cupsbindir64}/backend/cnijusb
install -c -m 755 ${RPM_BUILD_ROOT}%{_cupsbindir}/backend/cnijnet	${RPM_BUILD_ROOT}%{_cupsbindir64}/backend/cnijnet
install -c -m 755 ${RPM_BUILD_ROOT}%{_cupsbindir}/filter/cmdtocanonij	${RPM_BUILD_ROOT}%{_cupsbindir64}/filter/cmdtocanonij
install -c -m 755 ${RPM_BUILD_ROOT}%{_cupsbindir}/backend/cnijbe	${RPM_BUILD_ROOT}%{_cupsbindir64}/backend/cnijbe

install -c -m 644 etc/*.rules ${RPM_BUILD_ROOT}/etc/udev/rules.d/
%endif


%clean
rm -rf $RPM_BUILD_ROOT


%post
if [ -x /sbin/ldconfig ]; then
	/sbin/ldconfig
fi

%postun
# remove cnbp* libs
for LIBS in %{CNBP_LIBS}
do
	if [ -h %{_libdir}/${LIBS}%{MODEL_NUM}.so ]; then
		rm -f %{_libdir}/${LIBS}%{MODEL_NUM}.so
	fi	
done
# remove directory
if [ "$1" = 0 ] ; then
	rmdir -p --ignore-fail-on-non-empty %{_prefix}/share/locale/*/LC_MESSAGES
	rmdir -p --ignore-fail-on-non-empty %{_bindir}
fi
if [ -x /sbin/ldconfig ]; then
	/sbin/ldconfig
fi

%if %{with build_common_package}
%post -n cnijfilter-common
if [ -x /sbin/ldconfig ]; then
	/sbin/ldconfig
fi
if [ -x /sbin/udevadm ]; then
	/sbin/udevadm control --reload-rules 2> /dev/null
	/sbin/udevadm trigger --action=add --subsystem-match=usb 2> /dev/null
fi

%postun -n cnijfilter-common
for LIBS in %{COM_LIBS}
do
	if [ -h %{_libdir}/${LIBS}.so ]; then
		rm -f %{_libdir}/${LIBS}.so
	fi	
done
if [ "$1" = 0 ] ; then
	rmdir -p --ignore-fail-on-non-empty %{_libdir}/bjlib
fi
if [ -x /sbin/ldconfig ]; then
	/sbin/ldconfig
fi
%endif


%files
%defattr(-,root,root)
%{_ppddir}/share/cups/model/canon%{MODEL}.ppd

%{_bindir}/cif%{MODEL}
%{_libdir}/libcnbp*%{MODEL_NUM}.so*
%{_libdir}/bjlib/cif%{MODEL}.conf
%{_libdir}/bjlib/cnb_%{MODEL_NUM}0.tbl
%{_libdir}/bjlib/cnbpname%{MODEL_NUM}.tbl

%doc LICENSE-cnijfilter-%{VERSION}JP.txt
%doc LICENSE-cnijfilter-%{VERSION}EN.txt
%doc LICENSE-cnijfilter-%{VERSION}SC.txt
%doc LICENSE-cnijfilter-%{VERSION}FR.txt

%doc lproptions/lproptions-%{MODEL}-%{VERSION}JP.txt
%doc lproptions/lproptions-%{MODEL}-%{VERSION}EN.txt
%doc lproptions/lproptions-%{MODEL}-%{VERSION}SC.txt
%doc lproptions/lproptions-%{MODEL}-%{VERSION}FR.txt

%if %{with build_common_package}
%files -n cnijfilter-common
%defattr(-,root,root)
%{_cupsbindir}/filter/pstocanonij
%{_cupsbindir}/backend/cnijusb
%{_cupsbindir}/backend/cnijnet
%{_cupsbindir}/backend/cnijbe
%{_cupsbindir}/filter/cmdtocanonij
%{_cupsbindir64}/filter/pstocanonij
%{_cupsbindir64}/backend/cnijusb
%{_cupsbindir64}/backend/cnijnet
%{_cupsbindir64}/backend/cnijbe
%{_cupsbindir64}/filter/cmdtocanonij
%{_bindir}/cnijnpr
%{_bindir}/cngpij
%{_bindir}/cngpijmnt
%{_bindir}/cnijnetprn
%{_bindir}/cnijlgmon2
%{_libdir}/libcnnet.so*
%{_libdir}/libcnbpcnclapicom.so*
%attr(644, lp, lp) %{_libdir}/bjlib/cnnet.ini
%{_prefix}/share/locale/*/LC_MESSAGES/cnijlgmon2.mo
%{_prefix}/share/cnijlgmon2/*
%{_prefix}/share/cmdtocanonij/*


/etc/udev/rules.d/*.rules

%doc LICENSE-cnijfilter-%{VERSION}JP.txt
%doc LICENSE-cnijfilter-%{VERSION}EN.txt
%doc LICENSE-cnijfilter-%{VERSION}SC.txt
%doc LICENSE-cnijfilter-%{VERSION}FR.txt
%endif

%ChangeLog
