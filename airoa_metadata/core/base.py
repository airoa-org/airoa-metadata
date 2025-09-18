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
