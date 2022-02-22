from .base import BaseClient
from ..utils import LazyLog
from ..debug import register_redactions_from_response

import json


class Client(BaseClient):
    def _get_request(self, path, params):
        self.ensure_updated_refresh_token()

        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req %s: GET to %s, params=%s',
                req_num, dest, LazyLog(lambda: json.dumps(params, indent=4)))

        resp = self.session.get(dest, params=params)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp

    def _post_request(self, path, data):
        self.ensure_updated_refresh_token()

        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req %s: POST to %s, json=%s',
            req_num, dest, LazyLog(lambda: json.dumps(data, indent=4)))

        resp = self.session.post(dest, json=data)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp

    def _put_request(self, path, data):
        self.ensure_updated_refresh_token()

        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req %s: PUT to %s, json=%s',
            req_num, dest, LazyLog(lambda: json.dumps(data, indent=4)))

        resp = self.session.put(dest, json=data)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp

    def _patch_request(self, path, data):
        self.ensure_updated_refresh_token()

        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req %s: PATCH to %s, json=%s',
                req_num, dest, LazyLog(lambda: json.dumps(data, indent=4)))

        resp = self.session.patch(dest, json=data)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp

    def _delete_request(self, path):
        self.ensure_updated_refresh_token()

        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req %s: DELETE to %s'.format(req_num, dest))

        resp = self.session.delete(dest)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp
