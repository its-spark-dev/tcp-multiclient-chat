"""Application-level network condition simulation for experiment use."""

from dataclasses import dataclass
import random
import time
import math
import threading


@dataclass(frozen=True)
class DeliveryResult:
    """Outcome of applying simulated conditions to one message."""

    delivered: bool
    delay_ms: float


class NetworkConditions:
    """Apply artificial latency, jitter, and message loss to attempted messages."""

    def __init__(self, latency_ms=0.0, jitter_ms=0.0, loss_rate=0.0,
                 seed=None, sleep_func=time.sleep):
        if not math.isfinite(latency_ms) or latency_ms < 0:
            raise ValueError("latency_ms must be non-negative")
        if not math.isfinite(jitter_ms) or jitter_ms < 0:
            raise ValueError("jitter_ms must be non-negative")
        if not 0 <= loss_rate <= 1:
            raise ValueError("loss_rate must be between 0 and 1")

        self.latency_ms = float(latency_ms)
        self.jitter_ms = float(jitter_ms)
        self.loss_rate = float(loss_rate)
        self._random = random.Random(seed)
        self._sleep = sleep_func
        self._random_lock = threading.Lock()

    def apply(self, message):
        """Return a delivery result after applying conditions to ``message``."""
        del message  # The simulator measures delivery, not message contents.

        with self._random_lock:
            if self._random.random() < self.loss_rate:
                return DeliveryResult(delivered=False, delay_ms=0.0)
            jitter = self._random.uniform(-self.jitter_ms, self.jitter_ms)
        delay_ms = max(0.0, self.latency_ms + jitter)
        if delay_ms:
            self._sleep(delay_ms / 1000)
        return DeliveryResult(delivered=True, delay_ms=delay_ms)
