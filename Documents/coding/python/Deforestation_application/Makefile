RESOURCES_FILE = resources.py

default: compile

compile: $(RESOURCES_FILE)

%.py : %.qrc
	export PATH="/Applications/QGIS.app/Contents/MacOS/bin:$PATH"; export PYTHONPATH="/Applications/QGIS.app/Contents/Resources/python"; pyrcc4 -o $@ $<

clean:
	rm *pyc
	rm $(RESOURCES_FILE)