"""Docsie Workflow Builder client: one file, standard library only.

Works on your machine, in CI and inside Docsie Python steps. Reads DOCSIE_WORKFLOW_URL and
DOCSIE_WORKFLOW_TOKEN from the environment.
"""
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, build_opener, HTTPRedirectHandler
from urllib.parse import urlsplit


class DocsieError(Exception):
    """A refused or invalid call: status is the HTTP code, message is Docsie's reason."""

    def __init__(self, status, message):
        super().__init__(f'{status}: {message}')
        self.status, self.message = status, message


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class Docsie:
    def __init__(self, url=None, token=None):
        self.url = (url or os.environ['DOCSIE_WORKFLOW_URL']).rstrip('/')
        parsed = urlsplit(self.url)
        if (parsed.scheme != 'https' and not (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1'))
                or parsed.username or parsed.password or parsed.query or parsed.fragment):
            raise ValueError('Use an HTTPS gateway URL (HTTP is allowed only for local development)')
        self.token = token or os.environ['DOCSIE_WORKFLOW_TOKEN']
        self.opener = build_opener(_NoRedirect)

    def call(self, method, **arguments):
        if not method or any(c not in 'abcdefghijklmnopqrstuvwxyz_.' for c in method):
            raise ValueError('Invalid Docsie method name')
        request = Request(self.url + '/methods/' + method + '/', json.dumps(arguments).encode(),
                          {'Authorization': 'Bearer ' + self.token, 'Content-Type': 'application/json'})
        try:
            with self.opener.open(request, timeout=60) as response:
                raw = response.read(12 * 1024 * 1024 + 1)
        except HTTPError as error:
            # Surface Docsie's reason ("Resource is outside this credential grant") instead of a bare status.
            try:
                detail = json.loads(error.read(65536)).get('message', '')
            except ValueError:
                detail = ''
            raise DocsieError(error.code, detail or error.reason) from None
        if len(raw) > 12 * 1024 * 1024:
            raise ValueError('Docsie response exceeded the SDK limit')
        return json.loads(raw)['result']
