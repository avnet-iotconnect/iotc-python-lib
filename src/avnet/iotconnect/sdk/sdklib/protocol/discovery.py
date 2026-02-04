# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ProtocolDiscoveryDJson:
    ec: Optional[int] = field(default=None)
    bu: Optional[str] = field(default=None)
    pf: Optional[str] = field(default=None)
    dip: Optional[int] = field(default=None)
    errorMsg: Optional[str] = None


@dataclass
class IotcDiscoveryResponseJson:
    d: ProtocolDiscoveryDJson = field(default_factory=ProtocolDiscoveryDJson)
    status: Optional[int] = field(default=None)
    message: Optional[str] = field(default=None)
