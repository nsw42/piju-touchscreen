#! /bin/sh

amixer sset Headphone 100%
python3 $(dirname $0)/main.py --hide-mouse-pointer --no-close-button
