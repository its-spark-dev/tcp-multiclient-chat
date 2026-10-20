"""Run a repeatable application-level network condition experiment."""

import argparse
import time

from network_conditions import NetworkConditions


def non_negative_float(value):
    """Parse a non-negative command-line float."""
    number = float(value)
    if number < 0:
        raise argparse.ArgumentTypeError("must be non-negative")
    return number


def loss_rate(value):
    """Parse a loss rate between zero and one."""
    number = float(value)
    if not 0 <= number <= 1:
        raise argparse.ArgumentTypeError("must be between 0 and 1")
    return number


def parse_args():
    """Parse experiment settings."""
    parser = argparse.ArgumentParser(description="Run Feature 3 network condition experiments.")
    parser.add_argument("--messages", type=int, default=100, help="messages to attempt")
    parser.add_argument("--latency-ms", type=non_negative_float, default=50.0)
    parser.add_argument("--jitter-ms", type=non_negative_float, default=10.0)
    parser.add_argument("--loss-rate", type=loss_rate, default=0.1)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--compare-baseline", action="store_true",
                        help="run a zero-impairment baseline before the configured run")
    arguments = parser.parse_args()
    if arguments.messages <= 0:
        parser.error("--messages must be greater than 0")
    return arguments


def run_experiment(messages, latency_ms, jitter_ms, loss_rate_value, seed=None):
    """Run an experiment and return its measured metrics."""
    conditions = NetworkConditions(latency_ms, jitter_ms, loss_rate_value, seed)
    delivered = 0
    delays = []
    start = time.perf_counter()

    for message_number in range(messages):
        result = conditions.apply(message_number)
        if result.delivered:
            delivered += 1
            delays.append(result.delay_ms)

    elapsed = time.perf_counter() - start
    dropped = messages - delivered
    return {
        "attempted": messages,
        "delivered": delivered,
        "dropped": dropped,
        "delivery_rate": delivered / messages,
        "elapsed_seconds": elapsed,
        "average_delay_ms": sum(delays) / len(delays) if delays else 0.0,
        "min_delay_ms": min(delays) if delays else 0.0,
        "max_delay_ms": max(delays) if delays else 0.0,
        "effective_throughput": delivered / elapsed if elapsed else 0.0,
    }


def print_summary(label, metrics):
    """Print metrics in a report-friendly format."""
    print(label)
    print("-" * len(label))
    print(f"Messages attempted: {metrics['attempted']}")
    print(f"Messages delivered: {metrics['delivered']}")
    print(f"Messages dropped: {metrics['dropped']}")
    print(f"Delivery rate: {metrics['delivery_rate']:.2%}")
    print(f"Average delay: {metrics['average_delay_ms']:.2f} ms")
    print(f"Min delay: {metrics['min_delay_ms']:.2f} ms")
    print(f"Max delay: {metrics['max_delay_ms']:.2f} ms")
    print(f"Effective throughput (simulated delivery): "
          f"{metrics['effective_throughput']:.2f} messages/sec")
    print(f"Total elapsed time: {metrics['elapsed_seconds']:.3f} sec")


def main():
    arguments = parse_args()
    if arguments.compare_baseline:
        baseline = run_experiment(arguments.messages, 0, 0, 0, arguments.seed)
        print_summary("Baseline Experiment", baseline)
        print()

    impaired = run_experiment(arguments.messages, arguments.latency_ms,
                               arguments.jitter_ms, arguments.loss_rate,
                               arguments.seed)
    print_summary("Feature 3 Network Condition Experiment", impaired)


if __name__ == "__main__":
    main()
