import functools
import inspect
import os
import pathlib
import time

from dcoraid.api import CKANAPI, create_dcor_dev_user, is_valid_api_key


SERVER = "dcor-dev.mpl.mpg.de"


def get_api():
    api = CKANAPI(server=SERVER, api_key=get_api_key(), ssl_verify=True)
    return api


@functools.lru_cache
def get_api_key():
    """Return the API key of the test user

    The API key is taken from the `DCOR_API_KEY` environment variable.
    If that is not set, the key stored in the file `tests/api_key` is
    used. If that file does not exist or the key is invalid (users on
    DCOR-dev are purged regularly), a new user is created on DCOR-dev
    and its API key is written to `tests/api_key`.
    """
    key = os.environ.get("DCOR_API_KEY")
    if not key:
        kp = pathlib.Path(__file__).parent / "api_key"
        if kp.exists():
            key = kp.read_text().strip()
        if not is_valid_api_key(server=SERVER, api_key=key):
            key = create_dcor_dev_user(server=SERVER,
                                       fullname="DCOR remote tester")
            kp.write_text(key)
    return key


@functools.lru_cache
def get_user_name():
    """Return the name of the test user"""
    return get_api().get_user_dict()["name"]


def make_dataset_dict(circle=None, hint=None):
    """Generate a test dataset in a test circle

    Parameters
    ----------
    circle: str or None
        circle name; if None, the calling functions module is used,
        prefixed with the name of the test user (circle names are
        unique on DCOR and test users are created on the fly)
    hint: str
        descriptive dataset title string; if None, the calling function
        is used; the time since the epoch is added to the dataset title
    """
    # Default variables
    if hint is None:
        hint = "test " + inspect.currentframe().f_back.f_code.co_name
    if circle is None:
        filename = inspect.currentframe().f_back.f_code.co_filename
        module = filename.split("/")[-1].rsplit(".", 1)[0]
        circle = f"{get_user_name()}-{module}".replace("_", "-")
    dataset_dict = {
        "title": "{} {}".format(hint, time.time()),
        "private": True,
        "license_id": "CC0-1.0",
        "owner_org": circle,
        "authors": "Guybrush Ulysses Threepwood",
    }
    return dataset_dict
