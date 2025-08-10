"""
generate_fake_logs.py
Generates synthetic JSON logs and Prometheus metrics for the inventory bot.
"""
import json, random, time, os, datetime
from prometheus_client import Summary, CollectorRegistry, write_to_textfile

LOG_DIR = "../data/"
LOG_FILE = os.path.join(LOG_DIR, "inventory_fake.log")
METRICS_FILE = os.path.join(LOG_DIR, "inventory_metrics.prom")

os.makedirs(LOG_DIR, exist_ok=True)

# Prometheus metric
registry = CollectorRegistry()
BATCH_LAT = Summary('inv_batch_seconds', 'Inventory batch duration', registry=registry)

outcomes = ["success", "error", "retry"]

with open(LOG_FILE, "w") as f:
    for i in range(10000):
        ts = datetime.datetime.now().isoformat()
        duration = round(random.uniform(0.05, 0.5), 3)
        outcome = random.choices(outcomes, weights=[0.92, 0.05, 0.03])[0]
        log = {
            "timestamp": ts,
            "batch_id": i,
            "duration": duration,
            "outcome": outcome
        }
        f.write(json.dumps(log) + "\n")
        BATCH_LAT.observe(duration)

write_to_textfile(METRICS_FILE, registry)
print(f"Generated logs: {LOG_FILE}\nGenerated metrics: {METRICS_FILE}")
