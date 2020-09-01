import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    print('db/get_db')
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    print('db/close_db')
    db = g.pop('db', None)

    if db is not None:
        db.close()

## functions to run the schema.sql file
def init_db():
    print('db/init_db')
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

## command to initiate init_db() function from command line (CLI)
@click.command('init-db')
@with_appcontext
def init_db_command():
    print('db/init_db_command')
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

##Register close_db() and init_db_command functions with the Application
def init_app(app):
    print('db/init_app')
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
