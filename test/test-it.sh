#!/bin/bash
# Copyright 2007, Red Hat, Inc
# Adrian Likins <alikins@redhat.com>
#
# This software may be freely redistributed under the terms of the GNU
# general public license.
#

# this is pretty Red Hat distro specific at the moment
# I'll try to make it a bit more portable if there is
# interest

# where do we build stuff
BUILD_PATH="/tmp/func-build"

# more or less where we are running from, but also
# where to stash the rpms we build

RPM_PATH=`pwd`

# do we need to build package at all?
BUILD=Y

# do we do a fresh pull from git to build
BUILD_FROM_FRESH_CHECKOUT=N
# do we use the master repo, or clone localy
# you really need to change both of these
CLONE_LOCAL_REPO=Y

# do we build/uninstall via rpms?
INSTALL_VIA_RPMS=N

# should we backup existing func pki setup, since
# we are going to be deleting it from the normal spot?
BACKUP_FUNC_PKI="N"

# do we want to run the unit tests as well
RUN_UNITTESTS="Y"
# you can put conf stuff in test-it.conf 
# so you don't have to worry about checking in config stuff
if [ -f "test-it.conf" ] ; then
    source test-it.conf
fi


show_config()
{
    echo "BUILD_PATH=$BUILD_PATH"
    echo "RPM_PATH=$RPM_PATH"
    echo "BUILD=$BUILD"
    echo "BUILD_FROM_FRESH_CHECKOUT=$BUILD_FROM_FRESH_CHECKOUT"
    echo "INSTALL_VIA_RPMS=$INSTALL_VIA_RPMS"
    echo "BACKUP_FUNC_PKI=$BACKUP_FUNC_PKI"
    echo "RUN_UNITTESTS=$RUN_UNITTESTS"

}

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


check_out_repo()
{
    echo "BASE_DIR: $BASE_DIR"
    REPO=$1
    if [ "$CLONE_LOCAL_REPO" == "Y" ] ; then
	msg "Building from a checkout of the local git repo"
	git clone $BASE_DIR/$REPO
    else
	msg "Building from a checkout from $GIT_REPO"
	git clone "git://git.fedorahosted.org/$REPO.git"
    fi


}


check_out_code()
{
    echo "Build path is $BUILD_PATH"
    rm -rf $BUILD_PATH
    mkdir -p $BUILD_PATH
    pushd $BUILD_PATH

    check_out_repo func 
    check_out_repo certmaster 
    popd
}


copy_code_to_buildroot()
{

    rm -rf $BUILD_PATH

    msg "Copying current build dir  $BASE_DIR/func to $BUILD_PATH/func"
    rm -rf $BUILD_PATH

    ls -lart $BASE_DIR
    mkdir -p $BUILD_PATH/func/
    cp -ar $BASE_DIR/func/* $BUILD_PATH/func

    msg "Copying current build dir  $BASE_DIR/certmaster to $BUILD_PATH/certmaster"
    mkdir -p $BUILD_PATH/certmaster/
    cp -ar $BASE_DIR/certmaster/* $BUILD_PATH/certmaster
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
    echo $BUILD_PATH/$PKG
    pushd $BUILD_PATH/$PKG
    echo "BRT" $BRT "PKG" $PKG "BUILD_PATH/PKG" $BUILD_PATH/$PKG
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

uninstall_the_rpms()
{
        msg "Removing the func and certmaster rpms, if there is one"
	# just one package for now, easy enough
	rpm -e func
	rpm -e certmaster
}

install_the_rpms()
{
        msg "Installing the certmaster rpm"
	rpm -Uvh $RPM_PATH/rpms/certmaster*
	STATUS=$?
	
	msg "Installing the func rpm"
	rpm -Uvh $RPM_PATH/rpms/func*
	STATUS=$?

	# do something with the status	
}


install_the_func()
{
    msg "Installing func directly from $1 $BUILD_PATH"
    pushd $1/func
    # remove any remnants of func already installed
    make clean clean_hard
    make install 

    pushd $1/certmaster
    make install
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

backup_the_secret_of_the_func()
{
	# whatever, this should probably be some standard date format
	# but I just wanted something sans spaces
	DATE=`date  "+%F_%R"`
	tar -c /etc/pki/func/* /var/lib/certmaster/* > func-pki-backup-$DATE.tar
}

#yes, I'm in a funny variable naming mood, I'll change them
#later
no_more_secrets()
{
    rm -rf /etc/pki/certmaster/*
    rm -rf /var/lib/certmaster/*
}

find_certmaster_certs()
{
	MINION_CERTS=`certmaster-ca --list`
	STATUS=$?
	echo "certmaster found the following certs:"
	echo $MINION_CERTS
	if [ "$MINION_CERTS" == "No certificates to sign" ] ; then
		MINION_CERTS=""
	fi
}

sign_the_certmaster_certs()
{
	echo
	echo $MINION_CERTS
	for i in $MINION_CERTS
	do
		echo /usr/bin/certmaster-ca -s $i
		/usr/bin/certmaster-ca -s $i
	done
	
}


# just some random "poke at func and make sure it works stuff"
test_funcd()
{
	# it seems to take a second for the signed certs to be
	# ready, so this is here
	sleep 10

	func "*" list_minions

	for i in $MINION_CERTS
	do
		func $i call system listMethods
		func $i call test add "23" "45"
	done


}


run_async_test()
{
    msg "Running async_test.py to test async/forking"
    pushd $BUILD_PATH/func/test
    python async_test.py

}

run_unittests()
{
    msg "Running the unittest suite"
    pushd $BUILD_PATH/func/test
    nosetests -v -w unittest/
    
}



# start doing stuff

# this is really ugly, but we are doing lots of weird path
# stuff at various points and kind of just want to make this
# "just work"...

if [ -f "func.spec" ] || [ -f "certmaster.spec" ]; then
    # we are running from the top level dir
    BASE_DIR="`pwd`/../"
elif [ -f "test-it.sh" ] ; then
    BASE_DIR="`pwd`/../../"
else
    echo "You need to run this from the base func dir or the test/ dir"
    exit 1
fi


show_config


if [ "$BUILD" == "Y" ] ; then
	if [ "$BUILD_FROM_FRESH_CHECKOUT" == "Y" ] ; then
		check_out_code
	else
		# assume we want to build a copy of the current
	        # source tree, we copy it else where and build
                # so we dont 'splode any thing with the build process
	        copy_code_to_buildroot
	fi
	

	if [ "$INSTALL_VIA_RPMS" == "Y" ] ; then
	    # FIXME: red hat specifc
	    build_rpm func $BUILD_PATH
	    build_rpm certmaster $BUILD_PATH

	    #if we are building, then we should remove the installed
	    # versiones as well, and install the new
	    uninstall_the_rpms
	    

	    install_the_rpms
       else
	    uninstall_the_rpms
	    install_the_func $BUILD_PATH
       fi
fi

# see if func is install
# see if funcd is install
if [ "$INSTALL_VIA_RPMS" == "Y" ] ; then
    find_the_func
fi

if [ "$BACKUP_FUNC_PKI" == "Y" ] ; then
	backup_the_secret_of_the_func
fi

# remove any existing keys
no_more_secrets

# test start up of init scripts
start_the_func

#we seem to need to wait a bit for certmaster to create the certs and whatnot
sleep 5

find_certmaster_certs

sign_the_certmaster_certs


test_funcd



if [ "$RUN_UNITTESTS" == "Y" ] ; then
    run_unittests
fi

run_async_test

stop_the_func

# leaving the test cases with func not running is kind of
# annoying, so restart it
start_the_func


### probably do some stuff to test bad/no/malformed/unauthed certs as well



