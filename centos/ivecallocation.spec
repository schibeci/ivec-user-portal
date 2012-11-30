%define name ivecallocation
%define version 1.1.3
%define unmangled_version 1.1.3
%define unmangled_version 1.1.3
%define release 1
%define webapps /usr/local/webapps
%define installdir %{webapps}/%{name}
%define settingsdir %{installdir}/settings
%define logsdir %{installdir}/settings
%define scratchdir %{installdir}/scratch
%define staticdir %{installdir}/static

# Turn off brp-python-bytecompile because it makes it difficult to generate the file list
# We still byte compile everything by passing in -O paramaters to python
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Summary: iVEC Allocation
Name: %{name}
Version: %{version}
Release: %{release}
Source0: %{name}-%{unmangled_version}.tar.gz
License: UNKNOWN
Group: Applications/Internet
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: x86_64
Vendor: Centre for Comparative Genomics <web@ccg.murdoch.edu.au>
BuildRequires: python-virtualenv python-setuptools openldap-devel openssl-devel postgresql-devel
Requires: httpd mod_wsgi openldap-clients openssl postgresql-libs

%description
Django iVEC Allocation web application

%prep
#%setup -n %{name}-%{unmangled_version} -n %{name}-%{unmangled_version}

%build
# Nothing, all handled by install

%install

NAME=%{name}
INSTALLDIR=%{buildroot}/%{webapps}/%{name}
SETTINGSDIR=$INSTALLDIR/settings
LOGSDIR=$INSTALLDIR/logs
SCRATCHDIR=$INSTALLDIR/scratch
STATICDIR=$INSTALLDIR/static

echo "INSTALLDIR=$INSTALLDIR"

# Make sure the standard target directories exist
mkdir -p $SETTINGSDIR
mkdir -p $LOGSDIR
mkdir -p $SCRATCHDIR
mkdir -p $STATICDIR


# Create a python prefix
mkdir -p $INSTALLDIR/{lib,bin,include}

# Install package into the prefix
cd $CCGSOURCEDIR
export PYTHONPATH=$INSTALLDIR/lib
easy_install -O1 --prefix $INSTALLDIR --install-dir $INSTALLDIR/lib .

# Create settings symlink so we can run collectstatic with the default settings
touch $SETTINGSDIR/__init__.py
ln -fs ..`find $INSTALLDIR -path "*/$NAME/settings.py" | sed s:^$INSTALLDIR::` $SETTINGSDIR/settings.py

# Run collectstatic and add all those files to INSTALLED_FILES
python -O $INSTALLDIR/bin/django-admin.py collectstatic --noinput --pythonpath=$INSTALLDIR --settings=settings.settings

install -D ../centos/ivecallocation_mod_wsgi_daemons.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/ivecallocation_mod_wsgi_daemons.conf
install -D ../centos/ivecallocation_mod_wsgi.conf $RPM_BUILD_ROOT/etc/httpd/conf.d/ivecallocation_mod_wsgi.conf
install -D django.wsgi $INSTALLDIR/django.wsgi
install -m 0755 -D ivecallocation-manage.py $RPM_BUILD_ROOT/%{_bindir}/ivecallocation

# At least one python package has hardcoded shebangs to /usr/local/bin/python
find $INSTALLDIR -name '*.py' -type f | xargs sed -i 's:^#!/usr/local/bin/python:#!/usr/bin/python:'
find $INSTALLDIR -name '*.py' -type f | xargs sed -i 's:^#!/usr/local/python:#!/usr/bin/python:'

# Generate a file containing all files in the package, stripping out the BUILDROOT as we go
rm -f $RPM_BUILD_DIR/INSTALLED_FILES
find $RPM_BUILD_ROOT -xtype f | sed s:^$RPM_BUILD_ROOT:: > $RPM_BUILD_DIR/INSTALLED_FILES

%clean
#rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
/etc/httpd/conf.d/*
%{_bindir}/ivecallocation
%attr(-,apache,,apache) %{installdir}
