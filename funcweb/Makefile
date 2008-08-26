VERSION		= $(shell echo `awk '{ print $$1 }' version`)
RELEASE		= $(shell echo `awk '{ print $$2 }' version`)
NEWRELEASE	= $(shell echo $$(($(RELEASE) + 1)))


TOPDIR = $(shell pwd)
DIRS	= funcweb funcweb/config funcweb/identity funcweb/templates funcweb/tests funcweb/static \
		  funcweb/static/javascript funcweb/static/css funcweb/static/images 
PYDIRS	= funcweb funcweb/identity funcweb/tests 
INITDIR	= init-scripts

all: rpms

bumprelease:	
	-echo "$(VERSION) $(NEWRELEASE)" > version

setversion: 
	-echo "$(VERSION) $(RELEASE)" > version

build: clean
	python setup.py build -f

clean:
	-rm -f  MANIFEST
	-rm -rf build/
	-rm -rf dist/
	-rm -rf *~
	-rm -rf rpm-build/
	-rm -rf funcweb.egg-info/
	-for d in $(DIRS); do ($(MAKE) -C $$d clean ); done

clean_hard:
	-rm -rf $(shell python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")/funcweb 

clean_harder:
	-rm -rf /etc/httpd/conf.d/funcweb.conf
	-rm -rf /etc/funcweb

clean_hardest: clean_rpms

sdist:
	python setup.py sdist

install: build
	python setup.py install -f

install_hard: clean_hard install

install_harder: clean_harder install

install_hardest: clean_harder clean_rpms rpms install_rpm restart

install_rpm:
	-rpm -Uvh rpm-build/funcweb-$(VERSION)-$(RELEASE)$(shell rpm -E "%{?dist}").noarch.rpm

restart:
	-/etc/init.d/funcwebd restart

recombuild: install_harder restart

clean_rpms:
	-rpm -e funcweb

new-rpms: bumprelease rpms

pychecker:
	-for d in $(PYDIRS); do ($(MAKE) -C $$d pychecker ); done   
pyflakes:
	-for d in $(PYDIRS); do ($(MAKE) -C $$d pyflakes ); done	

money: clean
	-sloccount --addlang "makefile" $(TOPDIR) $(PYDIRS) $(EXAMPLEDIR) $(INITDIR) 

unittest:
	-nosetests -v -w funcweb/tests

rpms: build sdist
	mkdir -p rpm-build
	cp dist/*.gz rpm-build/
	cp funcweb.te rpm-build/
	cp version rpm-build/
	rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define '_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm' \
	--define "_specdir %{_topdir}" \
	--define "_sourcedir  %{_topdir}" \
	-ba funcweb.spec
