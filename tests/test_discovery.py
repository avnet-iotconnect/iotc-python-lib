import copy
import pytest
from pathlib import Path
import sys

from avnet.iotconnect.sdk.sdklib.dra import DeviceRestApi
from avnet.iotconnect.sdk.sdklib.error import DeviceConfigError

# Setup imports and paths
tests_dir = Path(__file__).parent
sys.path.insert(0, str(tests_dir))

@pytest.fixture
def device_properties():
    """Load device properties from config file"""
    try:
        from accountcfg import DEVICE_PROPERTIES
        return copy.deepcopy(DEVICE_PROPERTIES)
    except ImportError:
        pytest.fail("Missing accountcfg.py with DEVICE_PROPERTIES")

def test_configure(device_properties):
    """Test device configuration"""
    dra = DeviceRestApi(device_properties, trace_request=True)
    assert dra.get_identity_data() is not None

def test_validation(device_properties):
    """Test property validation"""
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
