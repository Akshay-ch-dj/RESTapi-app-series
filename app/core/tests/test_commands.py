from unittest.mock import patch  # Mock the behaviour of django get_database()
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


# Test class
class CommandTests(TestCase):
    """
    Functions to Test the command manager
    """

    # Test 1
    def test_wait_for_db_ready(self):
        """Test waiting for DB when DB is available"""
        # Simulate the behaviour of django when the DB is available,
        # django throws an operational error when db not available,
        # management command-> try and retrive the db connection from Django,
        # checks for operational Error, Error occurs-when DB is not available,
        # No Error - DB is avilable and command will continue..
        # To setup the test it needed to override the behaviour of connection
        # handler to make it return True(not throw any Exception) --
        # 'patch' is used to mock the connection handler
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Patch overrides the 'getitem()' fn. with the below mock behaviour
            gi.return_value = True
            # 'wait_for_db' is the name of management command
            call_command('wait_for_db')
            # Assertion: check for the get item is called only once/not
            self.assertEqual(gi.call_count, 1)

    # Test 2
    @patch('time.sleep', return_value=True)  # mocks the sleep fn.
    def test_wait_for_db(self, ts):  # 'ts' for ret. value of patch
        """Test waiting for DB"""
        # The management command delays(1sec) execution-if there is oper. Error
        # then tries again, to remove that delay(in test) patch decorator added
        # it replaces the beahaviour of 'time.sleep' and replaces with a mock
        # function returnes 'True'.(ie. no waiting in testing, speed up things)
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # Instead of return_value --> side effect[ useful option in
            # python.unittest.Mark module, allows one to set a side effect in
            # the mocking function]..
            # The mocking(fr'wait_for_db') is done like,The side effect try to
            # connect DB 5 times(fails and raise Op. err.)--> 6th time> sucess
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            # Assert the fn. is get called 6 times
            self.assertEqual(gi.call_count, 6)
