"""
Project-wide thread pool manager.

All background work that needs a thread should go through this module.
Using a bounded ThreadPoolExecutor prevents unbounded thread creation,
controls concurrency, and gives a single shutdown point.

Usage
-----
    from utils.thread_manager import thread_manager

    future = thread_manager.submit(my_function, arg1, arg2)

    # optional: block until done and retrieve result / exception
    result = future.result(timeout=30)

Configuration
-------------
The pool size is read from the environment variable THREAD_POOL_SIZE
(default: 4).  This is intentionally kept small — the project's work is
I/O-heavy (browser automation, LLM calls, DB writes) and does not benefit
from a large pool.

Lifecycle
---------
The pool is started lazily on first use and shut down cleanly on process
exit via an atexit handler.  It can also be shut down explicitly by calling
thread_manager.shutdown().
"""
from __future__ import annotations

import atexit
import os
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any, Callable

from utils.logging import JobStreamerLogger

logger = JobStreamerLogger().get_logger()

_DEFAULT_POOL_SIZE = 4


class ThreadManager:
    """
    Singleton wrapper around a bounded ThreadPoolExecutor.

    Attributes
    ----------
    max_workers : int
        Maximum number of concurrent threads in the pool.
    active_count : int
        Number of futures currently running or queued.
    """

    _instance: ThreadManager | None = None

    def __new__(cls) -> ThreadManager:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialise()
        return cls._instance

    def _initialise(self) -> None:
        self.max_workers: int = int(
            os.getenv("THREAD_POOL_SIZE", _DEFAULT_POOL_SIZE)
        )
        self._pool = ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="job-streamer",
        )
        self._active_count = 0
        logger.info(
            f"[ThreadManager] Pool initialised with max_workers={self.max_workers}"
        )
        atexit.register(self.shutdown)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit(self, fn: Callable, /, *args: Any, **kwargs: Any) -> Future:
        """
        Submit *fn* to the thread pool and return a Future.

        The pool is bounded — if all workers are busy, the task queues and
        waits for a free slot rather than spawning a new thread.

        Raises
        ------
        RuntimeError
            If the pool has been shut down.
        """
        if self._pool._shutdown:  # type: ignore[attr-defined]
            raise RuntimeError(
                "ThreadManager pool has been shut down. Cannot submit new tasks."
            )

        self._active_count += 1
        logger.debug(
            f"[ThreadManager] Submitting task '{fn.__name__}' "
            f"(active={self._active_count}/{self.max_workers})"
        )

        future = self._pool.submit(self._wrap(fn, *args, **kwargs))
        future.add_done_callback(self._on_done)
        return future

    def shutdown(self, wait: bool = True) -> None:
        """
        Shut down the pool gracefully.

        Parameters
        ----------
        wait : bool
            If True (default), block until all running tasks finish before
            returning.  Pass False for a best-effort immediate shutdown.
        """
        if not self._pool._shutdown:  # type: ignore[attr-defined]
            logger.info(
                f"[ThreadManager] Shutting down pool "
                f"(wait={wait}, active≈{self._active_count})"
            )
            self._pool.shutdown(wait=wait)

    @property
    def active_count(self) -> int:
        """Approximate number of tasks currently submitted (running + queued)."""
        return self._active_count

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _wrap(self, fn: Callable, /, *args: Any, **kwargs: Any) -> Callable:
        """Return a zero-argument callable that runs fn with error logging."""
        def _task():
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                logger.exception(
                    f"[ThreadManager] Unhandled exception in task '{fn.__name__}': {exc}"
                )
                raise  # re-raise so future.exception() / future.result() still works

        _task.__name__ = fn.__name__
        return _task

    def _on_done(self, future: Future) -> None:
        """Callback invoked when a submitted task finishes (success or error)."""
        self._active_count = max(0, self._active_count - 1)
        if future.cancelled():
            logger.debug("[ThreadManager] A task was cancelled.")
        elif future.exception():
            logger.error(
                f"[ThreadManager] Task finished with exception: {future.exception()}"
            )
        else:
            logger.debug("[ThreadManager] Task finished successfully.")


# Singleton instance — import this everywhere instead of creating raw threads.
thread_manager = ThreadManager()
