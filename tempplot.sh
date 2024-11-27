#!/bin/bash
LOGFILE=/tmp/temperature.log
CPUGREP="Tctl"
GPUGREP="edge"
DELAY="0.5"
CURSORRESET="\033[1;1H"
CURSORNOBLINK="\033[?25l"
CURSORNORMAL="\033[?25h"

echo -n "" > ${LOGFILE}
echo -en ${CURSORNOBLINK}

while : ; do
	(
		date +%H:%M:%S.%2N
		sensors | grep "${CPUGREP}\|${GPUGREP}" | cut -d '+' -f 2 | cut -c 1-4
	) | xargs | tr ' ' ',' >> ${LOGFILE}

	(( LINECOUNT = $(wc -l ${LOGFILE} | cut -d ' ' -f 1) ))
	if (( LINECOUNT > 8 )); then
		#clear
		echo -en ${CURSORRESET}
		tail -n $(( COLUMNS - 8 )) ${LOGFILE} | ./ccBlockPlot.py -saltzx -c1 bright_blue -c2 navy
	else
		echo "Gathering data... $(( 8 - LINECOUNT )) lines to go."
	fi

	read -sn 1 -t ${DELAY} KEY
	if (( ${#KEY} )); then
		break
	fi
done

echo -en ${CURSORNORMAL}

