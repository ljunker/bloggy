#!/bin/bash
PYTHONPATH=src coverage run -m pytest --json-report tests/ -v
coverage report
coverage html
coverage json