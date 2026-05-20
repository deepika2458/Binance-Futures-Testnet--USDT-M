"""
Streamlit UI for Binance Futures Testnet Trading Bot.

This module provides a lightweight graphical interface for placing orders.
It acts purely as a presentation layer, delegating all business logic
to the shared backend modules.
"""

import sys
from pathlib import Path

# Add project root to Python path for module resolution
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from bot import (
    get_logger,
    place_market_order,
    place_limit_order,
    ValidationError,
    ConfigurationError,
    OrderExecutionError,
)

# Order options (matching backend validators)
SIDES = ("BUY", "SELL")
ORDER_TYPES = ("MARKET", "LIMIT")

# Initialize logger
logger = get_logger()


def configure_page():
    """Configure Streamlit page settings."""
    st.set_page_config(
        page_title="Binance Futures Trading Bot",
        page_icon="📈",
        layout="centered",
    )


def render_header():
    """Render the application header."""
    st.title("📈 Binance Futures Trading Bot")
    st.caption("Testnet Environment — No Real Funds")
    st.divider()


def render_order_form():
    """Render the order input form and return submitted values."""
    with st.form("order_form", clear_on_submit=False):
        st.subheader("Place Order")

        # Symbol input
        symbol = st.text_input(
            "Trading Symbol",
            value="BTCUSDT",
            placeholder="e.g., BTCUSDT",
            help="Enter a valid Binance Futures trading pair",
        )

        # Side selection
        side = st.selectbox(
            "Order Side",
            options=SIDES,
            help="BUY to go long, SELL to go short",
        )

        # Order type selection
        order_type = st.selectbox(
            "Order Type",
            options=ORDER_TYPES,
            help="MARKET executes immediately, LIMIT waits for target price",
        )

        # Quantity input
        quantity = st.number_input(
            "Quantity",
            min_value=0.0,
            value=0.01,
            step=0.001,
            format="%.4f",
            help="Order quantity (must be positive)",
        )

        # Price input (conditionally required)
        price = None
        if order_type == "LIMIT":
            price = st.number_input(
                "Limit Price",
                min_value=0.0,
                value=0.0,
                step=0.01,
                format="%.2f",
                help="Required for LIMIT orders",
            )

        # Submit button
        submitted = st.form_submit_button("Place Order", use_container_width=True)

    return submitted, symbol, side, order_type, quantity, price


def display_order_summary(symbol, side, order_type, quantity, price):
    """Display the order request summary."""
    st.subheader("Order Request Summary")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Symbol", symbol.upper())
        st.metric("Side", side)
    with col2:
        st.metric("Order Type", order_type)
        st.metric("Quantity", f"{quantity:.4f}")

    if order_type == "LIMIT" and price:
        st.metric("Limit Price", f"{price:.2f}")


def display_order_result(response):
    """Display successful order result."""
    st.success("✅ Order placed successfully!")

    st.subheader("Order Details")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Order ID", response.get("order_id", "N/A"))
        st.metric("Status", response.get("status", "N/A"))
    with col2:
        st.metric("Executed Qty", f"{response.get('executed_qty', 0):.4f}")
        avg_price = response.get("avg_price")
        if avg_price:
            st.metric("Average Price", f"{avg_price:.2f}")

    # Show full response in expander
    with st.expander("View Full Response"):
        st.json(response)


def display_validation_error(error):
    """Display validation error message."""
    field_info = f" (Field: {error.field})" if hasattr(error, "field") and error.field else ""
    st.warning(f"⚠️ Validation Error{field_info}: {error.message}")


def display_configuration_error(error):
    """Display configuration error message."""
    st.error(f"🔧 Configuration Error: {str(error)}")
    st.info("Please ensure BINANCE_API_KEY and BINANCE_API_SECRET environment variables are set.")


def display_execution_error(error):
    """Display order execution error message."""
    error_code = f" (Code: {error.error_code})" if hasattr(error, "error_code") and error.error_code else ""
    st.error(f" Order Execution Failed{error_code}: {error.message}")


def display_unexpected_error(error):
    """Display unexpected error message."""
    st.error(" An unexpected error occurred. Please check the logs for details.")
    logger.error(f"Unexpected error in Streamlit interface: {str(error)}")


def execute_order(symbol, side, order_type, quantity, price):
    """Execute the order via backend and handle the response."""
    # Log the incoming request
    log_context = f"Symbol={symbol} Side={side} Type={order_type} Quantity={quantity}"
    if order_type == "LIMIT":
        log_context += f" Price={price}"
    log_context += " Source=Streamlit"

    logger.info(f"Order request received | {log_context}")

    try:
        # Call appropriate backend function based on order type
        if order_type == "MARKET":
            response = place_market_order(
                symbol=symbol.upper().strip(),
                side=side,
                quantity=quantity,
            )
        else:  # LIMIT
            response = place_limit_order(
                symbol=symbol.upper().strip(),
                side=side,
                quantity=quantity,
                price=price,
            )

        # Log success
        logger.info(
            f"Order placed successfully | "
            f"OrderID={response.get('order_id')} "
            f"Status={response.get('status')} "
            f"ExecutedQty={response.get('executed_qty')} "
            f"AvgPrice={response.get('avg_price')} "
            f"Source=Streamlit"
        )

        return {"success": True, "response": response}

    except ValidationError as e:
        logger.warning(f"Validation failed | Reason={e.message} Source=Streamlit")
        return {"success": False, "error_type": "validation", "error": e}

    except ConfigurationError as e:
        logger.error(f"Configuration error | Reason={str(e)} Source=Streamlit")
        return {"success": False, "error_type": "configuration", "error": e}

    except OrderExecutionError as e:
        logger.error(
            f"Order execution failed | "
            f"ErrorCode={getattr(e, 'error_code', 'N/A')} "
            f"Message={e.message} "
            f"Source=Streamlit"
        )
        return {"success": False, "error_type": "execution", "error": e}

    except Exception as e:
        return {"success": False, "error_type": "unexpected", "error": e}


def main():
    """Main application entry point."""
    configure_page()
    render_header()

    # Render form and get inputs
    submitted, symbol, side, order_type, quantity, price = render_order_form()

    # Handle form submission
    if submitted:
        # Basic UI-level validation
        if not symbol or not symbol.strip():
            st.warning("Please enter a trading symbol.")
            return

        if quantity <= 0:
            st.warning(" Quantity must be greater than zero.")
            return

        if order_type == "LIMIT" and (price is None or price <= 0):
            st.warning(" Price is required and must be greater than zero for LIMIT orders.")
            return

        st.divider()

        # Display order summary
        display_order_summary(symbol, side, order_type, quantity, price)

        st.divider()

        # Execute order with spinner
        with st.spinner("Placing order..."):
            result = execute_order(symbol, side, order_type, quantity, price)

        # Display result based on outcome
        if result["success"]:
            display_order_result(result["response"])
        else:
            error_type = result["error_type"]
            error = result["error"]

            if error_type == "validation":
                display_validation_error(error)
            elif error_type == "configuration":
                display_configuration_error(error)
            elif error_type == "execution":
                display_execution_error(error)
            else:
                display_unexpected_error(error)


if __name__ == "__main__":
    main()
