env:
	source leetcode/bin/activate

install:
	poetry shell && poetry install && cp .env.example .env

scrape:
	python3 src/main.py scrape

dev-scrape:
	python3 src/main.py scrape --verbose

dev-scrape-dry:
	python3 src/main.py scrape --dry --verbose

calendar:
	python3 src/main.py calendar

calendar-schedule:
	python3 src/main.py calendar schedule

calendar-list:
	python3 src/main.py calendar list

calendar-delete:
	python3 src/main.py calendar delete --verbose

dev-schedule:
	python3 src/main.py calendar schedule --dry --verbose

dev-calendar-delete:
	python3 src/main.py calendar delete --dry --verbose

dev-calendar-list:
	python3 src/main.py calendar list --verbose

config:
	python3 src/config.py

help:
	python3 src/main.py --help
