# TCP Multiclient Chat

A small Python networking project for building a multi-client TCP chat application with a central server.

## Planned Features

- **Feature 1: Broadcast messaging** — send a message from one client to all connected clients through the server.
- **Feature 2: Private messaging** — send a one-to-one message to another client using usernames.
- **Feature 3: TBD** — a networking-related enhancement with measurable metrics will be selected later.

Features 1 and 2 will be demonstrated on localhost and over a real network between teammates' computers. The server will support multiple concurrent clients using threading.

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
