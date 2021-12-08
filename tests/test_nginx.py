import requests

from helper import get_api


def test_nginx_dataset_redirect():
    api = get_api()
    resp = requests.get(api.server + "/89bf2177-ffeb-9893-83cc-b619fc2f6663")
    assert resp.ok
    assert resp.url == \
           "https://dcor-dev.mpl.mpg.de/dataset/figshare-7771184-v2"
