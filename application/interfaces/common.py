from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional

from application.dataclasses import LoopInfo
from application.dataclasses.common import MethodInfo, PlatformInfo


class LoopsRepo(ABC):

    @abstractmethod
    def get_loop_by_id(self, loop_id: int) -> List[LoopInfo]:
        ...

    @abstractmethod
    def get_curses_by_currency_name(
            self,
            cur_from: str,
            cur_to: str,
            platform_id: int,
            method_id: int
    ) -> Optional[float]:
        ...

    @abstractmethod
    def save_loop_info(
            self,
            loop_id: int,
            spread: float,
            max_flow: float,
            loop_speed: float,
            added: datetime
    ) -> None:
        ...

    @abstractmethod
    def check_status(self, key: str) -> bool:
        ...

    @abstractmethod
    def get_method_info(self, method_name: str) -> Optional[MethodInfo]:
        ...

    @abstractmethod
    def get_platform_info(self, platform_name: str) -> Optional[PlatformInfo]:
        ...
