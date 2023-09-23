import anyio
import asyncclick as click
from pprint import pprint

from google_calendar import GoogleCalendar
from logger import logger
from scraper import Scraper


@click.group()
def cli():
    """A CLI for scraping and scheduling problems from LeetCode"""


@cli.command(name="scrape", context_settings=dict(ignore_unknown_options=True))
@click.option("--dry", is_flag=True, help="Dry run")
@click.option("--verbose", is_flag=True, help="Verbose output")
async def scrape(dry=False, verbose=False):
    """Scrape problems from LeetCode"""
    scraper = Scraper(dry, verbose)
    await scraper.run()


@cli.group(invoke_without_command=True)
@click.pass_context
async def calendar(ctx):
    """Google Calendar commands"""
    if ctx.invoked_subcommand is None:
        await ctx.invoke(list)


@calendar.command(name="schedule", context_settings=dict(ignore_unknown_options=True))
@click.option("--dry", is_flag=True, help="Dry run")
@click.option("--verbose", is_flag=True, help="Verbose output")
async def schedule(dry=False, verbose=False):
    """Schedule problems to Google Calendar"""
    google_calendar = GoogleCalendar(dry, verbose)
    click.echo("Creating problem schedule...")
    events = await google_calendar.create_problem_schedule()
    click.echo(f"Scheduled {len(events)} events")


@calendar.command(name="delete", context_settings=dict(ignore_unknown_options=True))
@click.option("--dry", is_flag=True, help="Dry run")
@click.option("--verbose", is_flag=True, help="Verbose output")
async def delete(dry=False, verbose=False):
    """Delete all events from Google Calendar"""
    google_calendar = GoogleCalendar(dry, verbose)
    click.echo("Deleting all events...")
    event_ids = google_calendar.get_event_ids_from_calendar()
    click.echo(f"Got {len(event_ids)} event ids")
    count = await google_calendar.delete_all_events(event_ids)
    click.echo(f"Deleted {count} events")


@calendar.command(name="list", context_settings=dict(ignore_unknown_options=True))
@click.argument("start_time", type=click.DateTime(formats=["%Y-%m-%d"]), required=False)
@click.argument("max_results", type=int, required=False)
@click.option("--dry", is_flag=True, help="Dry run")
@click.option("--verbose", is_flag=True, help="Verbose output")
async def list(start_time=None, max_results=None, dry=False, verbose=False):
    """List all events from Google Calendar"""
    google_calendar = GoogleCalendar(dry, verbose)
    click.echo("Listing all events...")
    events = google_calendar.get_events(start_time, max_results)
    click.echo(f"Got {len(events)} events")
    # pprint(events)


if __name__ == "__main__":
    cli()
