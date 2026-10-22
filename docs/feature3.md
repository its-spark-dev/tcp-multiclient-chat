# Feature 3 — Network Condition Simulation

## Objective

Feature 3 evaluates how controlled, artificial network conditions affect message delivery time and effective throughput. The experiment is designed to be repeatable and to provide measurements that can be compared before and after the feature is integrated with the chat application.

## Design

The simulator is a small, reusable application-level component in `src/network_conditions.py`. For each attempted message, it first determines whether the message is lost. If the message is delivered, it calculates a non-negative delay from the configured latency and jitter, waits for that delay, and returns the delivery result. `src/feature3_experiment.py` applies the component to a configurable number of messages and summarizes the outcomes. An optional random seed supports reproducible loss and jitter decisions.

## Simulated Conditions

- **Artificial latency:** a fixed delay applied to each delivered message.
- **Artificial jitter:** a random positive or negative variation around the configured latency; the final delay is clamped at zero.
- **Application-level simulated message loss:** a configured probability that an attempted message is dropped before delivery.

These conditions are integrated into the server send path for user chat messages. Each broadcast recipient has a separate impairment decision; private messages have one intended recipient. Registration, setup and server-generated validation/error messages bypass impairment.

## Metrics

### Integrated server send path

The integrated server prints a cumulative summary on shutdown:

- **Delivery attempts:** one per intended recipient of a valid user message.
- **Simulated drops:** attempts rejected by the simulator, without socket sending.
- **Simulator passes:** attempts allowed through the simulator.
- **Socket send successes / failures:** simulator passes for which `sendall` completes / raises a socket error.
- **Server-send delivery rate:** socket send successes divided by delivery attempts (fraction from 0 to 1).
- **Artificial delay statistics:** mean, minimum and maximum configured artificial delay across simulator passes, including subsequent socket failures. These are requested delays, not measured end-to-end latency; unavailable statistics are printed as `None`.
- **Elapsed time:** wall-clock interval from the first attempt to the last completed outcome; includes gaps between messages, waiting and processing.
- **Effective throughput:** socket send successes divided by that elapsed time, in messages/sec. Zero is reported if the interval is zero.

At quiescence, attempts = drops + passes and passes = socket send successes + socket send failures. Socket send success does not establish remote receipt or display; no ACK protocol is used.

### Standalone experiment

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

For integrated runs, use the server commands in README, keep client count, recipients, workload and timing comparable, then stop the server with Ctrl+C to capture its summary. Count per-recipient attempts rather than sender input lines. Repeat runs and record configuration, seed and test environment. A seed reproduces decisions for the same call order; concurrent scheduling can change which recipient gets each decision. Timing varies with the operating system even with a fixed seed.

## Example Results Table

Replace the placeholders below with measurements from the final integrated experiment. Do not treat the effective-throughput column as actual network throughput.

| Condition | Recipient attempts | Socket send successes | Simulated drops | Server-send delivery rate | Mean artificial delay (ms) | Effective throughput (successful sends/sec) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Baseline | `[N]` | `[N]` | `[N]` | `[N%]` | `[N.N]` | `[N.N]` |
| Impaired | `[N]` | `[N]` | `[N]` | `[N%]` | `[N.N]` | `[N.N]` |

## Limitations

Application-level simulated message loss is not actual TCP packet loss and does not model TCP retransmissions or other transport-layer behavior. Neither experiment measures actual network throughput. The standalone experiment counts simulator passes as delivered; the integrated server separately counts socket send outcomes. Neither confirms remote receipt. Delays block each sending worker, so a broadcast's recipients are processed sequentially; this is a simple send-path simulation, not a full network model. Slow recipients can delay a worker. Shutdown waits for in-flight artificial delays to finish. Use modest delay values for demonstrations.

## Integration

The unified `src/server.py` calls `NetworkConditions.apply(message)` once per intended recipient before sending user chat text. Drops skip sending; passes proceed to the recipient's send lock and socket. `src/send_metrics.py` records outcomes independently of control traffic. Impairment defaults to zero and can be enabled using server CLI options. Final over-the-air testing and report measurements remain to be performed by the team.

## Generative AI Assistance

Generative AI tools were used to help refine the design of the network-condition simulator, suggest a modular implementation structure, generate and review unit-test cases, verify terminology for application-level simulated message loss, and improve the clarity of the Feature 3 documentation. Final design decisions, implementation review, and validation were performed by the team.

## Report-ready Summary

Feature 3 provides a modular application-level simulation of artificial latency, artificial jitter, and application-level simulated message loss in the integrated chat server. Baseline and impaired conditions can be compared using per-recipient delivery attempts, simulated drops, socket send outcomes, artificial delay statistics and effective throughput. The measurements characterize the server send path and do not establish remote receipt, actual TCP packet loss or actual network throughput. Final experimental results will be recorded after the team's controlled network tests.
