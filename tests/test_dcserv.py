import numpy as np

from helper import get_api


def test_access_public_data():
    api = get_api()
    res = api.get("dcserv",
                  id="fb719fb2-bd9f-817a-7d70-f4002af916f0",
                  query="valid")
    assert res is True


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
