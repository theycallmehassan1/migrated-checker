#!/usr/bin/env python3
"""
Legacy Endpoint Reachability Checker

A small utility for the discovery phase of a legacy-to-cloud or
zero-trust transition, the same step the Environment Intake workbook
in the Transition-State Zero Trust Adoption Toolkit calls for before
anything gets scored:

    https://github.com/theycallmehassan1/transition-state-zero-trust-toolkit

Given a CSV of hostname/IP and port pairs (typically exported from the
intake's Workload Register sheet), this script checks which are
currently reachable over TCP and reports how long the connection took.
It does nothing except open and close a socket. It sends no
credentials, no payloads, and performs no scanning beyond the single
port listed for each row.

Usage:
    python3 reachability_checker.py inventory.csv [--timeout 3] [--out results.csv]

inventory.csv columns (header row required):
    name,host,port

Example inventory.csv:
    name,host,port
    file-server,fs01.internal.example,445
    tax-software-db,db01.internal.example,1433
    m365-admin,outlook.office365.com,443
"""

import argparse
import csv
import socket
import sys
import time
from dataclasses import dataclass


@dataclass
class Result:
    name: str
    host: str
    port: int
    reachable: bool
    latency_ms: float
    error: str


def check_endpoint(host: str, port: int, timeout: float) -> tuple[bool, float, str]:
    start = time.perf_counter()
    try:
        with socket.create_connection((host, port), timeout=timeout):
            latency_ms = (time.perf_counter() - start) * 1000
            return True, latency_ms, ""
    except OSError as exc:
        latency_ms = (time.perf_counter() - start) * 1000
        return False, latency_ms, str(exc)


def load_inventory(path: str) -> list[dict]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        required = {"name", "host", "port"}
        if not required.issubset(reader.fieldnames or []):
            missing = required - set(reader.fieldnames or [])
            raise ValueError(f"inventory CSV is missing column(s): {', '.join(sorted(missing))}")
        return list(reader)


def run(inventory_path: str, timeout: float, out_path: str | None) -> list[Result]:
    rows = load_inventory(inventory_path)
    results: list[Result] = []

    for row in rows:
        name = row["name"].strip()
        host = row["host"].strip()
        port = int(row["port"].strip())

        reachable, latency_ms, error = check_endpoint(host, port, timeout)
        results.append(Result(name, host, port, reachable, round(latency_ms, 1), error))

        status = "reachable" if reachable else "unreachable"
        detail = f"{latency_ms:.0f} ms" if reachable else error
        print(f"[{status:>11}] {name:<24} {host}:{port}  ({detail})")

    if out_path:
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "host", "port", "reachable", "latency_ms", "error"])
            for r in results:
                writer.writerow([r.name, r.host, r.port, r.reachable, r.latency_ms, r.error])
        print(f"\nWrote {len(results)} result(s) to {out_path}")

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Check reachability of a legacy environment inventory.")
    parser.add_argument("inventory", help="Path to inventory CSV (columns: name,host,port)")
    parser.add_argument("--timeout", type=float, default=3.0, help="Connection timeout in seconds (default: 3.0)")
    parser.add_argument("--out", dest="out_path", help="Optional path to write results as CSV")
    args = parser.parse_args()

    try:
        results = run(args.inventory, args.timeout, args.out_path)
    except (FileNotFoundError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    unreachable = sum(1 for r in results if not r.reachable)
    if unreachable:
        print(f"\n{unreachable} of {len(results)} endpoint(s) unreachable.")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
