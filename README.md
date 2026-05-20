# Binance Futures Testnet Trading Bot

A Python-based trading bot that places **Market** and **Limit** orders on **Binance Futures Testnet (USDT-M)** using a clean, modular backend architecture.  
The project supports both a **Command-Line Interface (CLI)** and a **lightweight Streamlit UI**, sharing the same core business logic.

This repository emphasizes **code quality, documentation, logging, and error handling**, aligned with real-world backend engineering practices.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Setup Instructions](#setup-instructions)
- [How to Run](#how-to-run)
  - [CLI Usage](#cli-usage)
  - [Streamlit UI](#streamlit-ui)
- [Logging](#logging)
- [Phase-wise Execution](#phase-wise-execution)
- [Assumptions & Scope](#assumptions--scope)
- [Evaluation Alignment](#evaluation-alignment)
- [Notes](#notes)

---

## Overview

This project was built as part of a **Python Developer Internship assignment**.  
The goal is to create a **simplified trading bot** that can interact with the **Binance Futures Testnet**, demonstrating:

- Clean and reusable code structure
- Proper validation and error handling
- Structured logging
- Clear documentation
- Real API integration (testnet environment)

The project is intentionally **strategy-agnostic** and focuses purely on engineering quality.

---

## Features

- Place **Market** and **Limit** orders
- Supports both `BUY` and `SELL` sides
- Works with **Binance Futures Testnet (USDT-M)**
- CLI-based interface for scripting and automation
- Streamlit UI for interactive usage
- Centralized validation and logging
- Clear and structured project documentation

---

## Tech Stack

- **Language:** Python 3.x  
- **API:** Binance Futures Testnet  
- **Interface:**  
  - CLI (argparse / Typer-style)
  - Streamlit (lightweight UI)
- **Logging:** Python `logging` module  
- **Environment Configuration:** Environment variables  

---

## Project Structure

```
.
├── bot/                          # Core backend logic (interface-agnostic)
│   ├── client.py                 # Binance API client wrapper
│   ├── orders.py                 # Order execution logic
│   ├── validators.py             # Input validation
│   ├── logging_config.py         # Centralized logging configuration
│   └── __init__.py
│
├── interfaces/
│   ├── cli.py                    # CLI entry point
│   └── streamlit_app.py          # Streamlit UI
│
├── docs/
│   ├── TASK.md                   # Original assignment description
│   ├── ARCHITECTURE.md           # System architecture
│   ├── CLI_USAGE.md              # CLI usage guide
│   ├── LOGGING.md                # Logging strategy
│   ├── ASSUMPTIONS.md            # Assumptions & design decisions
│   └── PHASE_EXECUTION.md        # Phase-wise execution plan
│
├── logs/
│   └── trading_bot.log
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## Documentation

All detailed documentation is available in the `docs/` directory:

- **`TASK.md`** — Original assignment requirements (verbatim)
- **`ARCHITECTURE.md`** — System design and module responsibilities
- **`CLI_USAGE.md`** — Detailed CLI usage with examples
- **`LOGGING.md`** — Logging strategy and sample logs
- **`ASSUMPTIONS.md`** — Scope, trade-offs, and design assumptions
- **`PHASE_EXECUTION.md`** — Phase-wise development plan

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/Trading-Bot-on-Binance-Futures-Testnet.git
cd Trading-Bot-on-Binance-Futures-Testnet
```

---

### 2. Create a Virtual Environment (Recommended)

```bash
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Configure Environment Variables

Set your **Binance Futures Testnet** API credentials:

```bash
export BINANCE_API_KEY="your_testnet_api_key"
export BINANCE_API_SECRET="your_testnet_api_secret"
```

(Use `set` instead of `export` on Windows.)

---

## How to Run

### CLI Usage

The CLI allows placing orders directly from the terminal.

#### Market Order Example

```bash
python interfaces/cli.py \
  --symbol BTCUSDT \
  --side BUY \
  --type MARKET \
  --quantity 0.01
```

#### Limit Order Example

```bash
python interfaces/cli.py \
  --symbol BTCUSDT \
  --side SELL \
  --type LIMIT \
  --quantity 0.01 \
  --price 45000
```

Detailed CLI documentation is available in `docs/CLI_USAGE.md`.

---

### Streamlit UI

To launch the Streamlit interface:

```bash
streamlit run interfaces/streamlit_app.py
```

The UI provides:

* Form-based order input
* Real-time feedback
* Shared backend logic with CLI
* Unified logging

---

## Logging

* Logs are written to:

  ```
  logs/trading_bot.log
  ```
* Logs include:

  * Order requests
  * API responses
  * Validation errors
  * Runtime and network errors

Log files for **one Market order** and **one Limit order** are included as required by the assignment.

See `docs/LOGGING.md` for details.

---

## Phase-wise Execution

The project follows a **six-phase execution plan**:

1. Project Foundation & Documentation
2. Core Backend Setup
3. Validation & Order Execution Logic
4. CLI Interface
5. Streamlit Interface
6. Final Polish & Submission Readiness

Each phase has clearly defined deliverables.
Details are documented in `docs/PHASE_EXECUTION.md`.

---

## Assumptions & Scope

* Testnet only (no real trading)
* USDT-M futures only
* No leverage or risk management
* One order per execution
* No trading strategy or PnL calculation

See `docs/ASSUMPTIONS.md` for the complete list.

---

## Evaluation Alignment

This project directly aligns with the evaluation criteria by demonstrating:

* Correctness via successful testnet orders
* Clean, modular code structure
* Robust validation and error handling
* Meaningful and structured logging
* Clear, professional documentation

---

## Notes

* This project is for **evaluation and learning purposes only**
* No real funds are used
* API keys must never be committed to source control
