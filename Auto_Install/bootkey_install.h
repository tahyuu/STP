#install tools
rpm -qa | grep -i yum-utils
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed yum-utils.skip!"
else
  echo "install yum-utils"
  yum install -y Install/rpm_files/epel-release-7-9.noarch.rpm
fi
#install vim-enhanced
rpm -qa | grep -i vim-enhanced
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed vim-enhanced.skip!"
else
  echo "install vim-enhanced"
  yum install -y Install/rpm_files/vim-enhanced-7.4.160-2.el7.x86_64.rpm
fi
#install acpi
rpm -qa | grep -i acpi
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed acpi skip!"
else
  echo "install acpi"
  yum install -y Install/rpm_files/acpid-2.0.19-8.el7.x86_64.rpm
fi
#install net-tools
rpm -qa | grep -i net-tools
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed net-tools.skip!"
else
  echo "install net-tools"
  yum install -y Install/rpm_files/net-tools-2.0-0.22.20131004git.el7.x86_64.rpm
fi
#install pciutils
rpm -qa | grep -i pciutils
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed pciutils skip!"
else
  echo "install pciutils"
  yum install -y Install/rpm_files/pciutils-3.5.1-2.el7.x86_64.rpm
fi
#install epel-release
rpm -qa | grep -i epel-release
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed epel-release skip!"
else
  echo "install epel-release"
  yum install -y Install/rpm_files/epel-release-7-11.noarch.rpm
fi
#install python2-pip
rpm -qa | grep -i python2-pip
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed python2-pip skip!"
else
  echo "install python2-pip"
  yum install -y Install/rpm_files/python2-pip-8.1.2-5.el7.noarch.rpm
fi
#install pyserial
pip install pyserial-3.3-py2.py3-none-any.whl
#install zip/unzip
rpm -qa | grep -i unzip
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed zip/unzip skip!"
else
  echo "install unzip/zip"
  yum install -y Install/rpm_files/unzip-6.0-16.el7.x86_64.rpm Install/rpm_files/zip-3.0-11.el7.x86_64.rpm
fi
#install telnet
rpm -qa | grep -i telnet
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed telnet skip!"
else
  echo "install telnet"
  yum install -y Install/rpm_files/telnet-0.17-64.el7.x86_64.rpm
fi
#install OpenIPMI
rpm -qa | grep -i OpenIPMI
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed OpenIPMI skip!"
else
  echo "install OpenIPMI"
  yum install -y Install/rpm_files/OpenIPMI-modalias-2.0.19-15.el7.x86_64.rpm
fi
#install ipmitool
rpm -qa | grep -i ipmitool
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed ipmitool skip!"
else
  echo "install ipmitool"
  yum install -y Install/rpm_files/ipmitool-1.8.15-7.el7.x86_64.rpm 
fi
#install gcc-c++
rpm -qa | grep -i gcc-c++
if [ "$?" == 0 ] ;then
  echo ">>The system has been installed gcc-c++ skip!"
else
  echo "install gcc-c++"
  yum install -y Install/rpm_files/gcc-4.8.5-16.el7.x86_64.rpm
  yum install -y Install/rpm_files/gcc-c++-4.8.5-16.el7.x86_64.rpm
fi
#install smartmontools
rm -rf smartmontools-6.5
tar xf smartmontools-6.5.tar.gz
cd smartmontools-6.5/
./configure --with-nvme-devicescan
make
make install
cd ..
#instll the sg_utils
rm -rf sg3_utils-1.42
tar xf sg3_utils-1.42.tgz
cd sg3_utils-1.42/
./configure
make
make install
cd ..
#instll the mcelog
rm -rf mcelog-153
tar xf mcelog-153.tar.gz
cd mcelog-153/
make
make install
cd ..
#copy files
cp bash_profile ~/.bash_profile
cp bashrc ~/.bashrc
#create folder for UTS
mkdir -p /root/sw_to_install
mkdir -p /uts_tools
# change grub.cfg, to make the ethernet index from eth0
#sed -i "s/quiet/quiet net.ifnames=0/g" /etc/default/grub
#grub2-mkconfig -o /boot/efi/EFI/centos/grub.cfg
#grub2-mkconfig -o /boot/grub2/grub.cfg
#disable some service
chkconfig acpi on
chkconfig ModemManager off
chkconfig NetworkManager off
chkconfig firewalld off
chkconfig abrtd off
