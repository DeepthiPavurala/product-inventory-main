#!/bin/bash

set -e

mkdir -p reports

pytest --run-docker -q \
  --html=reports/pytest_report.html \
  --self-contained-html

echo ""
echo "Test report generated:"
echo "HTML Report: reports/pytest_report.html"