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

import dataclasses
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..core.base import MetadataBase
from .v1_3 import MetadataV1_3

logger = logging.getLogger(__name__)

SCHEMA_URI = "https://github.com/airoa-org/airoa-metadata/blob/feature/development/airoa_metadata/schemas/v2_0.json"


@dataclass
class FileV2_0:
    type: str
    name: str
    checksum: Optional[str] = None


@dataclass
class GitSourceV2_0:
    uri: str
    hash: str
    branch: str
    tag: Optional[str] = None


@dataclass
class SourceV2_0:
    git: Optional[GitSourceV2_0] = None


@dataclass
class RobotV2_0:
    type: str
    id: str
    config_uri: Optional[str] = None
    checksum: Optional[str] = None


@dataclass
class EnvironmentV2_0:
    type: str
    site: str
    location: Optional[str] = None


@dataclass
class RunnerV2_0:
    type: str
    organization: str
    name: str


@dataclass
class DeviceV2_0:
    role: str
    type: str
    id: str


@dataclass
class ProgramV2_0:
    role: str
    name: str
    source: SourceV2_0


@dataclass
class EpisodeV2_0:
    start_time: float
    end_time: float
    success: bool
    label: str


@dataclass
class SegmentV2_0:
    start_time: float
    end_time: float
    label_idx: int
    success: bool


@dataclass
class MetadataV2_0(MetadataBase):
    uuid: str
    schema_version: str = "2.0"
    robot: RobotV2_0 = field(default_factory=lambda: RobotV2_0(type="", id=""))
    files: List[FileV2_0] = field(default_factory=list)
    environment: EnvironmentV2_0 = field(
        default_factory=lambda: EnvironmentV2_0(type="real_world", site="")
    )
    runner: RunnerV2_0 = field(
        default_factory=lambda: RunnerV2_0(type="operator", organization="", name="")
    )
    devices: List[DeviceV2_0] = field(default_factory=list)
    programs: List[ProgramV2_0] = field(default_factory=list)
    episode: EpisodeV2_0 = field(
        default_factory=lambda: EpisodeV2_0(
            start_time=0.0, end_time=0.0, success=False, label=""
        )
    )
    labels: List[str] = field(default_factory=list)
    segments: List[SegmentV2_0] = field(default_factory=list)

    @property
    def version(self) -> str:
        return "2.0"

    def to_json(self) -> str:
        d = dataclasses.asdict(self)
        # Rename schema_version and add $schema field
        d.pop("schema_version", None)
        result = {"$schema": SCHEMA_URI, "schema_version": "2.0"}
        result.update(d)
        return json.dumps(result, indent=2)

    @classmethod
    def from_dict(
        cls, data: Dict[str, Any], extra_keys: Optional[Dict[str, Any]] = None
    ) -> "MetadataV2_0":
        files = [FileV2_0(**file_data) for file_data in data.get("files", [])]

        robot_data = data.get("robot", {})
        robot = RobotV2_0(
            type=robot_data.get("type", ""),
            id=robot_data.get("id", ""),
            config_uri=robot_data.get("config_uri"),
            checksum=robot_data.get("checksum"),
        )

        env_data = data.get("environment", {})
        environment = EnvironmentV2_0(
            type=env_data.get("type", "real_world"),
            site=env_data.get("site", ""),
            location=env_data.get("location"),
        )

        runner_data = data.get("runner", {})
        runner = RunnerV2_0(
            type=runner_data.get("type", "operator"),
            organization=runner_data.get("organization", ""),
            name=runner_data.get("name", ""),
        )

        devices = [DeviceV2_0(**dev_data) for dev_data in data.get("devices", [])]

        programs = []
        for prog_data in data.get("programs", []):
            git_data = prog_data.get("source", {}).get("git")
            git_source = GitSourceV2_0(**git_data) if git_data else None
            source = SourceV2_0(git=git_source)
            programs.append(
                ProgramV2_0(
                    role=prog_data["role"], name=prog_data["name"], source=source
                )
            )

        episode_data = data.get("episode", {})
        episode = EpisodeV2_0(
            start_time=episode_data.get("start_time", 0.0),
            end_time=episode_data.get("end_time", 0.0),
            success=episode_data.get("success", False),
            label=episode_data.get("label", ""),
        )

        labels = data.get("labels", [])

        segments = [SegmentV2_0(**seg_data) for seg_data in data.get("segments", [])]

        instance = cls(
            uuid=data.get("uuid", ""),
            schema_version=data.get("schema_version", "2.0"),
            robot=robot,
            files=files,
            environment=environment,
            runner=runner,
            devices=devices,
            programs=programs,
            episode=episode,
            labels=labels,
            segments=segments,
        )

        instance.verify()
        return instance

    @classmethod
    def preceding(cls) -> "MetadataV1_3":
        return MetadataV1_3

    @classmethod
    def convert(
        cls,
        metadata: MetadataBase,
        extra_keys: Optional[Dict[str, Any]] = None,
    ) -> "MetadataV2_0":
        if isinstance(metadata, MetadataV2_0):
            return metadata
        elif not isinstance(metadata, cls.preceding()):
            metadata = cls.preceding().convert(metadata, extra_keys=extra_keys)

        # Map files (add checksum=None)
        files = [
            {"type": f.type, "name": f.name, "checksum": None} for f in metadata.files
        ]

        # Map robot from entity with role="robot"
        robot_entity = next(
            (e for e in metadata.context.entities if e.role == "robot"), None
        )
        robot = {
            "type": "",
            "id": robot_entity.id if robot_entity else "",
        }

        # Map environment from entity with role="location"
        location_entity = next(
            (e for e in metadata.context.entities if e.role == "location"), None
        )
        environment = {
            "type": "real_world",
            "site": "",
            "location": location_entity.name if location_entity else None,
        }

        # Map runner from entity with role="operator"
        operator_entity = next(
            (e for e in metadata.context.entities if e.role == "operator"), None
        )
        org_entity = next(
            (e for e in metadata.context.entities if e.role == "organization"), None
        )
        runner = {
            "type": "operator",
            "organization": org_entity.name if org_entity else "",
            "name": operator_entity.id if operator_entity else "",
        }

        # Map components to programs
        programs = []
        for comp in metadata.context.components:
            git_dict = {
                "uri": comp.source.git.uri,
                "hash": comp.source.git.hash,
                "branch": comp.source.git.branch,
            }
            if comp.source.git.tag is not None:
                git_dict["tag"] = comp.source.git.tag
            programs.append(
                {
                    "role": comp.role,
                    "name": comp.name,
                    "source": {"git": git_dict},
                }
            )

        # Map instructions to labels (take first text variant of each instruction)
        labels = []
        for instr in metadata.run.instructions:
            if instr.text:
                labels.append(instr.text[0])

        # Map segments (instruction_idx -> label_idx, drop controlled_by/score/is_composite)
        segments = [
            {
                "start_time": seg.start_time,
                "end_time": seg.end_time,
                "label_idx": seg.instruction_idx,
                "success": seg.success,
            }
            for seg in metadata.run.segments
        ]

        # Derive episode from segments and run data
        if metadata.run.segments:
            episode_start = metadata.run.segments[0].start_time
            episode_end = metadata.run.segments[-1].end_time
            episode_success = all(seg.success for seg in metadata.run.segments)
        else:
            episode_start = 0.0
            episode_end = 0.0
            episode_success = False

        episode = {
            "start_time": episode_start,
            "end_time": episode_end,
            "success": episode_success,
            "label": getattr(metadata.run, "episode_label", None) or "",
        }

        # Devices: no v1.3 equivalent, default to empty list
        devices = []

        new_data = {
            "$schema": SCHEMA_URI,
            "schema_version": "2.0",
            "uuid": metadata.uuid,
            "robot": robot,
            "files": files,
            "environment": environment,
            "runner": runner,
            "devices": devices,
            "programs": programs,
            "episode": episode,
            "labels": labels,
            "segments": segments,
        }

        logger.info("Converting MetadataV1_3 to MetadataV2_0...")
        return cls.from_dict(new_data, extra_keys=extra_keys)
