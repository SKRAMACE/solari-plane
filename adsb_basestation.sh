#!/bin/bash

PORT=30003
pipe=$1

netcat localhost ${PORT} |awk 'BEGIN{FS=","} $1 !~ /MSG/{next} $2 ~ /1/{print $5,$7,$8,$11,$12,$22; fflush(stdout)} $2 ~ /[23]/ {print $5,$7,$8,$15,$16,$12,$22; fflush(stdout)}' >>${pipe}
