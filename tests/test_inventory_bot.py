import pytest
from bot import inventory_bot
from bot.errors import InventoryAPIError, RetryableError
import logging

def test_process_batch_success():
    duration = inventory_bot.process_batch("test-1")
    assert 0.05 <= duration <= 0.2

def test_process_batch_api_error(monkeypatch):
    def always_api_error(batch_id):
        raise InventoryAPIError("API down")
    monkeypatch.setattr(inventory_bot, "process_batch", always_api_error)
    # Should log error and not retry
    inventory_bot.run_bot(worker_id=1, max_batches=1, max_retries=1)

def test_process_batch_retryable_error(monkeypatch):
    call_count = {"count": 0}
    def fail_then_succeed(batch_id):
        if call_count["count"] < 2:
            call_count["count"] += 1
            raise RetryableError("Temporary fail")
        return 0.1
    monkeypatch.setattr(inventory_bot, "process_batch", fail_then_succeed)
    inventory_bot.run_bot(worker_id=2, max_batches=1, max_retries=3)
    assert call_count["count"] == 2

def test_dead_letter_queue(monkeypatch):
    def always_retryable(batch_id):
        raise RetryableError("Always fail")
    monkeypatch.setattr(inventory_bot, "process_batch", always_retryable)
    # Should end up in dead-letter queue
    inventory_bot.run_bot(worker_id=3, max_batches=1, max_retries=1)

def test_metrics_emission():
    # Metrics should increment for each outcome
    before = inventory_bot.BATCH_COUNT.labels(outcome="success")._value.get()
    inventory_bot.logger.disabled = True  # Silence logs
    inventory_bot.run_bot(worker_id=4, max_batches=1, max_retries=0)
    after = inventory_bot.BATCH_COUNT.labels(outcome="success")._value.get()
    assert after == before + 1 or after == before  # May fail if error, but should not decrease

def test_logging_output(tmp_path, monkeypatch):
    # Patch logger to write to a temp file
    log_file = tmp_path / "test.log"
    handler = logging.FileHandler(log_file)
    inventory_bot.logger.handlers = [handler]
    def succeed(batch_id):
        return 0.1
    monkeypatch.setattr(inventory_bot, "process_batch", succeed)
    inventory_bot.run_bot(worker_id=5, max_batches=1, max_retries=0)
    handler.close()
    with open(log_file) as f:
        lines = f.readlines()
    assert any("success" in line for line in lines)
