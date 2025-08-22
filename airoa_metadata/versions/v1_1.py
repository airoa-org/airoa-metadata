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
class FileV1_1:
    type: str
    name: str


@dataclass
class GitSourceV1_1:
    hash: str
    branch: str
    uri: Optional[str] = None
    tag: Optional[str] = None


@dataclass
class SourceV1_1:
    git: GitSourceV1_1


@dataclass
class EntityV1_1:
    role: str
    id: Optional[str] = None
    name: Optional[str] = None
    template: Optional[Dict[str, Any]] = None


@dataclass
class ComponentV1_1:
    role: str
    name: str
    source: SourceV1_1


@dataclass
class ContextV1_1:
    entities: List[EntityV1_1] = field(default_factory=list)
    components: List[ComponentV1_1] = field(default_factory=list)


@dataclass
class DataSchemaV1_1:
    uri: str


@dataclass
class InstructionV1_1:
    idx: int
    text: List[str]


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
class RunV1_1:
    total_time_s: float
    instructions: List[InstructionV1_1] = field(default_factory=list)
    segments: List[SegmentV1_1] = field(default_factory=list)
    episode_label: Optional[str] = None


@dataclass
class MetadataV1_1(MetadataBase):
    version: str = "1.1"
    files: List[FileV1_1] = field(default_factory=list)
    context: ContextV1_1 = field(default_factory=ContextV1_1)
    run: RunV1_1 = field(default_factory=RunV1_1)
    data_schema: Optional[DataSchemaV1_1] = None

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV1_1":
        files = [FileV1_1(**file_data) for file_data in data.get("files", [])]
        
        entities = []
        for entity_data in data.get("context", {}).get("entities", []):
            entities.append(EntityV1_1(**entity_data))
        
        components = []
        for comp_data in data.get("context", {}).get("components", []):
            git_data = comp_data["source"]["git"]
            git_source = GitSourceV1_1(**git_data)
            source = SourceV1_1(git=git_source)
            components.append(ComponentV1_1(
                role=comp_data["role"],
                name=comp_data["name"],
                source=source
            ))
        
        context = ContextV1_1(entities=entities, components=components)
        
        instructions = []
        for instr_data in data.get("run", {}).get("instructions", []):
            instructions.append(InstructionV1_1(**instr_data))
        
        segments = []
        for seg_data in data.get("run", {}).get("segments", []):
            segments.append(SegmentV1_1(**seg_data))
        
        run = RunV1_1(
            total_time_s=data.get("run", {}).get("total_time_s", 0.0),
            instructions=instructions,
            segments=segments,
            episode_label=data.get("run", {}).get("episode_label")
        )
        
        data_schema = None
        if "data_schema" in data:
            data_schema = DataSchemaV1_1(**data["data_schema"])
        
        instance = cls(
            version=data.get("version", "1.1"),
            files=files,
            context=context,
            run=run,
            data_schema=data_schema
        )
        instance.data = data
        instance.extra_keys = extra_keys or {}
        instance.verify()
        return instance

    @classmethod
    def preceding(cls) -> "MetadataV1_0":
        return MetadataV1_0

    @classmethod
    def convert(
        cls, metadata: MetadataBase, extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV1_1":
        if isinstance(metadata, cls):
            return metadata
        elif not isinstance(metadata, MetadataV1_0):
            metadata = MetadataV1_0.convert(metadata, extra_keys)

        # Convert v1.0 to v1.1 structure
        old_data = metadata.data.copy()
        
        # Transform to new hierarchical structure
        new_data = {
            "version": "1.1",
            "files": [{"type": "rosbag", "name": old_data.get("bag_path", "")}],
            "context": {
                "entities": [
                    {"role": "robot", "id": old_data.get("hsr_id", "")},
                    {"role": "location", "name": old_data.get("location_name", "")}
                ],
                "components": [
                    {
                        "role": "interface",
                        "name": old_data.get("interface", ""),
                        "source": {
                            "git": {
                                "hash": old_data.get("interface_git_hash", ""),
                                "branch": old_data.get("interface_git_branch", "")
                            }
                        }
                    },
                    {
                        "role": "data_collection",
                        "name": "rosbag_manager",
                        "source": {
                            "git": {
                                "hash": old_data.get("git_hash", ""),
                                "branch": old_data.get("git_branch", "")
                            }
                        }
                    }
                ]
            },
            "run": {
                "total_time_s": max([seg.end_time for seg in metadata.segments], default=0.0) - min([seg.start_time for seg in metadata.segments], default=0.0) if metadata.segments else 0.0,  # Calculate from segments
                "episode_label": old_data.get("label"),  # Map v1.0 label to episode_label
                "instructions": [
                    {"idx": i, "text": instr} 
                    for i, instr in enumerate(old_data.get("instructions", []))
                ],
                "segments": [
                    {
                        "start_time": seg.start_time,
                        "end_time": seg.end_time, 
                        "instruction_idx": seg.instructions_index,
                        "success": not seg.has_suboptimal,
                        "controlled_by": "operator" if seg.is_directed else "auto"
                    }
                    for seg in metadata.segments
                ]
            }
        }
        
        return cls.from_dict(new_data, extra_keys)