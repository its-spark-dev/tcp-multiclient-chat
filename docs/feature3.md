# Feature 3 — Network Condition Simulation

## Objective

Feature 3 studies how artificial network conditions affect message delivery time and effective throughput in a repeatable experiment. The standalone experiment does not measure actual network throughput because it is not connected to the chat application's socket send path.

## Simulated Conditions

- **Latency:** a fixed artificial delay applied to each delivered message.
- **Jitter:** a random positive or negative variation around the configured latency, clamped so the final delay is never negative.
- **Application-level message loss:** a configured probability that an attempted message is dropped before delivery.

These conditions are implemented in `src/network_conditions.py` and are not integrated into the chat client or server yet.

## Metrics

The experiment reports:

- messages attempted
- messages delivered
- messages dropped
- delivery rate
- total elapsed time
- average delay for delivered messages
- minimum and maximum delay for delivered messages
- effective throughput, expressed as simulated delivered messages per second

## Baseline vs Impaired Experiment

Run `python3 src/feature3_experiment.py --compare-baseline` to compare a zero-impairment baseline with the configured experiment. Use `--messages`, `--latency-ms`, `--jitter-ms`, `--loss-rate`, and `--seed` to configure an experiment. A fixed seed makes loss and jitter decisions reproducible. The reported effective throughput is simulated delivery throughput, not actual network throughput.

## Important Limitation

Simulated message loss occurs at the application level. It is not actual TCP packet loss and does not simulate TCP retransmissions or other transport-layer packet behavior. Use terms such as *simulated message loss*, *artificial latency*, and *artificial jitter* in the report.

## Integration

After Features 1 and 2 are integrated, the chat send path can call `NetworkConditions.apply(message)` before `socket.sendall(...)`. The caller can send only when the returned result indicates that the message was delivered. This module remains independent so it can be tested and evaluated before that integration.

## Generative AI Assistance

TODO: Add the team's final explanation of how generative AI contributed to Feature 3 after the implementation and report work are complete.
