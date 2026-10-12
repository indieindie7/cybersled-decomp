#!/bin/bash
# headless Ghidra on the CyberSled project. usage: csrun.sh <log> [headless args after project name]
log="$1"; shift
cd /c/Users/john/Documents/CyberSled/ghidra || exit 1
cmd //c "C:\Users\john\Documents\Tools\ghidra-headless.bat C:\Users\john\Documents\CyberSled\ghidra CyberSled $*" > "$log" 2>&1
tail -3 "$log"
