yametrikapy
===========

The library support only JSON format.

To sign in you need client_id, get it from https://tech.yandex.ru/oauth/doc/dg/tasks/register-client-docpage/ for your application.

To connect to Yandex.Metric, you need to get a code:

- `The token by code received automatically <https://tech.yandex.ru/oauth/doc/dg/reference/auto-code-client-docpage/>`_
- `The token by code entered by a user <https://tech.yandex.ru/oauth/doc/dg/reference/console-client-docpage/>`_

.. code-block:: python

    client_id = '6993a3cd88e34ac67574578th87h67r7fe341c'
    client_secret = 'AQAg4h45h4DJk4545gBDqIln6hNJGet45DHJgVxCjncQ'
    code = '3463468'

    metrika = Metrika(client_id, client_secret=client_secret, code=code)

or `to obtain a debug token manually <https://tech.yandex.ru/oauth/doc/dg/tasks/get-oauth-token-docpage/>`_.

.. code-block:: python

    client_id = '6993a3cd88e34ac67574578th87h67r7fe341c'
    token = 'AQAg4h45h4DJk4545gBDqIln6hNJGet45DHJgVxCjncQ'

    metrika = Metrika(client_id, token=token)

Installation
------------
::

    pip install yametrikapy

Example usage
-------------

.. code-block:: python

    from yametrikapy import Metrika

    def main():
        client_id = '6993a3cd88e34ac67574578th87h67r7fe341c'
        client_secret = 'AQAg4h45h4DJk4545gBDqIln6hNJGet45DHJgVxCjncQ'
        code = '3463468'

        metrika = Metrika(client_id, client_secret=client_secret, code=code)

        counters = metrika.counters().counters
        print(counters)

        counter_id = counters[0]['id']
        stat = metrika.stat_data(counter_id, 'ym:s:visits,ym:s:users', dimensions='ym:s:searchEngineName')
        print(stat.data)

        counter = metrika.add_counter('My new counter', 'my-site.ru')
        print(counter.counter['id'], counter.counter['name'])

        # Output obtained data
        print metrika.get_data()

    if __name__ == '__main__':
        main()
