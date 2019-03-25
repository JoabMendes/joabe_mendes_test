#!/usr/bin/env bash

echo "======== Testing Question C ==========="

python -m unittest test_lru_cache
flake8