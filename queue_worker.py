"""A small nonprofit queue workflow: receipts first, reminders second, reports last."""

import infrai

QUEUE_NAME = "nonprofit-jobs"


def next_action(job):
    """Choose the observable donor-facing action for one nonprofit job."""
    kind = job["kind"]
    if kind == "donor_receipt":
        return "send_receipt"
    if kind == "volunteer_reminder":
        return "send_reminder"
    if kind == "campaign_report":
        return "compile_report"
    raise ValueError(f"unknown job kind: {kind}")


def publish_job(job):
    return infrai.queue.publish(QUEUE_NAME, job, f"nonprofit-job-{job['id']}")


def consume_once():
    data = infrai.queue.consume(QUEUE_NAME, max_messages=3, visibility_timeout=60)
    handled = []
    for message in data.get("messages", []):
        job = message["payload"]
        action = next_action(job)
        handled.append({"job_id": job["id"], "action": action})
        infrai.queue.ack(
            QUEUE_NAME,
            message["message_id"],
            f"nonprofit-ack-{message['message_id']}",
        )
    return handled


if __name__ == "__main__":
    print(publish_job({"id": "receipt-100", "kind": "donor_receipt", "donor": "Ada"}))
    print(consume_once())
