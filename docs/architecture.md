# Architecture and Protocol

The application uses Python standard-library IPv4 TCP sockets. Run `src/server.py` and `src/client.py` from the repository root. Earlier implementations in `prototypes/` document the team's development history and are separate programs.

## Modules

| Module | Responsibility |
| --- | --- |
| `src/server.py` | Accept connections, register sessions, route messages, coordinate shutdown |
| `src/client.py` | Poll terminal input and receive server frames on a background thread |
| `src/protocol.py` | Shared newline-delimited UTF-8 encoding and byte buffering |
| `src/network_conditions.py` | Per-attempt simulated drop and requested artificial delay |
| `src/send_metrics.py` | Thread-safe per-recipient send accounting |
| `src/feature3_experiment.py` | Standalone simulator comparison and CLI numeric validators |
| `examples/fixed_port_client.py` | Alternative client example with positional address and fixed port 5000 |

## Connection Lifecycle

The accept loop wraps each socket in a `Peer` with its own send lock and starts a worker. The server tracks accepted peers, including connections that have not registered. A worker prompts for a username and consumes newline-delimited candidates until a valid unused name is registered or the connection closes. Names are case-sensitive, with 1–24 ASCII letters, digits, or underscores. Availability checking and insertion happen under the same shared-state lock.

After registration, the same buffered reader processes chat frames. Empty or whitespace-only chat frames are ignored; `/quit` closes the registered session. EOF, invalid UTF-8, or a socket error leads to cleanup. Cleanup removes the username only if its mapping still belongs to that peer, discards the tracked connection, and closes the socket. This avoids an old connection removing a newer registration that reused its name.

## Wire Format

Every integrated protocol message is a UTF-8 line ending in `\n`. Readers strip trailing carriage returns for CRLF compatibility. They accumulate bytes before decoding, so split UTF-8 characters and multiple frames in one read work correctly. A final unterminated frame is discarded at EOF. There is no escaping or multiline payload syntax.

| Direction / stage | Example | Meaning |
| --- | --- | --- |
| Server → unregistered client | `[Server] Enter username:` | Registration prompt |
| Client → server, first valid candidate | `Alice` | Register a username |
| Server → client | `[Server] Registered: Alice` | Registration accepted |
| Client → server, registered | `hello` | Broadcast to other registered clients |
| Server → recipients | `[Alice] hello` | Broadcast display line |
| Client → server, registered | `@Bob hello` | Private message |
| Server → Bob only | `[Private] Alice: hello` | Private display line |
| Client → server, registered | `/quit` | Disconnect |

Duplicate or invalid username candidates can be retried on the same connection. Private-message validation errors return only to the sender. Successful sends produce no acknowledgement. `[Server]` and `[Private]` are display conventions, not authenticated message types.

## Locks and Routing

- The server state lock protects username mappings and the set of connected peers. It is released before network I/O or artificial sleeps.
- Broadcast copies the current recipient list, excluding the sender. Private routing looks up one target. Disconnects may occur after either snapshot; failed sends are recorded and the stale recipient is cleaned up.
- A peer's send lock serializes complete encoded frames from different workers, including control messages. It does not establish a global message order.
- The simulator's random lock serializes random decisions, then releases before sleeping. Metrics have their own lock. A fixed seed cannot fix concurrent scheduling.

The worker handling a sender processes recipients sequentially. Other workers remain concurrent. Artificial delay occurs before acquiring the recipient send lock, so a delayed message does not hold that lock while sleeping.

## Impairment and Metrics

Only valid user-message recipient deliveries call `ChatServer.deliver()`. A simulated drop skips socket sending. A pass sleeps for the requested delay, then attempts `Peer.send()`. Registration and validation errors call `Peer.send()` directly and do not increment impairment metrics. Control messages still share the socket-send lock and may wait behind a blocking socket write.

At quiescence, attempts equal drops plus simulator passes; passes equal socket-send successes plus failures. A live snapshot can contain attempts still in flight. Shutdown prints the final summary after workers finish. See [Network condition simulation](feature3.md) for formulas, recorded measurements, and interpretation limits.

## Shutdown and Design Tradeoffs

Ctrl+C interrupts the server's accept loop. The server closes tracked sockets to unblock readers and joins worker threads before reporting metrics. In-flight artificial sleeps finish before workers exit. The main client polls stdin with `select`, receives on another thread, and shuts down its socket to unblock receiving before joining that thread. The alternative client example uses a daemon input reader so remote disconnects can terminate it even with keyboard input blocked.

The protocol intentionally avoids a framework or external runtime dependency. There are no authenticated identities, TLS, receipt acknowledgements, bounded frame sizes, connection quotas, or idle/send timeouts. Slow recipients and large delays can stall a worker; the project is intended for controlled networking experiments. Automated verification covers real localhost sockets and subprocess cleanup; [manual LAN checks](network-testing.md) cover communication between machines.
