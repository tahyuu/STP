#!/bin/bash

PROG=`basename $0`
BITPATH="/uts_tools/burnintest/64bit"


function usage_and_exit
{
    echo "Usage: $PROG -C <config> -U <usb_config> -D <duration> -p <refresh_interval> [-P <path>] [-c <count>]"
    echo "Run Passmark with the given configuration file, duration and display"
    echo "update interval."
    echo ""
    echo "Options:"
    echo "  -C  <config>      Passmark configuration file."
    echo "  -U  <usb_config>  Passmark USB configuration fragment."
    echo "  -D  <duration>    Duration in minutes."
    echo "  -p  <refresh>     Refresh interval in milliseconds."
    echo "  -P  <burninpath>  Path to burnintest (Passmark) utilities."
    echo "  -c  <count>       Number of USB devices."
    echo ""
    echo "Example:"
    echo "$PROG -C cmdline_config.template -U cmdline_config.usb -D 1 -p 10000"
    echo "  This will run Passmark with the given configuration file for 1 minute"
    echo "  updating the display every 10 seconds."
    echo ""
    exit 1
}

function now
{
    echo `date +'%s'`
}

DEFINES="`dirname $0`/defines.sh"

if [ ! -f "$DEFINES" ]; then
    echo "E> Error the defines file does not exist: '$DEFINES'"
    exit 255
fi

. $DEFINES

typeset -i runtime=60
typeset -i interval=10000
typeset -i usb_count=0
typeset -i format=0
config=
usb_config=


# ----------------------------------------------------------------------
# Get the supplied arguments.
# ----------------------------------------------------------------------
while getopts fp:c:P:D:C:U:h opt
do
    case $opt in
        p) interval=$OPTARG;;
        c) usb_count=$OPTARG;;
        D) runtime=$OPTARG;;
        C) config=$OPTARG;;
        U) usb_config=$OPTARG;;
        P) BITPATH=$OPTARG;;
        f) format=1;;
        h) usage_and_exit;;
        \?) usage_and_exit;;
    esac
done
shift $(( $OPTIND - 1 ))

# ----------------------------------------------------------------------
# Check usage
# ----------------------------------------------------------------------
var_not_null config usb_config
if [ $? -ne 0 ]; then
    print_error "Caller failed to provide configuration file information (-C, -U)."
    exit $EXIT_FAILURE
fi

# ----------------------------------------------------------------------
# Check that the configuration files exist.
# ----------------------------------------------------------------------
file_exists "$config" "$usb_config"
if [ $? -ne 0 ]; then
    print_error "One or both of the configuration files do not exist (-C, -U)."
    exit $EXIT_FAILURE
fi


# ----------------------------------------------------------------------
# Set up path
# ----------------------------------------------------------------------
if [ ! -d $BITPATH ]; then
    print_error "Burnintest directory does not exist: '$BITPATH'"
    exit $EXIT_FAILURE
fi
PATH=$PATH:$BITPATH

# ----------------------------------------------------------------------
# Make sure that the logging directory exists. The log PATH is called
# LogFilename - rather confusing.
# ----------------------------------------------------------------------
logpath=`grep -i "^LogFilename" $config | awk '{ print $2 }'`
logprefix=`grep -i "^LogPrefix" $config | awk '{ print $2 }'`
var_not_null logpath logprefix
if [ $? -ne 0 ]; then
    print_error "One or both LogFilename and LogPrefix are not defined in $config"
    exit $EXIT_FAILURE
fi

if [ ! -d "$logpath" ]; then
    print_info "Making log directory '$logpath' .."
    mkdir -p "$logpath"
    if [ $? -ne 0 ]; then
        print_error "Failed to create log directory: '$logpath'"
        exit $EXIT_FAILURE
    fi
fi

# ----------------------------------------------------------------------
# Determine the USB drives 
# ----------------------------------------------------------------------
the_config=/tmp/cmdline_config.passmark
cp $config $the_config

echo '<Disk>' >> $the_config
#devices=`sg_map -i |  grep -v ATA | grep -v AMI | grep -v LSI | grep -v TEAC | grep -v scd1 | grep -v scd0 | awk '{print $2 }'`
#dev_count=`sg_map -i |  grep -v ATA | grep -v AMI | grep -v LSI | grep -v TEAC | grep -v scd1 | grep -v scd0 | wc -l`

devices=`usb-devices.sh`
dev_count=`echo $devices | wc -w`

# ----------------------------------------------------------------------
# Check that the correct number were detected.
# ----------------------------------------------------------------------
if [ $usb_count -ne 0 ]; then
    if [ $usb_count -ne $dev_count ]; then
        print_error "Expected $usb_count devices, only got $dev_count devices"
        print_error "Devices: $devices"
        exit $EXIT_FAILURE
    fi
fi

# For clarity this is broken into pieces.

# ----------------------------------------------------------------------
# Unmount just in case
# ----------------------------------------------------------------------
#print_info "Unmounting devices"
#for device in $devices
#do
#    # ------------------------------------------------------------------
#    # Unmount just in case.
#    # ------------------------------------------------------------------
#    mount | grep $device 
#    if [ $? -eq 0 ]; then
#        umount "${device}" 1>/dev/null 2>&1
#        sleep 1
#    fi
#done
#
## ----------------------------------------------------------------------
## Format the devices
## ----------------------------------------------------------------------
#print_info "Formatting devices with ext4 filesystem"
#for device in $devices
#do
#    fs=`blkid -o value -s TYPE $device`
#    if [ $format -eq 0 ]; then
#        if [ "$fs" == "ext4" ]; then
#            print_info "Skipping $device as it already has an ext4 filesystem."
#            continue
#        fi
#    fi
#           
#    print_info "Make ext4 filesystem on ${device}"
#    mke2fs -t ext4 -F ${device}
#    if [ $? -ne 0 ];then
#        print_error "Failed to create filesystem on $device"
#        exit $EXIT_FAILURE
#    fi
#done
#
## ----------------------------------------------------------------------
## Make the directory to mount on
## ----------------------------------------------------------------------
#print_info "Make the directory to mount on"
#for device in $devices
#do
#    mntp="/root/`echo $device | sed -e 's!/!_!g'`"
#    print_info "Mounting $device on $mntp"
#    [ ! -d $mntp ] && mkdir $mntp
#    mount "${device}" $mntp
#    if [ $? -ne 0 ]; then
#        print_error "Could not mount ${device} on $mntp"
#        exit $EXIT_FAILURE
#    fi
#done
#    

# ----------------------------------------------------------------------
# Check that the devices have a partition on them.
# ----------------------------------------------------------------------


# ----------------------------------------------------------------------
# Now add to the configuration file. We add the partition.
# ----------------------------------------------------------------------
for device in $devices
do

    # ------------------------------------------------------------------
    # Check that the disk is mounted.
    # ------------------------------------------------------------------
    mount | grep $device
    if [ $? -ne 0 ]; then
        print_error "The device is not mounted. $device is not mounted."
        exit $EXIT_FAILURE
    fi

    # ------------------------------------------------------------------
    # Check that the disk is partitioned.
    # ------------------------------------------------------------------
    the_type=`file $device`
    if [[ ! $the_type =~ "block" ]]; then
        print_error "There is no partition on this device '$device'."
        exit $EXIT_FAILURE
    fi

    print_info "Add USB device $device to configuration file."
    cat $usb_config | sed -e "s!DEVICE!${device}1!" >> $the_config
done
echo '</Disk>' >> $the_config


# ----------------------------------------------------------------------
# Run Passmark. Seems to return 130 on a successful run - maybe other
# result codes so we do not check the return code. Use badline checking
# on the generated log file. We have to use the full path even though
# BITPATH was added to our PATH as Passmark will fail otherwise!
# ----------------------------------------------------------------------
$BITPATH/bit_cmd_line_x64 -C $the_config -D $runtime -p $interval

print_line
print_info "Passmark has completed. Please use chk_badlines on the two log files"
print_info "to check whether it passed or not."
print_info "Log Files:"
print_info "  - ${logpath}${logprefix}.log"
print_info "  - ${logpath}${logprefix}.trace"
print_line

# See note above.
exit $EXIT_SUCCESS


