Summary:	Graphical tools for certain user account management tasks
Name:		usermode
Version:	1.85
Release:	%mkrel 7
Epoch:		1
License:	GPL
Group:		System/Configuration/Other
BuildRequires:	autoconf2.5
BuildRequires:	gettext-devel
BuildRequires:	intltool
BuildRequires:	libglade2.0-devel
BuildRequires:	libuser-devel
BuildRequires:	pam-devel
BuildRequires:	desktop-file-utils libice-devel libsm-devel
Source0:	usermode-%{version}.tar.bz2
# extra translations
Source3:	usermode-pofiles.tar.bz2
Source10:	simple_root_authen.bz2
# allow more environment variables to be set in root environment
Patch1:		usermode-1.85-environment.patch
# allow simple authentication without config file (used by drakxtools)
Patch2:		usermode-1.85-simple_authen.patch
# (fc) 1.63-10mdk convert entry text to current locale, don't keep it utf-8
Patch5:		usermode-1.63-utf8.patch
# (fc) 1.85-1mdk fix tray icon transparency
Patch6:		usermode-1.85-transparency.patch
# (fc) 1.85-1mdk set password dialog to stick on all workspace
Patch7:		usermode-1.85-stick.patch
# http://qa.mandriva.com/show_bug.cgi?id=28955
Patch8:		usermode-1.85-passprompt.patch

Requires:	util-linux 
Requires:	pam >= 0.75-28mdk
Requires:	%{name}-consoleonly = %{epoch}:%{version}-%{release}
Conflicts:	SysVinit < 2.74-14 msec < 0.15-17mdk
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
The usermode package contains several graphical tools for users:
userinfo, usermount and userpasswd.  Userinfo allows users to change
their finger information.  Usermount lets users mount, unmount, and
format filesystems.  Userpasswd allows users to change their
passwords.

Install the usermode package if you would like to provide users with
graphical tools for certain account management tasks.

%package -n	%{name}-consoleonly
Summary:	Non graphical part of usermode
Group:		System/Libraries

%description -n	%{name}-consoleonly
This package contains only the usermode stuff which doesn't require
XFree or GTK to run.

%prep
%setup -q
%patch1 -p1 -b .environment
%patch2 -p1 -b .user_authen
%patch5 -p1 -b .utf8
%patch6 -p1 -b .transparency
%patch7 -p1 -b .stick
%patch8 -p1 -b .passprompt

%build
export RPM_OPT_FLAGS="$RPM_OPT_FLAGS -Os"
%configure2_5x
%make 

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall VENDOR=mandriva

mkdir -p $RPM_BUILD_ROOT%{_mandir}/{man1,man8}

# Stuff from pam_console, for sysvinit. Here for lack of a better
# place....
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pam.d $RPM_BUILD_ROOT%{_sysconfdir}/security/console.apps
for wrapapp in halt reboot poweroff ; do
  ln -sf consolehelper $RPM_BUILD_ROOT%{_bindir}/$wrapapp
  touch $RPM_BUILD_ROOT%{_sysconfdir}/security/console.apps/$wrapapp
  cp shutdown.pamd $RPM_BUILD_ROOT%{_sysconfdir}/pam.d/$wrapapp
done
rm -f $RPM_BUILD_ROOT%{_bindir}/shutdown

# install extra po files
bzcat %{SOURCE3} | tar xf -

for i in po/*.po ; do
  mkdir -p $RPM_BUILD_ROOT/%{_datadir}/locale/`basename $i .po`/LC_MESSAGES
  msgfmt -v -o $RPM_BUILD_ROOT/%{_datadir}/locale/`basename $i .po`/LC_MESSAGES/%{name}.mo $i || :
done
# 'zh' alone is wrong
[ -d  $RPM_BUILD_ROOT/%{_datadir}/locale/zh ] && \
	rm -rf $RPM_BUILD_ROOT/%{_datadir}/locale/zh
# "zh_??.encoding" are replaced with "zh_??"
[ -d  $RPM_BUILD_ROOT/%{_datadir}/locale/zh_CN.GB2312 ] && \
	rm -rf $RPM_BUILD_ROOT/%{_datadir}/locale/zh_CN.GB2312
[ -d  $RPM_BUILD_ROOT/%{_datadir}/locale/zh_TW.Big5 ] && \
	rm -rf $RPM_BUILD_ROOT/%{_datadir}/locale/zh_TW.Big5
# eu_ES is bad file
[ -d  $RPM_BUILD_ROOT/%{_datadir}/locale/eu_ES ] && \
	rm -rf $RPM_BUILD_ROOT/%{_datadir}/locale/eu_ES

bzcat %{SOURCE10} > $RPM_BUILD_ROOT/%{_sysconfdir}/pam.d/simple_root_authen


%find_lang %{name}

# remove unpackaged files
rm -f $RPM_BUILD_ROOT%{_datadir}/locale/*/LC_MESSAGES/@GETTEXT_PACKAGE@.mo \
 $RPM_BUILD_ROOT%{_datadir}/applications/*.desktop

%post
if [ ! -z "$SECURE_LEVEL" ];then
if [ -x /usr/sbin/msec -a "$SECURE_LEVEL" -gt "3" ]; then  /usr/sbin/msec $SECURE_LEVEL || true ; fi
fi
%update_menus

%postun
%clean_menus

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%{_bindir}/usermount
%{_bindir}/userinfo
%{_bindir}/userpasswd
%{_mandir}/man1/usermount.1*
%{_mandir}/man1/userinfo.1*
%{_mandir}/man1/userpasswd.1*
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
%config(missingok,noreplace) %{_sysconfdir}/security/console.apps/halt
%config(missingok,noreplace) %{_sysconfdir}/security/console.apps/reboot
%config(missingok,noreplace) %{_sysconfdir}/security/console.apps/poweroff


%changelog
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



* Tue Aug  8 2006 Olivier Blin <blino@mandriva.com> 1.85-3mdv2007.0
- don't use pam_stack in Source10 (from Andreas, #24200)
- remove unsupported categories from desktop files
- install desktop files with mandriva as vendor, not redhat
- xdg menu

* Tue Jun 06 2006 Per Øyvind Karlsen <pkarlsen@mandriva.com> 1.85-1mdv2007.0
- fix buildrequires
- %%mkrel
- cosmetics

* Mon May 15 2006 Frederic Crozat <fcrozat@mandriva.com> 1:1.85-1mdk
- Release 1.85
- Regenerate patches 1, 2
- Remove patches 3 (merged upstream), 4, 6 (no longer needed)
- Patch6: fix tray icon transparency
- Patch7: set password dialog to stick on all workspaces

* Sun Jan 01 2006 Mandriva Linux Team <http://www.mandrivaexpert.com/> 1.63-14mdk
- Rebuild

* Mon Jul 25 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 1:1.63-13mdk
- Rebuild

* Fri Oct 01 2004 Pablo Saratxaga <pablo@mandrakesoft.com> 1.63-12mdk
- Upodated translations

* Wed Sep 29 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 1.63-11mdk
- Patch6: fix build with latest gtk

* Wed Mar 17 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 1.63-10mdk
- Patch5: convert entry text to local encoding (not always UTF-8)
- Update translations (source 3) (pablo)

* Wed Feb 25 2004 Thierry Vignaud <tvignaud@mandrakesoft.com> 1.63-9mdk
- fix unstallable package (#8399)

* Mon Oct 20 2003 Frederic Lepied <flepied@mandrakesoft.com> 1.63-8mdk
- rebuild for rewriting /etc/pam.d file

* Fri Sep 26 2003 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.63-7mdk
- lib64 fixes

* Thu Sep 18 2003 Guillaume Cottenceau <gc@mandrakesoft.com> 1.63-6mdk
- use 1.63 sources since userpasswd is severely broken in 1.68,
  backport our 1.68 patches

* Tue Sep 16 2003 Guillaume Cottenceau <gc@mandrakesoft.com> 1.68-6mdk
- update patch #2 to try to not segfault too much when performing
  a simple_root_authen (I suck)

* Mon Sep 15 2003 Pixel <pixel@mandrakesoft.com> 1.68-5mdk
- do not unset SESSION_MANAGER and ICEAUTHORITY

* Wed Aug  6 2003 Guillaume Cottenceau <gc@mandrakesoft.com> 1.68-4mdk
- don't forget to have HOME set even in simple_root_authen mode,
  it triggers fontconfig crashes :)
- fix nplanel's env patch using strchr in place of strstr (you should read
  warnings during compilation!)

* Mon Aug 04 2003 Pablo Saratxaga <pablo@mandrakesoft.com> 1.68-3mdk
- updated translations

* Fri Jul 25 2003 Thierry Vignaud <tvignaud@mandrakesoft.com> 1.68-2mdk
- fix #3950

* Tue Jun 24 2003 Nicolas Planel <nplanel@mandrakesoft.com> 1.68-1mdk
- 1.68.

* Tue May 13 2003 Guillaume Cottenceau <gc@mandrakesoft.com> 1.67-2mdk
- fix nplanel sux b0rking simple authen patch when upgrading to 1.67

* Thu Apr 08 2003 Nicolas Planel <nplanel@mandrakesoft.com> 1.67-1mdk
- 1.67.

* Wed Mar 12 2003 Nicolas Planel <nplanel@mandrakesoft.com> 1.63-5mdk
- fix bad env patch (fix #2626)

* Tue Mar 11 2003 Guillaume Cottenceau <gc@mandrakesoft.com> 1.63-4mdk
- remove /usr/bin/shutdown to fix #408

* Tue Feb 04 2003 Pablo Saratxaga <pablo@mandrakesoft.com> 1.63-3mdk
- updated translations

* Thu Jan 30 2003 Stefan van der Eijk <stefan@eijk.nu> 1.63-2mdk
- BuildRequires

* Thu Nov 14 2002 Frederic Crozat <fcrozat@mandrakesoft.com> 1.63-1mdk
- Release 1.63
- Add missing pam-panel-icon
- Require pam version shipping with pam_timestamp_check
- Regenerate patch2
- Patch4: don't use desktop-file-install to install .desktop files
- Move pixmaps to main package

* Mon Oct  7 2002 Gwenole Beauchesne <gbeauchesne@mandrakesoft.com> 1.55-9mdk
- Patch3: Use X_LIBS variable to determine what are linker flags for X libs
- Fix Geoffrey's bad habits to nuke packages before he uploads. Most
  notably, 1.44-5mdk to 1.44-6mdk with their changes no longer exist.

* Thu Sep  5 2002 Pablo Saratxaga <pablo@mandrakesoft.com> 1.55-8mdk
- rebuild to include latest translations

* Wed Aug 28 2002 Pablo Saratxaga <pablo@mandrakesoft.com> 1.55-7mdk
- rebuild including latest translations

* Thu Aug 22 2002 Frederic Lepied <flepied@mandrakesoft.com> 1.55-6mdk
- update pam config file to maintain the authentification during 5 mn (using pam_timestamp)

* Thu Aug  8 2002 Stefan van der Eijk <stefan@eijk.nu> 1.55-5mdk
- BuildRequires

* Thu Jul 25 2002 Guillaume Cottenceau <gc@mandrakesoft.com> 1.55-4mdk
- simple root authen is a "session" so that we keep XAUTHORITY
- in simple root authen, don't display "bla bla you need more info to
  run program simple_root_authen", but a more neutral msg
- use %%configure2_5x

* Thu Jul 25 2002 Geoffrey lee <snailtalk@mandrakesoft.com> 1.55-3mdk
- Un-b0rk simple_root_authen (another rh stupidity bug).

* Wed Jul 24 2002 Geoffrey Lee <snailtalk@mandrakesoft.com> 1.55-2mdk
- Glade file missing.

* Mon Jul 01 2002 Geoffrey Lee <snailtalk@mandrakesoft.com> 1.55-1mdk
- New and shiny source.
- Obsolete Pixel's patch number 2. (Seems that it is no longer needed?)
- Remove poweroff halt reboot shutdown links by default, for better security.
  If you want it back, just recreate the links.
- (Rediffed everything basically).

* Thu Feb 21 2002 Guillaume Cottenceau <gc@mandrakesoft.com> 1.44-4mdk
- write patch #3, to fallback to a simple root authentication if 
  /etc/security/console.apps/<progname> doesn't exist, so that it
  now acts just like "kdesu -c"
- write patch #4, to split a non-gtk-required package

* Thu Feb 14 2002 Pablo Saratxaga <pablo@mandrakesoft.com> 1.44-3mdk
- added extra translations and updated others

* Tue Jan 22 2002 David BAUDENS <baudens@mandrakesoft.com> 1.44-2mdk
- Fix french translation of 'Cancel'

* Sun Oct 28 2001 Geoffrey Lee <snailtalk@mandrakesoft.com> 1.44-1mdk
- 1.44 from rawhide.

* Tue Oct 23 2001 Daouda LO <daouda@mandrakesoft.com> 1.43-2mdk
- menu entry for userpasswd ( frontend to change password)

* Tue Sep 25 2001 Geoffrey Lee <snailtalk@mandrakesoft.com> 1.43-1mdk
- RH merge.

* Mon Sep 17 2001 Pixel <pixel@mandrakesoft.com> 1.42-8mdk
- fix (?) running progs via usermode with 1</dev/null or 2>/dev/null

* Mon Sep 10 2001 Pablo Saratxaga <pablo@mandrakesoft.com> 1.42-7mdk
- included latest translations (this time they are in)

* Tue Sep 06 2001 Pablo Saratxaga <pablo@mandrakesoft.com> 1.42-6mdk
- included latest translations

* Mon Aug 27 2001 Renaud Chaillat <rchaillat@mandrakesoft.com> 1.42-5mdk
- updated post script to work when SECURE_LEVEL is not set

* Sat Aug 25 2001 Geoffrey Lee <snailtalk@mandrakesoft.com> 1.42-4mdk
- Sanity build for 8.1.

* Wed Jul 11 2001 Stefan van der Eijk <stefan@eijk.nu> 1.42-3mdk
- BuildRequires:	gtk+-devel
- BuildRequires:	pam-devel
- Removed BuildRequires:	XFree86-devel

* Wed Jul 11 2001 Frederic Crozat <fcrozat@mandrakesoft.com> 1.42-2mdk
- Use more macros
- Remove source 1, 2 + menu entry (not needed)
- Shutdown tools are back (conflict with msec < 0.15-17mdk) 
- Call msec at install time if installed

* Tue May 22 2001 Geoffrey Lee <snailtalk@mandrakesoft.com> 1.42-1mdk
- Bump a nice and tasty 1.42 out for cooker.
- s/Copyright/License/;

* Tue Apr 10 2001 Frederic Crozat <fcrozat@mandrakesoft.com> 1.37-5mdk
- Update patch 2 for better INITIAL_USER handling

* Mon Apr 09 2001 Pablo Saratxaga <pablo@mandrakesoft.com> 1.37-4mdk
- included latest translations

* Tue Apr  3 2001 Frederic Crozat <fcrozat@mandrakesoft.com> 1.37-3mdk
- Update patch 2 to set INITIAL_USER and BROWSER variable

* Wed Nov 29 2000 Geoffrey lee <snailtalk@mandrakesoft.com> 1.37-2mdk
- use optflags.

* Fri Nov 10 2000 Geoffrey Lee <snailtalk@mandrakesoft.com> 1.37-1mdk
- bump up version for security fix. (RH).

* Tue Oct 10 2000 Renaud Chaillat <rchaillat@mandrakesoft.com> 1.36-2mdk
- patch to set some more environment variables

* Tue Oct 10 2000 Geoffrey Lee <snailtalk@mandrakesoft.com> 1.36-1mdk
- bump up version for security fix. (RH)

* Mon Oct  9 2000 Pablo Saratxaga <pablo@mandrakesoft.com> 1.35-5mdk
- updated French, Spanish, etc. translations

* Mon Oct  9 2000 Pablo Saratxaga <pablo@mandrakesoft.com> 1.35-4mdk
- included translations into the rpm; and added new ones (new ones still
  very incomplete)

* Mon Oct  9 2000 Renaud Chaillat <rchaillat@mandrakesoft.com> 1.35-3mdk
- set gid also when no session

* Fri Oct  6 2000 Renaud Chaillat <rchaillat@mandrakesoft.com> 1.35-2mdk
- patch in userhelper to set gid when executing a foreign program
  (-w option) (thanks to Fred Lepied)

* Thu Sep 28 2000 Frederic Crozat <fcrozat@mandrakesoft.com> 1.35-1mdk
- Release 1.35

* Mon Aug 07 2000 Frederic Lepied <flepied@mandrakesoft.com> 1.22-4mdk
- automatically added BuildRequires

* Wed Aug 02 2000 Stefan van der Eijk <s.vandereijk@chello.nl> 1.22-3mdk
- macroszifications
- Makefile patch for new manpage location
- BM

* Tue Jul 18 2000 Vincent Danen <vdanen@mandrakesoft.com> 1.22-2mdk
- remove pam console wrappers (security fix)

* Sat Apr 08 2000 Christopher Molnar <molnarc@mandrakesoft.com> 1.22-1mdk
- updated to new version
- updated group information
- added menu code
- There are no doc files available.

* Thu Mar 09 2000 Nalin Dahyabhai <nalin@redhat.com>
- fix problem parsing userhelper's -w flag with other args

* Wed Mar 08 2000 Nalin Dahyabhai <nalin@redhat.com>
- ignore read() == 0 because the child exits

* Tue Mar 07 2000 Nalin Dahyabhai <nalin@redhat.com>
- queue notice messages until we get prompts in userhelper to fix bug #8745

* Fri Feb 03 2000 Nalin Dahyabhai <nalin@redhat.com>
- free trip through the build system

* Tue Jan 11 2000 Nalin Dahyabhai <nalin@redhat.com>
- grab keyboard input focus for dialogs

* Fri Jan 07 2000 Michael K. Johnson <johnsonm@redhat.com>
- The root exploit fix created a bug that only showed up in certain
  circumstances.  Unfortunately, we didn't test in those circumstances...

* Mon Jan 03 2000 Michael K. Johnson <johnsonm@redhat.com>
- fixed local root exploit

* Thu Sep 30 1999 Michael K. Johnson <johnsonm@redhat.com>
- fixed old complex broken gecos parsing, replaced with simple working parsing
- can now blank fields (was broken by previous fix for something else...)

* Tue Sep 21 1999 Michael K. Johnson <johnsonm@redhat.com>
- FALLBACK/RETRY in consolehelper/userhelper
- session management fixed for consolehelper/userhelper SESSION=true
- fix memory leak and failure to close in error condition (#3614)
- fix various bugs where not all elements in userinfo got set

* Mon Sep 20 1999 Michael K. Johnson <johnsonm@redhat.com>
- set $HOME when acting as consolehelper
- rebuild against new pwdb

* Tue Sep 14 1999 Michael K. Johnson <johnsonm@redhat.com>
- honor "owner" flag to mount
- ask for passwords with username

* Tue Jul 06 1999 Bill Nottingham <notting@redhat.com>
- import pam_console wrappers from SysVinit, since they require usermode

* Mon Apr 12 1999 Michael K. Johnson <johnsonm@redhat.com>
- even better check for X availability

* Wed Apr 07 1999 Michael K. Johnson <johnsonm@redhat.com>
- better check for X availability
- center windows to make authentication easier (improve later with
  transients and embedded windows where possible)
- applink -> applnk
- added a little padding, especially important when running without
  a window manager, as happens when running from session manager at
  logout time

* Wed Mar 31 1999 Michael K. Johnson <johnsonm@redhat.com>
- hm, need to be root...

* Fri Mar 19 1999 Michael K. Johnson <johnsonm@redhat.com>
- updated userhelper.8 man page for consolehelper capabilities
- moved from wmconfig to desktop entries

* Thu Mar 18 1999 Michael K. Johnson <johnsonm@redhat.com>
- added consolehelper
- Changed conversation architecture to follow PAM spec

* Wed Mar 17 1999 Bill Nottingham <notting@redhat.com>
- remove gdk_input_remove (causing segfaults)

* Tue Jan 12 1999 Michael K. Johnson <johnsonm@redhat.com>
- fix missing include files

* Mon Oct 12 1998 Cristian Gafton <gafton@redhat.com>
- strip binaries
- use defattr
- fix spec file ( rm -rf $(RPM_BUILD_ROOT) is a stupid thing to do ! )

* Tue Oct 06 1998 Preston Brown <pbrown@redhat.com>
- fixed so that the close button on window managers quits the program properly

* Thu Apr 16 1998 Erik Troan <ewt@redhat.com>
- use gtk-config during build
- added make archive rule to Makefile
- uses a build root

* Fri Nov  7 1997 Otto Hammersmith <otto@redhat.com>
- new version that fixed memory leak bug.

* Mon Nov  3 1997 Otto Hammersmith <otto@redhat.com>
- updated version to fix bugs

* Fri Oct 17 1997 Otto Hammersmith <otto@redhat.com>
- Wrote man pages for userpasswd and userhelper.

* Tue Oct 14 1997 Otto Hammersmith <otto@redhat.com>
- Updated the packages... now includes userpasswd for changing passwords
  and newer versions of usermount and userinfo.  No known bugs or
  misfeatures. 
- Fixed the file list...

* Mon Oct 6 1997 Otto Hammersmith <otto@redhat.com>
- Created the spec file.
