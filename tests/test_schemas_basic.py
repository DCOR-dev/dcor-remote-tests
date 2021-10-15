import pathlib

import pytest

import dcoraid
from dcoraid.api import dataset

from helper import get_api, make_dataset_dict

data_path = pathlib.Path(__file__).parent / "data"


def test_dataset_create():
    """All logged-in users should be able to create circles and datasets"""
    # create some metadata
    dataset_dict = make_dataset_dict()
    # post dataset creation request
    api = get_api()
    data = dataset.dataset_create(dataset_dict=dataset_dict,
                                  api=api,
                                  create_circle=True,
                                  activate=False)
    # simple test
    assert "authors" in data
    assert data["authors"] == dataset_dict["authors"]
    # A dataset is considered to be a draft when it does not contain resources
    assert data["state"] == "draft"
    # make sure it really worked
    data2 = api.get("package_show", id=data["id"])
    assert "authors" in data2
    assert data2["authors"] == dataset_dict["authors"]
    assert data2["state"] == "draft"


def test_dataset_create_public():
    """All logged-in users should be able to create circles and datasets"""
    # create some metadata
    dataset_dict = make_dataset_dict()
    dataset_dict["private"] = False
    # post dataset creation request
    api = get_api()
    data = dataset.dataset_create(dataset_dict=dataset_dict,
                                  api=api,
                                  create_circle=True)
    dataset.resource_add(dataset_id=data["id"],
                         path=data_path / "calibration_beads_47.rtdc",
                         api=get_api(),
                         )
    data2 = api.get("package_show", id=data["id"])
    assert not data2["private"]
    dataset.dataset_activate(dataset_id=data["id"],
                             api=get_api())


def test_dataset_create_fail_activate_without_resource():
    # create some metadata
    dataset_dict = make_dataset_dict()
    # post dataset creation request
    with pytest.raises(dcoraid.api.APIConflictError):
        dataset.dataset_create(dataset_dict=dataset_dict,
                               api=get_api(),
                               create_circle=True,
                               activate=True)


def test_dataset_create_with_resource():
    # create some metadata
    dataset_dict = make_dataset_dict()
    # post dataset creation request
    data = dataset.dataset_create(dataset_dict=dataset_dict,
                                  api=get_api(),
                                  create_circle=True)

    dataset.resource_add(dataset_id=data["id"],
                         path=data_path / "calibration_beads_47.rtdc",
                         api=get_api(),
                         )

    dataset.dataset_activate(dataset_id=data["id"],
                             api=get_api())


def test_delete_dataset_forbidden():
    # create some metadata
    dataset_dict = make_dataset_dict()
    # post dataset creation request
    data = dataset.dataset_create(dataset_dict=dataset_dict,
                                  api=get_api(),
                                  create_circle=True)

    dataset.resource_add(dataset_id=data["id"],
                         path=data_path / "calibration_beads_47.rtdc",
                         api=get_api(),
                         )

    dataset.dataset_activate(dataset_id=data["id"],
                             api=get_api())

    with pytest.raises(dcoraid.api.APIAuthorizationError):
        dataset.dataset_draft_remove(dataset_id=data["id"],
                                     api=get_api())


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
