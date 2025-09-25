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
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.base import MetadataBase
from .v1_1 import MetadataV1_1

logger = logging.getLogger(__name__)


@dataclass
class FileV1_2:
    type: str
    name: str


@dataclass
class GitSourceV1_2:
    uri: str
    hash: str
    branch: str
    tag: Optional[str] = None


@dataclass
class SourceV1_2:
    git: GitSourceV1_2


@dataclass
class TaskTemplateV1_2:
    name: str
    description: str


@dataclass
class EntityV1_2:
    role: str
    id: Optional[str] = None
    name: Optional[str] = None
    template: Optional[TaskTemplateV1_2] = None


@dataclass
class ComponentV1_2:
    role: str
    name: str
    source: SourceV1_2


@dataclass
class ContextV1_2:
    entities: List[EntityV1_2] = field(default_factory=list)
    components: List[ComponentV1_2] = field(default_factory=list)


@dataclass
class InstructionV1_2:
    idx: int
    text: List[str]


@dataclass
class SegmentV1_2:
    start_time: float
    end_time: float
    instruction_idx: int
    success: bool
    controlled_by: str
    score: Optional[float] = None
    is_composite: Optional[bool] = None


@dataclass
class RunV1_2:
    total_time_s: float
    instructions: List[InstructionV1_2] = field(default_factory=list)
    segments: List[SegmentV1_2] = field(default_factory=list)
    episode_label: Optional[str] = None


@dataclass
class MetadataV1_2(MetadataBase):
    uuid: str
    version: str = "1.2"
    files: List[FileV1_2] = field(default_factory=list)
    context: ContextV1_2 = field(default_factory=ContextV1_2)
    run: RunV1_2 = field(default_factory=RunV1_2)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV1_2":
        files = [FileV1_2(**file_data) for file_data in data.get("files", [])]

        entities = []
        for entity_data in data.get("context", {}).get("entities", []):
            template = None
            if entity_data.get("template"):
                template = TaskTemplateV1_2(**entity_data["template"])

            entities.append(
                EntityV1_2(
                    role=entity_data["role"],
                    id=entity_data.get("id"),
                    name=entity_data.get("name"),
                    template=template,
                )
            )

        components = []
        for comp_data in data.get("context", {}).get("components", []):
            git_data = comp_data["source"]["git"]
            git_source = GitSourceV1_2(**git_data)
            source = SourceV1_2(git=git_source)
            components.append(
                ComponentV1_2(
                    role=comp_data["role"], name=comp_data["name"], source=source
                )
            )

        context = ContextV1_2(entities=entities, components=components)

        instructions = []
        for instr_data in data.get("run", {}).get("instructions", []):
            instructions.append(InstructionV1_2(**instr_data))

        segments = []
        for seg_data in data.get("run", {}).get("segments", []):
            segments.append(SegmentV1_2(**seg_data))

        run = RunV1_2(
            total_time_s=data.get("run", {}).get("total_time_s", 0.0),
            instructions=instructions,
            segments=segments,
            episode_label=data.get("run", {}).get("episode_label"),
        )

        instance = cls(
            uuid=data.get("uuid", ""),
            version=data.get("version", "1.2"),
            files=files,
            context=context,
            run=run,
        )

        instance.verify()
        return instance

    @classmethod
    def preceding(cls) -> "MetadataV1_1":
        return MetadataV1_1

    @classmethod
    def convert(
        cls,
        metadata: MetadataBase,
        extra_keys: Optional[Dict[str, Any]] = None,
        invert_success: bool = False,
    ) -> "MetadataV1_2":
        if isinstance(metadata, MetadataV1_2):
            return metadata
        elif not isinstance(metadata, cls.preceding()):
            metadata = cls.preceding().convert(metadata, extra_keys=extra_keys)

        files = [FileV1_2(type=f.type, name=f.name) for f in metadata.files]

        entities = []
        for entity in metadata.context.entities:
            if entity.role == "task" and entity.template:
                template = TaskTemplateV1_2(
                    name=entity.template.get("name", ""),
                    description=entity.template.get(
                        "description", entity.template.get("name", "")
                    ),
                )
                entities.append(
                    EntityV1_2(role="task", id=entity.id, template=template)
                )
            else:
                entities.append(
                    EntityV1_2(role=entity.role, id=entity.id, name=entity.name)
                )

        components = []
        for comp in metadata.context.components:
            git_source = GitSourceV1_2(
                uri=comp.source.git.uri or "",
                hash=comp.source.git.hash,
                branch=comp.source.git.branch,
                tag=comp.source.git.tag,
            )
            source = SourceV1_2(git=git_source)
            components.append(
                ComponentV1_2(role=comp.role, name=comp.name, source=source)
            )

        context = ContextV1_2(entities=entities, components=components)  # noqa: F841

        instructions = [
            InstructionV1_2(idx=instr.idx, text=instr.text)
            for instr in metadata.run.instructions
        ]

        segments = []
        for i, seg in enumerate(metadata.run.segments):
            # Check if this segment overlaps with any other segment (making it composite)
            is_composite = seg.is_composite
            if not is_composite:  # Only check if not already marked as composite
                for j, other_seg in enumerate(metadata.run.segments):
                    if i != j:  # Don't compare with itself
                        # Check for overlap: segment A overlaps with B if A.start < B.end and B.start < A.end
                        if (
                            seg.start_time < other_seg.end_time
                            and other_seg.start_time < seg.end_time
                            and
                            # Also check if this segment is bigger (longer duration)
                            (seg.end_time - seg.start_time)
                            > (other_seg.end_time - other_seg.start_time)
                        ):
                            is_composite = True
                            break

            segments.append(
                SegmentV1_2(
                    start_time=seg.start_time,
                    end_time=seg.end_time,
                    instruction_idx=seg.instruction_idx,
                    success=seg.success,
                    controlled_by=seg.controlled_by,
                    score=seg.score,
                    is_composite=is_composite,
                )
            )

        run = RunV1_2(
            total_time_s=metadata.run.total_time_s,
            instructions=instructions,
            segments=segments,
            episode_label=getattr(metadata.run, "episode_label", None),
        )

        # Generate UUID if not present in source metadata or extra_keys
        metadata_uuid = getattr(metadata, "uuid", "") or ""
        extra_uuid = extra_keys.get("uuid", "") if extra_keys else ""
        final_uuid = metadata_uuid or extra_uuid or str(uuid.uuid4())

        new_data = {
            "uuid": final_uuid,
            "version": "1.2",
            "files": [{"type": file.type, "name": file.name} for file in files],
            "context": {
                "entities": [
                    {
                        k: v
                        for k, v in {
                            "role": entity.role,
                            "id": entity.id,
                            "name": entity.name,
                            "template": {
                                "name": entity.template.name,
                                "description": entity.template.description,
                            }
                            if entity.template
                            else None,
                        }.items()
                        if v is not None
                    }
                    for entity in entities
                ],
                "components": [
                    {
                        "role": comp.role,
                        "name": comp.name,
                        "source": {
                            "git": {
                                k: v
                                for k, v in {
                                    "uri": comp.source.git.uri,
                                    "hash": comp.source.git.hash,
                                    "branch": comp.source.git.branch,
                                    "tag": comp.source.git.tag,
                                }.items()
                                if v is not None
                            }
                        },
                    }
                    for comp in components
                ],
            },
            "run": {
                "total_time_s": run.total_time_s,
                "episode_label": run.episode_label,
                "instructions": [
                    {"idx": instr.idx, "text": instr.text} for instr in instructions
                ],
                "segments": [
                    {
                        k: v
                        for k, v in {
                            "start_time": seg.start_time,
                            "end_time": seg.end_time,
                            "instruction_idx": seg.instruction_idx,
                            "success": seg.success,
                            "controlled_by": seg.controlled_by,
                            "score": seg.score,
                            "is_composite": seg.is_composite,
                        }.items()
                        if v is not None
                    }
                    for seg in segments
                ],
            },
        }

        logger.info("Converting MetadataV1_1 to MetadataV1_2...")
        return cls.from_dict(new_data, extra_keys=extra_keys)
