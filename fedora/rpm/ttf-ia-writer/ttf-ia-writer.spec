# Mirrors omacom/omarchy-pkgs pkgbuilds/ttf-ia-writer: the static Mono, Duo and
# Quattro faces at one commit, plus the legacy Duospace family upstream keeps
# at its last pin. Based on kamm3r/omadora-pkg (MIT).

%global commit c6588670c71e9ac628acc27b72cde4bf12726b7f
%global legacy_commit b337fe1a4c93026268f70e4b2678371f3e89e2ce

Name:           ttf-ia-writer
Version:        20261002.r63
Release:        2%{?dist}
Summary:        Subset of the fonts provided by iA Writer
License:        OFL-1.1
URL:            https://github.com/iaolo/iA-Fonts
Source0:        %{url}/archive/%{commit}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{url}/archive/%{legacy_commit}.tar.gz#/%{name}-legacy-%{version}.tar.gz
BuildArch:      noarch
Requires:       fontconfig
Provides:       ttf-ia-writer-duospace = %{version}-%{release}

%description
Static iA Writer Mono, Duo and Quattro fonts, plus the legacy Duospace family.

%prep
%setup -q -n iA-Fonts-%{commit} -a 1
cp -a iA-Fonts-%{legacy_commit}/'iA Writer Duospace' .

%build

%install
install -d %{buildroot}%{_datadir}/fonts/%{name}
for family in Mono Duo Quattro; do
  install -m 0644 "iA Writer $family"/Static/iAWriter${family}S-*.ttf %{buildroot}%{_datadir}/fonts/%{name}/
done
install -m 0644 'iA Writer Duospace'/'TTF (PC)'/iAWriterDuospace-*.ttf %{buildroot}%{_datadir}/fonts/%{name}/

%files
%license iA\ Writer\ Mono/LICENSE.md
%{_datadir}/fonts/%{name}

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 20261002.r63-2
- Package for Omadora, based on kamm3r/omadora-pkg.
