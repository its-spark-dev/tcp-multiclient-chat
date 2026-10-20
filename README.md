# TCP Multiclient Chat

A small Python networking project for building a multi-client TCP chat application with a central server.

## Project Overview

This project is a small Python TCP chat application developed by a four-person team. The common TCP client/server foundation is in place, and the feature implementations will be added in parallel before final integration.

## Features

- **Feature 1: Broadcast messaging** — send a message from one client to all connected clients through the server.
- **Feature 2: Private messaging** — send a one-to-one message to another client using usernames.
- **Feature 3: Network condition simulation and performance metrics** — simulate artificial latency, jitter, and application-level message loss, then measure their impact.

Feature 3 is modular and is not integrated into the chat send path yet. Its simulated message loss occurs at the application level; it must not be described as actual TCP packet loss or TCP retransmission behavior. Its delivered-messages-per-second result should be described as effective throughput or simulated delivery throughput, not actual network throughput.

## Team Responsibilities

- **Jiho — Feature 1: Broadcast Messaging:** implement broadcast communication through the central TCP server.
- **Sumanth — Feature 2A: Username Registration and Client Management:** handle username registration, username/client mappings, and related connection management.
- **Sean — Feature 2B: Private Message Routing and Handling:** implement `@username` private-message parsing, routing, and related handling; also help polish the final report and presentation/demo video.
- **Sang — Feature 3: Network Condition Simulation and Performance Metrics:** simulate latency, jitter, and application-level message loss, and measure their performance impact.

All team members will participate in the final demonstration, and each implementation owner will document their technical contribution for the report.

## Current Development Status

The shared TCP foundation is implemented. Feature 1, Feature 2 username/client management, and Feature 2 private-message routing are not yet implemented. Feature 3's standalone simulator and experiment runner are available for development, but integration with the chat send path will happen later.

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
├── src/
│   ├── server.py
│   ├── client.py
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

Implementation is done collaboratively through feature branches and pull requests. Features 1 and 2 share the common TCP foundation and can proceed in parallel. Final integration and over-the-air testing between teammates' computers will occur after the feature branches are merged. Feature 3 should remain modular until that integration work is ready.

The Feature 3 experiment can be run with:

```bash
python3 src/feature3_experiment.py --compare-baseline
```

See [docs/feature3.md](docs/feature3.md) for the experiment design and terminology.
