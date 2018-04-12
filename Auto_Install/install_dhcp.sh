#install dhcp
rpm -qa | grep -i dhcp
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed dhcp skip!"
else
  echo "install dhcp"
  yum -y install dhcp
fi
#ifconfig -a
#input "please select device for dhcp service:"
cp pxe_server/dhcpd.conf /etc/dhcp/dhcpd.conf
service dhcpd restart
chkconfig dhcpd on
#chkconfig NetworkManager off
