%define _disable_lto 1

Summary:	Graphical tools for certain user account management tasks
Name:		usermode
Version:	1.114
Release:	3
Epoch:		1
License:	GPLv2+
Group:		System/Configuration/Other
Url:		https://pagure.io/usermode
Source0:	https://releases.pagure.org/usermode/usermode-%{version}.tar.xz
# being the console owner is enough
Source1:	distro-console-auth
# besides being the console owner, needs to authenticate as well
Source2:	distro-simple-auth
Source3:	config-util
Source4:	config-util-user
Source5:	https://github.com/OpenMandrivaSoftware/consolehelper/archive/consolehelper-master.tar.gz
Source10:	simple_root_authen
Source11:	simple_root_authen.apps
# allow more environment variables to be set in root environment
# bad patch, produce a segfault
# need to rewrite it and fix all copy-paste
Patch1:		usermode-1.114-environment.patch
# http://qa.mandriva.com/show_bug.cgi?id=32459
Patch3:		usermode-1.99-uz-po.patch
# (fc) 1.85-1mdk set password dialog to stick on all workspace
Patch7:		usermode-1.101-stick.patch
# (tpg) pam-panel-icon should check whether it is started from autostart or saved session
# without this we have more instances of pam-panel-icon running
# https://qa.mandriva.com/show_bug.cgi?id=44632
Patch10:	usermode-1.99-disable-session-restart.patch

BuildRequires:	autoconf
BuildRequires:	gettext-devel
BuildRequires:	intltool
BuildRequires:	pkgconfig(libglade-2.0)
BuildRequires:	pkgconfig(libuser)
BuildRequires:	pam-devel
BuildRequires:	desktop-file-utils
BuildRequires:	pkgconfig(ice)
BuildRequires:	pkgconfig(sm)
BuildRequires:	pkgconfig(libstartup-notification-1.0)
BuildRequires:	pkgconfig(blkid)
BuildRequires:	pkgconfig(Qt5Core)
BuildRequires:	pkgconfig(Qt5Gui)
BuildRequires:	pkgconfig(Qt5Widgets)
# For libsupc++
BuildRequires:	stdc++-static-devel
Requires:	passwd
Requires:	util-linux
Requires:	pam
Requires:	%{name}-consoleonly >= %{EVRD}

%description
The usermode package contains several graphical tools for users:
userinfo, usermount and userpasswd. Userinfo allows users to change
their finger information. Usermount lets users mount, unmount, and
format filesystems. Userpasswd allows users to change their passwords.

Install the usermode package if you would like to provide users with
graphical tools for certain account management tasks.

%package -n %{name}-consoleonly
Summary:	Non graphical part of usermode
Group:		System/Libraries

%description -n %{name}-consoleonly
This package contains only the usermode stuff which doesn't require
XFree or GTK to run.

%package gtk
Summary:	Gtk dialogs for usermode
Group:		System/Libraries

%description gtk
Gtk dialogs for usermode.

%prep
%autosetup -p1 -a 5

%build
%configure \
	--without-selinux

%make_build LIBS="-lm"

# Replace some insane g_junk...
cd consolehelper-master
export PATH=%{_libdir}/qt5/bin:$PATH
%make_build

%install
%make_install VENDOR="%(echo %{vendor} | tr A-Z a-z |sed -e 's#[ /()!?]#_#g')"

# Replace some insane g_junk...
cd consolehelper-master
%make_install
cd ..

mkdir -p %{buildroot}%{_mandir}/{man1,man8}
mkdir -p %{buildroot}%{_sysconfdir}/pam.d %{buildroot}%{_sysconfdir}/security/console.apps

install -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/pam.d/simple_root_authen
install -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/security/console.apps/simple_root_authen
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/distro-console-auth
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/pam.d/distro-simple-auth
install -p -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/security/console.apps/config-util
install -p -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/pam.d/config-util-user

# (tpg) https://issues.openmandriva.org/show_bug.cgi?id=61
# real workaround is to fix drakx and other to use common names
ln -sf %{_sysconfdir}/pam.d/distro-console-auth %{buildroot}%{_sysconfdir}/pam.d/mandriva-console-auth
ln -sf %{_sysconfdir}/pam.d/distro-simple-auth %{buildroot}%{_sysconfdir}/pam.d/mandriva-simple-auth

mkdir -p %{buildroot}%{_sysconfdir}/xdg/autostart
cat << EOF > %{buildroot}%{_sysconfdir}/xdg/autostart/pam-panel-icon.desktop
[Desktop Entry]
Name=Authentication applet
Comment=Allow to forget authenticated login
Exec=pam-panel-icon
Icon=dialog-password
Terminal=false
StartupNotify=false
Type=Application
Categories=GNOME;GTK;System;Utility;Core;
OnlyShowIn=GNOME;KDE;XFCE;
EOF

%find_lang %{name}

# remove unpackaged files
rm -f %{buildroot}%{_datadir}/locale/*/LC_MESSAGES/@GETTEXT_PACKAGE@.mo \
 %{buildroot}%{_datadir}/applications/*.desktop

%files
%{_sysconfdir}/pam.d/config-util-user
%{_bindir}/consolehelper-qt

%files gtk
%doc %{_mandir}/man8/consolehelper-gtk.8*
%{_bindir}/consolehelper-gtk
%{_bindir}/usermount
%{_bindir}/userinfo
%{_bindir}/userpasswd
%doc %{_mandir}/man1/usermount.1*
%doc %{_mandir}/man1/userinfo.1*
%doc %{_mandir}/man1/userpasswd.1*
%doc %{_mandir}/man1/pam-panel-icon.1*
%{_bindir}/pam-panel-icon
%{_datadir}/usermode
%{_datadir}/pixmaps/*
%{_sysconfdir}/xdg/autostart/pam-panel-icon.desktop

%files -n %{name}-consoleonly -f %{name}.lang
%attr(4755,root,root) %{_sbindir}/userhelper
%{_bindir}/consolehelper
%doc %{_mandir}/man8/userhelper.8*
%doc %{_mandir}/man8/consolehelper.8*
%config(noreplace) %{_sysconfdir}/pam.d/simple_root_authen
%config(noreplace) %{_sysconfdir}/pam.d/distro-simple-auth
%config(noreplace) %{_sysconfdir}/pam.d/distro-console-auth
%config(noreplace) %{_sysconfdir}/security/console.apps/simple_root_authen
%config(noreplace) %{_sysconfdir}/security/console.apps/config-util
%{_sysconfdir}/pam.d/mandriva-simple-auth
%{_sysconfdir}/pam.d/mandriva-console-auth
