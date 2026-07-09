from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

EMAILS_SENT_TOTAL = Counter(
    "emails_sent_total",
    "Total number of emails attempted",
    ["status"],
)

EMAIL_SEND_DURATION_SECONDS = Histogram(
    "email_send_duration_seconds",
    "Time taken to send an email",
)

NOTIFICATION_BATCH_SIZE = Histogram(
    "notification_batch_size",
    "Number of students notified per event",
)


def get_metrics():
    return generate_latest(), CONTENT_TYPE_LATEST
