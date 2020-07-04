import time  # Need inbuilt time module for waiting

# To test database connection is available
from django.db import connections
# OperationalError, when DB is not available
from django.db.utils import OperationalError
# Base class to build commands
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """
    Django command to pause execution until database is available
    """

    # Put the code in handle function( which runs whenever manag. command runs)
    # '*args, **options' allows passing in custom arguments(not used now,)
    # Here only checks the db when it is available -- exit
    def handle(self, *args, **options):
        """Exit only when DB is ready"""
        # To print some message to screen abt status of our commands etc..
        self.stdout.write('Waiting for database...')
        # Assign a variable indicates db connection
        db_conn = None
        # When connections unavailable django raises operational error, and
        # connections(dict) 'default' key set to the curr. status
        while not db_conn:
            try:
                db_conn = connections['default']
            except OperationalError:
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)  # Pauses the execution for 1 second

        self.stdout.write(self.style.SUCCESS('Database available!'))
        # Final message indicating DB is available, in 'SUCCESS' style(green)
