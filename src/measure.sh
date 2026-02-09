#!/bin/bash


if [ $# -lt 2 ] || [ $# -gt 4 ]; then
    echo "run this as $0 instances_path n [config_path] [filenames_list]"
    echo "where n is the number of instances that will be solved at the same time"
    exit 1
fi

SAVEIFS=$IFS
IFS=$(echo -en "\n\b")

if [ $# -le 3 ]; then
    find "$1" -name "*.soc" > "$1/files.txt"
else
    /bin/cp -f "$4" "$1/files.txt"
fi

cores=$2
if [ $# -ge 3 ];then
    flag="--config"
    config="$3"
fi

parallel --jobs $cores python3 main.py $flag $config --filename < "$1/files.txt" > "$1/res.csv" 2> "$1/debug.txt"
if [ $? -ne 0 ]; then
    echo "An error happened" >&2
fi

sort "$1/res.csv" | uniq > "$1/tmp.csv"
mv "$1/tmp.csv" "$1/res.csv"

IFS=$SAVEIFS