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
from .v0_0 import MetadataV0_0

logger = logging.getLogger(__name__)


@dataclass
class SegmentV1_0:
    start_time: float
    end_time: float
    instructions_index: int
    has_suboptimal: bool
    is_directed: bool


@dataclass
class MetadataV1_0(MetadataBase):
    # version: str
    bag_path: str
    hsr_id: str
    location_name: str
    interface: str
    instructions: List[List[str]] = field(default_factory=list)
    segments: List[SegmentV1_0] = field(default_factory=list)
    git_hash: str = ""
    git_branch: str = ""
    interface_git_hash: str = ""
    interface_git_branch: str = ""

    @property
    def version(self) -> str:
        return "1.0"

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV1_0":
        # Create the segments list from dicts.
        segments = [SegmentV1_0(**seg) for seg in data.get("segments", [])]
        instance = cls(
            # version=data.get("version", "1.0"),
            bag_path=data.get("bag_path", ""),
            hsr_id=data.get("hsr_id", ""),
            location_name=data.get("location_name", ""),
            interface=data.get("interface", ""),
            instructions=data.get("instructions", []),
            segments=segments,
            git_hash=data.get("git_hash", ""),
            git_branch=data.get("git_branch", ""),
            interface_git_hash=data.get("interface_git_hash", ""),
            interface_git_branch=data.get("interface_git_branch", ""),
        )
        instance.data = data  # Preserve raw data for conversion.
        instance.extra_keys = extra_keys or {}
        instance.verify()
        return instance

    @classmethod
    def preceding(cls) -> "MetadataV0_0":
        return MetadataV0_0

    @classmethod
    def convert(
        cls, metadata: MetadataBase, extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV1_0":
        """
        Convert a MetadataV0_0 instance into a MetadataV1_0 instance.
        The conversion renames segment key 'instruction_index' to 'instructions_index'
        and sets the version to '1.0'.
        """
        if isinstance(metadata, cls):
            return metadata
        elif not isinstance(metadata, MetadataV0_0):
            metadata = MetadataV0_0.convert(metadata, extra_keys)

        old = metadata.data.copy()

        # Convert segments: rename "instruction_index" to "instructions_index".
        new_segments = []
        for seg in old.get("segments", []):
            new_seg = seg.copy()
            if "instruction_index" in new_seg:
                new_seg["instructions_index"] = new_seg.pop("instruction_index")
            new_segments.append(new_seg)
        old["segments"] = new_segments

        logger.info("Converting MetadataV0_0 to MetadataV1_0...")
        return cls.from_dict(old, extra_keys=extra_keys)
