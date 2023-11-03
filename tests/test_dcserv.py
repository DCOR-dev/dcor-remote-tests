import pathlib

import pytest
import time

import numpy as np
import requests

import dclab
from dclab.rtdc_dataset.fmt_http import HTTPBasin
from dcoraid.api import dataset

from helper import get_api, make_dataset_dict

data_path = pathlib.Path(__file__).parent / "data"


def test_access_public_data():
    api = get_api()
    res = api.get("dcserv",
                  id="fb719fb2-bd9f-817a-7d70-f4002af916f0",
                  query="valid")
    assert res is True


def test_access_private_data():
    """Upload a private dataset and try to access it"""
    # create some metadata
    dataset_dict = make_dataset_dict()
    dataset_dict["private"] = True
    # post dataset creation request
    api = get_api()
    data = dataset.dataset_create(dataset_dict=dataset_dict,
                                  api=api,
                                  create_circle=True)
    dataset.resource_add(dataset_id=data["id"],
                         path=data_path / "calibration_beads_47.rtdc",
                         api=get_api(),
                         )
    dataset.dataset_activate(dataset_id=data["id"],
                             api=get_api())
    data2 = api.get("package_show", id=data["id"])
    assert data2["private"]
    res_id = data2["resources"][0]["id"]

    # Wait until all background jobs are successful
    for ii in range(120):
        # metadata
        res_dict = api.get("resource_show", id=res_id)
        if "dc:experiment:event count" in res_dict:
            # migration to S3
            if "s3_url" in res_dict:
                # check URL for condensed dataset
                curl = (f"{api.server}/dataset/{data['id']}"
                        f"/resource/{res_id}/condensed.rtdc")
                resp = requests.get(curl,
                                    stream=True,
                                    headers={"authorization": api.api_key})
                if resp.ok:
                    break
        time.sleep(.5)
    else:
        assert False, "Metadata not computed in background job!"

    # Can we access the resource?
    avail = api.get("dcserv", id=res_id, query="valid")
    assert avail is True

    # Can we get the feature list (version 1)?
    features = api.get("dcserv", id=res_id, query="feature_list&version=1")
    assert "deform" in features
    assert len(features) >= 36

    # Feature list for version 2 should be empty
    features2 = api.get("dcserv", id=res_id, query="feature_list&version=2")
    assert not features2

    # But we should still be able to get the feature data when we access
    # it with dclab.
    with dclab.new_dataset(res_id,
                           host=api.server,
                           api_key=api.api_key,
                           dcserv_api_version=2) as ds:
        # We should have HTTP basins
        assert len(ds.basins) == 2
        b1, b2 = ds.basins
        assert isinstance(b1, HTTPBasin)
        assert isinstance(b2, HTTPBasin)
        assert b1.is_available()
        assert b2.is_available()
        assert np.allclose(ds["deform"][0],
                           0.011666297,
                           atol=0, rtol=1e-5)

    # Try to access the private dataset as a public user
    with pytest.raises(dclab.rtdc_dataset.fmt_dcor.api.DCORAccessError):
        dclab.new_dataset(res_id, host=api.server, dcserv_api_version=2)


def test_access_public_data_features():
    api = get_api()

    # deformation
    res = api.get("dcserv",
                  id="fb719fb2-bd9f-817a-7d70-f4002af916f0",
                  query="feature",
                  feature="deform")
    deform = np.asarray(res)
    assert np.allclose(deform[0],
                       0.009741938672959805,
                       atol=0,
                       rtol=1e-10
                       )

    # volume (ancillary feature from condensed part)
    res2 = api.get("dcserv",
                   id="fb719fb2-bd9f-817a-7d70-f4002af916f0",
                   query="feature",
                   feature="volume")
    volume = np.asarray(res2)
    assert np.allclose(volume[0],
                       112.7559351790568,
                       atol=0,
                       rtol=1e-10
                       )
