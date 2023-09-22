env:
    source leetcode/bin/activate

install:
	poetry shell && poetry install && cp .env.example .env

dry-run:
    python3 src/main.py --dry --verbose

run:
    python3 src/main.py --scrape --schedule

dev-scrape:
	python3 src/main.py --scrape --verbose

dev-scrape-dry:
	python3 src/main.py --scrape --dry --verbose

dev-schedule:
	python3 src/main.py --schedule --verbose

dev-schedule-dry:
	python3 src/main.py --schedule --dry --verbose

prod-schedule:
	python3 src/main.py --schedule

config:
    python3 src/config.py

help:
	python3 src/main.py --help
