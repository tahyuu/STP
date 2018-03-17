#!/bin/bash

PROG=`basename $0`
BITPATH="/uts_tools/burnintest/64bit"


function usage_and_exit
{
    echo "Usage: $PROG -C <config> -U <hdd_config> -D <duration> -p <refresh_interval> [-P <path>] [-c <count>] devices"
    echo "Run Passmark with the given configuration file, duration and display"
    echo "update interval. Add storage devices to the configuration file."
    echo ""
    echo "Options:"
    echo "  -C  <config>      Passmark configuration file."
    echo "  -U  <hdd_config>  Passmark HDD configuration fragment."
    echo "  -D  <duration>    Duration in minutes."
    echo "  -p  <refresh>     Refresh interval in milliseconds."
    echo "  -P  <burninpath>  Path to burnintest (Passmark) utilities."
    echo "  -c  <count>       Number of USB devices."
    echo ""
    echo "Example:"
    echo "$PROG -C cmdline_config.template -U cmdline_config.usb -D 1 -p 10000 /dev/sda /dev/sdb"
    echo "  This will run Passmark with the given configuration file for 1 minute"
    echo "  updating the display every 10 seconds. The storage devices /dev/sda and /dev/sdb will"
    echo "  be used for testing."
    echo ""
    echo "$PROG -C cmdline_config.template -U cmdline_config.usb -D 1 -p 10000 `smartctl --scan | cut -f1 -d ' '`"
    echo "As above but use every storage device."
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
typeset -i hdd_count=0
typeset -i raw_disk_testing=0

config=
hdd_config=


# ----------------------------------------------------------------------
# Get the supplied arguments.
# ----------------------------------------------------------------------
while getopts p:c:P:D:C:U:h opt
do
    case $opt in
        p) interval=$OPTARG;;
        c) hdd_count=$OPTARG;;
        D) runtime=$OPTARG;;
        C) config=$OPTARG;;
        U) hdd_config=$OPTARG;;
        P) BITPATH=$OPTARG;;
        h) usage_and_exit;;
        \?) usage_and_exit;;
    esac
done
shift $(( $OPTIND - 1 ))

# ----------------------------------------------------------------------
# Everything else is a storage device
# ----------------------------------------------------------------------
devices="$@"

# ----------------------------------------------------------------------
# Check usage
# ----------------------------------------------------------------------
var_not_null config hdd_config
if [ $? -ne 0 ]; then
    print_error "Caller failed to provide configuration file information (-C, -U)."
    exit $EXIT_FAILURE
fi

# ----------------------------------------------------------------------
# Check that the configuration files exist.
# ----------------------------------------------------------------------
file_exists "$config" "$hdd_config"
if [ $? -ne 0 ]; then
    print_error "One or both of the configuration files do not exist (-C, -U)."
    exit $EXIT_FAILURE
fi

# ----------------------------------------------------------------------
# Are we using Raw disk testing?
# ----------------------------------------------------------------------
egrep '^TestAllRAWDisks' $hdd_config
if [ $? -eq 0 ]; then
    print_info "Disk testing will use RAW testing."
    raw_disk_testing=1
else
    print_info "Disk testing will use partition based testing."
    raw_disk_testing=0
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

the_config=/tmp/cmdline_config.passmark
cp $config $the_config

# ----------------------------------------------------------------------
# Handle any storage devices
# ----------------------------------------------------------------------
if [ -n "$devices" ]
then
    echo '<Disk>' >> $the_config

    for device in $devices
    do

        # ------------------------------------------------------------------
        # Check that the disks are mounted.
        # ------------------------------------------------------------------
        mount | grep "${device}1"
        if [ $? -ne 0 ]; then
            print_error "The partition on device $device is not mounted. ${device}1 not mounted."
            exit $EXIT_FAILURE
        fi

        # ------------------------------------------------------------------
        # Now add to the configuration file.
        # ------------------------------------------------------------------
        print_info "Add device ${device}1 to the configuration file."
        cat $hdd_config | sed -e "s!DEVICE!${device}1!" >> $the_config
    done
    echo '</Disk>' >> $the_config
fi

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


