#!/bin/bash
python -m celery -A executor worker -B -E --loglevel INFO --concurrency=4 &
python app.py