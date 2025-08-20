import yfinance as yf
import pandas as pd
from datetime import datetime
import os
import time
import schedule
import argparse
import sys
import logging

# Config
CSV_FILE = "nvda_prices.csv"
DEFAULT_SYMBOL = "NVDA"
LOG_LEVEL = logging.INFO

logging.basicConfig(level=LOG_LEVEL, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_current_price(symbol: str = DEFAULT_SYMBOL) -> dict:
    """
    Return dict with timestamp, symbol, current_price, previous_close, day_high, day_low, volume.
    Uses ticker.info when available, otherwise falls back to history.
    """
    ticker = yf.Ticker(symbol)
    now_ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Try info first
    try:
        info = ticker.info or {}
    except Exception as e:
        logger.debug(f"yfinance .info failed: {e}")
        info = {}

    # Best-effort fields
    current = info.get("currentPrice")
    prev_close = info.get("previousClose")
    day_high = info.get("dayHigh")
    day_low = info.get("dayLow")
    volume = info.get("volume")

    # Fallback to recent history if any field is missing
    if current is None or prev_close is None or day_high is None or day_low is None or volume is None:
        try:
            # get last 2 days minute data if possible
            hist = ticker.history(period="2d", interval="1m", actions=False)
            if not hist.empty:
                last_row = hist.iloc[-1]
                # Use history values if any of the main fields are missing
                current = float(last_row["Close"]) if current is None else current
                day_high = float(hist["High"].max()) if day_high is None else day_high
                day_low = float(hist["Low"].min()) if day_low is None else day_low
                volume = int(last_row["Volume"]) if volume is None else volume
                # previous close try from history prior day
                if prev_close is None:
                    # try to get previous day's close
                    day_hist = ticker.history(period="5d", interval="1d")
                    if len(day_hist) >= 2:
                        prev_close = float(day_hist["Close"].iloc[-2])
                    else:
                        prev_close = float(day_hist["Close"].iloc[-1]) if not day_hist.empty else None
        except Exception as e:
            logger.debug(f"yfinance history fallback failed: {e}")

    # final fallbacks
    if current is None:
        current = 0.0
    if prev_close is None:
        prev_close = 0.0
    if day_high is None:
        day_high = 0.0
    if day_low is None:
        day_low = 0.0
    if volume is None:
        volume = 0

    return {
        "timestamp": now_ts,
        "symbol": symbol,
        "current_price": float(current),
        "previous_close": float(prev_close),
        "day_high": float(day_high),
        "day_low": float(day_low),
        "volume": int(volume),
    }


def append_to_csv(row: dict, csv_path: str = CSV_FILE):
    """Append single row dict to CSV (create with header if not exists)."""
    df = pd.DataFrame([row])
    header = not os.path.exists(csv_path)
    df.to_csv(csv_path, mode="a", header=header, index=False)
    logger.info(f"Appended row to {csv_path}")


def print_summary(row: dict):
    """Print a concise summary to console."""
    print("\n" + "=" * 50)
    print(f"NVDA Quick Check - {row['timestamp']}")
    print("=" * 50)
    print(f"Symbol         : {row['symbol']}")
    print(f"Current Price  : ${row['current_price']:.2f}")
    print(f"Previous Close : ${row['previous_close']:.2f}")
    print(f"Day High       : ${row['day_high']:.2f}")
    print(f"Day Low        : ${row['day_low']:.2f}")
    print(f"Volume         : {row['volume']:,}")
    print("=" * 50 + "\n")


def job(symbol: str = DEFAULT_SYMBOL, csv_path: str = CSV_FILE):
    """One scheduled job iteration: get data, print, append."""
    try:
        row = get_current_price(symbol)
        print_summary(row)
        append_to_csv(row, csv_path)
    except Exception as e:
        logger.error(f"Job failed: {e}")


def run_scheduler(interval_minutes: int = 5, symbol: str = DEFAULT_SYMBOL, csv_path: str = CSV_FILE):
    """Start scheduler to run job every `interval_minutes` minutes."""
    logger.info(f"Starting scheduler: every {interval_minutes} minute(s) for symbol={symbol}")
    schedule.clear()
    schedule.every(interval_minutes).minutes.do(job, symbol=symbol, csv_path=csv_path)
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


def parse_args():
    parser = argparse.ArgumentParser(description="NVDA basic logger with scheduler")
    parser.add_argument("--symbol", type=str, default=DEFAULT_SYMBOL, help="Ticker symbol (default NVDA)")
    parser.add_argument("--once", action="store_true", help="Run single check and exit")
    parser.add_argument("--interval", type=int, default=5, help="Scheduler interval in minutes (default 5)")
    parser.add_argument("--csv", type=str, default=CSV_FILE, help="CSV output file path")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.once:
        job(symbol=args.symbol, csv_path=args.csv)
    else:
        run_scheduler(interval_minutes=args.interval, symbol=args.symbol, csv_path=args.csv)


if __name__ == "__main__":
    main()
