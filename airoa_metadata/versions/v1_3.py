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
from .v1_2 import MetadataV1_2

logger = logging.getLogger(__name__)


@dataclass
class FileV1_3:
    type: str
    name: str


@dataclass
class GitSourceV1_3:
    uri: str
    hash: str
    branch: str
    tag: Optional[str] = None


@dataclass
class SourceV1_3:
    git: GitSourceV1_3


@dataclass
class EntityV1_3:
    role: str
    id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None


@dataclass
class ComponentV1_3:
    role: str
    name: str
    source: SourceV1_3


@dataclass
class ContextV1_3:
    entities: List[EntityV1_3] = field(default_factory=list)
    components: List[ComponentV1_3] = field(default_factory=list)


@dataclass
class InstructionV1_3:
    idx: int
    text: List[str]


@dataclass
class SegmentV1_3:
    start_time: float
    end_time: float
    instruction_idx: int
    success: bool
    controlled_by: str
    score: Optional[float] = None
    is_composite: Optional[bool] = None


@dataclass
class RunV1_3:
    total_time_s: float
    instructions: List[InstructionV1_3] = field(default_factory=list)
    segments: List[SegmentV1_3] = field(default_factory=list)


@dataclass
class MetadataV1_3(MetadataBase):
    uuid: str
    version: str = "1.3"
    files: List[FileV1_3] = field(default_factory=list)
    context: ContextV1_3 = field(default_factory=ContextV1_3)
    run: RunV1_3 = field(default_factory=RunV1_3)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV1_3":
        files = [FileV1_3(**file_data) for file_data in data.get("files", [])]
        
        entities = []
        for entity_data in data.get("context", {}).get("entities", []):
            entities.append(EntityV1_3(**entity_data))
        
        components = []
        for comp_data in data.get("context", {}).get("components", []):
            git_data = comp_data["source"]["git"]
            git_source = GitSourceV1_3(**git_data)
            source = SourceV1_3(git=git_source)
            components.append(ComponentV1_3(
                role=comp_data["role"],
                name=comp_data["name"],
                source=source
            ))
        
        context = ContextV1_3(entities=entities, components=components)
        
        instructions = []
        for instr_data in data.get("run", {}).get("instructions", []):
            instructions.append(InstructionV1_3(**instr_data))
        
        segments = []
        for seg_data in data.get("run", {}).get("segments", []):
            segments.append(SegmentV1_3(**seg_data))
        
        run = RunV1_3(
            total_time_s=data.get("run", {}).get("total_time_s", 0.0),
            instructions=instructions,
            segments=segments
        )
        
        instance = cls(
            uuid=data.get("uuid", ""),
            version=data.get("version", "1.3"),
            files=files,
            context=context,
            run=run
        )
        
        instance.verify()
        return instance

    @classmethod
    def preceding(cls) -> "MetadataV1_2":
        return MetadataV1_2

    @classmethod
    def convert(
        cls,
        metadata: MetadataBase,
        extra_keys: Optional[Dict[str, Any]] = None,
        invert_success: bool = False,
    ) -> "MetadataV1_3":
        if isinstance(metadata, MetadataV1_3):
            return metadata
        elif not isinstance(metadata, cls.preceding()):
            metadata = cls.preceding().convert(metadata, extra_keys=extra_keys)

        files = [FileV1_3(type=file.type, name=file.name) for file in metadata.files]
        
        entities = []
        task_entity = None
        
        for entity in metadata.context.entities:
            if entity.role == "task":
                task_entity = entity
                entities.append(EntityV1_3(role="task-record", id=entity.id))
                if entity.template:
                    entities.append(EntityV1_3(
                        role="task-template",
                        id=f"{entity.id}-template" if entity.id else "template-1",
                        name=entity.template.name,
                        description=entity.template.description
                    ))
            else:
                entities.append(EntityV1_3(
                    role=entity.role,
                    id=entity.id,
                    name=entity.name
                ))
        
        components = []
        for comp in metadata.context.components:
            git_source = GitSourceV1_3(
                uri=comp.source.git.uri,
                hash=comp.source.git.hash,
                branch=comp.source.git.branch,
                tag=comp.source.git.tag
            )
            source = SourceV1_3(git=git_source)
            components.append(ComponentV1_3(
                role=comp.role,
                name=comp.name,
                source=source
            ))
        
        context = ContextV1_3(entities=entities, components=components)
        
        instructions = []
        for instr in metadata.run.instructions:
            instructions.append(InstructionV1_3(idx=instr.idx, text=instr.text))
        
        segments = []
        for seg in metadata.run.segments:
            segments.append(SegmentV1_3(
                start_time=seg.start_time,
                end_time=seg.end_time,
                instruction_idx=seg.instruction_idx,
                success=seg.success,
                controlled_by=seg.controlled_by,
                score=seg.score,
                is_composite=seg.is_composite
            ))
        
        run = RunV1_3(
            total_time_s=metadata.run.total_time_s,
            instructions=instructions,
            segments=segments
        )
        
        new_data = {
            "uuid": metadata.uuid,
            "version": "1.3",
            "files": [{"type": file.type, "name": file.name} for file in files],
            "context": {
                "entities": [
                    {k: v for k, v in {
                        "role": entity.role,
                        "id": entity.id,
                        "name": entity.name,
                        "description": entity.description
                    }.items() if v is not None}
                    for entity in entities
                ],
                "components": [
                    {
                        "role": comp.role,
                        "name": comp.name,
                        "source": {
                            "git": {k: v for k, v in {
                                "uri": comp.source.git.uri,
                                "hash": comp.source.git.hash,
                                "branch": comp.source.git.branch,
                                "tag": comp.source.git.tag
                            }.items() if v is not None}
                        }
                    }
                    for comp in components
                ]
            },
            "run": {
                "total_time_s": run.total_time_s,
                "instructions": [
                    {"idx": instr.idx, "text": instr.text}
                    for instr in instructions
                ],
                "segments": [
                    {k: v for k, v in {
                        "start_time": seg.start_time,
                        "end_time": seg.end_time,
                        "instruction_idx": seg.instruction_idx,
                        "success": seg.success,
                        "controlled_by": seg.controlled_by,
                        "score": seg.score,
                        "is_composite": seg.is_composite
                    }.items() if v is not None}
                    for seg in segments
                ]
            }
        }
        
        logger.info("Converting MetadataV1_2 to MetadataV1_3...")
        return cls.from_dict(new_data, extra_keys=extra_keys)