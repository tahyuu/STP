#!/bin/bash

PROG=`basename $0`
BITPATH="/uts_tools/burnintest/64bit"


function usage_and_exit
{
    echo "Usage: $PROG -C <config> -D <duration> -p <refresh_interval>"
    echo "Run Passmark with the given configuration file, duration and display"
    echo "update interval."
    echo ""
    echo "Options:"
    echo "  -C    <config>     Passmark configuration file."
    echo "  -D    <duration>   Duration in minutes."
    echo "  -p    <refresh>    Refresh interval in milliseconds."
    echo "  -P    <burninpath> Path to burnintest (Passmark) utilities."
    echo ""
    echo "Example:"
    echo "$PROG -C cmdline_config.usb -D 1 -p 10000"
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

# ----------------------------------------------------------------------
# Get the supplied arguments.
# ----------------------------------------------------------------------
while getopts p:P:D:C:h opt
do
    case $opt in
        p) interval=$OPTARG;;
        D) runtime=$OPTARG;;
        C) config=$OPTARG;;
        P) BITPATH=$OPTARG;;
        h) usage_and_exit;;
        \?) usage_and_exit;;
    esac
done
shift $(( $OPTIND - 1 ))

# ----------------------------------------------------------------------
# Check usage
# ----------------------------------------------------------------------
var_not_null config
if [ $? -ne 0 ]; then
    print_error "Caller failed to provide configuration file (-C)."
    exit $EXIT_FAILURE
fi

# ----------------------------------------------------------------------
# Check that the configuration file exists.
# ----------------------------------------------------------------------
file_exists "$config"
if [ $? -ne 0 ]; then
    print_error "The configuration file does not exist: '$config'"
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
# Run Passmark. Seems to return 130 on a successful run - maybe other
# result codes so we do not check the return code. Use badline checking
# on the generated log file. We have to use the full path even though
# BITPATH was added to our PATH as Passmark will fail otherwise!
# ----------------------------------------------------------------------
$BITPATH/bit_cmd_line_x64 -C $config -D $runtime -p $interval

print_line
print_info "Passmark has completed. Please use chk_badlines on the two log files"
print_info "to check whether it passed or not."
print_info "Log Files:"
print_info "  - ${logpath}${logprefix}.log"
print_info "  - ${logpath}${logprefix}.trace"
print_line

# See note above.
exit $EXIT_SUCCESS






