Name:           see
Version:        0.1.0
Release:        1%{?dist}
Summary:        CLI Command Helper

License:        MIT
URL:            https://github.com/example/see-helper
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
Requires:       python3
Requires:       xclip
# Recommends:     wl-copy

%description
A simple, powerful tool to save, search, and manage your frequently used CLI commands.
Features include tag-based organization, shell integration, and usage statistics.

%prep
%setup -q

%build
# Nothing to build for pure Python script, handled in install

%install
# 1. Install the main script and source code to /usr/share/see
mkdir -p %{buildroot}/%{_datadir}/%{name}
cp -r src %{buildroot}/%{_datadir}/%{name}/
install -m 755 see %{buildroot}/%{_datadir}/%{name}/

# 2. Install Shell Integration
# Install global shell scripts to /etc/profile.d/
mkdir -p %{buildroot}/%{_sysconfdir}/profile.d
install -m 644 etc/see.sh %{buildroot}/%{_sysconfdir}/profile.d/see.sh
install -m 644 etc/see.fish %{buildroot}/%{_sysconfdir}/profile.d/see.fish

# 3. Create a wrapper script/symlink in /usr/bin/
# We don't use a symlink because we want to ensure it runs with the right python context if needed,
# but a direct symlink is usually fine.
mkdir -p %{buildroot}/%{_bindir}
ln -s %{_datadir}/%{name}/see %{buildroot}/%{_bindir}/see

%files
%{_bindir}/see
%{_datadir}/%{name}
%{_sysconfdir}/profile.d/see.sh
%{_sysconfdir}/profile.d/see.fish
%license LICENSE
%doc README.md

%changelog
* Sat Jan 31 2026 Nishant Mohan <nishant040305@gmail.com> - 0.1.0-1
- Initial package with global shell integration
