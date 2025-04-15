import copy

from avnet.iotconnect.sdk.sdklib.config import DeviceProperties
from avnet.iotconnect.sdk.sdklib.dra import DeviceRestApi
from avnet.iotconnect.sdk.sdklib.error import DeviceConfigError

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
    props = DeviceProperties(
        duid="nik-gg-pc01",
        cpid="97FF86E8728645E9B89F7B07977E4B15",
        env="poc",
        platform="aws"
    )
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


    props.env = "1" # now expect validation for env to fail


except DeviceConfigError as ex:
    print(ex)



