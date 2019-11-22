#!/bin/bash

# https://stackoverflow.com/questions/192249/how-do-i-parse-command-line-arguments-in-bash

while [[ $# -gt 0 ]]
do
key="$1"

case $key in
    --cpu)
    CPU="$2"
    shift # past argument
    shift # past value
    ;;
    --mem)
    MEM="$2"
    shift # past argument
    shift # past value
    ;;
    --timeout)
    TIMEOUT="$2"
    shift # past argument
    shift # past value
    ;;
    *)    # unknown option
    shift # past argument
    ;;
esac
done

sleep $TIMEOUT

echo "Dummy result: $(expr $CPU + $MEM)"

# Uncomment to simulate command failure
# echo "But I have failed X_X" >&2
# exit 1