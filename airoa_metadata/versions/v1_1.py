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
from .v1_0 import MetadataV1_0

logger = logging.getLogger(__name__)


@dataclass
class OrganizationV1_1:
    id: Optional[str]
    name: str


@dataclass
class LocationV1_1:
    id: Optional[str]
    name: str


@dataclass
class RobotV1_1:
    id: Optional[str]
    model: str


@dataclass
class InterfaceV1_1:
    id: Optional[str]
    name: str
    git_hash: str
    git_branch: str
    git_tag: Optional[str]


@dataclass
class DataCaptureV1_1:
    git_hash: str
    git_branch: str
    git_tag: Optional[str]


@dataclass
class InstructionV1_1:
    id: Optional[str]
    text: List[str]


@dataclass
class TemplateV1_1:
    id: Optional[str]
    name: str
    instructions: List[InstructionV1_1] = field(default_factory=list)


@dataclass
class TaskV1_1:
    id: Optional[str]
    template: TemplateV1_1


@dataclass
class SegmentV1_1:
    start_time: float
    end_time: float
    instruction_idx: int
    success: bool
    controlled_by: str
    score: Optional[float] = None
    is_composite: Optional[bool] = None


@dataclass
class DataV1_1:
    segments: List[SegmentV1_1] = field(default_factory=list)


@dataclass
class MetadataV1_1(MetadataBase):
    data_files: List[str]
    robot: RobotV1_1
    organization: OrganizationV1_1
    location: LocationV1_1
    interface: InterfaceV1_1
    data_capture: DataCaptureV1_1
    task: TaskV1_1
    operator_id: Optional[str]
    data: DataV1_1
    version: str = "1.1"  # field(init=True, repr=True, default="1.1")

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV1_1":
        # In a real implementation you may need to transform nested objects.
        org_data = data.get("organization", {})
        loc_data = data.get("location", {})
        iface_data = data.get("interface", {})
        dc_data = data.get("data_capture", {})
        task_data = data.get("task", {})
        template_data = task_data.get("template", {})
        instructions = [
            InstructionV1_1(**instr) for instr in template_data.get("instructions", [])
        ]
        template = TemplateV1_1(
            id=template_data.get("id"),
            name=template_data.get("name", ""),
            instructions=instructions,
        )
        task = TaskV1_1(id=task_data.get("id"), template=template)
        segments = [
            SegmentV1_1(**seg) for seg in data.get("data", {}).get("segments", [])
        ]
        data_obj = DataV1_1(segments=segments)
        # TODO: add data verification for git hash, etc
        instance = cls(
            # version=data.get("version", "1.1"),
            data_files=data.get("data_files", [data.get("bag_path")] if data.get("bag_path") else []),
            robot=RobotV1_1(
                id=data.get("robot", {}).get("id", None),
                model=data.get("robot", {}).get("model", None),
            ),
            organization=OrganizationV1_1(
                id=data.get("organization", {}).get("id")
                or extra_keys.get("organization_id")
                if extra_keys
                else None,
                name=data.get("organization", {}).get("name")
                or data.get("location_name", ""),
            ),
            location=LocationV1_1(
                id=data.get("location", {}).get("id") or extra_keys.get("location_id")
                if extra_keys
                else None,
                name=data.get("location", {}).get("name") or "9f",
            ),
            interface=InterfaceV1_1(
                id=data.get("interface", {}).get("id") or extra_keys.get("interface_id")
                if extra_keys
                else None,
                name=data.get("interface", {}).get("name") or data.get("interface", ""),
                git_hash=data.get("interface", {}).get("git_hash")
                or data.get("interface_git_hash", "0" * 40),
                git_branch=data.get("interface", {}).get("git_branch")
                or data.get("interface_git_branch", "master"),
                git_tag=data.get("interface", {}).get("git_tag")
                or extra_keys.get("interface_git_tag")
                if extra_keys
                else None,
            ),
            data_capture=DataCaptureV1_1(
                git_hash=data.get("data_capture", {}).get("git_hash")
                or data.get("git_hash", "0" * 40),
                git_branch=data.get("data_capture", {}).get("git_branch")
                or data.get("git_branch", "master"),
                git_tag=data.get("data_capture", {}).get("git_tag")
                or extra_keys.get("git_tag")
                if extra_keys
                else None,
            ),
            task=task,
            operator_id=data.get("operator_id") or extra_keys.get("operator_id")
            if extra_keys
            else None,
            data=data_obj,
        )
        print(instance)
        instance.verify()
        return instance

    @classmethod
    def preceding(cls) -> "MetadataV1_0":
        """
        Placeholder for automatic chaining conversions.
        """
        return MetadataV1_0

    @classmethod
    def convert(
        cls,
        metadata: MetadataBase,
        extra_keys: Optional[Dict[str, Any]] = None,
        invert_success: bool = False,
    ) -> "MetadataV1_1":
        # Assume conversion from MetadataV1_0 to MetadataV1_1.
        if isinstance(metadata, MetadataV1_1):
            return metadata
        elif not isinstance(metadata, cls.preceding()):
            metadata = cls.preceding().convert(metadata, extra_keys=extra_keys)

        old = metadata.data

        def get_val(key: str, default: Any = None):
            # Use the key directly from the old data or look it up in extra_keys.
            if key in old and old[key]:
                return old[key]
            # WARNING: Duplicate of extra keys assignment
            if extra_keys and key in extra_keys:
                return extra_keys[key]
            return default

        new_data = {
            # "version": "1.1",
            "data_files": [get_val("bag_path")],
            "robot": {
                "id": get_val("hsr_id", None),
                "model": get_val("robot_model", None),
            },
            "organization": {
                "id": extra_keys.get("organization_id", None),
                "name": get_val("location_name", ""),
            },
            "location": {
                "id": extra_keys.get("location_id", None),
                "name": get_val("location_name", "9f"),
            },
            "interface": {
                "id": get_val("interface_id", None),
                "name": get_val("interface"),
                "git_hash": get_val("interface_git_hash", "0" * 40),
                "git_branch": get_val("interface_git_branch", "master"),
                "git_tag": get_val("interface_git_tag", None),
            },
            "data_capture": {
                "git_hash": get_val("git_hash", "0" * 40),
                "git_branch": get_val("git_branch", "master"),
                "git_tag": get_val("git_tag", None),
            },
            "task": {
                "id": get_val("task_id", None),
                "template": {
                    "id": get_val("template_id", None),
                    "name": get_val("template_name", "default_template"),
                    "instructions": [
                        {
                            "id": None,
                            "text": instr,
                        }
                        for instr in old.get("instructions", [])
                    ],
                },
            },
            "operator_id": get_val("operator_id", None),
            "data": {
                "segments": [
                    {
                        "start_time": seg.get("start_time"),
                        "end_time": seg.get("end_time"),
                        "instruction_index": seg.get("instructions_index"),
                        "success": not seg.get("has_suboptimal", False)
                        if not invert_success
                        else seg.get("has_suboptimal", False),
                        "is_operator_controlled": seg.get("is_directed"),
                    }
                    for seg in old.get("segments", [])
                ]
            },
        }
        logger.info("Converting MetadataV1_0 to MetadataV1_1...")
        # WARNING: Duplicate of extra keys assignment
        return cls.from_dict(new_data, extra_keys=extra_keys)
