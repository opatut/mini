default: run

run:
	python2 tools/run.py

setup:
	tools/setup.sh

seed:
	python2 tools/seed-database.py

init:
	python2 tools/init-database.py
