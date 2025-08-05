# -*- coding: utf-8 -*-
"""
Copyright (c) Tokyo University Matsuo Iwasawa Laboratory, Petr Khrapchenkov

This software is provided "as-is", without any express or implied warranty.
In no event will the authors be held liable for any damages arising from the use of this software.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software
and associated documentation files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify, merge, publish, distribute,
sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

1. The origin of this software must not be misrepresented; you must not claim that you wrote the original software.
   If you use this software in a product, an acknowledgment in the product documentation would be appreciated but is not required.
2. Altered source versions must be plainly marked as such, and must not be misrepresented as being the original software.
3. This notice may not be removed or altered from any source distribution.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.base import MetadataBase

logger = logging.getLogger(__name__)


@dataclass
class SegmentV0_0:
    start_time: float
    end_time: float
    # Note: In version 0.0, the key is "instruction_index"
    instruction_index: int
    has_suboptimal: bool
    is_directed: bool


@dataclass
class MetadataV0_0(MetadataBase):
    # version: str
    bag_path: str
    git_hash: str
    git_branch: str
    hsr_id: str
    location_name: str
    interface: str
    interface_git_hash: str
    interface_git_branch: str
    instructions: List[List[str]] = field(default_factory=list)
    segments: List[SegmentV0_0] = field(default_factory=list)

    # Internal fields for conversion support (not part of the public __init__)
    data: Dict[str, Any] = field(init=False, default_factory=dict)
    extra_keys: Dict[str, Any] = field(init=False, default_factory=dict)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV0_0":
        seg_list = [SegmentV0_0(**seg) for seg in data.get("segments", [])]
        instance = cls(
            # version=data.get("version", "0.0"),
            bag_path=data.get("bag_path", ""),
            git_hash=data.get("git_hash", ""),
            git_branch=data.get("git_branch", ""),
            hsr_id=data.get("hsr_id", ""),
            location_name=data.get("location_name", ""),
            interface=data.get("interface", ""),
            interface_git_hash=data.get("interface_git_hash", ""),
            interface_git_branch=data.get("interface_git_branch", ""),
            instructions=data.get("instructions", []),
            segments=seg_list,
        )
        instance.data = data.copy()
        instance.extra_keys = extra_keys or {}
        # instance.verify()
        logger.info("Loaded MetadataV0_0 from dict.")
        return instance

    @property
    def version(self) -> str:
        return "0.0"

    @classmethod
    def preceding(cls) -> None:
        """
        Placeholder for automatic chaining conversions.
        """
        raise NotImplementedError("No preceding class available.")

    @classmethod
    def convert(
        cls, previous: MetadataBase, extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV0_0":
        if isinstance(previous, MetadataV0_0):
            return previous
        raise ValueError(
            "Conversion to MetadataV0_0 is not supported from unknown version."
        )
