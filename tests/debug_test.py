import atexit
import io
import json
import logging
import tda
import unittest

from tda.client import Client
from .utils import MockResponse, no_duplicates
from unittest.mock import Mock, patch


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
        self.dump_logs = tda.debug._enable_bug_report_logging(
            output=self.captured, loggers=[self.logger])
        tda.LOG_REDACTOR = tda.debug.LogRedactor()

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
            {'BadNumber': '100001'},
            bad_patterns=['bad'])
        tda.debug.register_redactions(
            {'OtherBadNumber': '200002'},
            bad_patterns=['bad'])

        self.logger.info('Bad Number: 100001')
        self.logger.info('Other Bad Number: 200002')

        self.dump_logs()
        self.assertRegex(
            self.captured.getvalue(),
            r'\[.*\] Bad Number: <REDACTED BadNumber>\n' +
            r'\[.*\] Other Bad Number: <REDACTED OtherBadNumber>\n')

    @no_duplicates
    def test_list_of_dict(self):
        tda.debug.register_redactions(
            [{'GoodNumber': '900009'},
             {'BadNumber': '100001'},
             {'OtherBadNumber': '200002'}],
            bad_patterns=['bad'])

        self.logger.info('Good Number: 900009')
        self.logger.info('Bad Number: 100001')
        self.logger.info('Other Bad Number: 200002')

        self.dump_logs()
        self.assertRegex(
            self.captured.getvalue(),
            r'\[.*\] Good Number: 900009\n' +
            r'\[.*\] Bad Number: <REDACTED 1-BadNumber>\n' +
            r'\[.*\] Other Bad Number: <REDACTED 2-OtherBadNumber>\n')

    @no_duplicates
    def test_whitelist(self):
        tda.debug.register_redactions(
            [{'GoodNumber': '900009'},
             {'BadNumber': '100001'},
             {'OtherBadNumber': '200002'}],
            bad_patterns=['bad'],
            whitelisted=['otherbadnumber'])

        self.logger.info('Good Number: 900009')
        self.logger.info('Bad Number: 100001')
        self.logger.info('Other Bad Number: 200002')

        self.dump_logs()
        self.assertRegex(
            self.captured.getvalue(),
            r'\[.*\] Good Number: 900009\n' +
            r'\[.*\] Bad Number: <REDACTED 1-BadNumber>\n' +
            r'\[.*\] Other Bad Number: 200002\n')

    @no_duplicates
    @patch('tda.debug.register_redactions', new_callable=Mock)
    def test_register_from_request_success(self, register_redactions):
        resp = MockResponse({'success': 1}, 200)
        tda.debug.register_redactions_from_response(resp)
        register_redactions.assert_called_with({'success': 1})

    @no_duplicates
    @patch('tda.debug.register_redactions', new_callable=Mock)
    def test_register_from_request_not_okay(self, register_redactions):
        resp = MockResponse({'success': 1}, 403)
        tda.debug.register_redactions_from_response(resp)
        register_redactions.assert_not_called()

    @no_duplicates
    @patch('tda.debug.register_redactions', new_callable=Mock)
    def test_register_unparseable_json(self, register_redactions):
        class MR(MockResponse):
            def json(self):
                raise json.decoder.JSONDecodeError('e243rtdagew', '', 0)

        resp = MR({'success': 1}, 200)
        tda.debug.register_redactions_from_response(resp)
        register_redactions.assert_not_called()

class EnableDebugLoggingTest(unittest.TestCase):

    @patch('logging.Logger.addHandler')
    def test_enable_doesnt_throw_exceptions(self, _):
      try:
        tda.debug.enable_bug_report_logging()
      except AttributeError:
        self.fail("debug.enable_bug_report_logging() raised AttributeError unexpectedly")
