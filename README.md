## Leetcode Calendar

A Google calendar schedule generator for Leetcode questions.

### Installation

Ensure you have `Poetry` installed running:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

Then install dependencies:

```sh
poetry install
```

### Environment

Note: [Link to Guide to setting up Google Calendar API on Google Cloud Console](https://stateful.com/blog/events-in-the-google-calendar-API)

Setup your `environment` and add `CALENDAR_ID` from Google Calendar

```
cp .env.example .env
```

- Once you create a key, copy the JSON file you downloaded to `src/data` directory and set the filename in your `.env` as `CALENDAR_CREDENTIALS_FILE`.
- You can rename your file if you so desire ¯\_(ツ)_/¯

### Running the app

`--dry` option ensures you don't hit the network

`--verbose` option enables printing of logs on the cli

Scrape NeetCode for questions

```sh
python3 src/main.py --scrape --dry --verbose
```

Schedule your calendar

```sh
python3 src/main.py --scrape --dry --verbose
```

or use Makefile command found in `Makefile` file

```sh
make dry-run
```