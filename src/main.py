import anyio
import asyncclick as click
from pprint import pprint

from google_calendar import GoogleCalendar
from logger import logger
from scraper import Scraper


@click.group()
def cli(dry=False, verbose=False):
    """A CLI for scraping and scheduling problems from LeetCode"""


@cli.command(name="scrape", context_settings=dict(ignore_unknown_options=True))
@click.option("--dry", is_flag=True, help="Dry run")
@click.option("--verbose", is_flag=True, help="Verbose output")
async def scrape(dry=False, verbose=False):
    """Scrape problems from LeetCode"""
    scraper = Scraper(dry, verbose)
    await scraper.run()


@cli.command(name="schedule", context_settings=dict(ignore_unknown_options=True))
@click.option("--dry", is_flag=True, help="Dry run")
@click.option("--verbose", is_flag=True, help="Verbose output")
async def schedule(dry=False, verbose=False):
    """Schedule problems to Google Calendar"""
    google_calendar = GoogleCalendar(dry, verbose)
    await google_calendar.create_problem_schedule()
    # google_calendar.delete_all_events()
    # events = google_calendar.get_events(start_time="2023-09-22", max_results=20)
    # pprint(events)


if __name__ == "__main__":
    cli()
