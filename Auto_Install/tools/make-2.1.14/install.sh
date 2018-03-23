#!/usr/bin/env bash

INSTDIR=/uts_tools/fio

mkdir -p   $INSTDIR/
rm    -rf  $INSTDIR/*
cp    -r * $INSTDIR/

cd $INSTDIR/

tar xf fio.tgz

mkdir -p /usr/local/bin/
mv -f bin/*   /usr/local/bin/
rm -rf bin

mkdir -p /usr/local/share/fio/
mv -f share/* /usr/local/share/fio/
rm -rf share

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

