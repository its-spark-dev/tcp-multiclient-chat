# TCP Multiclient Chat

A four-person CSE 3461 Python networking project using the standard library.

## Implementation Status

- **Feature 1 — Broadcast Messaging:** implemented and integrated. Ordinary messages go to every other registered client, identified by sender username.
- **Feature 2A — Username Registration and Client Management:** implemented and integrated. Registration requires a unique, case-sensitive username of 1–24 ASCII letters, digits or underscores. Rejected usernames can be retried.
- **Feature 2B — Private Messaging:** implemented and integrated. `@username message` goes only to that recipient. Unknown targets, missing message bodies and self-messages produce sender-only errors.
- **Feature 3 — Network Condition Simulation:** implemented, tested and integrated into the server user-message send path. Artificial latency, artificial jitter and application-level simulated message loss apply independently per intended recipient. Registration, validation errors and other control messages bypass impairment.

Localhost integration is verified. Final over-the-air tests between teammates' computers, report measurements and the demonstration remain team tasks.

## Team Responsibilities

- **Jiho — Feature 1: Broadcast Messaging:** implement broadcast communication through the central TCP server.
- **Sumanth — Feature 2A: Username Registration and Client Management:** handle username registration, username/client mappings, and related connection management.
- **Sean — Feature 2B: Private Message Routing and Handling:** implement `@username` private-message parsing, routing, and related handling; also help polish the final report and presentation/demo video.
- **Sang — Feature 3: Network Condition Simulation and Performance Metrics:** simulate latency, jitter, and application-level message loss, and measure their performance impact.

All team members will participate in the final demonstration, and each implementation owner will document their technical contribution for the report.

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

Example impaired server:

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

## Feature 3 Measurements

On shutdown, the server prints delivery attempts, simulated drops, simulator passes, socket send successes/failures, artificial delay statistics and effective throughput. Each intended recipient counts as one attempt. Socket send success means `sendall` completed; it does not confirm receipt or display by the remote client. There is no ACK protocol.

Application-level simulated message loss is not actual TCP packet loss. Effective throughput is successful server sends per elapsed second, not actual network throughput. See [Feature 3 documentation](docs/feature3.md) for exact definitions and limitations.

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
│   ├── protocol.py               # shared newline framing
│   ├── network_conditions.py     # reusable Feature 3 simulator
│   ├── send_metrics.py           # integrated send-path counters
│   ├── feature3_experiment.py    # standalone experiment
│   └── feature2a.py              # historical Feature 2A/2B implementation
├── Feature 1 Server.py           # historical individual server
├── Feature 1 client.py           # historical individual client
├── tests/
│   ├── test_chat.py
│   └── test_network_conditions.py
├── docs/
│   └── feature3.md
├── README.md
└── .gitignore
```

Historical files preserve teammates' original contributions and are separate earlier implementations. Use `src/server.py` and `src/client.py` for the unified application.

## Development and Testing

Collaborate through feature branches and reviewed pull requests. The integration combines the original Feature 1 broadcast/threading design with Feature 2A registration and Feature 2B routing, and reuses Feature 3's simulator.

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
git diff --check
```

The suite includes deterministic simulator tests and actual localhost three-client smoke tests for baseline/impaired operation, registration, framing, broadcast/private isolation, errors and cleanup. Preliminary test metrics are not final report measurements.
