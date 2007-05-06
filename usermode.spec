Summary:	Graphical tools for certain user account management tasks
Name:		usermode
Version:	1.91
Release:	%mkrel 1
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
#Source3:	usermode-pofiles.tar.bz2
Source4:	userpasswd16.xpm.bz2
Source5:	userpasswd32.xpm.bz2
Source6:	userpasswd48.xpm.bz2
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
# (blino) remove unsupported categories from desktop files
perl -pi -e 's/.*--add-category (AdvancedSettings|Application).*\n//' Makefile*

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
#bzcat %{SOURCE3} | tar xf -

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

# menu 
mkdir -p $RPM_BUILD_ROOT/{%{_liconsdir},%{_miconsdir}}
bzcat %{SOURCE4} > $RPM_BUILD_ROOT%{_miconsdir}/userpasswd.xpm
bzcat %{SOURCE5} > $RPM_BUILD_ROOT%{_iconsdir}/userpasswd.xpm
bzcat %{SOURCE6} > $RPM_BUILD_ROOT%{_liconsdir}/userpasswd.xpm

mkdir -p $RPM_BUILD_ROOT%{_menudir}/
cat <<EOF > $RPM_BUILD_ROOT%{_menudir}/usermode
?package(usermode): needs=X11 \
section="Configuration/Other" \
title="Change Password" \
longtitle="A frontend to change user password" \
cqommand="/usr/bin/userpasswd" \
qicon="userpasswd.xpm" \
xdg="true"
EOF

%find_lang %{name}

# remove unpackaged files
rm -f $RPM_BUILD_ROOT%{_datadir}/locale/*/LC_MESSAGES/@GETTEXT_PACKAGE@.mo

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
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
# menu
%{_menudir}/usermode
%{_liconsdir}/*.xpm
%{_miconsdir}/*.xpm
%{_iconsdir}/*.xpm

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
