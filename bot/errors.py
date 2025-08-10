class InventoryBotError(Exception):
    """Base class for inventory bot errors."""
    pass

class InventoryAPIError(InventoryBotError):
    """Raised when the inventory API fails."""
    pass

class RetryableError(InventoryBotError):
    """Raised for retryable errors."""
    pass

class DeadLetterError(InventoryBotError):
    """Raised when a batch is sent to the dead-letter queue."""
    pass
