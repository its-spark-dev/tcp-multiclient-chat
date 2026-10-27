# LAN Testing Guide

This guide provides a repeatable procedure for checking the integrated application across machines; it is not a verbatim record of the recorded experiment configuration. See [Feature 3 results](feature3.md#recorded-demonstration-results) for the team-provided measurements.

Use one server computer and at least three client sessions, preferably on separate computers. Run all commands from the repository root of the same source version, using a Git checkout. The primary interactive client (`src/client.py`) supports macOS/Linux terminals; Windows console input is not supported or validated.

## 1. Network and IP Setup

Connect the computers to the same Wi-Fi or another mutually reachable network. Guest Wi-Fi may isolate clients; if connections fail, try a network that permits device-to-device traffic.

Find the server computer's IPv4 address:

- macOS: System Settings → Wi-Fi → connected network details → TCP/IP.
- Linux: run `ip -4 addr` and identify the address of the connected interface.

Replace `SERVER_IP` below with the server's reachable IPv4 address. Allow inbound TCP connections on port `5001` through the server firewall.

- `127.0.0.1` means the local computer; do not use it to connect to a remote server.
- `0.0.0.0` lets the server listen on all IPv4 interfaces. Clients must use the server's reachable IP address instead.
- The client and server port must match. Run only one server on a given address/port.

## 2. Start the Baseline Application

On the server computer:

```bash
python3 src/server.py --host 0.0.0.0 --port 5001
```

On each client computer:

```bash
python3 src/client.py --host SERVER_IP --port 5001
```

Register distinct usernames, such as `Sang`, `Jiho`, and `Sean`. Usernames are case-sensitive and contain 1–24 ASCII letters, digits or underscores.

An additional compatible client is available as `src/client2.py`. It accepts a positional server IP and always uses port `5000`, so start the server on that port when using it:

```bash
python3 src/server.py --host 0.0.0.0 --port 5000
python3 src/client2.py SERVER_IP
```

Run each command in its own terminal. Do not pass `--host` or `--port` to `client2.py`. Ordinary messages, `@username message` and `/quit` retain the same behavior. Its UTF-8 streaming and disconnect fixes are regression-tested; Windows console behavior has not been validated.

If connection fails, check the server is running, the IP and port are correct, the firewall allows the port, and the network permits communication between devices.

## 3. Feature 1: Broadcast Messaging

From Sang, enter:

```text
hello everyone
```

Verify that Jiho and Sean receive `[Sang] hello everyone`, and Sang does not receive an echoed broadcast. Repeat from each client to check that all clients can send and receive.

## 4. Feature 2: Registration and Private Messaging

From Sang, enter:

```text
@Jiho private test
```

Verify that only Jiho receives `[Private] Sang: private test`. Sean must receive nothing. Successful private messages do not generate a sender confirmation; inspect the recipient's screen.

From Sang, test:

```text
@Unknown hello
@Jiho
@Sang hello
```

Verify sender-only errors for an unknown target, a missing message body, and a self-message. Use a target name that is not registered for the first case.

Open an additional client and try an existing username. Verify rejection and successful retry with a different name. Check rejection of an empty or invalid username. Disconnect a registered client using `/quit`, then verify a new client can register that released username.

## 5. Feature 3: Impaired Conditions

The following settings are an illustrative repeat test, not the known configuration of the recorded demonstration. If using `client2.py`, substitute port `5000` for `5001`.

Stop the baseline server with Ctrl+C and save its metrics. Restart with:

```bash
python3 src/server.py --host 0.0.0.0 --port 5001 \
  --latency-ms 20 --jitter-ms 5 --loss-rate 0.2 --seed 42
```

Reconnect and register all clients. Repeat broadcast and private-message checks with numbered messages, for example:

```text
broadcast-01
broadcast-02
@Jiho private-01
@Jiho private-02
```

Verify that user messages experience artificial latency, artificial jitter, or application-level simulated message loss. Each broadcast recipient gets a separate impairment decision. Registration and server-generated validation/error messages must remain available.

A 20% loss probability does not guarantee exactly 20% drops in a short run. For a separate deterministic loss check, restart with `--loss-rate 1`: user chat messages should never reach recipients, while registration and errors still work. Restore baseline or the intended experiment settings afterward.

## 6. Record and Interpret Results

Stop the server with Ctrl+C to print the cumulative summary. Save the output and record:

- Git commit, operating systems, network type, client count and server options.
- Message count, message content, intended recipients and input timing.
- Recipient screens or logs showing broadcast/private-message behavior.
- Baseline and impaired server summaries, with repeat runs where practical.

| Metric | Interpretation |
| --- | --- |
| Delivery attempts | One attempt per intended recipient of a valid user message |
| Simulated drops | Attempts blocked before socket sending |
| Simulator passes | Attempts allowed through the simulator |
| Socket send successes / failures | Whether the socket send completed or raised an error |
| Server-send delivery rate | Socket send successes divided by all delivery attempts |
| Artificial delay statistics | Requested artificial delays across simulator passes |
| Effective throughput | Successful server sends per elapsed second |

One broadcast to two recipients counts as two attempts. Socket send success does not confirm that the remote client received or displayed a message; this application does not use receipt acknowledgements.

Keep the workload and input timing comparable between baseline and impaired runs. Elapsed time includes gaps between messages, so manual typing speed affects effective throughput. A fixed seed reproduces random decisions for the same call order; concurrent scheduling can change the recipient associated with each decision.

These metrics characterize the server send path. Application-level simulated message loss is not actual TCP packet loss, and effective throughput is not actual network throughput. Label automated smoke-test output, recorded demo results and any additional experiments separately. See [Feature 3 documentation](feature3.md) for complete metric definitions and the recorded run's 96 attempts, 16 simulated drops and 80 successful socket sends.

## 7. Finish

Exit clients with `/quit` or Ctrl+C, stop the server with Ctrl+C, and confirm no test application processes remain running. Retain the server summaries and recipient observations with the experiment configuration for reproducibility.
