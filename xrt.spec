Name:		xrt
# TODO: This is just the NPU bits, really...
Summary:	Xilinx Runtime for AIE and FPGA based platforms 
URL:		https://github.com/Xilinx/XRT
%define xrt_rev d5835aaa7fcdbcb749f4d837d9a0a605c1a4d312
Version:	202510.2.19.0~20250415gitd5835aa
Release:	3%{?dist}
License:	TODO

%define aiebu_url https://github.com/Xilinx/aiebu
%define aiebu_rev 89c754fe41edb615abbb3072eca42ca14c7f4e5f
%define aiert_url https://github.com/Xilinx/aie-rt
%define aiert_rev 9f57b82c41c92effae468912c45ced031f56b54a
Source:		%{url}/archive/%{xrt_rev}.tar.gz
Source:		%{aiebu_url}/archive/%{aiebu_rev}.tar.gz
Source:		%{aiert_url}/archive/%{aiert_rev}.tar.gz
Patch:		0001-Patch-in-Fedora-HIP-system-paths.patch
Patch:		0002-GCC-15-fixup-utils.h-needs-cstdint-header.patch

# TODO: Upstream says only x86_64 aarch64 ppc64le are supported?
#ExclusiveArch:	x86_64 aarch64 ppc64le

%ifarch x86_64
%bcond_without rocm
%else
%bcond_with rocm
%endif

# TODO: move to packageconfig(lib) format?
BuildRequires:	cmake
BuildRequires:	g++
BuildRequires:	libdrm-devel
BuildRequires:	ocl-icd-devel
BuildRequires:	boost-devel
BuildRequires:	ncurses-devel
BuildRequires:	openssl-devel
BuildRequires:	rapidjson-devel
BuildRequires:	protobuf-devel
BuildRequires:	python3-devel
BuildRequires:	pybind11-devel
BuildRequires:	libuuid-devel
BuildRequires:	systemtap-sdt-devel
BuildRequires:	elfio-devel
BuildRequires:	libcurl-devel
BuildRequires:	systemd-devel
BuildRequires:	git-core
BuildRequires:	pkgconfig(libelf)
# aiebu-asm needs static libs
BuildRequires:	glibc-static
BuildRequires:	libstdc++-static
# aiebu needs cxxopts
BuildRequires:	cxxopts-devel
%if %{with rocm}
BuildRequires:	rocm-hip-devel
BuildRequires:	rocm-comgr-devel
BuildRequires:	rocm-runtime-devel
%endif
Requires:	opencl-filesystem
# Neither of the bundled dependencies have upstream releases
Provides:	bundled(aiebu)
Provides:	bundled(aie-rt)

%description
XRT supports both PCIe based accelerator cards and MPSoC based embedded
architecture provides standardized software interface to Xilinx® FPGA. The key
user APIs are defined in xrt.h header file.

%prep
%autosetup -p1 -n XRT-%{xrt_rev}
%setup -D -T -a 1 -n XRT-%{xrt_rev}
rmdir src/runtime_src/core/common/aiebu/
mv aiebu-%{aiebu_rev}/ src/runtime_src/core/common/aiebu/
%setup -D -T -a 2 -n XRT-%{xrt_rev}
rmdir src/runtime_src/core/common/aiebu/lib/aie-rt/
mv aie-rt-%{aiert_rev}/ src/runtime_src/core/common/aiebu/lib/aie-rt/

%build
# Note that we build our options to cmake by *manually* looking at the build.sh script
# It's not quite the same, but we are looking to do something like
# ./build.sh -npu -opt -hip -disable-werror -verbose
%if %{with rocm}
%define enable_hip ON
%else
%define enable_hip OFF
%endif
%cmake \
	-DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
	-DXRT_ENABLE_HIP=%{enable_hip} \
	-DXRT_NPU=1 \
	-DXRT_ENABLE_WERROR=0 \
	-DXRT_INSTALL_PREFIX=%{_prefix}
%cmake_build

%install
# The upstream build.sh uses make VERBOSE=1 DESTDIR=yadayada install
# and then make xrt_docs for docs
#make install
#make xrt_docs
# TODO: This doesn't install the full set of aiebu bits...
%cmake_install

%check
# Tests currently fail at build time. :(
#ctest

%files
%{_prefix}/aiebu
%{_prefix}/xrt
%{_sysconfdir}/OpenCL/vendors/xilinx.icd
%{_libdir}/pkgconfig/xrt.pc

%changelog
%autochangelog
