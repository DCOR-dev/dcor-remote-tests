DCOR remote tests
=================

|Tests Status|

Test DCOR functionality remotely (i.e. from a user's point of view).
The tests are run regularly on travis-ci.com.


Running the tests
-----------------
You need to have Python 3 installed. Either define the environment variable
`DCOR_API_KEY` or create the file `api_key` containing your API key in the
`tests` directory. Then run:

::

    pip install -r requirements
    py.test tests

Note that datasets, collections, and circles created during testing are
only purged for registered testing users (e.g. "remote_tester").


.. |Tests Status| image:: https://img.shields.io/travis/DCOR-dev/DCOR-remote-tests.svg?label=tests
   :target: https://travis-ci.com/DCOR-dev/DCOR-remote-tests

