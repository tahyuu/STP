#!/bin/bash -
set -o nounset	
#==============================================================
# FILE: update_fru.sh
# USAGE: ./update_fru.sh 
# DESCRIPTION: Update FRU
# OPTIONS: NONE
# REQUIERMENT: IPMI Services
# BUGS: FRU can't write when FRU Damaged
# NOTES: Reboot System afterwards
#-----------------------------------------------------------------
# AUTHOR: 
# ORGANIZATION: 
# COMPANY: FLEX
# CREATED: 2017/07/26 19:12:33 CST
# REVISION: V0.2
# ----------------------------------------------------------------
#=================================================================

if [ $UID -ne 0 ]; then
	/bin/echo "You must be root to run this script, exiting."
	exit
fi


product_manufacturer="FLEX"
product_name="CANNONBALL16"
serial_num=$(ipmitool fru print 0 | awk '/Board Serial/ {print $4}')
/bin/sleep 1 
asset_tag=$(ipmitool fru print 0 | awk '/Product Asset Tag/ {print $5}')
/bin/sleep 1
part_num=$(ipmitool fru print 0 | awk '/Board Part Number/ {print $5}')
isparent=`ps aux | grep update_all.sh | grep -v "grep" | wc -l`

INTERACTIVE=1
VERBOSE=1

while getopts f:hnqt OPT; do
    case "${OPT}" in
        "n")
            INTERACTIVE=0
            ;;
        "q")
            VERBOSE=0
            ;;
    esac
done

case "$(arch)" in
	"i686")
		platform="32"
	;;
	"x86_64")
		platform="64"
	;;
	*)
		/bin/echo "Unknown Platform, exiting" 
		exit 1
	;;
esac

function pathfile () {
    if [[ "${1:-unset}" != /* ]];then
        cd ..
	pathfile=`pwd`
        pathfile="$pathfile/$1"
	cd - > /dev/null
    else
        pathfile=$1
    fi
}

function find_ORDER_FILE(){ 
	contain_f=`ps aux | awk -F '-f ' '/update_all.sh/{print $2}' | awk '{print $1}' | grep -v "print" |tail -n1`
	if [ -z "$contain_f"  ]; then 	
		ORDER_FILE="../update_order.cfg"
	else 
		orderpath="$contain_f"
		pathfile $orderpath
		ORDER_FILE=$pathfile	
	fi
}

# create log file 
function logfile () {
        logfile="../LOG/update_log"

        if [ ! -f $logfile ];then
                touch $logfile
        elif [ "$isparent" -gt 0 ]; then         
		first=`head -n 1 $ORDER_FILE`
                currentdir=`pwd | awk -F "/" '{print $NF}'`
                if [ "$currentdir" = "$first" ] ;then
                        rm -rf $logfile
                        touch $logfile
                fi
        else
                rm -rf $logfile
                touch $logfile

        fi
}

function yesNo () {
	case ${response} in
		[Yy][Ee][Ss]|[Yy])
			# exit and continue
		;;
		[Nn][Oo]|[Nn])
			# return to the calling function to try the alternative.
			runIt
		;;
		*)
			# try again
			${FUNCNAME[1]} 
		;;
	esac
}

function sernum () {
	testIt () {
		if [ -z $serial_num ];then
			/bin/echo "Serial Number is empty!"
		fi
	}
	runIt () {
		read -p "Enter or scan the serial number :" serial_num
		/bin/echo -e "The current chassis serial number is ${serial_num}"
		testIt
		read -p "Is this correct (Y/N) : " response
		yesNo ${response}
	}
	/bin/echo -e "The current chassis serial number is ${serial_num}"
	testIt
	read -p "Is this correct (Y/N) : " response
	yesNo ${response}

}

function atag () {
	testIt () {
		if [ -z $asset_tag ] ;then
			/bin/echo "Asset Tag is empty!"
		fi
	}
	runIt () {
		read -p "Enter or scan the asset tag :" asset_tag
		/bin/echo -e "The current asset tag is ${asset_tag}"
		testIt
		read -p "Is this correct (Y/N) : " response
		yesNo ${response}
	}
	/bin/echo -e "The current asset tag is ${asset_tag}"
	testIt
	read -p "Is this correct (Y/N) : " response
	yesNo ${response}
}

function find_PN () {
SNPIN=${serial_num:0:4}
case $SNPIN in
        *)
        	part_num="1A21K0T00-600-G"
	;;
esac
}

function update_fru () {
	 

	/bin/echo "Updating FRU, please wait..."
	# array of fields to update with values from variables
	field_array=( 	\
		 	[0]="/CSN ${serial_num}" \
			[1]="/PN ${product_name}" \
			[2]="/PSN ${serial_num}" \
			[3]="/PAT ${asset_tag}" \
                        [4]="/CPN ${part_num}" \
                        [5]="/PPN ${part_num}" \ 
			[6]="/PM ${product_manufacturer}");
	for i in $(seq 0 $((${#field_array[@]}-1))); do
		/bin/echo "./fru_write.sh ${field_array[$i]}" 
		./fru_write.sh ${field_array[$i]} > /dev/null 2>&1
		if [ ${PIPESTATUS[0]} -ne 0 ];then
		       /bin/echo "Flash Failed on ${field_array[$i]}" 
		       exit 1
		fi
		/bin/sleep 1
	done
}

check_passorfail() {

    if [ "${1:-unset}" -ne 0 ]; then       
    	if [ "${2:-unset}" = "-showfail" ]; then
	 	/bin/cat $logfile | /bin/grep -i "Failed"
	fi 
        exit 1
    else
        /bin/echo "Update FRU ------------------- [PASS]" | tee -a $logfile
        if [ "$isparent" -gt 0 ]; then
                last=`tail -n 1 $ORDER_FILE`
                currentdir=`pwd | awk -F "/" '{print $NF}'`
                if [ "$currentdir" = "$last" ] ;then
                        /bin/echo "Remember to cold reset if the updating process finished! (cold reset command: ipmitool chassis power cycle)" | tee -a $logfile
                fi
        else
        /bin/echo "Remember to cold reset if the updating process finished! (cold reset command: ipmitool chassis power cycle)" | tee -a $logfile
        fi
    fi

}

check_order_dmifru() {

        if [ "$isparent" -gt 0 ]; then
                dmilocate=`grep -n DMI $ORDER_FILE | awk -F ":" '{print $1}'`
                frulocate=`grep -n FRU $ORDER_FILE | awk -F ":" '{print $1}'`
	        if [ -n "$dmilocate" ] && [ -n "$frulocate" ]; then
                        if [ "$frulocate" -gt "$dmilocate" ]; then
                                currentdir=`pwd | awk -F "/" '{print $NF}'`
                                if [ "$currentdir" = "DMI" ]; then
                                        sernum
                                        atag
                                else
                                        serial_num=$(dmidecode -t3 | awk '/Serial/ {print $3}')
                                        asset_tag=$(dmidecode -t3 | awk '/Asset/ {print $3}')
                                fi
                        elif [ "$frulocate" -lt "$dmilocate" ]; then
                                currentdir=`pwd | awk -F "/" '{print $NF}'`
                                if [ "$currentdir" = "FRU" ]; then
                                        sernum
                                        atag
                                fi
                        fi
                else
                        sernum
                        atag
                fi

	else
                sernum
                atag
        fi
}

#---MAIN---# 
find_ORDER_FILE
logfile

if [ "${VERBOSE}" -eq 0 ] && [ "${INTERACTIVE}" -eq 0 ]; then
         update_fru >> $logfile
         rval=${PIPESTATUS[0]}
         check_passorfail $rval -showfail

elif [ "${VERBOSE}" -ge 1 ] && [ "${INTERACTIVE}" -eq 0 ]; then
         update_fru | tee -a $logfile
         rval=${PIPESTATUS[0]}
         check_passorfail $rval

elif [ "${VERBOSE}" -eq 0 ] && [ "${INTERACTIVE}" -ge 1 ]; then
         check_order_dmifru
         update_fru >> $logfile
         rval=${PIPESTATUS[0]}
         check_passorfail $rval -showfail

else
         check_order_dmifru
         update_fru | tee -a $logfile
         rval=${PIPESTATUS[0]}
         check_passorfail $rval
fi

