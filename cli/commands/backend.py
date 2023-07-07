import click
import json
from console import runner, console
from tables import FarmsTable


@click.group()
def entry_backend():
    pass

@entry_backend.command()
@click.option('--provision', '-p', is_flag=True, default=False)
@click.option('--calendars', '-c', type=click.Path(exists=True, readable=True), default=None)
@click.option('--worktasks', '-w', type=click.Path(exists=True, readable=True), default=None)
def bootstrap(provision: bool, calendars=None, worktasks=None):
    contents = ''

    if provision:
        runner.call('/backend/provision', 'POST', 500, 'unable to provision database')
    
    if calendars:
        with open(calendars, 'r') as fh:
            contents = json.loads(fh.read())
        runner.call('/backend/calendars', 'POST', 500, 'unable to bootstrap crop calendars', payload=contents)
    if worktasks:
        with open(worktasks, 'r') as fh:
            contents = json.loads(fh.read())
        runner.call('/backend/worktasks', 'POST', 500, 'unable to bootstrap work tasks', payload=contents)