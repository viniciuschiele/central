********************************************
Central
********************************************
Central is a configuration library for Python inspirited by `Netflix Archaius <https://github.com/Netflix/archaius>`_
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
using Central you can do it without having to restart your application.

.. code-block:: python

    import requests
    import requests.adapters

    from central.config import FileConfig
    from central.property import PropertyManager

    config = FileConfig('./config.json').reload_every(60000)
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

    $ pip install central


Requirements
==========

- Python >= 2.7 or >= 3.4

Central has no external dependencies outside of the Python standard library.

Roadmap
==========
- Add documentation
- Add support for reload on change to file configuration
- Add possibility to customize composition
- Add Cassandra as a configuration source
- Add Database as a configuration source
- Add DynamoDB as a configuration source
- Add MongoDB as a configuration source
- Add Redis as a configuration source

License
==========
MIT licensed. See the bundled `LICENSE <https://github.com/viniciuschiele/central/blob/master/LICENSE>`_ file for more details.


.. |Coverage| image:: https://codecov.io/github/viniciuschiele/central/coverage.svg
    :target: https://codecov.io/github/viniciuschiele/central

.. |Travis| image:: https://travis-ci.org/viniciuschiele/central.svg
    :target: https://travis-ci.org/viniciuschiele/central
