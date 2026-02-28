#!/bin/bash
FILE="$1"

RES=`csvgrep -c 3 -m "$2" "$FILE" | csvcut -c "RB_System_Signal_Name","RB_Value","RB_Unit","RB_SYS_Signal_Description"`
if grep -qi "$2" "$FILE"; then
	len=`echo "$RES" | wc -l | cut -d " " -f 1`
	if [ "$len" -le "1" ]; then 
		echo "Might be there but with different casing:"
		grep --color=always -i "$2" "$FILE"
	else
		echo "$RES"
	fi
	exit 0
fi
echo "Not found"
exit 1
