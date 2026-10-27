# Contributors

This repository represents collaborative work by all four contributors. The integrated application builds on their individual implementations; integration commits do not replace the authorship of the earlier designs and code. GitHub contributor history remains the authoritative record of code authorship. Existing commits, author identities, and merge history are preserved.

The real-name/GitHub mappings below were supplied by the team. Technical responsibilities were checked against commit diffs and the existing project documentation. Commit IDs refer to the original history; prototype paths describe the current tree.

## Jiho Choi (@whwlgkqjxm)

Implemented Feature 1's TCP broadcast server and interactive client, including per-client threads, recipient snapshots under a shared lock, per-recipient send locks, newline-based reading, and disconnect handling. These implementations are preserved in `prototypes/feature1/`.

Evidence: `e52e431` (broadcast client), `99ac56b` (client filename change), and `b4bc41e` (broadcast server). GitHub attributes these commits to `whwlgkqjxm`, matching the public-facing account above. Historical author metadata has not been changed. No separate test-suite authorship is inferred from these commits.

## Sumanth Gopal (@sumanthgopal22)

Implemented Feature 2A's socket foundation, username registration, username-to-connection mapping, shared-state locking, per-client handlers, and disconnect cleanup. Added clean server shutdown. This work forms the registration/client-management foundation of the combined system; its earlier implementation is preserved in `prototypes/feature2/feature2a.py`.

Evidence: `1e98f7a` (socket foundation), `7f10518` (registration/client management), and `b27f193` (shutdown). The original registration accepted usernames directly; the integrated application's uniqueness and format validation were added during integration.

## Sean Kong (@SeanK000)

Implemented Feature 2B's `@username message` parsing, target lookup, private routing, and error handling for missing bodies, unknown targets, self-messages, and socket-send failures in the Feature 2 prototype. Also authored the additional compatible terminal client, `examples/fixed_port_client.py`.

Evidence: `27d8162` (private messaging) and `fad7fd9` (additional client). The existing team-responsibility documentation also credits report and demo polishing; this is a documented team responsibility, rather than a claim of separately committed code. Later UTF-8 and disconnect fixes to `client2.py` are attributed below.

## Sang Park (@its-spark-dev)

Implemented Feature 3's network-condition simulator, standalone experiment, metrics, and simulator tests. Integrated the broadcast, username-management, and private-message work into the primary server/client, with shared byte-buffered TCP framing, username validation, and integrated send-path impairment. Added integration tests, client2 UTF-8/disconnect regression fixes, architecture/testing documentation, and recorded-results documentation.

Evidence: `f10447d` (initial TCP foundation), `c004a81` (simulator/experiment/tests), `f9dd8d8` (combined routing/framing), `eb49b33` (send-path simulation/metrics), `3947a76` (integrated tests), `83a2ac5` (network testing guide), `0d45e54` (client2 fixes/tests), and `e226103` (recorded results/documentation). The original Feature 1 and Feature 2 implementations retain the attribution described above.

## Interpreting the History

Inspect any referenced change with `git show COMMIT_ID`. Follow moved files with, for example:

```bash
git log --follow -- prototypes/feature1/server.py
git log --follow -- prototypes/feature2/feature2a.py
```

Commit authorship records repository changes; it does not measure all collaboration, review, or presentation work. No contribution percentages are assigned. The team's existing disclosure of generative AI assistance for Feature 3 is retained in [docs/feature3.md](docs/feature3.md#generative-ai-assistance).
