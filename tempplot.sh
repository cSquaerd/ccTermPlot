#!/bin/bash
LOGFILE=/tmp/temperature.log
CPUGREP="Tctl"
GPUGREP="edge"
DELAY="2"
CURSORRESET="\033[1;1H"
CURSORNOBLINK="\033[?25l"
CURSORNORMAL="\033[?25h"

echo -n "" > ${LOGFILE}
echo -en ${CURSORNOBLINK}
TD=${DELAY}

while : ; do
	(
		date +%H:%M:%S.%2N
		sensors | grep "${CPUGREP}\|${GPUGREP}" | cut -d '+' -f 2 | cut -c 1-4
	) | xargs | tr ' ' ',' >> ${LOGFILE}

	(( LINECOUNT = $(wc -l ${LOGFILE} | cut -d ' ' -f 1) ))
	if (( LINECOUNT > 8 )); then
		#clear
		echo -en ${CURSORRESET}

		T0=$(date "+%s.%3N")
		tail -n $(( COLUMNS - 8 )) ${LOGFILE} | ./ccBlockPlot.py -saltx -c1 bright_blue -c2 navy -y0 30 -yn 90
		T1=$(date "+%s.%3N")

		TD=$(echo "${DELAY} - (${T1} - ${T0})" | bc)
		if (( $(echo "${TD} < 0" | bc) )); then
			TD=${DELAY}
		fi
		#echo ${TD}
	else
		echo "Gathering data... $(( 8 - LINECOUNT + 1 )) lines to go."
	fi

	read -sn 1 -t ${TD} KEY
	if (( ${#KEY} )); then
		break
	fi
done

echo -en ${CURSORNORMAL}

