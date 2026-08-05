%global pypi_name rs3tk
%global core_name rs3tk_core

Name:           python3-%{pypi_name}
Version:        1.0.3
Release:        1%{?dist}
Summary:        Open-source Jagex Launcher replacement for Linux

License:        MIT
URL:            https://github.com/CalebWhiting/rs3tk
Source0:        %{pypi_name}-%{version}-py3-none-any.whl
Source1:        %{core_name}-%{version}-py3-none-any.whl

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools >= 68.0
BuildRequires:  python3-pip
BuildRequires:  python3-wheel
Requires:       python3-httpx >= 0.27
Requires:       python3-pydantic >= 2.0
Requires:       python3-keyring >= 25.0
Requires:       python3-click >= 8.1
Requires:       python3-rich >= 13.0

%global _description %{expand:
rs3tk is an open-source implementation of the Jagex Launcher.
It authenticates via OAuth2, manages game sessions, and launches
RS3/OSRS clients (Official, RuneLite, HDOS).}

%description %_description

%prep
# No prep needed for wheel-based package

%build
# No build needed for wheel-based package

%install
mkdir -p %{buildroot}%{python3_sitelib}
pip3 install --no-deps --root=%{buildroot} %{_sourcedir}/*.whl

%files
%license LICENSE
%doc README.md
%{python3_sitelib}/%{core_name}/
%{python3_sitelib}/%{pypi_name}_cli/
%{python3_sitelib}/%{pypi_name}-%{version}.dist-info/
%{python3_sitelib}/%{core_name}-%{version}.dist-info/
%{_bindir}/%{pypi_name}

%changelog
* Wed Aug 05 2026 Caleb <caleb.andrew.whiting@gmail.com> - 1.0.3-1
- Bump to 1.0.3

* Sat Aug 02 2026 Caleb <caleb.andrew.whiting@gmail.com> - 1.0.2-1
- Bump to 1.0.2

* Sat Aug 01 2026 Caleb <caleb.andrew.whiting@gmail.com> - 1.0.1-1
- Initial package