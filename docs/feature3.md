# Network Condition Simulation

## Objective

The network-condition simulator studies communication behavior under artificial latency, artificial jitter and application-level simulated message loss. It is integrated into the chat server and records server-send-path outcomes, requested artificial delays and effective throughput. A reproducible workload is described below, separately from the original recorded measurements.

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

## Reproducible Server Experiment

This example fixes the configuration and traffic sequence; it is not a reconstruction of the original recorded demonstration or a promise of particular benchmark output. Use the same Python version for repeat runs. Run commands from the repository root, stop any earlier server on port `5001`, and do not connect other clients during this workload.

### Start a Fresh Impaired Server

In one terminal:

```bash
python3 src/server.py --host 127.0.0.1 --port 5001 \
  --latency-ms 50 --jitter-ms 10 --loss-rate 0.2 --seed 42
```

| Setting | Value and meaning |
| --- | --- |
| Artificial latency | 50 ms per simulator pass |
| Artificial jitter | Uniform variation from -10 to +10 ms; requested delays are therefore 40–60 ms |
| Application-level simulated message loss | Probability 0.2 per intended recipient attempt |
| Random seed | 42 |
| Workload | 20 numbered private messages from one sender to one registered recipient |

Registration and control errors bypass impairment. Keeping exactly one sending worker and one intended recipient fixes the simulator call order. Restart the server before each repetition to reset the seed and cumulative counters.

### Generate the Traffic

In a second terminal, run this standard-library client workload. It registers both sockets, keeps the recipient open, and sends 20 complete newline-delimited private-message frames. The final unknown-target error is a processing barrier: the same sender worker returns it only after processing the preceding 20 messages. It is a control response, not a delivery acknowledgement.

```bash
python3 - <<'PY'
from contextlib import ExitStack
import socket

with ExitStack() as stack:
    def register(name):
        connection = stack.enter_context(
            socket.create_connection(("127.0.0.1", 5001), timeout=5))
        replies = stack.enter_context(connection.makefile("rb"))
        assert b"Enter username" in replies.readline()
        connection.sendall((name + "\n").encode("utf-8"))
        assert b"Registered: " + name.encode("utf-8") in replies.readline()
        return connection, replies

    recipient, _ = register("Receiver")
    sender, replies = register("Sender")
    for number in range(1, 21):
        sender.sendall(f"@Receiver sample-{number:02d}\n".encode("utf-8"))

    sender.sendall(b"@Missing workload-complete\n")
    assert replies.readline() == b"[Server] User 'Missing' not found.\n"
    print("20 private-message attempts processed; stop the server to see metrics.")
    sender.sendall(b"/quit\n")
    recipient.sendall(b"/quit\n")
PY
```

The receiver is deliberately kept open without reading chat payloads; this workload measures the server send path, not recipient display or end-to-end delivery. The small workload fits ordinary socket buffers. Socket failures are still possible and must be reported rather than counted as simulated drops. A timeout or failed assertion means the workload did not complete as specified; investigate it instead of interpreting partial counters as a complete run.

### Observe and Interpret the Summary

After the workload finishes, press Ctrl+C in the server terminal. Observe:

- `delivery_attempts`: 20 for a completed run on a fresh server; one recipient per private message. Registration, the processing barrier, and `/quit` do not add attempts.
- `simulated_drops` and `simulator_passes`: their sum should equal the attempts after processing completes. A configured loss probability of 0.2 does not imply exactly four drops out of 20.
- `socket_send_successes` and `socket_send_failures`: their sum should equal simulator passes. A socket-send success is not proof of remote application receipt; this workload does not read the chat payloads or send receipt acknowledgements.
- `average_artificial_delay_ms`, `min_artificial_delay_ms`, and `max_artificial_delay_ms`: requested artificial delays across simulator passes, within 40–60 ms for these settings. These are not measured end-to-end latencies; if all attempts drop, the delay statistics are `None`.
- `server_send_delivery_rate`: successful socket sends divided by all recipient attempts, including simulated drops and socket failures.
- `elapsed_seconds` and `effective_throughput`: the interval from first attempt to last recorded outcome and successful sends per second over that interval. Effective throughput is not physical network throughput or a link-bandwidth measurement.

With the same Python version, seed, and simulator call order, the random decisions and requested delays are repeatable. Operating-system scheduling, socket outcomes, elapsed time, and effective throughput are not guaranteed to match. No measured result table is asserted for this example; the historical measurements below remain a separate run with incomplete configuration information.

For a baseline comparison, stop the impaired server, start a fresh zero-impairment server with the following command, and run the identical traffic snippet again:

```bash
python3 src/server.py --host 127.0.0.1 --port 5001 \
  --latency-ms 0 --jitter-ms 0 --loss-rate 0 --seed 42
```

Capture both summaries with the Git commit and Python/OS versions, and repeat runs before drawing performance conclusions. Do not infer a baseline reduction from the older recorded measurements, which lack a matching baseline.

## Recorded Demonstration Results

The team supplied the following integrated server output from its network-condition simulation demonstration. Values are transcribed without replacing them with later automated test results.

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

Generative AI tools were used to help refine the design of the network-condition simulator, suggest a modular implementation structure, generate and review unit-test cases, verify terminology for application-level simulated message loss, and improve the clarity of the network-condition simulation documentation. Final design decisions, implementation review, and validation were performed by the team.

## Technical Summary

The simulator provides a modular application-level simulation of artificial latency, artificial jitter, and application-level simulated message loss in the integrated chat server. In the recorded demonstration, 96 recipient delivery attempts produced 16 simulated drops and 80 successful socket sends, with no socket send failures. The server-send delivery rate was 83.33%, mean artificial delay was 49.28 ms, and effective throughput was approximately 4.785 successful sends per second. These measurements characterize the server send path and do not establish remote receipt, actual TCP packet loss or actual network throughput. A baseline reduction cannot be quantified from this run alone.
