#!/usr/bin/env python3
"""
Call local hummingbot-api backtesting endpoint and print exact response details.

Usage:
  python debug_backtesting_response.py \
    --config bots/conf/controllers/PPM_simple_0.1.yml \
    --start 2026/04/25 \
    --end 2026/04/26 \
    --resolution 1h
"""

import argparse
import base64
import datetime as dt
import json
import urllib.request
from pathlib import Path

import yaml


def parse_date_to_epoch(value: str) -> int:
    parsed = dt.datetime.strptime(value, "%Y/%m/%d")
    return int(parsed.replace(tzinfo=dt.timezone.utc).timestamp())


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to controller yml file")
    parser.add_argument("--start", required=True, help="Start date (YYYY/MM/DD)")
    parser.add_argument("--end", required=True, help="End date (YYYY/MM/DD)")
    parser.add_argument("--resolution", default="1h")
    parser.add_argument("--trade-cost", type=float, default=0.0006)
    parser.add_argument("--url", default="http://localhost:8000/backtesting/run-backtesting")
    parser.add_argument("--username", default="admin")
    parser.add_argument("--password", default="admin")
    args = parser.parse_args()

    config = yaml.safe_load(Path(args.config).read_text())
    payload = {
        "start_time": parse_date_to_epoch(args.start),
        "end_time": parse_date_to_epoch(args.end),
        "backtesting_resolution": args.resolution,
        "trade_cost": args.trade_cost,
        "config": config,
    }

    req = urllib.request.Request(
        args.url,
        data=json.dumps(payload).encode(),
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    token = base64.b64encode(f"{args.username}:{args.password}".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")

    response = json.loads(urllib.request.urlopen(req).read().decode())
    print("=== Backtesting Response Debug ===")
    print(f"executors_count: {len(response.get('executors', []))}")
    print(f"results: {json.dumps(response.get('results', {}), default=str)}")
    print(f"processed_data_type: {type(response.get('processed_data')).__name__}")
    if isinstance(response.get("processed_data"), dict):
        print(f"processed_data_keys: {list(response['processed_data'].keys())}")
    print(f"error: {response.get('error')}")


if __name__ == "__main__":
    main()
