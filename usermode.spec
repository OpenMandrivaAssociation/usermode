Summary:	Graphical tools for certain user account management tasks
Name:		usermode
Version:	1.111
Release:	5
Epoch:		1
License:	GPLv2+
Group:		System/Configuration/Other
Url:		https://fedorahosted.org/usermode/
Source0:	https://fedorahosted.org/releases/u/s/usermode/%{name}-%{version}.tar.xz
# being the console owner is enough
Source1:	distro-console-auth
# besides being the console owner, needs to authenticate as well
Source2:	distro-simple-auth
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
BuildRequires:	pkgconfig(libglade-2.0)
BuildRequires:	pkgconfig(libuser)
BuildRequires:	pam-devel
BuildRequires:	desktop-file-utils
BuildRequires:	pkgconfig(ice)
BuildRequires:	pkgconfig(sm)
BuildRequires:	pkgconfig(libstartup-notification-1.0)
BuildRequires:	pkgconfig(blkid)
Requires:	util-linux
Requires:	pam >= 0.75-28mdk
Requires:	%{name}-consoleonly = %{epoch}:%{version}-%{release}
Conflicts:	SysVinit < 2.74-14
Conflicts:	msec < 0.15-17mdk

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
%serverbuild_hardened
%configure2_5x \
	--without-selinux

%make

%install
%makeinstall_std VENDOR="%(echo %{vendor} | tr A-Z a-z |sed -e 's#[ /()!?]#_#g')"

mkdir -p %{buildroot}%{_mandir}/{man1,man8}

mkdir -p %{buildroot}%{_sysconfdir}/pam.d %{buildroot}%{_sysconfdir}/security/console.apps

install -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/pam.d/simple_root_authen
install -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/security/console.apps/simple_root_authen
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/pam.d/distro-console-auth
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/pam.d/distro-simple-auth

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

%post
if [ ! -z "$SECURE_LEVEL" ];then
if [ -x /usr/sbin/msec -a "$SECURE_LEVEL" -gt "3" ]; then  /usr/sbin/msec $SECURE_LEVEL || true ; fi
fi

%files
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
%attr(4755,root,root) %{_sbindir}/userhelper
%{_mandir}/man8/userhelper.8*
%{_bindir}/consolehelper
%{_mandir}/man8/consolehelper.8*
%config(noreplace) %{_sysconfdir}/pam.d/simple_root_authen
%config(noreplace) %{_sysconfdir}/pam.d/distro-simple-auth
%config(noreplace) %{_sysconfdir}/pam.d/distro-console-auth
%config(noreplace) %{_sysconfdir}/security/console.apps/simple_root_authen
%{_sysconfdir}/pam.d/mandriva-simple-auth
%{_sysconfdir}/pam.d/mandriva-console-auth

%changelog
* Wed Oct 10 2012 Alexander Kazancev <kazancas@mandriva.orf> 1:1.111
- 1.111
- minor spec cleaning
- this removes poweroff/halt/reboot, moving to systemd package

* Sun Jun 19 2011 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.107-1mdv2011.0
+ Revision: 686011
- update to new version 1.107

* Fri May 06 2011 Oden Eriksson <oeriksson@mandriva.com> 1:1.106.1-2
+ Revision: 670755
- mass rebuild

* Sun Oct 03 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.106.1-1mdv2011.0
+ Revision: 582709
- update to new version 1.106.1

* Sat Aug 28 2010 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.106-1mdv2011.0
+ Revision: 573993
- update to new version 1.106
- rediff patches 2 and 9

* Sun Nov 08 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.102-1mdv2010.1
+ Revision: 462906
- add missing manpages
- update to new version 1.102

* Sat Sep 26 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.101-1mdv2010.0
+ Revision: 449571
- update to new version 1.101
- rediff patch 7
- disable patch 8 for now
- update to new version 1.101

* Wed Sep 09 2009 Frederic Crozat <fcrozat@mandriva.com> 1:1.100-3mdv2010.0
+ Revision: 435273
- Update patch1 to no longer let dbus go through, conflicts with GNOME apps

* Tue Jun 09 2009 Frederic Crozat <fcrozat@mandriva.com> 1:1.100-2mdv2010.0
+ Revision: 384370
- Switch to libblkid-devel

* Sat Jun 06 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.100-1mdv2010.0
+ Revision: 383291
- update to new version 1.100
- Patch8: rediff

* Fri Apr 03 2009 Frederic Crozat <fcrozat@mandriva.com> 1:1.99-5mdv2009.1
+ Revision: 363691
- Update patch1 to allow META_CLASS to go through

* Fri Mar 13 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.99-4mdv2009.1
+ Revision: 354736
- Patch10: disable session restart (mdvbz #44632)
- start under Xfce too (one more time ;)

* Wed Mar 11 2009 Frederic Crozat <fcrozat@mandriva.com> 1:1.99-3mdv2009.1
+ Revision: 353668
- Start pam-panel-icon under KDE too

* Tue Mar 03 2009 Frederic Crozat <fcrozat@mandriva.com> 1:1.99-2mdv2009.1
+ Revision: 347910
- Ensure pam_xauth is called for simple_root_auth (Mdv bug #41416)

* Tue Feb 03 2009 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.99-1mdv2009.1
+ Revision: 337194
- rediff patches 3 and 8
- update to new version 1.99
- redif patches 1,2 and 7
- Patch9: fix build with -Werror=format-security
- do not start pam-panel-icon under Xfce (workaround for mdvbz#44632)

* Wed Oct 01 2008 Frederic Crozat <fcrozat@mandriva.com> 1:1.98-5mdv2009.0
+ Revision: 290442
- Update patch5 to let dbus session variable go through, allow drakxtools to ask session to end

* Sun Sep 14 2008 Tomasz Pawel Gajc <tpg@mandriva.org> 1:1.98-4mdv2009.0
+ Revision: 284767
- run authentication applet for Xfce also
- use %%{buildroot}
- fix mixture of tabs and spaces
- some spec file clean

* Fri Aug 22 2008 Frederic Crozat <fcrozat@mandriva.com> 1:1.98-3mdv2009.0
+ Revision: 275139
- Update patch1 to export gtk modules list and orbit socket dir to allow a11y support for root applications

* Tue Aug 05 2008 Frederic Crozat <fcrozat@mandriva.com> 1:1.98-2mdv2009.0
+ Revision: 263849
- Add autostart .desktop file for pam-panel-icon for GNOME

* Tue Aug 05 2008 Frederic Crozat <fcrozat@mandriva.com> 1:1.98-1mdv2009.0
+ Revision: 263838
- Release 1.98
- New url / update license
- Regenerate patches 2, 7, 8

* Wed Jun 18 2008 Thierry Vignaud <tv@mandriva.org> 1:1.94-2mdv2009.0
+ Revision: 225912
- rebuild

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Fri Feb 08 2008 Frederic Crozat <fcrozat@mandriva.com> 1:1.94-1mdv2008.1
+ Revision: 164279
- Release 1.94
- Update patch1 to allow GTK2 applications to use user specified theme (Mdv bug #37602)
- Remove patch4 and source12, merged upstream
- Regenerate patch 8, partially merged upstream

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Oct 02 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.92-7mdv2008.0
+ Revision: 94733
- update et translation, from Marek Laane

* Mon Oct 01 2007 Funda Wang <fwang@mandriva.org> 1:1.92-6mdv2008.0
+ Revision: 94129
- fix bug#33827
- Add zh_CN translation patch for usermode

* Thu Sep 13 2007 Anne Nicolas <ennael@mandriva.org> 1:1.92-5mdv2008.0
+ Revision: 85057
- add translations for authentication chain

* Wed Sep 12 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.92-4mdv2008.0
+ Revision: 84809
- introduce common pam configuration files for usermode
- don't use timestamp for when requiring only console ownership

* Wed Sep 12 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.92-3mdv2008.0
+ Revision: 84627
- fix Uzbek translation (#32459)

* Tue Sep 04 2007 Olivier Blin <oblin@mandriva.com> 1:1.92-2mdv2008.0
+ Revision: 79161
- remove Icon extension in desktop files
- fix some typos in the proxy environment patch (reset correct environment variables if some are invalid)
- add back proxy environment patch (#31028)

* Fri Aug 17 2007 Frederic Crozat <fcrozat@mandriva.com> 1:1.92-1mdv2008.0
+ Revision: 64868
- Fix buildrequires
- Release 1.92
- Remove source3 (extra translations are no longer up to date)
- uncompress source10
- add console.apps file for simple_root_authen
- Regenerate patches 1, 2
- Remove patches 5, 6, 8 (no longer needed)
- Remove cflags changes (no longer needed for years)
- update patch1 to allow LINES and COLUMNS
- bunzip patches
- patched another instance of the password prompt issue (#28955)

  + Funda Wang <fwang@mandriva.org>
    - revert changes to r23251
    - no more extra msgfmt needed
    - Rediff patch1, patch2
    - New upstream version 1.91
    - do not use old translations.


* Fri Mar 23 2007 Frederic Crozat <fcrozat@mandriva.com> 1.85-7mdv2007.1
+ Revision: 148636
- update patch1 to allow LINES and COLUMNS
- bunzip patches

* Wed Mar 21 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.85-6mdv2007.1
+ Revision: 147241
- patched another instance of the password prompt issue (#28955)

* Tue Mar 20 2007 Andreas Hasenack <andreas@mandriva.com> 1:1.85-5mdv2007.1
+ Revision: 147126
- fix #28955 (Incorrect and confusing password prompt)

* Wed Mar 14 2007 Frederic Crozat <fcrozat@mandriva.com> 1:1.85-4mdv2007.1
+ Revision: 143557
- Remove .desktop, there are better alternatives out there
- Import usermode

* Tue Sep 26 2006 Olivier Blin <blino@mandriva.com> 1.85-4mdv2007.0
- from Mathieu Geli <mathieu.geli@gmail.com>:
  add proxy variables (ftp_proxy/http_proxy) in new environnement
- add more proxy variables (https_proxy/no_proxy)

* Wed Aug 09 2006 Olivier Blin <blino@mandriva.com> 1.85-3mdv2007.0
- don't use pam_stack in Source10 (from Andreas, #24200)
- remove unsupported categories from desktop files
- install desktop files with mandriva as vendor, not redhat
- xdg menu

* Wed Jun 07 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 1.85-1mdv2007.0
- fix buildrequires
- %%mkrel
- cosmetics

* Tue May 16 2006 Frederic Crozat <fcrozat@mandriva.com> 1:1.85-1mdk
- Release 1.85
- Regenerate patches 1, 2
- Remove patches 3 (merged upstream), 4, 6 (no longer needed)
- Patch6: fix tray icon transparency
- Patch7: set password dialog to stick on all workspaces

* Sun Jan 01 2006 Mandriva Linux Team <http://www.mandrivaexpert.com/> 1.63-14mdk
- Rebuild

* Tue Jul 26 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 1:1.63-13mdk
- Rebuild

* Sat Oct 02 2004 Pablo Saratxaga <pablo@mandrakesoft.com> 1.63-12mdk
- Upodated translations

* Thu Sep 30 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 1.63-11mdk
- Patch6: fix build with latest gtk

* Wed Mar 17 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 1.63-10mdk
- Patch5: convert entry text to local encoding (not always UTF-8)
- Update translations (source 3) (pablo)

* Wed Feb 25 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 1.63-9mdk
- fix unstallable package (#8399)

* Tue Oct 21 2003 Frederic Lepied <flepied@mandrakesoft.com> 1.63-8mdk
- rebuild for rewriting /etc/pam.d file

* Sat Sep 27 2003 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.63-7mdk
- lib64 fixes

