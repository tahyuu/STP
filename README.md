# STP
STP is a stand test platform for Server Test. it combine for CPU, RAM, BIOS, BMC,ETH, FIBER, SSD Test.
### Setup SFT/Burin Tester(software).
----
#### Clone the latest Program
Boot the system(you can use any PC including your laptop) from our USB boot OS(window to go). Enter system. Open a terminal and input below command to get the latest code.
```
cd
```
```
git clone git@192.168.4.2：~/cmcc_silk_road.git CMCC
```
```
yes
```
```
your_password
```
### Set the Environment and install the tools and package for sft/burnin tester.
----
In this step, you need connect to outside internet web so that we can get the tool and package from outside. Suggest to use flex visitor as below step
* Disconnect the Ethernet from our git server[192.168.4.2] otherwise this will impact our package and tools install. 
* Connect to internet.
* execute below command to install the tool and package and set environment
```
cd /root/CMCC/Auto_Install/
```

```
./sft_install
```
### How to Run Test
#### How to setup test unit for test(hardware)
* 1XUSB need to install into the Test Unit.
* 1XMouse need to insert into Test Unit.
* 1XKey board need to insert into Test Unit.
* 1XMonitor connect to Test Unit
* 1X “Windows to go” need to insert into Test Unit.
* Conncet to the Fibber Card two port with a Fibber Cable.
* Connect the BMC port, Two Ethernet Ports to our dhcp server
#### Run SFT tester
We have 4 Model. S1,s2,s3,s4, each of them have sft program and runin program. As below table</br>
Model|	SFT Program| 	Runin Program|How to run	</br>
   S1|	 s1_sft.sku|	 s1_runin.sku|	cmcc s1_xxx.sku</br>
   S2|	 s2_sft.sku|   s2_runin.sku|	cmcc s2_xxx.sku</br>
   S3|	 s3_sft.sku|   s3_runin.sku|	cmcc s3_xxx.sku</br>
   S4|	 s4_sft.sku|   s4_runin.sku|	cmcc s4_xxx.sku</br>
#### Where is the log
You can find the log in /root/FTLog/PASS or /root/FTLog/FAIL
#### PASS and FAIL
When the test pass, it will show pass interface, and also Fail will show fail interface.
