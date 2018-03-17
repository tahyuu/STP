EXIT_SUCCESS=0
EXIT_USAGE=1
EXIT_FAILURE=2
EXIT_ABORT=255

#function print_info  { PF="#I>"; echo "${PF} $@"; }
#function print_error { PF="#E>"; echo "${PF} $@"; }

function print_info  { echo "`date +'%H:%M:%S [INFO ]'` $@"; }
function print_error { echo "`date +'%H:%M:%S [ERROR]'` $@"; }

function print_line  { print_info "-------------------------------------------------------------"; }
function print_eline { print_error "-------------------------------------------------------------"; }

function file_exists
{
    for f in $@
    do
        if [ ! -f "$f" ]; then
            print_error "File does not exist: '$f'"
            return $EXIT_FAILURE
        fi
    done
    return $EXIT_SUCCESS
}

function directory_exists
{
    for f in $@
    do
        if [ ! -d "$f" ]; then
            print_error "Directory does not exist: '$f'"
            return $EXIT_FAILURE
        fi
    done
    return $EXIT_SUCCESS
}

function var_not_null
{
    for v in $@
    do
        eval N=\$$v
        if [ -z "$N" ]; then
            print_error "Variable is not defined: $v"
            return $EXIT_FAILURE
        fi
    done
    return $EXIT_SUCCESS
}

