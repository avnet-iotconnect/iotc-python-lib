import copy
import sys

from avnet.iotconnect.sdk.sdklib.config import DeviceProperties
from avnet.iotconnect.sdk.sdklib.dra import DeviceRestApi
from avnet.iotconnect.sdk.sdklib.error import DeviceConfigError


def load_device_properties() -> DeviceProperties:
    try:
        from accountcfg import DEVICE_PROPERTIES
        return DEVICE_PROPERTIES
    except ImportError:
        print("accountcfg.py needs to exist in this directory in order to run this test. Please refer to TESTS_CONFIGURATION.md", file=sys.stderr)
        sys.exit(-1)

def test_configure(device_properties: DeviceProperties):
    dra = DeviceRestApi(device_properties, trace_request=True)
    print(dra.get_identity_data().__dict__)

def test_validation(device_properties: DeviceProperties):
    try:
        device_properties.validate()
        raise ValueError("Validation test failed") # should not reach here
    except DeviceConfigError as ex:
        print(f"Validation success. Caught {ex.msg}")


try:
    props = load_device_properties()
    props.validate()

    props_test = copy.copy(props)
    props_test.cpid = "X"
    test_validation(props_test)

    props_test = copy.copy(props)
    props_test.env = "X"
    test_validation(props_test)

    props_test = copy.copy(props)
    props_test.platform = None
    test_validation(props_test)

    test_configure(props)


except DeviceConfigError as ex:
    print(ex)



