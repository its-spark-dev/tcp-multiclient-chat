# TCP Multiclient Chat

A small Python networking project for building a multi-client TCP chat application with a central server.

## Project Overview

This project is a small Python TCP chat application developed by a four-person team. The common TCP foundation is in place, and the feature implementations are currently maintained in separate files while development continues toward final consolidation.

## Features

- **Feature 1: Broadcast messaging** — implemented in the standalone Feature 1 server/client files with multiple clients, per-client threading, broadcast messaging, connection cleanup, and configurable host/port.
- **Feature 2: Private messaging** — Feature 2A username registration and client management is implemented; Feature 2B private-message routing is not yet implemented.
- **Feature 3: Network condition simulation and performance metrics** — simulate artificial latency, jitter, and application-level message loss, then measure their impact.

Feature 3 is modular and is not integrated into the chat send path yet. Its simulated message loss occurs at the application level; it must not be described as actual TCP packet loss or TCP retransmission behavior. Its delivered-messages-per-second result should be described as effective throughput or simulated delivery throughput, not actual network throughput.

## Team Responsibilities

- **Jiho — Feature 1: Broadcast Messaging:** implement broadcast communication through the central TCP server.
- **Sumanth — Feature 2A: Username Registration and Client Management:** handle username registration, username/client mappings, and related connection management.
- **Sean — Feature 2B: Private Message Routing and Handling:** implement `@username` private-message parsing, routing, and related handling; also help polish the final report and presentation/demo video.
- **Sang — Feature 3: Network Condition Simulation and Performance Metrics:** simulate latency, jitter, and application-level message loss, and measure their performance impact.

All team members will participate in the final demonstration, and each implementation owner will document their technical contribution for the report.

## Current Development Status

### Implemented

- **Feature 1 — Broadcast Messaging:** `Feature 1 Server.py` and `Feature 1 client.py` support multiple clients, per-client threading, broadcast messaging, connection cleanup, and configurable host/port.
- **Feature 2A — Username Registration and Client Management:** `src/feature2a.py` supports username registration, username/socket mappings, connected-client management, threaded client handling, and username-based message display/broadcast.
- **Feature 3 — Network Condition Simulation:** the standalone simulator, experiment runner, and tests are complete.

### In Progress

- **Feature 2B — Private Messaging:** will add `@username` private-message routing and handling.

### Awaiting Integration

- The currently separate Feature 1 and Feature 2 components will be consolidated into the main client/server application after Feature 2B is complete.
- Feature 3 will be integrated into the unified chat socket send path only after the consolidated chat implementation exists. Final Feature 3 measurements will be collected at that stage.

## Running the Current Foundation

Start the server with the default local address and port:

```bash
python3 src/server.py
```

In another terminal, connect a client:

```bash
python3 src/client.py
```

The default address is `127.0.0.1` and the default port is `5000`. Use `--host` and `--port` to choose a custom address, for example:

```bash
python3 src/server.py --host 0.0.0.0 --port 5001
python3 src/client.py --host 192.168.1.10 --port 5001
```

The current foundation accepts connections and closes them immediately. It does not send chat messages or provide threading, usernames, broadcast messaging, private messaging, or Feature 3.

## Repository Structure

```text
tcp-multiclient-chat/
├── Feature 1 Server.py
├── Feature 1 client.py
├── src/
│   ├── server.py
│   ├── client.py
│   ├── feature2a.py
│   ├── network_conditions.py
│   └── feature3_experiment.py
├── tests/
│   └── test_network_conditions.py
├── docs/
│   └── feature3.md
├── README.md
└── .gitignore
```

## Development

Implementation is done collaboratively through feature branches and pull requests. Feature 1 and Feature 2A are currently implemented in separate components, while Feature 2B is still in progress. After Feature 2B is complete, the separate Feature 1 and Feature 2 components will be consolidated into the main client/server application. Feature 3 should remain modular until the unified chat implementation exists; its integration and final measurements will follow that consolidation. Final over-the-air testing between teammates' computers will occur after integration.

The Feature 3 experiment can be run with:

```bash
python3 src/feature3_experiment.py --compare-baseline
```

See [docs/feature3.md](docs/feature3.md) for the experiment design and terminology.
