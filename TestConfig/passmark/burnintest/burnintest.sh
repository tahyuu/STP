#!/bin/bash

DIR="$( cd -P "$( dirname "${BASH_SOURCE[0]}" )" && pwd)"

#Check if 64 bit or 32 bit
platform=$(uname -m)
if [ "$platform" = "x86_64" ]; then
bitexe="$DIR/64bit/bit_gui_x64" 
echo "64-bit OS detected, launching" $bitexe
else
bitexe="$DIR/32bit/bit_gui_x32" 
echo "32-bit OS detected, launching" $bitexe
fi

echo
#Check if required libraries are there, warn if not

#for i in $( ldd $bitexe |cut -f2 | cut -d' ' -f1 ); do
count=0
for i in $( ldd $bitexe | grep "not found" |cut -f2 | cut -d' ' -f1 ); do
    echo "Missing Library: " $i
    count=1
done

echo
if [ $count -gt 0 ]; then
echo "Missing libraries detected!"
echo "To use the GUI version of BurnInTest you will need to install the above" 
echo "libraries using your prefered package manager before running BurnInTest"
echo "A command line version of BurnInTest that requires less libraries"
echo "is also available in the 32bit and 64bit directories." 
else
exec $bitexe $@
fi
