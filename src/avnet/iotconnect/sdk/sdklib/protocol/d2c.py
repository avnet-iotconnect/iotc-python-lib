# SPDX-License-Identifier: MIT
# Copyright (C) 2024 Avnet
# Authors: Nikola Markovic <nikola.markovic@avnet.com> et al.

from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class ProtocolTelemetryEntryJson:
    d: dict[str, Any] = field(default_factory=dict)
    dt: Optional[str] = field(default=None)
    id: Optional[str] = field(default=None)
    tg: Optional[str] = field(default=None)


@dataclass
class ProtocolTelemetryMessageJson:
    d: list[ProtocolTelemetryEntryJson] = field(default_factory=list[ProtocolTelemetryEntryJson])
    dt: Optional[str] = field(default=None) # optional top level timestamp - time when this record set was recorded

@dataclass
class ProtocolAckDJson:
    ack: Optional[str] = field(default=None)
    type: Optional[int] = field(default=None)
    st: Optional[int] = field(default=None)
    msg: Optional[str] = field(default=None)

@dataclass
class ProtocolAckMessageJson:
    d: ProtocolAckDJson = field(default_factory=ProtocolAckDJson)
    dt: Optional[str] = field(default=None)
