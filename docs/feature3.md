# Feature 3 — Network Condition Simulation

## Objective

Feature 3 studies communication behavior under artificial latency, artificial jitter and application-level simulated message loss. It is integrated into the chat server and records server-send-path outcomes, requested artificial delays and effective throughput. The team has completed the recorded demonstration and supplied the results below.

## Design

The simulator is a small, reusable application-level component in `src/network_conditions.py`. For each attempt, it first decides whether to simulate a drop. A simulator pass receives a non-negative artificial delay before the caller attempts socket sending. `src/feature3_experiment.py` also runs the component independently of sockets and summarizes simulated outcomes. An optional random seed supports reproducible loss and jitter decisions for a fixed call order.

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
- average requested artificial delay for simulator passes
- minimum and maximum requested artificial delay for simulator passes
- effective throughput, expressed as simulated delivered messages per second

## Experimental Method

The standalone runner supports `--messages`, `--latency-ms`, `--jitter-ms`, `--loss-rate`, and `--seed`; `--compare-baseline` runs a zero-impairment baseline and an impaired condition with the same message count. For additional integrated comparisons, use the same workload and client arrangement while changing only the impairment settings.

For integrated runs, use the server commands in README, keep client count, recipients, workload and timing comparable, then stop the server with Ctrl+C to capture its summary. Count per-recipient attempts rather than sender input lines. Repeat runs and record configuration, seed and test environment. A seed reproduces decisions for the same call order; concurrent scheduling can change which recipient gets each decision. Timing varies with the operating system even with a fixed seed.

## Recorded Demonstration Results

The team supplied the following integrated server output from its Feature 3 demonstration. Values are transcribed without replacing them with later automated test results.

| Output metric | Recorded value |
| --- | ---: |
| `delivery_attempts` | 96 |
| `simulated_drops` | 16 |
| `simulator_passes` | 80 |
| `socket_send_successes` | 80 |
| `socket_send_failures` | 0 |
| `server_send_delivery_rate` | 0.8333333333333334 |
| `average_artificial_delay_ms` | 49.280207984262816 |
| `min_artificial_delay_ms` | 40.12997519356122 |
| `max_artificial_delay_ms` | 59.92242760480194 |
| `elapsed_seconds` | 16.71994487498887 |
| `effective_throughput` | 4.784704770149744 |

The accounting is consistent: 96 attempts = 16 drops + 80 passes, and 80 passes = 80 socket send successes + 0 failures. The server-send delivery rate was **83.33%**, and the observed simulated-drop proportion was **16.67%** of recipient attempts. All simulator passes completed socket sending. Mean artificial delay was **49.28 ms**, ranging from **40.13 to 59.92 ms**. Effective throughput was approximately **4.785 successful sends/sec** over **16.720 seconds**, including inter-message gaps.

The supplied output does not include the configured latency, jitter, loss probability, seed, client count, operating systems or network setup. The observed drop proportion is not the configured loss probability. No matching baseline measurements were supplied, so these results establish the recorded impaired run's outcomes, not a quantified change from baseline. The commands in README and the network testing guide are examples rather than a reconstruction of this run.

## Limitations

Application-level simulated message loss is not actual TCP packet loss and does not model TCP retransmissions or other transport-layer behavior. Neither experiment measures actual network throughput. The standalone experiment counts simulator passes as delivered; the integrated server separately counts socket send outcomes. Neither confirms remote receipt. Delays block each sending worker, so a broadcast's recipients are processed sequentially; this is a simple send-path simulation, not a full network model. Slow recipients can delay a worker. Shutdown waits for in-flight artificial delays to finish. Use modest delay values for demonstrations.

## Integration

The unified `src/server.py` calls `NetworkConditions.apply(message)` once per intended recipient before sending user chat text. Drops skip sending; passes proceed to the recipient's send lock and socket. `src/send_metrics.py` records outcomes independently of control traffic. Impairment defaults to zero and can be enabled using server CLI options. Integration is complete, and the team's recorded demo measurements are presented above.

## Generative AI Assistance

Generative AI tools were used to help refine the design of the network-condition simulator, suggest a modular implementation structure, generate and review unit-test cases, verify terminology for application-level simulated message loss, and improve the clarity of the Feature 3 documentation. Final design decisions, implementation review, and validation were performed by the team.

## Technical Summary

Feature 3 provides a modular application-level simulation of artificial latency, artificial jitter, and application-level simulated message loss in the integrated chat server. In the recorded demonstration, 96 recipient delivery attempts produced 16 simulated drops and 80 successful socket sends, with no socket send failures. The server-send delivery rate was 83.33%, mean artificial delay was 49.28 ms, and effective throughput was approximately 4.785 successful sends per second. These measurements characterize the server send path and do not establish remote receipt, actual TCP packet loss or actual network throughput. A baseline reduction cannot be quantified from this run alone.
