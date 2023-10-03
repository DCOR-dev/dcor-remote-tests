from dclab.external.packaging import parse as parse_version

from helper import get_api


def test_ckan_version():
    api = get_api()
    assert api.ckan_version_object >= parse_version("2.10.1")


def test_extensions():
    api = get_api()
    extensions = api.get("status_show")["extensions"]
    for key in ["stats", "text_view", "image_view", "dcor_depot",
                "dcor_schemas", "dc_serve", "dc_view", "dc_log_view",
                "dcor_theme"]:
        assert key in extensions, f"extension '{key}' not loaded!"
