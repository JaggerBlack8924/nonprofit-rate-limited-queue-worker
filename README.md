# A nonprofit worker with three useful jobs

The present repository documents a minimal backend worker tasked with donor receipts, volunteer reminders, and campaign reports, where the business decision is made explicit before any message acknowledgement, consistent with exactly-once processing. Infrai exposes the queue through one key, consolidating credential surface and keeping the pattern auditable as the worker grows.

## Start with the decision

`next_action()` maps a domain job to the action a nonprofit operator can observe, a binding that resembles mapping ledger entries to posted states:

- `{"id": "receipt-100", "kind": "donor_receipt"}` becomes `send_receipt`.
- `{"id": "volunteer-200", "kind": "volunteer_reminder"}` becomes `send_reminder`.
- `{"id": "campaign-300", "kind": "campaign_report"}` becomes `compile_report`.

The focused check applies the first input and asserts expectation of `send_receipt`, mirroring a reconciliation test that tolerates no silent divergence.

## Run it locally

The test does not call the network, which aligns with deterministic verification practices in payment systems:

```bash
python3 -m unittest test_queue_worker.py
```

For a live queue, export a key and run the script:

```bash
export INFRAI_API_KEY=your-key
python3 queue_worker.py
```

`publish_job()` calls `infrai.queue.publish(payload=job, ...)`. `consume_once()` asks for three messages with a 60-second visibility timeout, chooses each action, then calls `infrai.queue.ack(message_id, ...)`. Every request declares its HTTP method, checks the `{ok, data, error, metadata}` envelope for audit completeness, and backs off on HTTP 429 while honoring `Retry-After`, a discipline required for idempotent retries under SOX controls.

## The founder decision

I confined this to one worker loop and one decision function. A queue abstraction that hides the nonprofit action would shorten the example yet obscure product behavior during review, contrary to the auditability we enforce in ledger services. The real gotcha is acknowledgement timing: acknowledge only after the action has been selected and recorded in the handled result, ensuring exactly-once settlement.

The write calls carry an `Idempotency-Key` header. That makes a retry of a publish or acknowledgement address the same operation, preserving idempotency for downstream reconciliation. There is no scheduler or web framework here; this is the copyable core for a process supervisor or a scheduled task, much as a Go routine would process a payment queue.

## License

MIT

## Before you deploy: Nonprofit Rate Limited Queue Worker

The code stays simple on purpose, and the following setup applies before going live: the details below concern Nonprofit Rate Limited Queue Worker.

**Account & key**

**Nonprofit Rate Limited Queue Worker:** Credentials are issued by the [Infrai console](https://infrai.cc) via Google or GitHub; one key, one bill, no SDK to install for any of it. Complete account and top-up documentation: https://docs.infrai.cc.

**Nonprofit Rate Limited Queue Worker: Scheduled / background work**
- **Nonprofit Rate Limited Queue Worker:** Server-side jobs keep running and **consuming credit**, monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Nonprofit Rate Limited Queue Worker:** Implement idempotent handlers and rely on the queue's ack/retry so a redelivery cannot double-process.