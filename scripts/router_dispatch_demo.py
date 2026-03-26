#!/usr/bin/env python3
"""Explicit router-style dispatch (no LLM router). Aligns with notebook Router pattern.

Usage:
  python workshop/scripts/router_dispatch_demo.py add 3 5
  python workshop/scripts/router_dispatch_demo.py weather seattle
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime


def handle_math(op: str, a: float, b: float) -> str:
  if op == "add":
    return str(a + b)
  if op == "mul":
    return str(a * b)
  if op == "sub":
    return str(a - b)
  return "unknown op"


def handle_time() -> str:
  return datetime.now().strftime("%H:%M:%S")


def handle_weather(city: str) -> str:
  fake = {"seattle": "52°F drizzle", "paris": "12°C clear"}
  return fake.get(city.lower(), f"(demo) Weather for {city}: unavailable")


def main() -> int:
  parser = argparse.ArgumentParser(description="Router dispatch demo")
  parser.add_argument("route", help="math | time | weather")
  parser.add_argument("args", nargs="*", default=[])
  ns = parser.parse_args()
  r = ns.route.lower()

  if r == "math":
    if len(ns.args) < 3:
      print("math needs: op add|mul|sub a b", file=sys.stderr)
      return 1
    op, x, y = ns.args[0], float(ns.args[1]), float(ns.args[2])
    print(handle_math(op, x, y))
  elif r == "time":
    print(handle_time())
  elif r == "weather":
    city = ns.args[0] if ns.args else "seattle"
    print(handle_weather(city))
  else:
    print(f"Unknown route: {r}. Use math | time | weather", file=sys.stderr)
    return 1
  return 0


if __name__ == "__main__":
  raise SystemExit(main())
