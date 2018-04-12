#!/bin/bash
# author:yong.tan
# install dhcp server

rpm -qa | grep -i dhcp-4
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed dhcp skip!"
else
  echo "install dhcp"
  yum -y install dhcp
fi

echo "###################start install dhcp server#####################3";
echo "We will install dhcp server on：$1";
echo "      $1 Ip will be fixed as：$2";
obj_eth=ifcfg-$1
echo $obj_eth
echo "1,making ethernet config file"
cp ifcfg-ethX /etc/sysconfig/network-scripts/$obj_eth
sed -i "s/eth./$1/g" /etc/sysconfig/network-scripts/$obj_eth
sed -i "s/IPADDR.\{11,\}/IPADDR=$2/g" /etc/sysconfig/network-scripts/$obj_eth
ifconfig $1 $2/24 up
service network restart
#yum -y install dhcp
#ifconfig -a
cp pxe_server/dhcpd.conf /etc/dhcp/dhcpd.conf
service dhcpd restart
chkconfig dhcpd on
service dhcpd status
#chkconfig NetworkManager off
