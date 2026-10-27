# Historical Team Implementations

These files were moved with `git mv` and retain their original contents. They document the foundations contributed by the team and are separate from the recommended integrated execution path: `src/server.py` and `src/client.py`.

| Directory | Implementation | Attribution |
| --- | --- | --- |
| `feature1/` | Original TCP broadcast server/client with threaded handling and send locks | Jiho Choi (@whwlqkqjxm) |
| `feature2/feature2a.py` | Username/client-management server, extended with private messaging | Sumanth Gopal (@sumanthgopal22), then Sean Kong (@SeanK000) |

The Feature 1 protocol identifies senders by socket address and has no registration. The Feature 2 prototype uses a simpler receive strategy and differs from the integrated protocol and validation behavior. These programs are historical examples, not replacements for the primary application or its supported test path. See [verified contributions](../CONTRIBUTORS.md) and `git log --follow -- PATH` for their history.
