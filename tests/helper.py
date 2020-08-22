import inspect
import os
import pathlib
import time

SERVER = "dcor-dev.mpl.mpg.de"


def get_api_key():
    key = os.environ.get("DCOR_API_KEY")
    if not key:
        # local file
        kp = pathlib.Path(__file__).parent / "api_key"
        if not kp.exists():
            raise ValueError("No DCOR_API_KEY variable or api_key file!")
        key = kp.read_text().strip()
    return key


def make_dataset_dict(circle=None, hint=None):
    """Generate a test dataset in a test circle

    Parameters
    ----------
    circle: str or None
        circle name; if None, the calling functions module is used
    hint: str
        descriptive dataset title string; if None, the calling function
        is used; the time since the epoch is added to the dataset title
    """
    # Default variables
    if hint is None:
        hint = "test " + inspect.currentframe().f_back.f_code.co_name
    if circle is None:
        filename = inspect.currentframe().f_back.f_code.co_filename
        circle = filename.split("/")[-1].rsplit(".", 1)[0]
    dataset_dict = {
        "title": "{} {}".format(hint, time.time()),
        "private": True,
        "license_id": "CC0-1.0",
        "owner_org": circle,
        "authors": "Guybrush Ulysses Threepwood",
    }
    return dataset_dict
