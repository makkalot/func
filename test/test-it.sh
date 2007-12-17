#!/bin/bash

# where do we build stuff
BUILD_PATH="/tmp/func-build"

# more or less where we are running from, but also
# where to stash the rpms we build

RPM_PATH=`pwd`

# do we need to build package at all?
BUILD=Y

# do we do a fresh pull from git to build
BUILD_FROM_FRESH_CHECKOUT=Y

rm -rf $RPM_PATH/rpms
rm -rf $RPM_PATH/srpms
rm -rf $RPM_PATH/tars
mkdir -p $RPM_PATH/rpms $RPM_PATH/srpms $RPM_PATH/tars


msg()
{
    echo 
    echo "============ $1 ============"
    echo 
}


check_out_code()
{
    echo "Build path is $BUILD_PATH"
    rm -rf $BUILD_PATH
    mkdir -p $BUILD_PATH
    pushd $BUILD_PATH
    git clone git://git.fedorahosted.org/func.git
    echo $?
    popd
}


build_rpm()
{
    PKG=$1
    BRT=$2
    echo;echo;echo
    echo "======================================"
    echo "Building $PKG in $BRT"
    echo "======================================"
    echo
    pushd $BUILD_PATH/$PKG
    make clean
    make rpms
    if [ $? != 0 ]; then
        echo "kaboom building $PKG"
        exit 1
    fi
    mv rpm-build/*.src.rpm $RPM_PATH/srpms
    mv rpm-build/*.rpm $RPM_PATH/rpms
    mv rpm-build/*.tar.gz $RPM_PATH/tars
    make clean
    popd
    if [ $? != 0 ]; then
        echo "kaboom cleaning up $PKG"
        exit 1
    fi
}

uninstall_the_func()
{
	# just one package for now, easy enough
	rpm -e func
}

install_the_func()
{
	rpm -Uvh $RPM_PATH/rpms/func*
	STATUS=$?
	# do something with the status	
}


find_the_func()
{
	INSTALLED_FUNC=`rpm -q func`
	STATUS=$?
	if [ "$STATUS" == "1" ] ; then
		msg "We were unable to find the func installed"
		exit 1
	fi
	msg "$INSTALLED_FUNC was found"
}

stop_the_func()
{
	/etc/init.d/funcd stop
	/etc/init.d/certmaster stop
}

start_the_func()
{
	# shut everything down first
	stop_the_func

	/etc/init.d/certmaster start
	CERT_STATUS=$?
	/etc/init.d/funcd start
	FUNCD_STATUS=$?
	if [ "$CERT_STATUS" != "0" ] ; then
		msg "certmaster startup failed with code: $CERT_STATUS"
	fi
	if [ "$FUNCD_STATUS" != "0" ] ; then
                msg "funcd startup failed with code: $FUNCD_STATUS"
        fi

}


if [ "$BUILD" == "Y" ] ; then
	if [ "$BUILD_FROM_FRESH_CHECKOUT" == "Y" ] ; then
		check_out_code
	else
		# assume we are running from the test dir
		BUILD_PATH="`pwd`/../../"
	fi
	
	build_rpm func $BUILD_PATH

	#if we are building, then we should remove the installed
	# versiones as well, and install the new
	uninstall_the_func

	install_the_func
fi

# see if func is install
# see if funcd is install
find_the_func


# test start up of init scripts
start_the_func

# see if funcd is running
# see if certmaster is installed
# see if cermtasterd is running

# setup certs
## see if we have certs set up properly
### probably do some stuff to test bad/no/malformed/unauthed certs as well

# see if we can connect to funcd with the overloard

# see what modules we have available
# for each module, call the info stuff on them

# / start walking over the modules, doing commandliney stuff to each, and
# trying to check return data and return code as much as possible 

# test shut down of init scripts


