VERSION		= $(shell echo `awk '{ print $$1 }' version`)
RELEASE		= $(shell echo `awk '{ print $$2 }' version`)
NEWRELEASE	= $(shell echo $$(($(RELEASE) + 1)))

MESSAGESPOT=po/messages.pot

all: rpms

clean:
	-rm -f  MANIFEST
	-rm -rf dist/ build/
	-rm -rf *~
	-rm -rf rpm-build/

#manpage:
#	pod2man --center="cobbler" --release="" cobbler.pod | gzip -c > cobbler.1.gz
#	pod2html cobbler.pod > cobbler.html

#test:
#	python tests/tests.py
#	-rm -rf /tmp/_cobbler-*

messages: server/*.py
	xgettext -k_ -kN_ -o $(MESSAGESPOT) server/*.py 
	sed -i'~' -e 's/SOME DESCRIPTIVE TITLE/func/g' -e 's/YEAR THE PACKAGE'"'"'S COPYRIGHT HOLDER/2007 Red Hat, inc. /g' -e 's/FIRST AUTHOR <EMAIL@ADDRESS>, YEAR/Adrian Likins <alikins@redhat.com>, 2007/g' -e 's/PACKAGE VERSION/func $(VERSION)-$(RELEASE)/g' -e 's/PACKAGE/func/g' $(MESSAGESPOT)


bumprelease:	
	-echo "$(VERSION) $(NEWRELEASE)" > version

setversion: 
	-echo "$(VERSION) $(RELEASE)" > version

build: clean
	python setup.py build -f

install: build 
	python setup.py install -f

sdist: clean messages
	python setup.py sdist

new-rpms: bumprelease rpms


rpms: sdist 
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
