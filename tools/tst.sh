#!/bin/bash

VAR='R 1'
if [[ "$VAR" =~ ^R*[0123]$ ]]; then
  echo "Cmd: $VAR - Valid cmd"
else
  echo "Unknown command: '$VAR'"
fi
if [[ "$VAR" == "R "[0-3] ]]; then
  echo "Cmd: $VAR - Valid cmd"
else
  echo "Unknown command: '$VAR'"

fi

