#!/bin/bash
if [ -f ".report.json" ]; then
          PASSED=$(python -c 'import json; print(json.load(open(".report.json"))["summary"]["passed"])')
          TOTAL=$(python -c 'import json; print(json.load(open(".report.json"))["summary"]["total"])')
          echo $PASSED
fi