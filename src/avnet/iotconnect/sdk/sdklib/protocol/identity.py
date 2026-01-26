# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> and Zackary Andraka <zackary.andraka@avnet.com> et al.
import json
# The JSON to object mapping was originally created with assistance from OpenAI's ChatGPT.
# For more information about ChatGPT, visit https://openai.com/

from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class ProtocolMetaJson:
    at: Optional[int] = None
    df: Optional[int] = None
    cd: Optional[str] = None
    gtw: Optional[int] = None
    edge: Optional[int] = None
    pf: Optional[int] = None
    hwv: str = field(default="")
    swv: str = field(default="")
    v: float = field(default=0.0)


@dataclass
class ProtocolHasJson:
    d: int = field(default=0)
    attr: int = field(default=0)
    set: int = field(default=0)
    r: int = field(default=0)
    ota: int = field(default=0)


@dataclass
class ProtocolSetJson:
    pub: Optional[str] = None
    sub: Optional[str] = None
    pubForAll: Optional[str] = None
    subForAll: Optional[str] = None


@dataclass
class ProtocolTopicsJson:
    rpt: Optional[str] = None
    flt: Optional[str] = None
    od: Optional[str] = None
    hb: Optional[str] = None
    ack: Optional[str] = None
    dl: Optional[str] = None
    di: Optional[str] = None
    c2d: Optional[str] = None
    set: ProtocolSetJson = field(default_factory=ProtocolSetJson)


@dataclass
class ProtocolVideoStreamingJson:
    url: Optional[str] = None  # AWS IoT credentials endpoint
    as_: Optional[bool] = field(default=None, metadata={'alias': 'as'})  # Auto-start flag

    # "as" is a keyword in Python, so we use "as_" in the dataclass and map it to "as" in JSON
    def __post_init__(self):
        if hasattr(self, 'as'):
            self.as_ = getattr(self, 'as')


@dataclass
class ProtocolBucketsJson:
    bn: Optional[str] = None    # Bucket name
    ca: Optional[bool] = None   # ca="customer account"
    rarn: Optional[str] = None  # role arn


@dataclass
class ProtocolFsJson:
    '''
    Note about credentials:
    1 .Obtain temprrary STS credentials (accessKeyId, secretAccessKey, sessionToken) from the /credentials GET URL.
    Ensure that the GET request also includes "x-amzn-iot-thingname" header with the device's client ID (thing name).
    This request will retrun
    2. If bucket's ca==true, it means that we have to invoke another ASSUME ROLE request to the corss-account STS endpoint
    to obtain A NEW SET OF STS crednetials that will be used in the request BELOW.
    We will be using the role ARN provided in the "rarn" field to assume the role in the customer account.
    3. Use the obtained STS credentials for S3 access to the bucket.
    '''
    url: Optional[str] = None  # AWS IoT credentials endpoint
    buckets: List[ProtocolBucketsJson] = field(default=None)

@dataclass
class ProtocolIdentityPJson:
    n: Optional[str] = None
    h: Optional[str] = None
    p: int = field(default=0)
    id: Optional[str] = None
    un: Optional[str] = None
    topics: ProtocolTopicsJson = field(default_factory=ProtocolTopicsJson)
    vs: Optional[ProtocolVideoStreamingJson] = None
    fs: Optional[ProtocolFsJson] = None


@dataclass
class ProtocolIdentityDJson:
    ec: int = field(default=0)
    ct: int = field(default=0)
    meta: ProtocolMetaJson = field(default_factory=ProtocolMetaJson)
    has: ProtocolHasJson = field(default_factory=ProtocolHasJson)
    p: ProtocolIdentityPJson = field(default_factory=ProtocolIdentityPJson)
    dt: Optional[str] = None


@dataclass
class ProtocolIdentityResponseJson:
    d: ProtocolIdentityDJson = field(default_factory=ProtocolIdentityDJson)
    status: int = field(default=0)
    message: str = field(default="")


@dataclass
class HttpCredentialsResponseJson:
    d: ProtocolIdentityDJson = field(default_factory=ProtocolIdentityDJson)
    status: int = field(default=0)
    message: str = field(default="")
