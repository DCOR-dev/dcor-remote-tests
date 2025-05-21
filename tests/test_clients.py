import pathlib

import pytest

from dcoraid.api import errors

from helper import get_api

data_path = pathlib.Path(__file__).parent / "data"


def test_current_client_version():
    api = get_api()
    api.get("status_show")


@pytest.mark.parametrize("dcoraid_version", [
    "0.1.0",
    "0.6.0",
    "0.6.9",
    "0.7.1",
    "0.7.6",  # no version branding in dclab.RTDCWriter
    "0.13.0",
    "0.14.1",
    ])
def test_forbidden_client_versions(dcoraid_version):
    """Old clients should not work"""
    api = get_api()
    api.headers["user-agent"] = f"DCOR-Aid/{dcoraid_version}"
    with pytest.raises(errors.APIOutdatedError, match="outdated"):
        api.get("status_show")


@pytest.mark.parametrize("dcoraid_version", [
    "0.15.5",
    ])
def test_allowed_client_versions(dcoraid_version):
    """Old clients should not work"""
    api = get_api()
    api.headers["user-agent"] = f"DCOR-Aid/{dcoraid_version}"
    api.get("status_show")
