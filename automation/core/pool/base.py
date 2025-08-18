from typing import Dict, Literal
from threading import Lock
from automation.core.utils import SingletonPool
from conf.settings import Settings, Modules
from automation.core.driver.base import ChromeDriver
from datetime import datetime
import random
from utils.logging import JobStreamerLogger


SETTINGS = Settings()
logger = JobStreamerLogger().get_logger()


class InstancesPool:
    """
    The Pool is used for storing instances and reusing free instances.
    """

    _pools: Dict[str, SingletonPool] = {}
    _singleton_pool: SingletonPool[ChromeDriver] = SingletonPool[ChromeDriver]
    INSTANCE_LIMIT: int = SETTINGS.SE_NODE_MAX_SESSIONS
    _lock: Lock = Lock()
    driver_class = ChromeDriver

    def __new__(cls, module_name: Modules) -> ChromeDriver:
        """
        Create or get an instance of the pool.
        """
        return cls._extract_instance(module_name)

    @classmethod
    def create_instance(cls) -> ChromeDriver:
        """
        Create a new driver instance.
        """
        driver_options = [
            "--remote-debugging-pipe",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--disable-extensions",
        ]
        return cls.driver_class.initailize_driver(driver_options)

    @classmethod
    def _extract_instance(cls, module_name: Modules) -> ChromeDriver:
        """
        Extract an instance from the pool or create a new one.
        This method is thread safe.
        """
        cls._clear_old_instances()
        with cls._lock:
            pool_key = f"{module_name}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            pool_length = len(cls._pools)
            logger.info(f"Pool length: {pool_length}")

            if pool_length >= cls.INSTANCE_LIMIT:
                # look for a free instance
                logger.info(
                    f"Looking for a free instance in the pool of {pool_length} instances"
                )
                for _, instance in cls._pools.items():
                    if not instance.lock.locked():
                        with instance.lock:
                            return instance.driver_instance
                else:
                    # if no free instance, select a random instance
                    logger.info(f"No free instance found, selecting a random instance")
                    random_instance = random.choice(list(cls._pools.values()))
                    return random_instance.driver_instance
            # create a new instance
            logger.info(f"Creating a new instance for {module_name}")
            instance = cls.create_instance()
            cls._pools[pool_key] = SingletonPool[ChromeDriver](
                driver_instance=instance, created_at=datetime.now(), lock=Lock()
            )
            return instance

    @classmethod
    def _clear_old_instances(cls) -> None:
        """
        Clear old instances from the pool.
        """
        with cls._lock:
            for key, instance in cls._pools.items():
                if (
                    datetime.now() - instance.created_at
                ).total_seconds() > SETTINGS.SE_NODE_SESSION_TIMEOUT:
                    logger.info(f"Clearing old instance {key}")
                    cls._pools.pop(key)
