from dcoraid.dbmodel.model_api import CKANAPI
from dcoraid.upload import create_dataset

from helper import SERVER, get_api_key, make_dataset_dict


def test_create_dataset():
    """All logged-in users should be able to create circles and datasets"""
    # create some metadata
    dataset_dict = make_dataset_dict()
    # post dataset creation request
    data = create_dataset(dataset_dict=dataset_dict,
                          server=SERVER,
                          api_key=get_api_key(),
                          create_circle=True,
                          activate=True)
    # simple test
    assert "authors" in data
    assert data["authors"] == dataset_dict["authors"]
    assert data["state"] == "active"
    # make sure it really worked
    api = CKANAPI(server=SERVER, api_key=get_api_key())
    data2 = api.get("package_show", id=data["id"])
    assert "authors" in data2
    assert data2["authors"] == dataset_dict["authors"]
    assert data2["state"] == "active"


if __name__ == "__main__":
    # Run all tests
    loc = locals()
    for key in list(loc.keys()):
        if key.startswith("test_") and hasattr(loc[key], "__call__"):
            loc[key]()
