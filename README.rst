DCOR remote tests
=================

|Tests Status|

Test DCOR functionality remotely (i.e. from a user's point of view).
The tests are run regularly on travis-ci.com.


Running the tests
-----------------
You need to have Python 3 installed. You may define the environment variable
`DCOR_API_KEY` or create the file `api_key` containing your API key in the
`tests` directory. Otherwise, a test user is created automatically on DCOR-dev
and its API key is stored in `tests/api_key`. Then run:

::

    pip install -r requirements
    py.test tests

Note that all users, datasets, collections, and circles on DCOR-dev are
purged regularly.


.. |Tests Status| image:: https://img.shields.io/github/actions/workflow/status/DCOR-dev/dcor-remote-tests/check.yml
   :target: https://github.com/DCOR-dev/dcor-remote-tests/actions?query=workflow%3AChecks

