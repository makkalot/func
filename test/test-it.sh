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
BUILD_FROM_FRESH_CHECKOUT=Y

# should we backup existing func pki setup, since
# we are going to be deleting it from the normal spot?
BACKUP_FUNC_PKI="N"

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

backup_the_secret_of_the_func()
{
	# whatever, this should probably be some standard date format
	# but I just wanted something sans spaces
	DATE=`date  "+%F_%R"`
	tar -c /etc/pki/func/*  /var/lib/func/* > func-pki-backup-$DATE.tar
	
}

#yes, I'm in a funny variable naming mood, I'll change them
#later
no_more_secrets()
{
	rm -rf /etc/pki/func/*
	rm -rf /var/lib/func/certmaster/*
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


pound_on_the_threads()
{
    msg "Trying to poke at the threads a bit"
    THREAD_COUNT=5
    for i in $MINION_CERTS
    do
	for Q in `seq 1 $THREAD_COUNT`
	do
	    # background these so they run more or less in parallel to
	    # each minion
	    echo "test add $Q 6" for $i
	    func $i call test add "$Q" "6" &
	done
    done

    # this is kind of dumb and ugly, but it gives a change for all the
    # connections to complete before we shut the server down
    sleep 10

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
    python async_test.py

}

run_unittests()
{
    nosetests -v -w unittest/
    
}

if [ "$BUILD" == "Y" ] ; then
	if [ "$BUILD_FROM_FRESH_CHECKOUT" == "Y" ] ; then
		check_out_code
	else
		# assume we are running from the test dir
		BUILD_PATH="`pwd`/../../"
	fi
	
	# FIXME: red hat specifc
	build_rpm func $BUILD_PATH

	#if we are building, then we should remove the installed
	# versiones as well, and install the new
	uninstall_the_func

	install_the_func
fi

# see if func is install
# see if funcd is install
find_the_func

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

pound_on_the_threads

run_unittests

run_async_test

stop_the_func
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


