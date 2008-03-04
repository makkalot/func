
PYFILES		= $(wildcard *.py)

PYCHECKER       = /usr/bin/pychecker
PYFLAKES	= /usr/bin/pyflakes

clean::
	@rm -fv *.pyc *~ .*~ *.pyo
	@find . -name .\#\* -exec rm -fv {} \;
	@rm -fv *.rpm
	-for d in $(DIRS); do ($(MAKE) -C $$d clean ); done

pychecker::
	@$(PYCHECKER) $(PYFILES) || exit 0

pyflakes::
	@$(PYFLAKES) $(PYFILES) || exit 0
