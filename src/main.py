import anyio
import asyncclick as click
from pprint import pprint

from google_calendar import GoogleCalendar
from logger import logger
from scraper import Scraper

@click.command()
@click.option('--scrape', is_flag=True, help='Scrape')
@click.option('--schedule', is_flag=True, help='Schedule')
@click.option('--dry', is_flag=True, help='Dry run')
@click.option('--verbose', is_flag=True, help='Verbose output')
async def main(scrape = False, schedule = False, dry = False, verbose = False):
    if dry:
        logger.info("Doing a dry run!")
    
    if scrape:
        scraper = Scraper(dry, verbose)
        await scraper.run()

    if schedule:
        google_calendar = GoogleCalendar(dry, verbose)
        await google_calendar.create_problem_schedule()
        # google_calendar.delete_all_events()
        # events = google_calendar.get_events(start_time="2023-09-22", max_results=20)
        # pprint(events)
    
if __name__ == '__main__':
    main()