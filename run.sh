#!/bin/bash

set -ex

cd /app/src
#cd ./src
python3 -u _1_Enforcing_speed.py
python3 -u _2_Enforcing_current.py
python3 -u _3_Enforcing_wheel_motor.py

python3 -u Table_Enforcing_speed.py
python3 -u Table_Enforcing_current.py
python3 -u Table_Enforcing_wheel_motor.py

echo "All tasks completed successfully!"
exit 0