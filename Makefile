VERSION		= $(shell echo `awk '{ print $$1 }' version`)
RELEASE		= $(shell echo `awk '{ print $$2 }' version`)
NEWRELEASE	= $(shell echo $$(($(RELEASE) + 1)))

MESSAGESPOT=po/messages.pot

TOPDIR = $(shell pwd)
DIRS	= modules minion overlord func docs scripts
PYDIRS	= modules minion overlord func scripts
EXAMPLEDIR = examples
INITDIR	= init-scripts

all: rpms

clean:
	-rm -f  MANIFEST
	-rm -rf dist/ build/
	-rm -rf *~
	-rm -rf rpm-build/
	-rm -rf docs/*.gz
	-for d in $(DIRS); do ($(MAKE) -C $$d clean ); done

clean_hard:
	-rm -rf $(shell python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")/func 

clean_harder:
	-rm -rf /etc/pki/func
	-rm -rf /etc/func
	-rm -rf /var/lib/func

clean_hardest: clean_rpms

manpage:
	pod2man --center="funcd" --release="" ./docs/funcd.pod | gzip -c > ./docs/funcd.1.gz
	pod2man --center="func" --release="" ./docs/func.pod | gzip -c > ./docs/func.1.gz
	pod2man --center="certmaster" --release="" ./docs/certmaster.pod | gzip -c > ./docs/certmaster.1.gz
	pod2man --center="certmaster-ca" --release="" ./docs/certmaster-ca.pod | gzip -c > ./docs/certmaster-ca.1.gz

messages: minion/*.py
	xgettext -k_ -kN_ -o $(MESSAGESPOT) minion/*.py 
	sed -i'~' -e 's/SOME DESCRIPTIVE TITLE/func/g' -e 's/YEAR THE PACKAGE'"'"'S COPYRIGHT HOLDER/2007 Red Hat, inc. /g' -e 's/FIRST AUTHOR <EMAIL@ADDRESS>, YEAR/Adrian Likins <alikins@redhat.com>, 2007/g' -e 's/PACKAGE VERSION/func $(VERSION)-$(RELEASE)/g' -e 's/PACKAGE/func/g' $(MESSAGESPOT)


bumprelease:	
	-echo "$(VERSION) $(NEWRELEASE)" > version

setversion: 
	-echo "$(VERSION) $(RELEASE)" > version

build: clean
	python setup.py build -f

install: build manpage
	python setup.py install -f

install_hard: clean_hard install

install_harder: clean_harder install

install_hardest: clean_harder clean_rpms rpms install_rpm restart

install_rpm:
	-rpm -Uvh rpm-build/func-$(VERSION)-$(RELEASE)$(shell rpm -E "%{?dist}").noarch.rpm

restart:
	-/etc/init.d/certmaster restart
	-/etc/init.d/funcd restart

recombuild: install_harder restart

clean_rpms:
	-rpm -e func

sdist: messages
	python setup.py sdist

new-rpms: bumprelease rpms

pychecker:
	-for d in $(PYDIRS); do ($(MAKE) -C $$d pychecker ); done   
pyflakes:
	-for d in $(PYDIRS); do ($(MAKE) -C $$d pyflakes ); done	

money: clean
	-sloccount --addlang "makefile" $(TOPDIR) $(PYDIRS) $(EXAMPLEDIR) $(INITDIR)
 
rpms: build manpage sdist
	mkdir -p rpm-build
	cp dist/*.gz rpm-build/
	cp version rpm-build/
	rpmbuild --define "_topdir %(pwd)/rpm-build" \
	--define "_builddir %{_topdir}" \
	--define "_rpmdir %{_topdir}" \
	--define "_srcrpmdir %{_topdir}" \
	--define '_rpmfilename %%{NAME}-%%{VERSION}-%%{RELEASE}.%%{ARCH}.rpm' \
	--define "_specdir %{_topdir}" \
	--define "_sourcedir  %{_topdir}" \
	-ba func.spec
