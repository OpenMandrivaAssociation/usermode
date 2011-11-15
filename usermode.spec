Summary:	Graphical tools for certain user account management tasks
Name:		usermode
Version:	1.108
Release:	%mkrel 1
Epoch:		1
License:	GPLv2+
Group:		System/Configuration/Other
Url:		https://fedorahosted.org/usermode/
Source0:	https://fedorahosted.org/releases/u/s/usermode/%{name}-%{version}.tar.xz
# being the console owner is enough
Source1:	mandriva-console-auth
# besides being the console owner, needs to authenticate as well
Source2:	mandriva-simple-auth
Source10:	simple_root_authen
Source11:	simple_root_authen.apps
# allow more environment variables to be set in root environment
Patch1:		usermode-1.99-environment.patch
# allow simple authentication without config file (used by drakxtools)
Patch2:		usermode-1.108-user_authen.patch
# http://qa.mandriva.com/show_bug.cgi?id=32459
Patch3:		usermode-1.99-uz-po.patch
# (fc) 1.85-1mdk set password dialog to stick on all workspace
Patch7:		usermode-1.101-stick.patch
Patch8:		usermode-1.100-sl-po.patch
Patch9:		usermode-1.106-format_not_a_string_literal_and_no_format_arguments.patch
# (tpg) pam-panel-icon should check whether it is started from autostart or saved session
# without this we have more instances of pam-panel-icon running
# https://qa.mandriva.com/show_bug.cgi?id=44632
Patch10:	usermode-1.99-disable-session-restart.patch
BuildRequires:	autoconf2.5
BuildRequires:	gettext-devel
BuildRequires:	intltool
BuildRequires:	libglade2.0-devel
BuildRequires:	libuser-devel
BuildRequires:	pam-devel
BuildRequires:	desktop-file-utils
BuildRequires:	libice-devel
BuildRequires:	libsm-devel
BuildRequires:	startup-notification-devel
# don't build with startup-notification for now, not fully functionnal
#BuildRequires:  startup-notification-devel
BuildRequires:	libblkid-devel
Requires:	util-linux
Requires:	pam >= 0.75-28mdk
Requires:	%{name}-consoleonly = %{epoch}:%{version}-%{release}
Conflicts:	SysVinit < 2.74-14
Conflicts:	msec < 0.15-17mdk
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

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

%prep
%setup -q

%patch1 -p1 -b .environment
%patch2 -p1 -b .user_authen
%patch3 -p1 -b .uz
%patch7 -p1 -b .stick
#%patch8 -p1 -b .newpo
%patch9 -p1
%patch10 -p1

%build
%configure2_5x \
	--without-selinux
%make

%install
rm -rf %{buildroot}
%makeinstall_std VENDOR=mandriva

mkdir -p %{buildroot}%{_mandir}/{man1,man8}

# Stuff from pam_console, for sysvinit. Here for lack of a better
# place....
mkdir -p %{buildroot}%{_sysconfdir}/pam.d %{buildroot}%{_sysconfdir}/security/console.apps
for wrapapp in halt reboot poweroff ; do
  ln -sf consolehelper %{buildroot}%{_bindir}/$wrapapp
  touch %{buildroot}%{_sysconfdir}/security/console.apps/$wrapapp
  cp shutdown.pamd %{buildroot}%{_sysconfdir}/pam.d/$wrapapp
done
rm -f %{buildroot}%{_bindir}/shutdown

install -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/pam.d/simple_root_authen
install -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/security/console.apps/simple_root_authen
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/mandriva-console-auth
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/pam.d/mandriva-simple-auth

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

%post
if [ ! -z "$SECURE_LEVEL" ];then
if [ -x /usr/sbin/msec -a "$SECURE_LEVEL" -gt "3" ]; then  /usr/sbin/msec $SECURE_LEVEL || true ; fi
fi
%if %mdkversion < 200900
%update_menus
%endif

%if %mdkversion < 200900
%postun
%clean_menus
%endif

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root)
%{_sysconfdir}/xdg/autostart/pam-panel-icon.desktop
%{_bindir}/usermount
%{_bindir}/userinfo
%{_bindir}/userpasswd
%{_mandir}/man1/usermount.1*
%{_mandir}/man1/userinfo.1*
%{_mandir}/man1/userpasswd.1*
%{_mandir}/man1/pam-panel-icon.1*
%{_mandir}/man8/consolehelper-gtk.8*
%{_bindir}/consolehelper-gtk
%{_bindir}/pam-panel-icon
%{_datadir}/usermode
%{_datadir}/pixmaps/*

%files -n %{name}-consoleonly -f %{name}.lang
%defattr(-,root,root)
%attr(4755,root,root) %{_sbindir}/userhelper
%{_mandir}/man8/userhelper.8*
%{_bindir}/consolehelper
%{_mandir}/man8/consolehelper.8*
# PAM console wrappers
%{_bindir}/halt
%{_bindir}/reboot
%{_bindir}/poweroff
%config(noreplace) %{_sysconfdir}/pam.d/halt
%config(noreplace) %{_sysconfdir}/pam.d/reboot
%config(noreplace) %{_sysconfdir}/pam.d/poweroff
%config(noreplace) %{_sysconfdir}/pam.d/simple_root_authen
%config(noreplace) %{_sysconfdir}/pam.d/mandriva-simple-auth
%config(noreplace) %{_sysconfdir}/pam.d/mandriva-console-auth
%config(missingok,noreplace) %{_sysconfdir}/security/console.apps/halt
%config(missingok,noreplace) %{_sysconfdir}/security/console.apps/reboot
%config(missingok,noreplace) %{_sysconfdir}/security/console.apps/poweroff
%config(noreplace) %{_sysconfdir}/security/console.apps/simple_root_authen
