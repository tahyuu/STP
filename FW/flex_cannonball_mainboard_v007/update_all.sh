#!/usr/bin/env /bin/bash

export PATH=/bin:/usr/bin:/sbin:/usr/sbin

# exit_with_message - exit function with specific exit code and message
#   $1 is the exit code
#   $2 is the message to print, default is "Exiting exitcode"
function exit_with_message() {
    ECODE=$(echo ${1} | sed -e 's/[^0-9]//g' | sed -e 's/^0*//')
    echo "${2:-Exiting ${ECODE:=99}}"
    exit ${ECODE}
}

# abort_exit - Cleanup function when exiting on unexpected signal
function abort_exit() {
    exit_with_message 99 "Execution aborted by user."
}

# cmd_name - Create command name from update directory
#   $1 is the directory name the update exists in.
#
#   Example: cmd_name BIOS returns update_bios.sh
function cmd_name() {
    CMD=$(echo "${1}" | tr '[:upper:]' '[:lower:]')
    echo "update_${CMD}.sh"
}

# print_help - Display help message for user.
#   function takes not arguments.
function print_help() {
    cat <<EOF
Usage: $(basename $0) [OPTION]
Update all ODM firmware for this host.
Example: $(basename $0)

Options:
  -f FILE   Specify the order file. Default: update_order.cfg
  -h        Print this help message
  -n        Do not prompt for anything.
  -q        Quiet. Be less verbose.
  -t        Test mode. Assumes verbose.

EOF
}

# What signals get trapped
trap abort_exit INT TERM

# By default, be verbose and interactive, using update_order.cfg as the order file.
ORDER_FILE="update_order.cfg"
INTERACTIVE=1
VERBOSE=1
TEST_MODE=0

while getopts f:hnqt OPT; do
    case "${OPT}" in
        "f")
            ORDER_FILE=${OPTARG}
            ;;
        "h")
            print_help
            exit 0
            ;;
        "n")
            INTERACTIVE=0
            FLAGS="${FLAGS} -n"
            ;;
        "q")
            VERBOSE=0
            FLAGS="${FLAGS} -q"
            ;;
        "t")
            TEST_MODE=1
            FLAGS="${FLAGS} -t"
            ;;
    esac
done

if [ ! -r "${ORDER_FILE}" ]; then
    exit_with_message 1 "Order file \"${ORDER_FILE}\" not found."
fi

for UPDATE_DIR in $(cat "${ORDER_FILE}"); do
    if [ "${VERBOSE}" -ge 1 ]; then
        echo "Beginning ${UPDATE_DIR} update"
    fi
    if [ ! -d "${UPDATE_DIR}" ]; then
        exit_with_message 2 "Update dir ${UPDATE_DIR} not found."
    fi
    CMD=$(cmd_name "${UPDATE_DIR}")
    pushd "${UPDATE_DIR}" >/dev/null 2>&1
    if [ ! -f "${CMD}" ]; then
        exit_with_message 3 "Update command \"${CMD}\" not found."
    fi
    if [ ${TEST_MODE} -ge 1 ]; then
        echo "Test: ./${CMD} ${FLAGS}"
    else
        if [ ${VERBOSE} -ge 1 ]; then
            echo "Running: ./${CMD} ${FLAGS}"
        fi
        ./${CMD} ${FLAGS}
        rval=$?
        if [ $rval -ne 0 ]; then
            exit_with_message ${rval} "${CMD} ${FLAGS} exited with non-zero code. [${rval}]"
        fi
    fi
    popd >/dev/null 2>&1
done

exit_with_message 0 "Updates completed successfully"
