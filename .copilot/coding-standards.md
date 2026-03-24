# Coding Standards

Language: Python

## Style

- Use type hints
- Prefer dataclasses
- Avoid global state

## Error Handling

Always use domain exceptions.

Example:

class InventoryError(Exception):
    pass

## Logging

Use structured logging.

logger.info("inventory_updated", productId=id)

## Async

Prefer async for IO operations.