from unittest.mock import patch
from django.core.management import call_command
from django.db.utils import OperationalError
from django.test import TestCase


class CommandTests(TestCase):
    """ Test db connection behavior.
    Test waiting for db when db is available"""

    def test_wait_for_db_ready(self):
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            gi.return_value = True
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 1)

    # decorating with patch, you pass in return value
    # as part of the function call
    @patch('time.sleep', return_value=True)
    def test_wait_for_db(self, ts):
        """Test waiting for db Check to see if ConnectionHandler raises an operation error"""
        with patch('django.db.utils.ConnectionHandler.__getitem__') as gi:
            # first 5 times the error is raised. 6th time is true
            gi.side_effect = [OperationalError] * 5 + [True]
            call_command('wait_for_db')
            self.assertEqual(gi.call_count, 6)
