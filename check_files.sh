#!/usr/bin/env bash

FOLDER=$1
FORMAT=${2:-m4a}

echo
echo "The following files for $FOLDER are missing:"
echo
for phrase in $(cat phrase-list.txt)
do
    if [[ ! -f $FOLDER/$phrase.$FORMAT ]]
    then
        echo "    $phrase.$FORMAT"
    fi
done
echo

