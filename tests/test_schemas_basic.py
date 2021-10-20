import pathlib
import time

import pytest
import requests

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


def test_package_revise_update_resource_not_allowed_draft():
    """only editing "description" is allowed"""
    api = get_api()
    dataset_dict = make_dataset_dict()
    data = dataset.dataset_create(dataset_dict=dataset_dict,
                                  api=api,
                                  create_circle=True)
    dataset.resource_add(dataset_id=data["id"],
                         path=data_path / "calibration_beads_47.rtdc",
                         api=api,
                         )

    # this should work
    req = requests.post(
        api.api_url + "package_revise",
        data={"match__id": data["id"],
              "update__resources__-1": '{"description": "new description"}',
              },
        headers=api.headers)
    assert req.ok

    # make sure that worked
    pkg_dict = api.get("package_show", id=data["id"])
    assert pkg_dict["resources"][0]["description"] == "new description"

    # wait until the background jobs finished
    for ii in range(60):
        pkg_dict = api.get("package_show", id=data["id"])
        if "dc:setup:flow rate" in pkg_dict["resources"][0]:
            break
        else:
            time.sleep(1)
    else:
        assert False, "background jobs did not run for 60s!"

    # this must not work
    req = requests.post(
        api.api_url + "package_revise",
        data={"match__id": data["id"],
              "update__resources__-1": '{"dc:setup:flow rate": 0.123}',
              },
        headers=api.headers)
    assert not req.ok
    error = req.json()["error"]
    assert "Editing not allowed" in error["message"]

    # make sure that it didn't work
    pkg_dict = api.get("package_show", id=data["id"])
    assert pkg_dict["resources"][0]["dc:setup:flow rate"] != 0.123

    # for active datasets, we should not be able to edit the description
    dataset.dataset_activate(dataset_id=data["id"],
                             api=get_api())

    req = requests.post(
        api.api_url + "package_revise",
        data={"match__id": data["id"],
              "update__resources__-1": '{"description": "two description"}',
              },
        headers=api.headers)
    assert not req.ok
    error = req.json()["error"]
    assert "not allowed for non-draft" in error["message"]

    # make sure that it didn't work
    pkg_dict = api.get("package_show", id=data["id"])
    assert pkg_dict["resources"][0]["description"] == "new description"


def test_package_revise_upload_not_allowed_active_dataset():
    # create some metadata
    api = get_api()
    dataset_dict = make_dataset_dict()
    data = dataset.dataset_create(dataset_dict=dataset_dict,
                                  api=api,
                                  create_circle=True)
    dataset.resource_add(dataset_id=data["id"],
                         path=data_path / "calibration_beads_47.rtdc",
                         api=api,
                         )
    dataset.dataset_activate(dataset_id=data["id"],
                             api=get_api())
    # now try to add a resource with package_revise
    path = data_path / "calibration_beads_47.rtdc"
    with path.open("rb") as fd:
        req = requests.post(
            api.api_url + "package_revise",
            data={"match__id": data["id"],
                  "update__resources__extend": '[{"name":"peter.rtdc"}]',
                  },
            files=[("update__resources__-1__upload", ("peter.rtdc", fd))],
            headers=api.headers)
    assert not req.ok
    assert not req.json()["success"]
    error = req.json()["error"]
    assert "resources to non-draft datasets not allowed" in error["message"]
    pkg_data = api.get("package_show", id=data["id"])
    assert len(pkg_data["resources"]) == 1


def test_package_revise_delete_not_allowed_active_dataset():
    # create some metadata
    api = get_api()
    dataset_dict = make_dataset_dict()
    data = dataset.dataset_create(dataset_dict=dataset_dict,
                                  api=api,
                                  create_circle=True)
    dataset.resource_add(dataset_id=data["id"],
                         path=data_path / "calibration_beads_47.rtdc",
                         api=api,
                         )
    dataset.resource_add(dataset_id=data["id"],
                         path=data_path / "calibration_beads_47.rtdc",
                         resource_name="peter.rtdc",
                         api=api,
                         )
    dataset.dataset_activate(dataset_id=data["id"],
                             api=get_api())
    # now try to delete a resource with package_revise
    req = requests.post(
        api.api_url + "package_revise",
        data={"match__id": data["id"],
              "filter": ["-resources__1"],
              },
        headers=api.headers)

    assert not req.ok
    assert not req.json()["success"]
    error = req.json()["error"]
    assert "Changing 'resources' not allowed" in error["message"]
    pkg_data = api.get("package_show", id=data["id"])
    assert len(pkg_data["resources"]) == 2


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
