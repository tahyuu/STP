#!/bin/bash
set -o nounset	
#==============================================================
# FILE: fru_write.sh
# USAGE:  
# DESCRIPTION: Write FRU data into FRU device 
# OPTIONS: NONE
# REQUIERMENT: IPMI Services
# BUGS: 
# NOTES: Block empty string input.
#-----------------------------------------------------------------
# AUTHOR: luke.chen@flex.com
# ORGANIZATION: 
# COMPANY: Flex
# CREATED: JUN/7/2017 
# REVISION: V0.1
# ----------------------------------------------------------------
#=================================================================

if [ $UID -ne 0 ]; then
	/bin/echo "You must be root to run this script, exiting."
	exit
fi

IPMITOOL="ipmitool"
FRUID=0

function send_errmsg () {
    /bin/echo "Update FRU field error in $1"
}

function update_field () {
    ret=$($IPMITOOL fru edit $FRUID field "$1" "$2" "$3")
    if [ $? != 0 ] ; then
        #Check if updated FRU field to new data
        /bin/echo "$ret" | grep -q 'Done'
        if [ $? != 0 ] ; then
            return 1
        fi
    fi
    
    return 0
}

#Main entry
data=${2:-}

if [ -z ${data} ] ; then
    /bin/echo "Input data is empty"
    exit 1
fi

case "$1" in
    /CSN)
        update_field c 1 ${data}
        if [ $? != 0 ] ; then
            send_errmsg "Chassis info - Serial Number"
            exit 1
        fi
        ;;
    /PN)
        update_field p 1 ${data}
        if [ $? != 0 ] ; then
            send_errmsg "Product info - Product Name"
            exit 1
        fi
        ;;
    /PSN)
        update_field p 4 ${data}
        if [ $? != 0 ] ; then
            send_errmsg "Product info - Serial Number"
            exit 1
        fi
        ;;    
    /PAT)
        update_field p 5 ${data}
        if [ $? != 0 ] ; then
            send_errmsg "Product info - Asset tag"
            exit 1
        fi
        ;;
    /CPN)
        update_field c 0 ${data}
        if [ $? != 0 ] ; then
            send_errmsg "Chassis info - Part Name"
            exit 1
        fi
        ;;
    /PPN)
        update_field p 2 ${data}
        if [ $? != 0 ] ; then
            send_errmsg "Product info - Part Number"
            exit 1
        fi
        ;;
    /PM)
        update_field p 0 ${data}
        if [ $? != 0 ] ; then
            errmsg="Product info - Manufacture Number"
            exit 1
        fi
        ;;
    *)
        echo "No such argument for fru_write"
        exit 1
esac

exit 0

