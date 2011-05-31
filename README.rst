yametrikapy
===========

The library support only JSON format.

Sign in via login and password, code or token.

To sign in you need client_id, get it from http://api.yandex.ru/oauth/doc/dg/tasks/register-client.xml for your application.

Example usage
-------------

::

    #!/usr/bin/env python
    # -*- coding: UTF-8 -*-

    from yametrikapy import Metrika

    def main():
        client_id = '6993a3cd88e34ac686504790c7fe341c'
        login = ''
        password = ''

        metrika = Metrika(client_id, login, password)

        counters = metrika.GetCounterList().counters
        print counters

        # output obtained data
        print metrika.GetData()

    if __name__ == '__main__':
        main()