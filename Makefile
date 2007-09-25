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
	-rm -rf docs/*.gz

manpage:
	pod2man --center="funcd" --release="" ./docs/funcd.pod | gzip -c > ./docs/funcd.1.gz
	pod2man --center="func" --release="" ./docs/func.pod | gzip -c > ./docs/func.1.gz
	pod2man --center="certmaster" --release="" ./docs/certmaster.pod | gzip -c > ./docs/certmaster.1.gz

messages: minion/*.py
	xgettext -k_ -kN_ -o $(MESSAGESPOT) minion/*.py 
	sed -i'~' -e 's/SOME DESCRIPTIVE TITLE/func/g' -e 's/YEAR THE PACKAGE'"'"'S COPYRIGHT HOLDER/2007 Red Hat, inc. /g' -e 's/FIRST AUTHOR <EMAIL@ADDRESS>, YEAR/Adrian Likins <alikins@redhat.com>, 2007/g' -e 's/PACKAGE VERSION/func $(VERSION)-$(RELEASE)/g' -e 's/PACKAGE/func/g' $(MESSAGESPOT)


bumprelease:	
	-echo "$(VERSION) $(NEWRELEASE)" > version

setversion: 
	-echo "$(VERSION) $(RELEASE)" > version

build:
	python setup.py build -f

install: build manpage
	python setup.py install -f

sdist: messages
	python setup.py sdist

new-rpms: bumprelease rpms


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
