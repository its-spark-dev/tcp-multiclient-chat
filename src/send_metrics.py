"""Thread-safe counters for user-message server send attempts only."""

import threading
import time


class SendMetrics:
    def __init__(self):
        self.lock = threading.Lock()
        self.started = None
        self.finished = None
        self.attempts = self.drops = self.passes = 0
        self.successes = self.failures = 0
        self.delay_total = 0.0
        self.delay_min = self.delay_max = None

    def attempt(self):
        with self.lock:
            if self.started is None:
                self.started = time.perf_counter()
            self.attempts += 1

    def record(self, result, success=False):
        with self.lock:
            self.finished = time.perf_counter()
            if not result.delivered:
                self.drops += 1
                return
            self.passes += 1
            self.successes += int(success)
            self.failures += int(not success)
            delay = result.delay_ms
            self.delay_total += delay
            self.delay_min = delay if self.delay_min is None else min(self.delay_min, delay)
            self.delay_max = delay if self.delay_max is None else max(self.delay_max, delay)

    def summary(self):
        with self.lock:
            elapsed = (self.finished - self.started) if self.finished is not None else 0
            return {
                "delivery_attempts": self.attempts,
                "simulated_drops": self.drops,
                "simulator_passes": self.passes,
                "socket_send_successes": self.successes,
                "socket_send_failures": self.failures,
                "server_send_delivery_rate": self.successes / self.attempts if self.attempts else 0,
                "average_artificial_delay_ms": self.delay_total / self.passes if self.passes else None,
                "min_artificial_delay_ms": self.delay_min,
                "max_artificial_delay_ms": self.delay_max,
                "elapsed_seconds": elapsed,
                "effective_throughput": self.successes / elapsed if elapsed else 0,
            }
