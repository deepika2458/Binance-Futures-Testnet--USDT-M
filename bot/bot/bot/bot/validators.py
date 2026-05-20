Input Validation Module

This module provides centralized input validation for order parameters.
All validation logic is interface-agnostic and can be used by CLI,
Streamlit, or any other interface layer.

Validation is performed before any API calls to ensure fail-fast behavior
and prevent invalid requests from reaching the Binance API.
"""

from typing import Any, Optional, Union

from bot.logging_config import get_logger


# Valid values for order parameters
VALID_SIDES = ("BUY", "SELL")
VALID_ORDER_TYPES = ("MARKET", "LIMIT")


class ValidationError(Exception):
    """
    Raised when input validation fails.
    
    This exception provides clear, user-friendly error messages
    for invalid order parameters.
    
    Attributes:
        message: Human-readable description of the validation failure.
        field: The name of the field that failed validation (optional).
    """
    
    def __init__(self, message: str, field: Optional[str] = None) -> None:
        self.message = message
        self.field = field
        super().__init__(self.message)


def validate_symbol(symbol: Any) -> str:
    """
    Validate the trading symbol.
    
    Args:
        symbol: The trading pair symbol (e.g., 'BTCUSDT').
        
    Returns:
        The validated symbol as an uppercase string.
        
    Raises:
        ValidationError: If symbol is empty or not a string.
    """
    logger = get_logger()
    
    if symbol is None:
        logger.warning("Validation failed: Symbol is required")
        raise ValidationError("Symbol is required.", field="symbol")
    
    if not isinstance(symbol, str):
        logger.warning(f"Validation failed: Symbol must be a string, got {type(symbol).__name__}")
        raise ValidationError("Symbol must be a string.", field="symbol")
    
    symbol = symbol.strip()
    
    if not symbol:
        logger.warning("Validation failed: Symbol cannot be empty")
        raise ValidationError("Symbol cannot be empty.", field="symbol")
    
    return symbol.upper()


def validate_side(side: Any) -> str:
    """
    Validate the order side.
    
    Args:
        side: The order side ('BUY' or 'SELL').
        
    Returns:
        The validated side as an uppercase string.
        
    Raises:
        ValidationError: If side is not 'BUY' or 'SELL'.
    """
    logger = get_logger()
    
    if side is None:
        logger.warning("Validation failed: Order side is required")
        raise ValidationError("Order side is required.", field="side")
    
    if not isinstance(side, str):
        logger.warning(f"Validation failed: Order side must be a string, got {type(side).__name__}")
        raise ValidationError("Order side must be a string.", field="side")
    
    side = side.strip().upper()
    
    if side not in VALID_SIDES:
        logger.warning(f"Validation failed: Invalid order side '{side}'")
        raise ValidationError(
            f"Invalid order side. Allowed values are {', '.join(VALID_SIDES)}.",
            field="side"
        )
    
    return side


def validate_order_type(order_type: Any) -> str:
    """
    Validate the order type.
    
    Args:
        order_type: The order type ('MARKET' or 'LIMIT').
        
    Returns:
        The validated order type as an uppercase string.
        
    Raises:
        ValidationError: If order_type is not 'MARKET' or 'LIMIT'.
    """
    logger = get_logger()
    
    if order_type is None:
        logger.warning("Validation failed: Order type is required")
        raise ValidationError("Order type is required.", field="order_type")
    
    if not isinstance(order_type, str):
        logger.warning(f"Validation failed: Order type must be a string, got {type(order_type).__name__}")
        raise ValidationError("Order type must be a string.", field="order_type")
    
    order_type = order_type.strip().upper()
    
    if order_type not in VALID_ORDER_TYPES:
        logger.warning(f"Validation failed: Invalid order type '{order_type}'")
        raise ValidationError(
            f"Invalid order type. Allowed values are {', '.join(VALID_ORDER_TYPES)}.",
            field="order_type"
        )
    
    return order_type


def validate_quantity(quantity: Any) -> float:
    """
    Validate the order quantity.
    
    Args:
        quantity: The order quantity (must be a positive number).
        
    Returns:
        The validated quantity as a float.
        
    Raises:
        ValidationError: If quantity is not a positive number.
    """
    logger = get_logger()
    
    if quantity is None:
        logger.warning("Validation failed: Quantity is required")
        raise ValidationError("Quantity is required.", field="quantity")
    
    try:
        quantity = float(quantity)
    except (ValueError, TypeError):
        logger.warning(f"Validation failed: Quantity must be a number, got '{quantity}'")
        raise ValidationError("Quantity must be a valid number.", field="quantity")
    
    if quantity <= 0:
        logger.warning(f"Validation failed: Quantity must be positive, got {quantity}")
        raise ValidationError("Quantity must be a positive number.", field="quantity")
    
    return quantity


def validate_price(price: Any, order_type: str) -> Optional[float]:
    """
    Validate the order price.
    
    Args:
        price: The limit price (required for LIMIT orders).
        order_type: The order type to determine if price is required.
        
    Returns:
        The validated price as a float, or None for MARKET orders.
        
    Raises:
        ValidationError: If price is required but missing or invalid.
    """
    logger = get_logger()
    
    # Price is not required for MARKET orders
    if order_type == "MARKET":
        if price is not None:
            logger.info("Price provided for MARKET order will be ignored")
        return None
    
    # Price is required for LIMIT orders
    if price is None:
        logger.warning("Validation failed: Price is required for LIMIT orders")
        raise ValidationError("Price is required for LIMIT orders.", field="price")
    
    try:
        price = float(price)
    except (ValueError, TypeError):
        logger.warning(f"Validation failed: Price must be a number, got '{price}'")
        raise ValidationError("Price must be a valid number.", field="price")
    
    if price <= 0:
        logger.warning(f"Validation failed: Price must be positive, got {price}")
        raise ValidationError("Price must be a positive number.", field="price")
    
    return price


def validate_order_inputs(
    symbol: Any,
    side: Any,
    order_type: Any,
    quantity: Any,
    price: Any = None
) -> dict:
    """
    Validate all order inputs and return a validated parameter dictionary.
    
    This is the main entry point for order validation. It validates all
    inputs in sequence and returns a dictionary of validated parameters
    ready for order execution.
    
    Args:
        symbol: The trading pair symbol (e.g., 'BTCUSDT').
        side: The order side ('BUY' or 'SELL').
        order_type: The order type ('MARKET' or 'LIMIT').
        quantity: The order quantity (positive number).
        price: The limit price (required for LIMIT orders).
        
    Returns:
        dict: Validated order parameters with keys:
            - symbol: Validated symbol (uppercase)
            - side: Validated side (uppercase)
            - order_type: Validated order type (uppercase)
            - quantity: Validated quantity (float)
            - price: Validated price (float or None)
            
    Raises:
        ValidationError: If any input fails validation.
        
    Example:
        >>> params = validate_order_inputs(
        ...     symbol="btcusdt",
        ...     side="buy",
        ...     order_type="limit",
        ...     quantity="0.01",
        ...     price="45000"
        ... )
        >>> print(params)
        {'symbol': 'BTCUSDT', 'side': 'BUY', 'order_type': 'LIMIT',
         'quantity': 0.01, 'price': 45000.0}
    """
    logger = get_logger()
    logger.info("Starting order input validation")
    
    # Validate each field in sequence (fail-fast)
    validated_symbol = validate_symbol(symbol)
    validated_side = validate_side(side)
    validated_order_type = validate_order_type(order_type)
    validated_quantity = validate_quantity(quantity)
    validated_price = validate_price(price, validated_order_type)
    
    validated_params = {
        "symbol": validated_symbol,
        "side": validated_side,
        "order_type": validated_order_type,
        "quantity": validated_quantity,
        "price": validated_price,
    }
    
    logger.info(
        f"Validation successful: Symbol={validated_symbol} Side={validated_side} "
        f"Type={validated_order_type} Quantity={validated_quantity} "
        f"Price={validated_price if validated_price else 'N/A'}"
    )
    
    return validated_params
