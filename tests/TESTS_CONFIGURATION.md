# Test Setup

Before running these tests, ensure to either:
* provide IOTC_TEST_DUID, IOTC_TEST_CPID, IOTC_TEST_ENV (default="poc"), IOTC_TEST_PF (default="aws")
environment variables.
* or create [accountcfg.py](accountcfg.py) in this directory

If using accountcfg.py, use this example content, and have it reflect your account information: 

```python
from avnet.iotconnect.sdk.sdklib.config import DeviceProperties

DEVICE_PROPERTIES = DeviceProperties(
    duid="myduid",
    cpid="ABCDEFG123456",
    env="poc",
    platform="aws"
)

```

The purpose of this file is to allow you to specify 
your own account and device to test discovery with
and configure the library portions that need account-specific information.

If just testing the protocol json generation without interacting with /IOTCONNECT
services and back end, most of these values can be default values from the above example.

# Running The Tests

Execute [scripts/run-tests.sh](scripts/run-tests.sh) with bash.

htmlconv directory will be generated with test coverage.

