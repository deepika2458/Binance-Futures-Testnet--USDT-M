Order Execution Logic Module

This module provides the orchestration layer between input validation
and the Binance API client. It handles order preparation, execution,
and response normalization.

The module is interface-agnostic and can be used by CLI, Streamlit,
or any other interface layer.
"""

from typing import Any, Optional

from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.logging_config import get_logger
from bot.client import BinanceTestnetClient, ConfigurationError
from bot.validators import validate_order_inputs, ValidationError


# Default time-in-force for LIMIT orders
DEFAULT_TIME_IN_FORCE = "GTC"  # Good-Til-Canceled


class OrderExecutionError(Exception):
    """
    Raised when order execution fails due to API or network errors.
    
    This exception wraps underlying API errors and provides a clean
    interface for error handling in higher layers.
    
    Attributes:
        message: Human-readable description of the error.
        error_code: The API error code (if available).
        original_exception: The underlying exception (if any).
    """
    
    def __init__(
        self,
        message: str,
        error_code: Optional[int] = None,
        original_exception: Optional[Exception] = None
    ) -> None:
        self.message = message
        self.error_code = error_code
        self.original_exception = original_exception
        super().__init__(self.message)


class OrderExecutor:
    """
    Handles order execution on Binance Futures Testnet.
    
    This class acts as the orchestration layer, coordinating:
    - Input validation
    - Order payload preparation
    - API communication
    - Response normalization
    
    Attributes:
        client: The Binance Testnet client instance.
        logger: The centralized application logger.
        
    Example:
        executor = OrderExecutor()
        result = executor.execute_order(
            symbol="BTCUSDT",
            side="BUY",
            order_type="MARKET",
            quantity=0.01
        )
        print(f"Order ID: {result['order_id']}")
    """
    
    def __init__(self, client: Optional[BinanceTestnetClient] = None) -> None:
        """
        Initialize the OrderExecutor.
        
        Args:
            client: Optional BinanceTestnetClient instance. If not provided,
                    a new client will be created.
                    
        Raises:
            ConfigurationError: If client initialization fails due to
                               missing credentials.
        """
        self.logger = get_logger()
        
        if client is not None:
            self._client = client
        else:
            self.logger.info("Initializing Binance client for order execution")
            self._client = BinanceTestnetClient()
    
    def execute_order(
        self,
        symbol: Any,
        side: Any,
        order_type: Any,
        quantity: Any,
        price: Any = None
    ) -> dict:
        """
        Execute an order on Binance Futures Testnet.
        
        This method validates inputs, prepares the order payload,
        sends the order to the API, and returns a normalized response.
        
        Args:
            symbol: The trading pair symbol (e.g., 'BTCUSDT').
            side: The order side ('BUY' or 'SELL').
            order_type: The order type ('MARKET' or 'LIMIT').
            quantity: The order quantity (positive number).
            price: The limit price (required for LIMIT orders).
            
        Returns:
            dict: Normalized order response with keys:
                - order_id: The unique order identifier
                - symbol: The trading pair
                - side: The order side
                - order_type: The order type
                - status: The order status
                - quantity: The requested quantity
                - executed_qty: The executed quantity
                - price: The order price (for LIMIT orders)
                - avg_price: The average fill price (if available)
                - time_in_force: Time-in-force setting (for LIMIT orders)
                
        Raises:
            ValidationError: If input validation fails.
            OrderExecutionError: If order execution fails due to API
                                or network errors.
        """
        # Log the incoming order request
        self.logger.info(
            f"Order request received: Symbol={symbol} Side={side} "
            f"Type={order_type} Quantity={quantity} "
            f"Price={price if price else 'N/A'}"
        )
        
        # Step 1: Validate inputs (fail-fast)
        validated_params = validate_order_inputs(
            symbol=symbol,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=price
        )
        
        # Step 2: Prepare order payload
        order_payload = self._prepare_order_payload(validated_params)
        
        # Step 3: Execute order via API
        api_response = self._send_order(order_payload)
        
        # Step 4: Normalize and return response
        normalized_response = self._normalize_response(api_response, validated_params)
        
        self.logger.info(
            f"Order placed successfully: OrderID={normalized_response['order_id']} "
            f"Status={normalized_response['status']} "
            f"ExecutedQty={normalized_response['executed_qty']} "
            f"AvgPrice={normalized_response['avg_price']}"
        )
        
        return normalized_response
    
    def _prepare_order_payload(self, validated_params: dict) -> dict:
        """
        Prepare the order payload for the Binance API.
        
        Args:
            validated_params: Dictionary of validated order parameters.
            
        Returns:
            dict: Order payload ready for the API.
        """
        payload = {
            "symbol": validated_params["symbol"],
            "side": validated_params["side"],
            "type": validated_params["order_type"],
            "quantity": validated_params["quantity"],
        }
        
        # Add price and timeInForce for LIMIT orders
        if validated_params["order_type"] == "LIMIT":
            payload["price"] = validated_params["price"]
            payload["timeInForce"] = DEFAULT_TIME_IN_FORCE
        
        self.logger.info(f"Order payload prepared: {payload}")
        
        return payload
    
    def _send_order(self, payload: dict) -> dict:
        """
        Send the order to Binance Futures Testnet.
        
        Args:
            payload: The order payload.
            
        Returns:
            dict: Raw API response.
            
        Raises:
            OrderExecutionError: If the API call fails.
        """
        try:
            self.logger.info("Sending order to Binance Futures Testnet")
            
            response = self._client.client.futures_create_order(**payload)
            
            self.logger.info(f"API response received: {response}")
            
            return response
            
        except BinanceAPIException as e:
            error_msg = f"API error during order placement: Code={e.code} Message={e.message}"
            self.logger.error(error_msg)
            raise OrderExecutionError(
                message=f"Order rejected by exchange: {e.message}",
                error_code=e.code,
                original_exception=e
            )
            
        except BinanceRequestException as e:
            error_msg = f"Request error during order placement: {e}"
            self.logger.error(error_msg)
            raise OrderExecutionError(
                message="Failed to send order request. Please check your network connection.",
                original_exception=e
            )
            
        except Exception as e:
            error_msg = f"Unexpected error during order placement: {e}"
            self.logger.error(error_msg, exc_info=True)
            raise OrderExecutionError(
                message=f"Unexpected error occurred: {str(e)}",
                original_exception=e
            )
    
    def _normalize_response(self, api_response: dict, validated_params: dict) -> dict:
        """
        Normalize the API response for consistent interface consumption.
        
        Args:
            api_response: Raw API response from Binance.
            validated_params: The validated order parameters.
            
        Returns:
            dict: Normalized response with consistent field names.
        """
        # Extract and normalize fields from API response
        normalized = {
            "order_id": api_response.get("orderId"),
            "symbol": api_response.get("symbol"),
            "side": api_response.get("side"),
            "order_type": api_response.get("type"),
            "status": api_response.get("status"),
            "quantity": float(api_response.get("origQty", 0)),
            "executed_qty": float(api_response.get("executedQty", 0)),
            "price": float(api_response.get("price", 0)) if api_response.get("price") else None,
            "avg_price": float(api_response.get("avgPrice", 0)) if api_response.get("avgPrice") else None,
            "time_in_force": api_response.get("timeInForce"),
        }
        
        return normalized


def place_market_order(
    symbol: str,
    side: str,
    quantity: float,
    client: Optional[BinanceTestnetClient] = None
) -> dict:
    """
    Convenience function to place a MARKET order.
    
    Args:
        symbol: The trading pair symbol (e.g., 'BTCUSDT').
        side: The order side ('BUY' or 'SELL').
        quantity: The order quantity.
        client: Optional BinanceTestnetClient instance.
        
    Returns:
        dict: Normalized order response.
        
    Raises:
        ValidationError: If input validation fails.
        OrderExecutionError: If order execution fails.
    """
    executor = OrderExecutor(client=client)
    return executor.execute_order(
        symbol=symbol,
        side=side,
        order_type="MARKET",
        quantity=quantity
    )


def place_limit_order(
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    client: Optional[BinanceTestnetClient] = None
) -> dict:
    """
    Convenience function to place a LIMIT order.
    
    Args:
        symbol: The trading pair symbol (e.g., 'BTCUSDT').
        side: The order side ('BUY' or 'SELL').
        quantity: The order quantity.
        price: The limit price.
        client: Optional BinanceTestnetClient instance.
        
    Returns:
        dict: Normalized order response.
        
    Raises:
        ValidationError: If input validation fails.
        OrderExecutionError: If order execution fails.
    """
    executor = OrderExecutor(client=client)
    return executor.execute_order(
        symbol=symbol,
        side=side,
        order_type="LIMIT",
        quantity=quantity,
        price=price
    )
