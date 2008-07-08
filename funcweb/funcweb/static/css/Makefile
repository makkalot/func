clean::
	@rm -fv *.pyc *~ .*~ *.pyo 
	@find . -name .\#\* -exec rm -fv {} \;
	@rm -fv *.rpm
	-for d in $(DIRS); do ($(MAKE) -C $$d clean ); done	
		
