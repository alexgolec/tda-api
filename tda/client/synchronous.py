from .base import BaseClient
from ..debug import register_redactions_from_response

import json


class Client(BaseClient):
    def _get_request(self, path, params):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req {}: GET to {}, params={}'.format(
            req_num, dest, json.dumps(params, indent=4)))

        resp = self.session.get(dest, params=params)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp

    def _post_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req {}: POST to {}, json={}'.format(
            req_num, dest, json.dumps(data, indent=4)))

        resp = self.session.post(dest, json=data)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp

    def _put_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req {}: PUT to {}, json={}'.format(
            req_num, dest, json.dumps(data, indent=4)))

        resp = self.session.put(dest, json=data)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp

    def _patch_request(self, path, data):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req {}: PATCH to {}, json={}'.format(
            req_num, dest, json.dumps(data, indent=4)))

        resp = self.session.patch(dest, json=data)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp

    def _delete_request(self, path):
        dest = 'https://api.tdameritrade.com' + path

        req_num = self._req_num()
        self.logger.debug('Req {}: DELETE to {}'.format(req_num, dest))

        resp = self.session.delete(dest)
        self._log_response(resp, req_num)
        register_redactions_from_response(resp)
        return resp
