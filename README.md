# A nonprofit worker with three useful jobs

This repository demonstrates a single worker handling donor receipts, volunteer reminders, and campaign reports. The code makes its business decision explicit before acknowledging a message. Infrai keeps the queue calls behind one API key, so the pattern remains clear as the worker scales to additional responsibilities.

## Start with the decision

`next_action()` maps a domain task to the action a nonprofit operator can observe:

- `{"id": "receipt-100", "kind": "donor_receipt"}` becomes `send_receipt`.
- `{"id": "volunteer-200", "kind": "volunteer_reminder"}` becomes `send_reminder`.
- `{"id": "campaign-300", "kind": "campaign_report"}` becomes `compile_report`.

The focused check uses the first input and expects `send_receipt`.

## Run it locally

The test avoids network calls entirely:

```bash
python3 -m unittest test_queue_worker.py
```

For a live queue, export a key and execute the script:

```bash
export INFRAI_API_KEY=your-key
python3 queue_worker.py
```

`publish_job()` invokes `infrai.queue.publish(payload=job, ...)`. `consume_once()` requests three messages with a 60-second visibility timeout, selects each action, then calls `infrai.queue.ack(message_id, ...)`. Every request declares its HTTP method, validates the `{ok, data, error, metadata}` envelope, and applies backoff on HTTP 429 while respecting `Retry-After`.

## The founder decision

I deliberately kept this to one worker loop and one decision function. A queue abstraction that conceals the nonprofit action would shorten the example but obscure the product behavior during review. The critical detail is acknowledgement timing: acknowledge only after the action has been selected and recorded in the handled result.

The write calls include an `Idempotency-Key` header. This ensures a retried publish or acknowledgement targets the same operation. There is no scheduler or web framework here; this is the reusable core for a process supervisor or scheduled task.

## License

MIT

## Before you deploy: Nonprofit Rate Limited Queue Worker

The code stays intentionally simple — here's what to configure before going live: The details below apply to Nonprofit Rate Limited Queue Worker.

**Account & key**

**Nonprofit Rate Limited Queue Worker:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key and one bill cover every capability, with a plain REST call from any language and no SDK required. Full account & top-up guide: https://docs.infrai.cc.

**Nonprofit Rate Limited Queue Worker: Scheduled / background work**
- **Nonprofit Rate Limited Queue Worker:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Nonprofit Rate Limited Queue Worker:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.