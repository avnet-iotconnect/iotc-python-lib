# Test Setup

Before running these tests, ensure to create [accountcfg.py](accountcfg.py)
with the content as follows that reflects your account information, for example: 

```python
from avnet.iotconnect.sdk.sdklib.config import DeviceProperties

DEVICE_PROPERTIES = DeviceProperties(
    duid="nik-gg-pc01",
    cpid="97FF86E8728645E9B89F7B07977E4B15",
    env="poc",
    platform="aws"
)

```

The purpose of this file is to allow you to specify 
your own account and device to test discovery with
and configure the library portions that need account-specific information.

If just testing the protocol json generation without interacting with /IOTCONNECT
services and back end, most of these values can be default values from the above example.


