﻿#!/bin/bash
set -o nounset
	
#==============================================================
# FILE: update_bios.sh
# USAGE: ./update_bios.sh 
# DESCRIPTION: Update BIOS
# OPTIONS: NONE
# REQUIERMENT: Development Tools
#-----------------------------------------------------------------
# AUTHOR: felix.hu@flex.com
# ORGANIZATION: 
# COMPANY: 
# CREATED: 2017/7/10
# REVISION: V0.1
# ----------------------------------------------------------------
#=================================================================

if [ $UID -ne 0 ]; then
  /bin/echo "You must be root to run this script, exiting."
  exit
fi

BASE=$(dirname "$0")
IMAGE=${1:-$BASE/CANBL050.BIN}
ARCH=$(uname -m | cut -b 1-6)
logfile="$BASE/../LOG/update_log"
isparent=`ps aux | grep update_all.sh | grep -v "grep" | wc -l`

INTERACTIVE=1
VERBOSE=1

# print_help - Display help message for user.
function print_help () {
  cat << EOF
Usage: $(basename $0) [OPTION]
Update BIOS firmware.
Example: $(basename $0)

Options:
  -f FILE   Specify the firmware image file.
  -h        Print this help message

EOF
}
#  -n        Do not prompt for anything.
#  -q        Quiet. Be less verbose.


# create log file 
function create_log_file () {
  if [ ! -f $logfile ];then
      touch $logfile
  elif [ "$isparent" -eq 0 ]; then
    rm -fr $logfile
    touch $logfile
  fi
}


case "$ARCH" in
i686 )
  /bin/echo "Not support 32bit."
  exit 1
  ;;
x86_64 )
  afulnx="$BASE/afulnx_64"
  ;;
esac


while getopts f:hnq OPT; do
  case "${OPT}" in
  "f" )
    IMAGE=${OPTARG}
    ;;
  "h" )
    print_help
    exit 0
    ;;
  "n" )
    INTERACTIVE=0
    ;;
  "q" )
    VERBOSE=0
    ;;
  esac
done


#---MAIN---# 

create_log_file

"$afulnx" "$IMAGE" /p /b /n /me
if [ $? -ne 0 ] ; then
    echo "fail to flash BIOS" | tee -a $logfile
    exit 1
fi
/bin/sleep 1
 
 