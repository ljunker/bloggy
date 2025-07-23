#!/bin/bash
PYTHONPATH=src coverage run -m pytest tests/ -v
coverage report
coverage html
coverage json