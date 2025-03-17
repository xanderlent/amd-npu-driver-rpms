Name:		xdna-driver
Summary:	AMD XDNA Driver for Linux
URL:		https://github.com/amd/xdna-driver
%define xdna_version 2.19.0~20250314gitedbd030
%define xdna_rev edbd0308e677344ec0151ea3a72942487e587914
Version:	%{xdna_version}
Release:	1%{?dist}
License:	TODO

%define XRT_url https://github.com/Xilinx/XRT
%define XRT_rev 79f5f5adad712270371bbb5c6eee78473cba038e
%define XRT_version 202510.2.19.0~20250227git79f5f5a
%define XRT_aiebu_url https://github.com/Xilinx/aiebu
%define XRT_aiebu_rev 89f332a2d7f33c08a471fe560d87859edd7e4576
%define XRT_aiert_url https://github.com/Xilinx/aie-rt
%define XRT_aiert_rev 3640b761ded1619ac06478a0985bb4a2fb2b3e26
Source:		%{url}/archive/%{xdna_rev}.tar.gz
Source:		%{XRT_url}/archive/%{XRT_rev}.tar.gz
Source:		%{XRT_aiebu_url}/archive/%{XRT_aiebu_rev}.tar.gz
Source:		%{XRT_aiert_url}/archive/%{XRT_aiert_rev}.tar.gz
Patch:		0001-HACK-Disable-debug-messages-unconditionally.patch
# TODO: Patch out the build of the .ko and dkms bits to reduce dependencies

# TODO: XRT can also handle aarch64 and ppc64le, can XDNA do too?
ExclusiveArch:	x86_64

# These BRs are the same as XRT, since we build this module using that sources
BuildRequires:	cmake
BuildRequires:	g++
BuildRequires:	pkgconfig(libdrm)
# TODO: pkgconfig(OpenCL) brings in OpenCL-ICD-Loader-devel
# but that would conflict with ROCm's ocl-icd-devel
#BuildRequires:	pkgconfig(OpenCL)
BuildRequires:	ocl-icd-devel
BuildRequires:	boost-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(RapidJSON)
BuildRequires:	pkgconfig(protobuf)
BuildRequires:	pkgconfig(uuid)
BuildRequires:	systemtap-sdt-devel
BuildRequires:	elfio-devel
# This BR is for the kernel driver
BuildRequires:	kernel-devel-matched
# TODO: The upstream code makes a package that depends on XRT-npu, maybe do that?
# The build process bundles XRT at a specific version
Provides:	bundled(XRT) = %{XRT_version}
# Neither of XRT's bundled dependencies have upstream releases
Provides:	bundled(aiebu)
Provides:	bundled(aie-rt)

%description
This package contains the userspace driver components for the AMD XDNA family
of NPU devices. (Ocasionally called the AMD IPU.)

%prep
%autosetup -p1 -n xdna-driver-%{xdna_rev}
%setup -D -T -a 1 -q -n xdna-driver-%{xdna_rev}
rmdir xrt/
mv XRT-%{XRT_rev}/ xrt/
%setup -D -T -a 2 -q -n xdna-driver-%{xdna_rev}
rmdir xrt/src/runtime_src/core/common/aiebu/
mv aiebu-%{XRT_aiebu_rev}/ xrt/src/runtime_src/core/common/aiebu/
%setup -D -T -a 3 -q -n xdna-driver-%{xdna_rev}
rmdir xrt/src/runtime_src/core/common/aiebu/lib/aie-rt/
mv aie-rt-%{XRT_aiert_rev}/ xrt/src/runtime_src/core/common/aiebu/lib/aie-rt/

%build
# Note that we build our options to cmake by *manually* looking at the build.sh script
# It's not quite the same, but we are looking to do something like
# ./build.sh -release -install_prefix /usr
# Note that the packaging step (including downloading some binaries) and the example builds happen separately from the above
%cmake \
	-DXRT_INSTALL_PREFIX=%{_prefix} \
	-DUMQ_HELLO_TEST=0 \
%cmake_build

%install
# Yes, the upstream package does not use cmake install
# It instead runs the Makefile inside the build directory
pushd %_vpath_builddir
make VERBOSE=1 DESTDIR=%{buildroot} install
popd
pushd %{buildroot}
# delete the libraries built from xrt sources
rm -r bins
# delete the kernel module bits
rm usr/xrt/amdxdna/amdxdna.tar.gz
rm usr/xrt/amdxdna/dkms.conf
rm usr/xrt/amdxdna/dkms_driver.sh
rm usr/xrt/amdxdna/version.json
popd
# TODO: Packages generated by upstream have the latest firmware included
# as well as validation and other binaries...
# Do we even need the newer firmware or can we use the older ones packaged in Fedora?

%check
# TODO: Official test is build and run the example program?

%files
#TODO: figure out how to get files in reasonable locations -> /usr/lib64 instead of /usr/xrt
#TODO: upstream uses a single package, we can split further if needed
%{_prefix}/xrt/amdxdna/io_page_fault_flags
%{_prefix}/xrt/amdxdna/npu_perf_analyze.sh
%{_prefix}/xrt/amdxdna/npu_perf_trace.sh
%{_prefix}/xrt/lib/libxrt_driver_xdna.so
%{_prefix}/xrt/lib/libxrt_driver_xdna.so.2
%{_prefix}/xrt/lib/libxrt_driver_xdna.so.2.19.0

%changelog
%autochangelog
