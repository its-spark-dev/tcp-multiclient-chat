# Feature 3 — Network Condition Simulation

## Objective

Feature 3 evaluates how controlled, artificial network conditions affect message delivery time and effective throughput. The experiment is designed to be repeatable and to provide measurements that can be compared before and after the feature is integrated with the chat application.

## Design

The simulator is a small, reusable application-level component in `src/network_conditions.py`. For each attempted message, it first determines whether the message is lost. If the message is delivered, it calculates a non-negative delay from the configured latency and jitter, waits for that delay, and returns the delivery result. `src/feature3_experiment.py` applies the component to a configurable number of messages and summarizes the outcomes. An optional random seed supports reproducible loss and jitter decisions.

## Simulated Conditions

- **Artificial latency:** a fixed delay applied to each delivered message.
- **Artificial jitter:** a random positive or negative variation around the configured latency; the final delay is clamped at zero.
- **Application-level simulated message loss:** a configured probability that an attempted message is dropped before delivery.

These conditions are simulated in the application and are not integrated into the chat client or server yet.

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

## Experimental Method

The experiment compares a zero-impairment baseline with a selected impaired condition. Both runs attempt the same number of messages. The impaired run is configured with artificial latency, artificial jitter, and application-level simulated message loss. The command supports `--messages`, `--latency-ms`, `--jitter-ms`, `--loss-rate`, and `--seed`; `--compare-baseline` enables the baseline comparison. Final integrated measurements should use the same message count and configuration across comparable runs.

## Example Results Table

Replace the placeholders below with measurements from the final integrated experiment. Do not treat the effective-throughput column as actual network throughput.

| Condition | Messages attempted | Delivered | Dropped | Delivery rate | Average delay (ms) | Effective throughput (simulated messages/sec) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | `[N]` | `[N]` | `[N]` | `[N%]` | `[N.N]` | `[N.N]` |
| Impaired | `[N]` | `[N]` | `[N]` | `[N%]` | `[N.N]` | `[N.N]` |

## Limitations

Application-level simulated message loss is not actual TCP packet loss and does not model TCP retransmissions or other transport-layer behavior. Before integration, the experiment also does not measure actual network throughput: its effective-throughput value is based on simulated delivery timing. Results may additionally differ from a real network because the simulator does not reproduce every operating-system, network-path, or congestion effect.

## Integration Plan

After Features 1 and 2 are merged, the chat send path can call `NetworkConditions.apply(message)` before `socket.sendall(...)`. The caller will send only when the result indicates delivery. The module should remain separate from username management, private-message routing, and broadcast logic so it can be enabled for controlled comparisons during final localhost and over-the-air testing.

## Generative AI Assistance

Generative AI tools were used to help refine the design of the network-condition simulator, suggest a modular implementation structure, generate and review unit-test cases, verify terminology for application-level simulated message loss, and improve the clarity of the Feature 3 documentation. Final design decisions, implementation review, and validation were performed by the team.

## Report-ready Summary

Feature 3 provides a modular application-level simulation of artificial latency, artificial jitter, and application-level simulated message loss. A repeatable experiment compares a zero-impairment baseline with a selected impaired condition using delivery counts, delay statistics, and effective throughput measured in simulated delivered messages per second. Because the simulator is not itself connected to the chat application's socket send path, these results do not represent actual TCP packet loss or actual network throughput. The module is intended for integration after the broadcast and private-messaging features are merged, at which point the team can perform controlled end-to-end comparisons.
