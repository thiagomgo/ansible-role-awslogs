import os
import imp
import json

import requests_mock
import pytest

ROLE_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RECONFIG_PATH = os.path.join(ROLE_BASE_DIR, 'files', 'awslogs-reconfig')

reconfig = imp.load_source('', RECONFIG_PATH)


@pytest.fixture
def metadata():
    """
    Isolates the dependence on the name within the module
    """
    return reconfig.EnhancedMetadata()


def test_import():
    """
    This test basically passes if the module imports and has a main
    """
    assert 'main' in dir(reconfig)


def test_region_property(metadata):
    """
    Test that the region property is working outide of an EC2 instance
    """
    with requests_mock.mock() as m:
        m.get(reconfig.METADATA.format('placement/availability-zone'), text='us-west-1a')
        assert metadata.region == 'us-west-1'


def test_instance_id_property(metadata):
    """
    Test that the instance_id property is working outside of an EC2 instance
    """
    expected_instance_id = 'i-8909234ge'
    with requests_mock.mock() as m:
        m.get(reconfig.METADATA.format('instance-id'), text=expected_instance_id)
        assert metadata.instance_id == expected_instance_id


def test_private_address_property(metadata):
    """
    Test the private_address property is working outside of an EC2 instance
    """
    expected_ipv4 = '10.100.97.88'
    with requests_mock.mock() as m:
        m.get(reconfig.METADATA.format('local-ipv4'), text=expected_ipv4)
        assert metadata.private_address == expected_ipv4


def test_iam_info_property(metadata):
    """
    Test that the IAM Info property is working outside of an EC2 instance
    """
    expected_iaminfo = json.dumps({'notreal': {'notrealiam': 'role'}})
    with requests_mock.mock() as m:
        m.get(reconfig.METADATA.format('iam/info'), text=expected_iaminfo)
        actual_iaminfo = metadata.iam_info
        assert isinstance(actual_iaminfo, dict)
        assert actual_iaminfo['notreal']['notrealiam'] == 'role'


def test_nlmaccount_int_property(metadata):
    """
    Test that the NLM Account property is working for an NLM-INT subnet
    """
    urlforip = reconfig.METADATA.format('local-ipv4')
    with requests_mock.mock() as m:
        m.get(urlforip, text='10.154.240.17')
        assert metadata.nlmaccount == 'NLM-INT'


def test_nlmaccount_qa_property(metadata):
    """
    Test that the NLM Account property is working for an NLM-QA subnet
    """
    urlforip = reconfig.METADATA.format('local-ipv4')
    with requests_mock.mock() as m:
        m.get(urlforip, text='10.154.233.2')
        assert metadata.nlmaccount == 'NLM-QA'


def test_nlmaccount_dflt_property(metadata):
    """
    Test the response when the local IP is outside the private range
    """
    urlforip = reconfig.METADATA.format('local-ipv4')
    with requests_mock.mock() as m:
        m.get(urlforip, text='10.100.3.23')
        assert metadata.nlmaccount is None
