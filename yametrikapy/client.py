# coding: utf-8

from os.path import basename
import gzip
import time
from http import client as httplib
from http.client import ResponseNotReady
from urllib.parse import urlencode, urlparse
from io import BytesIO


class UnsupportedScheme(httplib.HTTPException):
    pass


class APIClient(object):
    debug = False

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ru,en-us;q=0.7,en;q=0.3',
        'Accept-Encoding': 'deflate',
        'Accept-Charset': 'utf-8;q=0.7,*;q=0.7',
        'Keep-Alive': '300',
        'Connection': 'keep-alive'
    }

    def __init__(self):
        self.status = 0
        self.reason = ''

    @property
    def user_agent(self):
        return self.HEADERS['User-Agent']

    @user_agent.setter
    def user_agent(self, user_agent):
        self.HEADERS['User-Agent'] = user_agent

    def _get_scheme(self, uri):
        if not uri.scheme or (uri.scheme == 'http'):
            return 'http'
        elif uri.scheme == 'https':
            return 'https'

        raise UnsupportedScheme('"%s" is not supported.' % uri.scheme)

    def _get_port(self, uri):
        host = ''
        port = None

        host_parts = uri.netloc.split(':')

        if host_parts[0]:
            host = host_parts[0]

        if len(host_parts) > 1:
            port = int(host_parts[1])
            if not port:
                port = None

        return host, port

    def _get_connection(self, uri):
        """Open a socket connection to the server to set up an HTTP request.

        Args:
          uri: The full URL for the request as a Uri object.
        """
        scheme = self._get_scheme(uri)
        host, port = self._get_port(uri)

        if scheme == 'https':
            return httplib.HTTPSConnection(host, port=port)

        return httplib.HTTPConnection(host, port)

    def _gunzip(self, stream):
        gz = gzip.GzipFile(fileobj=BytesIO(stream))
        return gz.read()

    def urlencode(self, **kwargs):
        return urlencode(kwargs)

    def get_header(self, key, default=''):
        if self.headers is None:
            raise ResponseNotReady()

        headers = self.headers.get_all(key) or default
        if isinstance(headers, str) or not hasattr(headers, '__iter__'):
            return headers

        return ', '.join(headers)

    def _encode_multipart(self, f):
        """ Build a multipart/form-data body with generated random boundary

        :param f: file-like object
        :return: str
        """
        filename = basename(getattr(f, 'name', 'file.csv'))

        boundary = '----------------------------%s' % hex(int(time.time() * 1000))

        data = ['--%s' % boundary]
        data.append('Content-Disposition: form-data; name="file"; filename="%s"' % filename)
        data.append('Content-Type: text/csv\r\n')
        data.append(f.read())
        data.append('--%s--' % boundary)

        return '\r\n'.join(data), boundary

    def _request(self, method, uri, params, headers):
        self.headers = None
        if isinstance(uri, str):
            uri = urlparse(uri)
        else:
            raise TypeError('Invalid URL')

        connection = self._get_connection(uri)

        if self.debug:
            connection.debuglevel = 1

        query = uri.path
        if uri.query:
            query += '?%s' % uri.query

        if (method in ('GET', 'DELETE')) and params:
            query += '?%s' % params
            params = ''

        connection.putrequest(method, query)

        # Send the HTTP headers.
        for name, value in headers.items():
            connection.putheader(name, value)

        if method in ('POST', 'PUT'):
            if getattr(params, 'read', None):
                data, boundary = self._encode_multipart(params)
                if 'Content-type' not in headers:
                    connection.putheader('Content-type', 'multipart/form-data; boundary=%s' % boundary)
                if 'Content-length' not in headers:
                    connection.putheader('Content-length', str(len(data)))
                params = data
            else:
                if 'Content-type' not in headers:
                    connection.putheader('Content-type', 'application/x-yametrika+json')
                if 'Content-length' not in headers:
                    connection.putheader('Content-length', str(len(params)))

        connection.endheaders()

        if params:
            connection.send(params.encode())

        return connection.getresponse()

    def request(self, method, url, params=None, headers=None):
        if not headers:
            headers = self.HEADERS

        if params and isinstance(params, dict):
            params = self.urlencode(**params)

        with self._request(method, url, params or '', headers) as _response:
            self.status = _response.status
            self.reason = _response.reason
            self.headers = _response.headers

            page = _response.read()

            s = self.get_header('Content-Encoding')
            if s and (s.find('gzip') > -1):
                page = self._gunzip(page)

            return page
