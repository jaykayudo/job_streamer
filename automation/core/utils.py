import threading
from dataclasses import dataclass
from typing import Generic, Optional, TypeVar
from datetime import datetime


T = TypeVar("T")


@dataclass
class SingletonPool(Generic[T]):
    """
    Singleton pool for storing the data of a driver instance
    """

    instance: T
    created_at: Optional[datetime] = None
    lock: Optional[threading.Lock] = None
