import pytest
from bot import inventory_bot

def test_process_batch_success():
    # Should not raise for normal case
    duration = inventory_bot.process_batch("test-1")
    assert 0.05 <= duration <= 0.2

def test_run_bot_handles_errors(monkeypatch):
    # Simulate error and ensure retries
    call_count = {"count": 0}
    def fail_once(batch_id):
        if call_count["count"] == 0:
            call_count["count"] += 1
            raise Exception("Simulated error")
        return 0.1
    monkeypatch.setattr(inventory_bot, "process_batch", fail_once)
    # Should not raise
    inventory_bot.run_bot(worker_id=99, max_batches=1, max_retries=2)
