Name:		XRT
Summary:	Xilinx Runtime for AIE and FPGA based platforms 
URL:		https://github.com/Xilinx/XRT
Version:	202420.2.18.179
Release:	1%{?dist}
License:	TODO

%define aiebu_url https://github.com/Xilinx/aiebu
%define aiebu_rev 89f332a2d7f33c08a471fe560d87859edd7e4576
%define aiert_url https://github.com/Xilinx/aie-rt
%define aiert_rev 3640b761ded1619ac06478a0985bb4a2fb2b3e26
Source:		%{url}/archive/refs/tags/%{version}.tar.gz
Source:		%{aiebu_url}/archive/%{aiebu_rev}.tar.gz
Source:		%{aiert_url}/archive/%{aiert_rev}.tar.gz
Patch:		0001-Patch-in-Fedora-HIP-system-paths.patch

ExclusiveArch:	x86_64 aarch64 ppc64le

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
%autosetup -p1
%setup -D -T -a 1
rmdir src/runtime_src/core/common/aiebu/
mv aiebu-%{aiebu_rev}/ src/runtime_src/core/common/aiebu/
%setup -D -T -a 2
rmdir src/runtime_src/core/common/aiebu/lib/aie-rt/
mv aie-rt-%{aiert_rev}/ src/runtime_src/core/common/aiebu/lib/aie-rt/

%build
# Note that we build our options to cmake by *manually* looking at the build.sh script
# It's not quite the same, but we are looking to do something like
# ./build.sh -hip -noalveo -disable-werror -noert
%if %{with rocm}
%define enable_hip ON
%else
%define enable_hip OFF
%endif
%cmake \
	-DCMAKE_EXPORT_COMPILE_COMMANDS=ON \
	-DXRT_ENABLE_HIP=%{enable_hip} \
	-DXRT_ENABLE_WERROR=0 \
	-DXRT_INSTALL_PREFIX=%{_prefix}
%cmake_build

%install
%cmake_install

%check
# TODO: get ctest working

%files
#TODO: figure out how to get files in reasonable locations
#TODO: split package into subpackages like upstream does
# OpenCL ICD file goes in the right place
/etc/OpenCL/vendors/xilinx.icd
# xaiengine.h seems to go to the right places
%{_includedir}/xaiengine.h
%{_includedir}/xaiengine
# PackageConfig file goes in the right place
%{_libdir}/pkgconfig/xrt.pc
# TODO: and basically everything else is in the wrong place...

%changelog
%autochangelog
