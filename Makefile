default: run

run:
	. env/bin/activate && python2 tools/run.py

setup:
	tools/setup.sh

clean:
	rm -r env/

kill:
	. env/bin/activate && python2 tools/kill-database.py

init:
	. env/bin/activate && python2 tools/init-database.py
