#! /bin/sh

host=$1

if [ "$host" ]; then
  host="--host $host"
fi

amixer sset Headphone 100%
python3 $(dirname $0)/src/main.py --hide-mouse-pointer --no-close-button --screenblanker-profile=onoff $host
