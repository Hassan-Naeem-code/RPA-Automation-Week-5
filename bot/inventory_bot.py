"""
Inventory Automation Bot
- Processes inventory batches
- Emits structured logs
- Exposes Prometheus metrics
- Handles errors and retries
- Ready for horizontal scaling
"""
import logging, logging.handlers, json, random, time, os
from prometheus_client import start_http_server, Summary, Counter
from multiprocessing import Process
from bot.errors import InventoryAPIError, RetryableError, DeadLetterError

# Logging setup
LOG_DIR = "../logs/"
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "inventory.log")
class JsonLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
        }
        # If the message is already a dict, merge it
        try:
            msg = json.loads(record.getMessage())
            if isinstance(msg, dict):
                log_record.update(msg)
            else:
                log_record["message"] = msg
        except Exception:
            log_record["message"] = record.getMessage()
        return json.dumps(log_record)

handler = logging.handlers.TimedRotatingFileHandler(
    filename=LOG_FILE, when="midnight", backupCount=7
)
handler.setFormatter(JsonLogFormatter())
logger = logging.getLogger()
logger.handlers = []
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Prometheus metrics
REQUEST_LAT = Summary('inv_batch_seconds', 'Inventory batch duration')
BATCH_COUNT = Counter('inv_batches_total', 'Total inventory batches processed', ['outcome'])

# Simulated inventory batch processing

@REQUEST_LAT.time()
def process_batch(batch_id):
    duration = random.uniform(0.05, 0.2)
    time.sleep(duration)
    # Simulate random errors
    r = random.random()
    if r < 0.03:
        raise InventoryAPIError("Inventory API error")
    elif r < 0.05:
        raise RetryableError("Temporary network issue")
    return duration

def run_bot(worker_id=0, max_batches=1000, max_retries=3):
    dead_letter_queue = []
    for i in range(max_batches):
        batch_id = f"{worker_id}-{i}"
        retries = 0
        while retries <= max_retries:
            try:
                duration = process_batch(batch_id)
                logger.info(json.dumps({
                    "batch_id": batch_id,
                    "duration": duration,
                    "outcome": "success"
                }))
                BATCH_COUNT.labels(outcome="success").inc()
                break
            except RetryableError as e:
                logger.warning(json.dumps({
                    "batch_id": batch_id,
                    "error": str(e),
                    "outcome": "retryable_error",
                    "retry": retries
                }))
                BATCH_COUNT.labels(outcome="error").inc()
                retries += 1
                time.sleep(0.1 * (2 ** retries))  # Exponential backoff
            except InventoryAPIError as e:
                logger.error(json.dumps({
                    "batch_id": batch_id,
                    "error": str(e),
                    "outcome": "api_error"
                }))
                BATCH_COUNT.labels(outcome="error").inc()
                break
        else:
            logger.error(json.dumps({
                "batch_id": batch_id,
                "outcome": "dead_letter"
            }))
            BATCH_COUNT.labels(outcome="dead_letter").inc()
            dead_letter_queue.append(batch_id)

if __name__ == "__main__":
    # Start Prometheus metrics server
    start_http_server(9100)
    # Horizontal scaling: run multiple processes
    num_workers = int(os.environ.get("BOT_WORKERS", 2))
    procs = []
    for w in range(num_workers):
        p = Process(target=run_bot, args=(w, 500))
        p.start()
        procs.append(p)
    for p in procs:
        p.join()
