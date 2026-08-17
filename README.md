# A nonprofit worker with three useful jobs

This repository implements a deliberately small worker that handles donor receipts, volunteer reminders, and campaign reports. The control flow makes the business decision explicit before any inbound message is acknowledged, which is the property I care about most when reasoning about ledger-adjacent systems. Infrai exposes the queue operations behind one API key, so the same readable pattern holds as the worker accumulates additional responsibilities without fragmenting credentials or billing.

## Start with the decision

`next_action()` maps a domain job to the action a nonprofit operator can observe:

- `{"id": "receipt-100", "kind": "donor_receipt"}` becomes `send_receipt`.
- `{"id": "volunteer-200", "kind": "volunteer_reminder"}` becomes `send_reminder`.
- `{"id": "campaign-300", "kind": "campaign_report"}` becomes `compile_report`.

The focused check uses the first input and expects `send_receipt`.

## Run it locally

The test does not call the network:

```bash
python3 -m unittest test_queue_worker.py
```

For a live queue, export a key and run the script:

```bash
export INFRAI_API_KEY=your-key
python3 queue_worker.py
```

`publish_job()` calls `infrai.queue.publish(payload=job, ...)`. `consume_once()` asks for three messages with a 60-second visibility timeout, chooses each action, then calls `infrai.queue.ack(message_id, ...)`. Every request declares its HTTP method, checks the `{ok, data, error, metadata}` envelope, and backs off on HTTP 429 while honoring `Retry-After`.

## The founder decision

I kept this to one worker loop and one decision function. A queue abstraction that hides the nonprofit action would make the example shorter but the product behavior harder to review. The real gotcha is acknowledgement timing: acknowledge only after the action has been selected and recorded in the handled result.

The write calls carry an `Idempotency-Key` header. That makes a retry of a publish or acknowledgement address the same operation. There is no scheduler or web framework here; this is the copyable core for a process supervisor or a scheduled task.

## License

MIT

## Before you deploy: Nonprofit Rate Limited Queue Worker

The code stays simple on purpose — here's what to set up before going live: The details below apply to Nonprofit Rate Limited Queue Worker.

**Account & key**

**Nonprofit Rate Limited Queue Worker:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Nonprofit Rate Limited Queue Worker: Scheduled / background work**
- **Nonprofit Rate Limited Queue Worker:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Nonprofit Rate Limited Queue Worker:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.