#!/bin/bash

python runtime/yagpt.py &

cd front
uvicorn frontback:app --reload --host 0.0.0.0 --port 8081 &

wait
