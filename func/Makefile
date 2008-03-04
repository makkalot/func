
DIRS	= minion overlord 

PYFILES		= $(wildcard *.py)
PYDIRS = minion overlord

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

pychecker::
	-for d in $(PYDIRS); do ($(MAKE) -C $$d pychecker ); done   
pyflakes::
	-for d in $(PYDIRS); do ($(MAKE) -C $$d pyflakes ); done	
