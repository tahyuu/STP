#!/usr/bin/env bash

INSTDIR=/uts_tools/fio_f

mkdir -p    $INSTDIR/
mv sh_sys_usage /bin/
cp    -rf * $INSTDIR/

if [ $? == 0 ];
then
    #---------------------------------------------
    # Do not change this message!
    # Dialogue file expects
    #   'Installation successful'
    # output.
    #---------------------------------------------
    echo "Installation successful."
    exit 0
else
    echo "#e> Installation failed."
    exit 1
fi

