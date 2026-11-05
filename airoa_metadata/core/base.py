# -*- coding: utf-8 -*-
# Copyright 2025-2026 AI Robot Association (AIRoA)
# SPDX-License-Identifier: Apache-2.0

import dataclasses
import json
import logging
from typing import Any, Dict, Optional, Type, TypeVar

T = TypeVar("T", bound="MetadataBase")

logger = logging.getLogger(__name__)


class MetadataBase:
    # version: str = "unknown"

    @property
    def version(self) -> str:
        return "unknown"

    def __init__(
        self, data: Dict[str, Any], extra_keys: Optional[Dict[str, Any]] = None
    ) -> None:
        # Save a copy of the data and store extra keys.
        self.data = data.copy()
        self.extra_keys = extra_keys or {}
        # Verification may have already been done externally.
        self.verify()

    def verify(self) -> None:
        """
        General verification logic.
        Subclasses can override this method.
        """
        logger.info(
            f"[VERIFY] {self.__class__.__name__} (version {self.version}) verified."
        )

    def to_json(self) -> str:
        """
        Serialize the metadata to a JSON string.
        """
        return json.dumps(dataclasses.asdict(self), indent=2)

    @classmethod
    def from_previous(
        cls: Type[T],
        previous: "MetadataBase",
        extra_keys: Optional[Dict[str, Any]] = None,
    ) -> T:
        if isinstance(previous, cls):
            return previous
        return cls.convert(previous, extra_keys=extra_keys)

    @classmethod
    def convert(
        cls: Type[T],
        metadata: "MetadataBase",
        extra_keys: Optional[Dict[str, Any]] = None,
    ) -> T:
        raise NotImplementedError("Subclasses must implement convert().")

    @classmethod
    def preceding(self) -> Type[T]:
        """
        Placeholder for automatic chaining conversions.
        """
        raise NotImplementedError("Subclasses must implement preceding.")
