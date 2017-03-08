********************************************
configd
********************************************
configd is a configuration library for Python inspirited by `Netflix Archaius <https://github.com/Netflix/archaius>`_
that provides APIs to access and utilize properties that can change dynamically at runtime.

|Coverage| |Travis|

Features
===============
- Read configuration from anywhere (Env variables, File system, web services, S3, ...) using a single interface
- Auto configuration reload, no longer need to restart your application to fetch new configurations
- Dynamic properties where the values are of specific types and can change at runtime
- Composite configurations with ordered hierarchy for applications willing to use convention based configuration locations

Quick Start
==========
Assuming you are using requests library to access an external web service,
you may want to change the max number of connections to tune your application,
using configd you can do it without having to restart your application.

.. code-block:: python

    import requests
    import requests.adapters

    from configd.config import FileConfig
    from configd.property import PropertyManager

    config = FileConfig('./config.json').polling(60000)
    config.load()

    properties = PropertyManager(config)
    pool_maxsize = properties.get_property('pool_maxsize').as_int(5)

    adapter = requests.adapters.HTTPAdapter(pool_maxsize=pool_maxsize.get())
    session = requests.Session()
    session.mount('http://', adapter)


    @pool_maxsize.on_updated
    def pool_maxsize_updated(value):
        adapter = requests.adapters.HTTPAdapter(pool_maxsize=value)
        session.mount('http://', adapter)


    response = session.get('http://date.jsontest.com')


Get It Now
==========

::

    $ pip install configd


Requirements
==========

- Python >= 2.7 or >= 3.4

configd has no external dependencies outside of the Python standard library.

Roadmap
==========
- Add documentation
- Add support for reload on change to file configuration
- Add more unit tests and make coverage >= 90%
- Add Cassandra as a configuration source
- Add Database as a configuration source
- Add DynamoDB as a configuration source
- Add MongoDB as a configuration source
- Add Redis as a configuration source

License
==========
MIT licensed. See the bundled `LICENSE <https://github.com/viniciuschiele/configd/blob/master/LICENSE>`_ file for more details.


.. |Coverage| image:: https://codecov.io/github/viniciuschiele/configd/coverage.svg
    :target: https://codecov.io/github/viniciuschiele/configd

.. |Travis| image:: https://travis-ci.org/viniciuschiele/configd.svg
    :target: https://travis-ci.org/viniciuschiele/configd
