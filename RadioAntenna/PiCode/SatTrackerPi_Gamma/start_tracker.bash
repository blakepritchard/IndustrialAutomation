#!/bin/bash
logfileRotctl=pseudoterminalsRotctl.txt
logfileWebsite=pseudoterminalsWebsite.txt
verbosityLevel="20"

trap "kill 0 & rm $logfileRotctl & rm $logfileWebsite" EXIT


echo $(date -u) " Open Virtual Com Port to RotorContol-GPredict (rotctld)"
(`socat -d -d -lf $logfileRotctl pty,raw,echo=0 pty,raw,echo=0`)&

sleep 2

declare -a arraySocatRotctlOutput
mapfile -t arraySocatRotctlOutput < "$logfileRotctl"

path_rotctld_out="$(cut -d' ' -f7 <<<"${arraySocatRotctlOutput[0]}")"
path_tracker_in="$(cut -d' ' -f7 <<<"${arraySocatRotctlOutput[1]}")"

echo $(date -u) " The rotctld servicer will write to: ${path_rotctld_out} "
(`rotctld -m 202 -s 9600 -r ${path_rotctld_out}`)&

echo $(date -u) " The SatTrackerPi listener will listen to: ${path_tracker_in} for Heading-Azimuth and Inclination-Elevation"

echo $(date -u) " Opening Virtual Com Port to Website"
(`socat -d -d -lf $logfileWebsite pty,raw,echo=0 pty,raw,echo=0`)&

sleep 2

declare -a arraySocatWebsiteOutput
mapfile -t arraySocatWebsiteOutput < "$logfileWebsite"

path_nginx_out="$(cut -d' ' -f7 <<<"${arraySocatWebsiteOutput[0]}")"
path_website_in="$(cut -d' ' -f7 <<<"${arraySocatWebsiteOutput[1]}")"

echo $(date -u) " The WebSite will write to: ${path_nginx_out} and the Tracker will listen to: ${path_website_in} "
(`echo SERIAL_PORT_NAME=\"${path_nginx_out}\" > ./SatTrackerPiDaemon/webclient_serial.config`)&

sleep 2

(`chown www-data ${path_nginx_out}`)&

sleep 2

python ./SatTrackerPiDaemon/SatTrackerPiDaemon.py -r ${path_tracker_in} -w ${path_website_in} -l ${verbosityLevel}
wait
