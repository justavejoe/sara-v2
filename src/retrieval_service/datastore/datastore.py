# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, List, Optional, TypeVar

import models


class AbstractConfig(ABC):
    kind: str


C = TypeVar("C", bound=AbstractConfig)


class classproperty:
    def __init__(self, func):
        self.fget = func

    def __get__(self, instance, owner):
        return self.fget(owner)


class Client(ABC, Generic[C]):
    @classproperty
    @abstractmethod
    def kind(cls):
        pass


    @abstractmethod
    async def initialize_data(self) -> None:
        pass

    @abstractmethod
    async def search_documents(
        self, query_embedding: list[float], top_k: int
    ) -> list[dict]:
        raise NotImplementedError("Subclass should implement this!")
async def create(config: AbstractConfig) -> Client:
    for cls in Client.__subclasses__():
        if config.kind == cls.kind:
            return await cls.create(config)  # type: ignore
    raise TypeError(f"No clients of kind '{config.kind}'")