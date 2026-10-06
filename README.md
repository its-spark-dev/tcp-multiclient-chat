# TCP Multiclient Chat

A small Python networking project for building a multi-client TCP chat application with a central server.

## Planned Features

- **Feature 1: Broadcast messaging** — send a message from one client to all connected clients through the server.
- **Feature 2: Private messaging** — send a one-to-one message to another client using usernames.
- **Feature 3: TBD** — a networking-related enhancement with measurable metrics will be selected later.

Features 1 and 2 will be demonstrated on localhost and over a real network between teammates' computers. Broadcast messaging, private messaging, and threaded client handling are planned but not yet implemented. Feature 3 is also not yet selected or implemented.

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
│   └── client.py
├── tests/
│   └── .gitkeep
├── docs/
│   └── .gitkeep
├── README.md
└── .gitignore
```

## Development

Implementation will be done collaboratively through feature branches and pull requests. Changes should be reviewed and merged into the shared project branch by the team.
