#!/bin/bash
logfile=pseudoterminals.txt

trap "kill 0 & rm $logfile" EXIT



(`socat -d -d -lf $logfile pty,raw,echo=0 pty,raw,echo=0`)&

sleep 2

declare -a arraySocatOutput
mapfile -t arraySocatOutput < "$logfile"

path_rotctld_out="$(cut -d' ' -f7 <<<"${arraySocatOutput[0]}")"
path_tracker_in="$(cut -d' ' -f7 <<<"${arraySocatOutput[1]}")"

echo "The rotctld servicer will write to: ${path_rotctld_out} "
(`rotctld -m 202 -s 9600 -r ${path_rotctld_out}`)&

echo "The SatTrackerPi listener will listen to: ${path_tracker_in}"
('python SatTrackerPiDaemon -p ${path_tracker_in}')

wait
