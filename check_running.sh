#!/bin/bash

while true
do
  if pgrep -f my_algo.py > 0
  then
      printf "\n=== BASH PROCESS RUNNING ===\n"
  else
      printf "=== LAUNCHING ALGO ===\n"
      python3 ./my_algo.py $1 $2 &
  fi
  sleep 1m
done
