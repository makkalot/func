

PYFILES		= $(wildcard *.py)

PYCHECKER       = /usr/bin/pychecker
PYFLAKES	= /usr/bin/pyflakes

clean::
	@rm -fv *.pyc *~ .*~ *.pyo 
	@find . -name .\#\* -exec rm -fv {} \;
	@rm -fv *.rpm
	

pychecker:: 
	@$(PYCHECKER) $(PYFILES) || exit 0

pyflakes::
ifneq ($(PYFILES)x, x)
	@$(PYFLAKES) $(PYFILES) || exit 0
endif
