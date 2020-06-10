import atexit
import io
import logging
import tda
import unittest

from tda.client import Client
from tests.test_utils import no_duplicates
from unittest.mock import ANY, MagicMock, Mock, patch


class RedactorTest(unittest.TestCase):

    def setUp(self):
        self.redactor = tda.debug.LogRedactor()

    @no_duplicates
    def test_no_redactions(self):
        self.assertEqual('test message', self.redactor.redact('test message'))

    @no_duplicates
    def test_simple_redaction(self):
        self.redactor.register('secret', 'SECRET')

        self.assertEqual(
            '<REDACTED SECRET> message',
            self.redactor.redact('secret message'))

    @no_duplicates
    def test_multiple_registrations_same_string(self):
        self.redactor.register('secret', 'SECRET')
        self.redactor.register('secret', 'SECRET')

        self.assertEqual(
            '<REDACTED SECRET> message',
            self.redactor.redact('secret message'))

    @no_duplicates
    def test_multiple_registrations_same_string_different_label(self):
        self.redactor.register('secret-A', 'SECRET')
        self.redactor.register('secret-B', 'SECRET')

        self.assertEqual(
            '<REDACTED SECRET-1> message <REDACTED SECRET-2>',
            self.redactor.redact('secret-A message secret-B'))


class RegisterRedactionsTest(unittest.TestCase):

    def setUp(self):
        self.captured = io.StringIO()
        self.logger = logging.getLogger('test')
        self.dump_logs = tda.debug.enable_bug_report_logging(
            output=self.captured, loggers=[self.logger])

    @no_duplicates
    def test_empty_string(self):
        tda.debug.register_redactions('')

    @no_duplicates
    def test_empty_dict(self):
        tda.debug.register_redactions({})

    @no_duplicates
    def test_empty_list(self):
        tda.debug.register_redactions([])

    @no_duplicates
    def test_dict(self):
        tda.debug.register_redactions(
            {'accountId': '100001'},
            bad_patterns=['id'])
        tda.debug.register_redactions(
            {'otherAccountId': '200002'},
            bad_patterns=['id'])

        self.logger.info('Account ID: 100001')
        self.logger.info('Other Account ID: 200002')

        self.dump_logs()
        self.assertRegex(
            self.captured.getvalue(),
            r'\[.*\] Account ID: <REDACTED accountId>\n' +
            r'\[.*\] Other Account ID: <REDACTED otherAccountId>\n')

    @no_duplicates
    def test_list_of_dict(self):
        tda.debug.register_redactions(
            [{'accountId': '100001'}, {'otherAccountId': '200002'}],
            bad_patterns=['id'])

        self.logger.info('Account ID: 100001')
        self.logger.info('Other Account ID: 200002')

        self.dump_logs()
        self.assertRegex(
            self.captured.getvalue(),
            r'\[.*\] Account ID: <REDACTED accountId>\n' +
            r'\[.*\] Other Account ID: <REDACTED otherAccountId>\n')
