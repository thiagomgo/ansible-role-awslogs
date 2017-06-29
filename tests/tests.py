import os
import imp
import requests_mock

ROLE_BASE_DIR = os.path.dirname(os.path.dirname(__file__))
RECONFIG_PATH = os.path.join(ROLE_BASE_DIR, 'files', 'awslogs-reconfig')

reconfig = imp.load_source('', RECONFIG_PATH)


def test_import():
    '''
    This test basically passes if the module imports and has a main
    '''
    assert 'main' in dir(reconfig)


# NOTE: this requires a lot of mocking to test outside of AWS...
def test_base_metadata():
    with requests_mock.mock() as m:
        m.get(reconfig.METADATA.format('placement/availability-zone'), text='us-west-1a')
        basemeta = reconfig.BaseMetadata()
        assert basemeta.region == 'us-west-1'
