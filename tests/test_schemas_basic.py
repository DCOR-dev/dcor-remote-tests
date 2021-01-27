import pathlib

import pytest

from dcoraid.dbmodel.model_api import CKANAPI
from dcoraid import upload

from helper import SERVER, get_api_key, make_dataset_dict

data_path = pathlib.Path(__file__).parent / "data"


def test_create_dataset():
    """All logged-in users should be able to create circles and datasets"""
    # create some metadata
    dataset_dict = make_dataset_dict()
    # post dataset creation request
    data = upload.create_dataset(dataset_dict=dataset_dict,
                                 server=SERVER,
                                 api_key=get_api_key(),
                                 create_circle=True,
                                 activate=False)
    # simple test
    assert "authors" in data
    assert data["authors"] == dataset_dict["authors"]
    # A dataset is considered to be a draft when it does not contain resources
    assert data["state"] == "draft"
    # make sure it really worked
    api = CKANAPI(server=SERVER, api_key=get_api_key())
    data2 = api.get("package_show", id=data["id"])
    assert "authors" in data2
    assert data2["authors"] == dataset_dict["authors"]
    assert data2["state"] == "draft"


def test_create_dataset_fail_activate_without_resource():
    # create some metadata
    dataset_dict = make_dataset_dict()
    # post dataset creation request
    with pytest.raises((ValueError, AssertionError)):
        upload.create_dataset(dataset_dict=dataset_dict,
                              server=SERVER,
                              api_key=get_api_key(),
                              create_circle=True,
                              activate=True)


def test_create_dataset_with_resource():
    # create some metadata
    dataset_dict = make_dataset_dict()
    # post dataset creation request
    data = upload.create_dataset(dataset_dict=dataset_dict,
                                 server=SERVER,
                                 api_key=get_api_key(),
                                 create_circle=True)

    upload.add_resource(dataset_id=data["id"],
                        path=data_path / "calibration_beads_47.rtdc",
                        server=SERVER,
                        api_key=get_api_key(),
                        )

    upload.activate_dataset(dataset_id=data["id"],
                            server=SERVER,
                            api_key=get_api_key())


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
