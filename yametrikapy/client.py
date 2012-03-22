#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#-------------------------------------------------------------------------------
# Name:        client
# Purpose:
#
# Author:      Sergey Pikhovkin (s@pikhovkin.ru)
#
# Created:     10.02.2011
# Copyright:   (c) Sergey Pikhovkin 2012
# Licence:     MIT
#-------------------------------------------------------------------------------

import gzip
import httplib
from urllib import urlencode
from urlparse import urlparse
from StringIO import StringIO


class UnsupportedScheme(httplib.HTTPException):
    pass


class APIClient(object):
    """
    """
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

    @property
    def UserAgent(self):
        return self.HEADERS['User-Agent']

    @UserAgent.setter
    def UserAgent(self, user_agent):
        self.HEADERS['User-Agent'] = user_agent

    def __init__(self):
        self.Status = int(0)
        self.Reason = str()

    def _get_scheme(self, uri):
        if not uri.scheme or (uri.scheme == 'http'):
            return 'http'
        elif uri.scheme == 'https':
            return 'https'
        else:
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
        return (host, port)

    def _get_connection(self, uri):
        """Opens a socket connection to the server to set up an HTTP request.

        Args:
          uri: The full URL for the request as a Uri object.
        """
        scheme = self._get_scheme(uri)
        host, port = self._get_port(uri)
        connection = None
        if scheme == 'https':
            connection = httplib.HTTPSConnection(host, port=port)
        else:
            connection = httplib.HTTPConnection(host, port)
        return connection

    def _gunzip(self, stream):
        gz = gzip.GzipFile(fileobj=StringIO(stream))
        return gz.read()

    def get_header(self, key, default=''):
        return self._response.getheader(key, default)

    def _http_request(self, method, uri, params='', headers={}):
        if isinstance(uri, (str, unicode)):
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
        for name, value in headers.iteritems():
            connection.putheader(name, value)

        if method in ('POST', 'PUT'):
            if 'Content-type' not in headers:
                connection.putheader('Content-type',
                    'application/x-yametrika+json')
            if 'Content-length' not in headers:
                connection.putheader('Content-length', str(len(params)))

        connection.endheaders()

        if params:
            connection.send(params)

        return connection.getresponse()

    def request(self, method, url, params={}, headers={}):
        if not headers:
            headers = self.HEADERS
        if params and isinstance(params, dict):
            params = urlencode(params)
        self._response = self._http_request(method, url, params, headers)
        self.Status = self._response.status
        self.Reason = self._response.reason

        page = self._response.read()
        s = self._response.getheader('Content-Encoding')
        if s and (s.find('gzip') > -1):
            page = self._gunzip(page)
        return page
