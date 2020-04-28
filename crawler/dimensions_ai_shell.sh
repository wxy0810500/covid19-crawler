#!/bin/bash
echo "usage ./dimension_ai_shell.sh {source file dir} {output file dir} {redownload raw file}:default=false"

redownload=${1:-false}
sourceFileDir=${3:-.}
outFileDir=${2:-.}

today=$(date +%F)
DOWNLOAD_FILE="${sourceFileDir}/raw_dimension_ai_${today}.csv"
DOWNLOAD_URL="https://docs.google.com/spreadsheets/d/1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw/export?format=csv&id=1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw&gid=1470772867"
OUT_FILE="${outFileDir}/formatted_dimension_ai_${today}_upToNow.csv"

if [ -a "$DOWNLOAD_FILE" ]
then
    if [ "$redownload" == True ]
    then
        echo "raw file exsit,redownload it"
        rm "$DOWNLOAD_FILE"
        wget -O "$DOWNLOAD_FILE" "$DOWNLOAD_URL"
    else
        echo "raw file exsit, do not redownload"
    fi
else
    # shellcheck disable=SC2086
    wget -O "$DOWNLOAD_FILE" $DOWNLOAD_URL
fi

if [ -a "$DOWNLOAD_FILE" ]
then
    tail -n +2 "$DOWNLOAD_FILE" | awk -F ',' 'BEGIN{printf "%s\t%s\t%s\t%s\t%s\t%s\n","data_add", "title", "abstract", "Publication date", "doi", "source_link"} {printf "%s\t%s\t%s\t%s\t%s\t%s\n",$1,$8,$7,$12,$3,$30;}' > $OUT_FILE
else
    echo "out_file doesn't exist!"
fi