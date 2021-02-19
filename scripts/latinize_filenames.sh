#!/bin/sh
for i in *.txt ; do mv "$i" "$(echo "$i" | uconv -x 'Any-Latin;Latin-ASCII' | tr " " "_" | tr -d "'")"; done
