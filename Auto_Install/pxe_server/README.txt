1. build tftp server
    1.1 install tftp server application
           yum(apt-get/zypper) install tftp tftpd-hpa xinetd   
    1.2 config, copy file 'tftp' to '/etc/xinetd.d/' and modify the tftp root directory in 'tftp' file
    1.3 change the attribute of the tftp root directory 
           chmod -R 777 /tftpboot
           chown -R nobody /tftpboot
    1.4 restart tftp service
           /etc/init.d/xinetd restart
    1.5 Enable the app when OS reboot
           chkconfig xinetd on
    1.6 enable firewall
           iptables -I INPUT -p udp --dport 69 -j ACCEPT
    1.7 Copy the following files to tftp boot directory. Note: the 'pxelinux.cfg' should be created
           pxelinux.0 menu.c32 hdt.c32 memdisk memtest pxelinux.cfg/default vmlinuz initrd.img 
  
2. build dhcp server
    1.1 install dhcp server application
           yum install dhcp -y
    1.2 modify the file '/etc/dhcpd.conf' like the directory 'dhcpd.conf'
    1.3 restart dhcp service
           service dhcpd restart
    1.4 Enable the app when OS reboot
           chkconfig dhcpd on
