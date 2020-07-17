****************
Flask-Idempotent
****************
-----

Flask-Idempotent is an exceedingly simple (by design) idempotent request handler for Flask. Implemented as an extension. The original repo is using Redis as both a lock and response datastore, instead, this repo simply using memory (a dictionary variable and a new class) for even higher speed and super ease of use, this will help you add idempotency to any endpoint on your Flask application with just a few click.

============
Installation
============

.. code-block:: bash

    $ pip install flask-idempotent-memory #(Not yet available)

=====
Usage
=====

.. code-block:: python

    from flask import Flask
    from flask_idempotent-memory import Idempotent
    my_app = Flask(__name__)
    Idempotent(my_app)

.. code-block:: html

    <form>
      {{ idempotent_input() }}
      <!-- the rest of your form -->
    </form>

And thats it! (well, if the defaults work for you)

============
How it Works
============

Any request that includes **__idempotent_key** in the request arguments or post data, or **X-Idempotent-Key** in the request's headers will be tracked as a idempotent request. This only takes effect for 240 seconds by default, but this is configurable.

When the first request with a key comes in, Flask-Idempotent will attempt to get IDEMPOTENT_{KEY} in key store. If that key does not exists in key store, it will then process the request like normal and save the response in key store for future requests to return.

Any subsequent (simultaneous or otherwise) requests will not be re-process, as its response already generated and stored in key store. They will then wait for the master request to finished, retrieve the prior response and return that.

To reduce the memory usage, every time when key store being read, the key store will check the current time against the clean up interval, if it is met, the key store will delete all keys that are expired.

==================
Why should I care?
==================

You can't trust user input. Thats rule one of web development. This won't beat malicious attempts to attack your form submissions, but it will help when a user submits a page twice, or an api request is sent twice, due to network failure or otherwise. This will prevent those double submissions and any subsequent results of them.

=============
Configuration
=============

Flask-Idempotent requires Redis to function. It defaults to using redis on the local machine, and the following configuration values are available. Just set them in your flask configuration

.. code-block:: python

    # In seconds, the timeout for a secondary request to wait for the first to
    #  complete
    IDEMPOTENT_TIMEOUT = 60

    # In seconds, the amount of time to store the master response before
    #  expiration in key store
    IDEMPOTENT_EXPIRE = 240
