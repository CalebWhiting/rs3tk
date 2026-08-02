%define appname rs3tk-electron

Name:           %{appname}
Version:        1.0.1
Release:        1%{?dist}
Summary:        RS3TK - RuneScape 3 Toolkit (Electron GUI)
License:        MIT
URL:            https://github.com/CalebWhiting/rs3tk
Source0:        %{url}/releases/download/v%{version}/RS3TK-%{version}.AppImage

BuildArch:      x86_64
BuildRequires:  desktop-file-utils
Requires:       gtk3 nss at-spi2-atk cups-libs libdrm mesa-libgbm alsa-lib
Recommends:     libappindicator-gtk3

%description
RS3TK is an open-source implementation of the Jagex Launcher.
It authenticates via OAuth2, manages game sessions, and launches
RS3/OSRS clients (Official, RuneLite, HDOS).

This package provides the Electron-based GUI.

%prep
chmod +x %{_sourcedir}/RS3TK-%{version}.AppImage
%{_sourcedir}/RS3TK-%{version}.AppImage --appimage-extract

%build
# No build needed - pre-built AppImage

%install
mkdir -p %{buildroot}/opt/rs3tk
cp -r squashfs-root/* %{buildroot}/opt/rs3tk/

# Fix the binary and create wrapper
if [ -f %{buildroot}/opt/rs3tk/rs3tk-electron ]; then
    mv %{buildroot}/opt/rs3tk/rs3tk-electron %{buildroot}/opt/rs3tk/rs3tk-electron-bin
fi

mkdir -p %{buildroot}/usr/bin
cat > %{buildroot}/usr/bin/rs3tk-electron << 'WRAPPER'
#!/bin/sh
APPDIR="/opt/rs3tk"
export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
export XDG_DATA_DIRS="${APPDIR}/usr/share:${XDG_DATA_DIRS}:/usr/share/gnome:/usr/local/share:/usr/share"
export GSETTINGS_SCHEMA_DIR="${APPDIR}/usr/share/glib-2.0/schemas:${GSETTINGS_SCHEMA_DIR}"
exec "${APPDIR}/rs3tk-electron-bin" --no-sandbox "$@"
WRAPPER
chmod 755 %{buildroot}/usr/bin/rs3tk-electron

# Desktop file
mkdir -p %{buildroot}/usr/share/applications
cat > %{buildroot}/usr/share/applications/rs3tk-electron.desktop << 'DESKTOP'
[Desktop Entry]
Name=RS3TK
Comment=Open-source Jagex Launcher replacement
Exec=rs3tk-electron %U
Icon=rs3tk
Type=Application
Categories=Game;
Terminal=false
StartupNotify=true
DESKTOP

# Icon
mkdir -p %{buildroot}/usr/share/icons/hicolor/256x256/apps
if [ -f %{buildroot}/opt/rs3tk/rs3tk-electron.png ]; then
    cp %{buildroot}/opt/rs3tk/rs3tk-electron.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/rs3tk.png
elif [ -f %{buildroot}/opt/rs3tk/usr/share/icons/hicolor/256x256/apps/rs3tk-electron.png ]; then
    cp %{buildroot}/opt/rs3tk/usr/share/icons/hicolor/256x256/apps/rs3tk-electron.png %{buildroot}/usr/share/icons/hicolor/256x256/apps/rs3tk.png
fi

%files
/opt/rs3tk/
/usr/bin/rs3tk-electron
/usr/share/applications/rs3tk-electron.desktop
/usr/share/icons/hicolor/256x256/apps/rs3tk.png

%changelog
* Sat Aug 01 2026 Caleb <caleb.andrew.whiting@gmail.com> - 1.0.1-1
- Initial RPM package