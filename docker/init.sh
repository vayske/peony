#!/bin/bash
screen -dmS mirai bash -c "cd ${MIRAI_DIR} && ./mcl"
sleep 1m
screen -dmS rumina bash -c "cd ${RUMINA_DIR} && python3 Rumina.py"

while true; do 
    sleep 30m
done
