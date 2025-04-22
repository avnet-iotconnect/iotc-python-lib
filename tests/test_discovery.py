import copy
import os

import pytest
from pathlib import Path
import sys

from avnet.iotconnect.sdk.sdklib.config import DeviceProperties
from avnet.iotconnect.sdk.sdklib.dra import DeviceRestApi
from avnet.iotconnect.sdk.sdklib.error import DeviceConfigError

@pytest.fixture
def device_properties():
    e = os.environ
    if e.get('IOTC_TEST_DUID') is not None:
        env = e.get('IOTC_TEST_ENV')
        pf = e.get('IOTC_TEST_PF')
        if env is None:
            env = 'poc'
        if pf is None:
            pf = 'aws'
        return DeviceProperties(
            duid=e['IOTC_TEST_DUID'],
            cpid=e['IOTC_TEST_CPID'],
            env=env,
            platform=pf
        )
    try:
        # Setup imports and paths so that we can open accountcfg.py
        tests_dir = Path(__file__).parent
        sys.path.insert(0, str(tests_dir))
        from accountcfg import DEVICE_PROPERTIES
        return copy.deepcopy(DEVICE_PROPERTIES)
    except ImportError:
        pytest.fail("Missing accountcfg.py with DEVICE_PROPERTIES")

def test_configure(device_properties):
    dra = DeviceRestApi(device_properties, verbose=False)
    assert dra.get_identity_data() is not None

def test_validation(device_properties):
    # Each test gets fresh copy of properties
    props = copy.deepcopy(device_properties)
    props.cpid = "X"
    with pytest.raises(DeviceConfigError):
        props.validate()

    props = copy.deepcopy(device_properties)
    props.env = "X"
    with pytest.raises(DeviceConfigError):
        props.validate()

    props = copy.deepcopy(device_properties)
    props.platform = None
    with pytest.raises(DeviceConfigError):
        props.validate()
