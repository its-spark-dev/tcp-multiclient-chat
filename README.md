# TCP Multiclient Chat

A four-person CSE 3461 Python networking project using the standard library.

## Implementation Status

- **Feature 1 — Broadcast Messaging:** implemented and integrated. Ordinary messages go to every other registered client, identified by sender username.
- **Feature 2A — Username Registration and Client Management:** implemented and integrated. Registration requires a unique, case-sensitive username of 1–24 ASCII letters, digits or underscores. Rejected usernames can be retried.
- **Feature 2B — Private Messaging:** implemented and integrated. `@username message` goes only to that recipient. Unknown targets, missing message bodies and self-messages produce sender-only errors.
- **Feature 3 — Network Condition Simulation:** implemented, tested and integrated into the server user-message send path. Artificial latency, artificial jitter and application-level simulated message loss apply independently per intended recipient. Registration, validation errors and other control messages bypass impairment.

Localhost integration is verified by automated tests, and the team has completed its recorded group demonstration. The recorded Feature 3 server-send-path results are documented in [docs/feature3.md](docs/feature3.md). The network testing guide remains available for repeating the checks.

Team-provided [demonstration recording](https://drive.google.com/file/d/197RvJehJyeoTg7UpOCVCWLBoGXtqvAN_/view). Confirm that evaluators can view and download the recording using the shared link.

## Team Responsibilities

- **Jiho — Feature 1: Broadcast Messaging:** implement broadcast communication through the central TCP server.
- **Sumanth — Feature 2A: Username Registration and Client Management:** handle username registration, username/client mappings, and related connection management.
- **Sean — Feature 2B: Private Message Routing and Handling:** implement `@username` private-message parsing, routing, and related handling; also help polish the final report and presentation/demo video.
- **Sang — Feature 3: Network Condition Simulation and Performance Metrics:** simulate latency, jitter, and application-level message loss, and measure their performance impact.

The team has recorded its group demonstration. Each implementation owner's technical contribution should also be described in the accompanying project report.

## Running the Integrated Application

Baseline server (default: `127.0.0.1:5000`, zero impairment):

```bash
python3 src/server.py
```

In each client terminal:

```bash
python3 src/client.py
```

Enter a username when prompted. Send ordinary text for broadcast, `@Jiho hello` for a private message, and `/quit` to leave. Ctrl+C exits either application.

Example impaired server (illustrative settings, not a reconstruction of the recorded demonstration):

```bash
python3 src/server.py --latency-ms 20 --jitter-ms 5 --loss-rate 0.2 --seed 42
```

For teammates on a reachable network, bind the server to all interfaces and connect clients to the server computer's reachable IPv4 address:

```bash
python3 src/server.py --host 0.0.0.0 --port 5001
python3 src/client.py --host 192.168.1.10 --port 5001
```

Replace the example IP with the actual server address and allow the selected port through the host firewall. Run only one server on a given host/port. The terminal client's keyboard polling uses `select` on stdin, as in Feature 1; macOS/Linux terminals are supported. Windows console input has not been supported or validated.

The server uses per-client threads, newline-delimited UTF-8 framing, a locked username mapping and per-client send locks. Incomplete frames remain buffered; a trailing frame without a newline is discarded at disconnect.

### Additional Client: client2.py

`src/client2.py` is a separate, compatible terminal client contributed by the team. It preserves plain broadcast text, `@username message`, and local `/quit` handling. It accepts an optional positional server IP and always connects to port `5000`:

```bash
python3 src/server.py --host 0.0.0.0 --port 5000
python3 src/client2.py 192.168.1.10
```

Run these commands in separate server/client terminals. Omitting the IP defaults to `127.0.0.1`. Unlike `client.py`, this client has no `--host` or `--port` options. Its UTF-8 streaming and disconnect fixes preserve the message format; regression tests cover both. Windows console behavior has not been validated.

## Feature 3 Measurements

On shutdown, the server prints delivery attempts, simulated drops, simulator passes, socket send successes/failures, artificial delay statistics and effective throughput. Each intended recipient counts as one attempt. Socket send success means `sendall` completed; it does not confirm receipt or display by the remote client. There is no ACK protocol.

Application-level simulated message loss is not actual TCP packet loss. Effective throughput is successful server sends per elapsed second, not actual network throughput. See [Feature 3 documentation](docs/feature3.md) for exact definitions and limitations.

The team-provided recorded run contained 96 recipient delivery attempts, 16 simulated drops, 80 simulator passes, 80 socket send successes and no socket send failures. The server-send delivery rate was 83.33%, mean artificial delay was 49.28 ms, and effective throughput was approximately 4.785 successful sends/sec over 16.720 seconds. These are recorded demo results, distinct from automated smoke-test output. A matching baseline result and the exact recorded-run configuration were not supplied, so no baseline performance reduction is claimed.

The standalone simulator experiment remains available:

```bash
python3 src/feature3_experiment.py --messages 10 --latency-ms 20 --jitter-ms 5 --loss-rate 0.2 --seed 42 --compare-baseline
```

## Repository Structure

```text
tcp-multiclient-chat/
├── src/
│   ├── server.py                 # final integrated server
│   ├── client.py                 # final integrated interactive client
│   ├── client2.py                # additional compatible client, fixed port 5000
│   ├── protocol.py               # shared newline framing
│   ├── network_conditions.py     # reusable Feature 3 simulator
│   ├── send_metrics.py           # integrated send-path counters
│   ├── feature3_experiment.py    # standalone experiment
│   └── feature2a.py              # historical Feature 2A/2B implementation
├── Feature 1 Server.py           # historical individual server
├── Feature 1 client.py           # historical individual client
├── tests/
│   ├── test_chat.py
│   ├── test_client2.py
│   └── test_network_conditions.py
├── docs/
│   ├── feature3.md
│   └── network-testing.md
├── README.md
└── .gitignore
```

Historical files preserve teammates' original contributions and are separate earlier implementations. Use `src/server.py` and `src/client.py` for the unified application, or `src/client2.py` as the additional client on port 5000.

## Development and Testing

See [testing between teammates' computers](docs/network-testing.md) for IP setup, server/client commands, Feature 1–3 verification, and result collection.

Collaborate through feature branches and reviewed pull requests. The integration combines the original Feature 1 broadcast/threading design with Feature 2A registration and Feature 2B routing, and reuses Feature 3's simulator.

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
```

These commands work from the extracted source ZIP; no third-party dependencies are required. In a Git checkout only, `git diff --check` can additionally check whitespace changes.

The latest verification passed all 17 tests. The suite includes deterministic simulator tests, actual localhost three-client smoke tests for baseline/impaired operation, registration, framing, broadcast/private isolation, errors and cleanup, plus `client2.py` UTF-8, wire-format and shutdown regression tests. Automated test metrics are verification results, not the recorded demo measurements.
