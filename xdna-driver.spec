Name:		xdna-driver
Summary:	AMD XDNA Driver for Linux
URL:		https://github.com/amd/xdna-driver
%define xdna_version 2.19.0~20250423git75bc2dc
%define xdna_rev 75bc2dc16dc9725d13eee68a7f410865c28ebc9b
Version:	%{xdna_version}
Release:	2%{?dist}
License:	TODO

%define XRT_url https://github.com/Xilinx/XRT
%define XRT_rev d5835aaa7fcdbcb749f4d837d9a0a605c1a4d312
%define XRT_version 202510.2.19.0~20250415gitd5835aa
%define XRT_aiert_url https://github.com/Xilinx/aie-rt
%define XRT_aiert_rev 9f57b82c41c92effae468912c45ced031f56b54a
%define XRT_aiebu_url https://github.com/Xilinx/aiebu
%define XRT_aiebu_rev 89c754fe41edb615abbb3072eca42ca14c7f4e5f
Source:		%{url}/archive/%{xdna_rev}.tar.gz
Source:		%{XRT_url}/archive/%{XRT_rev}.tar.gz
Source:		%{XRT_aiebu_url}/archive/%{XRT_aiebu_rev}.tar.gz
Source:		%{XRT_aiert_url}/archive/%{XRT_aiert_rev}.tar.gz
Patch:		0001-HACK-Disable-debug-messages-unconditionally.patch

# TODO: XRT can also handle aarch64 and ppc64le, can XDNA do too?
ExclusiveArch:	x86_64

# These BRs are the same as XRT, since we build this module using that sources
BuildRequires:	cmake
BuildRequires:	g++
BuildRequires:	pkgconfig(libdrm)
# TODO: pkgconfig(OpenCL) brings in OpenCL-ICD-Loader-devel
# but that would conflict with ROCm's ocl-icd-devel
#BuildRequires:	pkgconfig(OpenCL)
#BuildRequires:	OpenCL-ICD-Loader-devel
BuildRequires:	ocl-icd-devel
BuildRequires:	boost-devel
BuildRequires:	pkgconfig(ncurses)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(RapidJSON)
BuildRequires:	pkgconfig(protobuf)
BuildRequires:	pkgconfig(uuid)
BuildRequires:	systemtap-sdt-devel
BuildRequires:	elfio-devel
BuildRequires:	guidelines-support-library-devel
BuildRequires:	pkgconfig(libelf)
BuildRequires:	git-core
# TODO: The upstream code makes a package that depends on XRT-npu, maybe do that?
# We lack these requirements so far
#   - nothing provides xrt-base >= 2.19 needed by xrt_plugin-amdxdna-2.19.0-1.x86_64 from @commandline
#  - nothing provides xrt-base < 2.20 needed by xrt_plugin-amdxdna-2.19.0-1.x86_64 from @commandline
# We already have these because the RPM process is smart about dynmaic libraries
#  - nothing provides libxrt_core.so.2()(64bit) needed by xrt_plugin-amdxdna-2.19.0-1.x86_64 from @commandline
#  - nothing provides libxrt_coreutil.so.2()(64bit) needed by xrt_plugin-amdxdna-2.19.0-1.x86_64 from @commandline
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
	-DSKIP_KMOD=ON
%cmake_build


%install
# The ./build.sh -package step downloads devel firmware, copies over the validation bins,
# and then invokes the packaging/install step.
# Yes, the upstream package does not use cmake install.
# It instead runs the CMake-generate Makefile inside the build directory.
pushd %_vpath_builddir
make VERBOSE=1 DESTDIR=%{buildroot} install
popd
pushd %{buildroot}
# delete various misc bits that shouldn't be packaged
rm -r bins
# delete the extraneous version.json file
rm usr/xrt/amdxdna/version.json
popd
# Handle copying the validation binaries to the right place
cp -ar tools/bins %{buildroot}/usr/xrt/amdxdna/bins
# Still TODO: Also install devel firmware.

%check
# TODO: Official test is build and run the example program?

%files
#TODO: figure out how to get files in reasonable locations -> /usr/lib64 instead of /usr/xrt
#TODO: upstream uses a single package, we can split further if needed
%{_prefix}/xrt/amdxdna/bins
%{_prefix}/xrt/amdxdna/io_page_fault_flags
%{_prefix}/xrt/amdxdna/npu_perf_analyze.sh
%{_prefix}/xrt/amdxdna/npu_perf_trace.sh
%{_prefix}/xrt/lib/libxrt_driver_xdna.so
%{_prefix}/xrt/lib/libxrt_driver_xdna.so.2
%{_prefix}/xrt/lib/libxrt_driver_xdna.so.2.19.0

%changelog
%autochangelog
