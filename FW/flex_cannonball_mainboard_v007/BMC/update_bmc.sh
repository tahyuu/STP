#!/bin/bash
set -o nounset
set -o pipefail

#=================================================================
# FILE: update_bmc.sh
# USAGE: ./update_bmc.sh 
# DESCRIPTION: Update BMC
#              This script will call socflash to update BMC firmware
#              After BMC update completed, it will wait about 60
#              seconds to wait BMC boot up.
# OPTIONS: -h    Print this help message
#          -n    Do not prompt for anything.
#          -q    Quiet. Be less verbose.
# REQUIERMENT: IPMI Services
#-----------------------------------------------------------------
# AUTHOR: colin.huang1@flex.com
# ORGANIZATION: 
# COMPANY: 
# REVISION: V0.1
# ----------------------------------------------------------------
#=================================================================

if [ $UID -ne 0 ]; then
        echo "You must be root to run this script, exiting."
        exit
fi

BASE=$(dirname "$0")
IMAGE=${1:-$BASE/rom.ima}
ARCH=$(uname -m | cut -b 1-6)
isparent=`ps aux | grep update_all.sh | grep -v "grep" | wc -l`
logfile="$BASE/../LOG/update_log"

# By default, be verbose and interactive, using rom.ima as the image file.
INTERACTIVE=1
VERBOSE=1




# print_help - Display help message for user.
#   function takes not arguments.
function print_help() {
    cat <<EOF
Usage: $(basename $0) [OPTION]
Update BMC firmware.
Example: $(basename $0)

Options:
  -f FILE   Specify the firmware image file. Default: rom.ima
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
    i686)
        socflash="$BASE/socflash/socflash-x86"
        ;;

    x86_64)
        socflash="$BASE/socflash/socflash-x64"
        ;;
esac



while getopts f:hnq OPT; do
    case "${OPT}" in
        "f")
            IMAGE=${OPTARG}
            ;;
        "h")
            print_help
            exit 0
            ;;
        "n")
            INTERACTIVE=0
            ;;
        "q")
            VERBOSE=0
            ;;
    esac
done

create_log_file
#echo "$socflash if=$IMAGE count=$(stat --format=%s $IMAGE) offset=0"
#exit 0
#service ipmi start 2>&1  | tee -a $logfile

# write to EEPROM the fact that firmware update is going to start
if ! ipmitool raw 6 0x52 13 0xa0 0 0x1d 0x00 1 >/dev/null 2>&1; then
    echo "fail to notify BMC that firmware update is going to start" | tee -a $logfile
    #exit 1
fi
sleep 1

# keep fan speed to 50% when firmware update
if ! ipmitool raw 0x30 0xfa 0xfa 0x7f >/dev/null 2>&1; then
    echo "fail to set fan speed"  | tee -a $logfile
    #exit 1
fi
sleep 1

"$socflash" if="$IMAGE" count="$(stat --format=%s "$IMAGE")" offset=0
if [ $? -ne 0 ] ; then
    echo "fail to socflash BMC" | tee -a $logfile
    exit 1
fi
sleep 45
