# Mirrors omacom/omarchy-pkgs pkgbuilds/ttf-jetbrains-mono-nerd-basic.
# Based on kamm3r/omadora-pkg (MIT).

Name:           ttf-jetbrains-mono-nerd-basic
Version:        3.5.1
Release:        1%{?dist}
Summary:        JetBrains Mono Nerd Font, regular and bold faces with italics
License:        OFL-1.1-no-RFN
URL:            https://github.com/ryanoasis/nerd-fonts
Source0:        %{url}/releases/download/v%{version}/JetBrainsMono.zip#/JetBrainsMono-%{version}.zip
BuildArch:      noarch
BuildRequires:  unzip
Requires:       fontconfig
Provides:       ttf-font-nerd

%description
Regular, Bold, Italic and Bold Italic faces of the JetBrains Mono Nerd Font,
the font Omarchy's bar, prompt and terminal icons are drawn with.

%prep
%setup -q -c -T
unzip -q %{SOURCE0} JetBrainsMonoNerdFont-Regular.ttf JetBrainsMonoNerdFont-Bold.ttf JetBrainsMonoNerdFont-Italic.ttf JetBrainsMonoNerdFont-BoldItalic.ttf OFL.txt

%build

%install
install -d %{buildroot}%{_datadir}/fonts/%{name}
install -m 0644 JetBrainsMonoNerdFont-{Regular,Bold,Italic,BoldItalic}.ttf %{buildroot}%{_datadir}/fonts/%{name}/

%files
%license OFL.txt
%{_datadir}/fonts/%{name}

%changelog
* Mon Oct 12 2026 Dominik Lichnovsky <dlichnovsky1@gmail.com> - 3.5.1-1
- Package for Omadora, based on kamm3r/omadora-pkg.
