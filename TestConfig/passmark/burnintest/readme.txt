PassMark (TM) Software's BurnInTest for Linux
Copyright (C) 2013 PassMark Software
All Rights Reserved
http://www.passmark.com

Overview
========
Passmark's BurnInTest for Linux is a software tool that allows all
the major sub-systems of a computer to be simultaneously
tested for reliability and stability.
<For more details see PDF format help file>


Status
======
This is a shareware program.
This means that you need to buy it if you would like
to continue using it after the evaluation period.


What's in the "burnintest" folder?
====================================
1.	BITErrorClassification.txt (see documentation how to customize your errors).
2. 	help folder (html based help)
3.	32bit folder containing 
		bit_gui_x32 (BurnInTest Linux GUI 32 bit version, double-click to launch app).
		bit_cmd_line_x32 (BurnInTest Linux command line 32 bit version).
		cmdline_config.txt (Text based config file for command line version)
		savedkey.dat (to get you started with the unregistered shareware version)
4.	64bit folder containing 
		bit_gui_x64 (BurnInTest Linux GUI 64 bit version, double-click to launch app).
		bit_cmd_line_x64 (BurnInTest Linux command line 64 bit version).
		cmdline_config.txt (Text based config file for command line version)
		savedkey.dat (to get you started with the unregistered shareware version)
5.	BurnInTest_Linux_CLI_EULA.txt
6.	readme.txt
7. 	burnintest.sh (a script to check for 32/64 bit libraries and launch BurnInTest)


Installation
============
1.	Uninstall any previous version of BurnInTest Linux by
	deleting it's folder.
2.	Copy the new "burnintest" folder to your desired location
	or copy the contents of the new "burnintest" folder
	to your desired folder
	(I shall call this the destination_folder throughout this documentation).
3.	Make sure you have read write permission for the destination_folder.
	This can be done with a CTL-I when you select the destination_folder's icon
	and changing the permission to read/write for owner, group and others.
	This can also be done via the command line with
	"chmod 774 destination_folder". 
	You can only do this if you are the owner of the destination_folder
	or if you logged in as root user.
	(To change ownership of files/folders, use
	"chown user_name:user_group file_name".
	Type "man chmod" or "man chown" if you need assistance.)
4.	Also make sure you have read/write permission for the "savedkey.dat"
	file and "LastUsed.cfg" file by following step (3).

UnInstallation
==============
Delete the folder that it was previously installed in or delete
the contents of the folder.


How to launch application
==========================
1.	Application can be launched by double-clicking on the "burnintest.sh" icon, or 
	entering the 32 bit or 64 bit directory and choosing a specific instance of
	BurnInTest to run.

2.	To run application via the command line, from your terminal:
	i)	Change the current working directory to the destination_folder by
		typing "cd path_to_destination_folder"  (There is an easy way to copy
		path by dragging the destination_folder's icon into the terminal).
	ii)	To be sure you have changed your working directory to destination_folder,
		issue a "pwd" command on the command line.  This will print the path
		of the working directory.  In this case, "path_to_destination_folder"
		should be the output.
	iii)	Run the launch script by typing "./burnintest.sh" which will determine 
		if you are using 32 or 64 bit linux, if the required libraries are 
		available and launch BurnInTest	
3.	To choose which versions of BurnInTest to run (32/64 bit, GUI/command line)	
	i)	Change the current working directory to the destination_folder by
		typing "cd path_to_destination_folder"  (There is an easy way to copy
		path by dragging the destination_folder's icon into the terminal).
	ii)	To be sure you have changed your working directory to destination_folder,
		issue a "pwd" command on the command line.  This will print the path
		of the working directory.  In this case, "path_to_destination_folder"
		should be the output.	
	iii)	Change the working directory to the 32bit or 64bit directory 
	iv)	Launch the application by typing "./bit_gui_x32" for 32 bit GUI version,
		"./bit_cmd_line_x32" for 32 bit command line version,
		"./bit_gui_x64" for 64 bit GUI version,
		"./bit_cmd_line_x64" for 64 bit command line version
	

Hardware Requirements
======================
-	Intel and AMD compatible CPU.
-	Recommended 256MB of memory.
-	10MB Disk space (more is required to run the disk test).
-	Optional serial and parallel loop back plugs for port testing.
-	A network connection for network testing.
-	A CD ROM + 1 Music CD or Data CD to run the CD test.
-	Optional specialized PassMark test CD/DVDs to run PassMark's CD/DVD test.
-	Optional PassMark USB2 test plugs for usb test


Software Requirements:  	
======================
- Linux kernel 2.6.9 or higher.
- KDE 3.5 and higher
- Qt 4.6 and higher
- Open GL 1.2 and higher (for 3D graphics test plus working Open GL drivers
  for your video card).
- libusb 1.0
- Administrator privilleges are required for certain tests.



Linux distributions that meet these requirement (GUI version):  	
=========================================================
So far, the following distributions have been tested (or reported) that
met these requirements:

Fedora Core 11 (with Qt 4.6.2 installed)
OpenSUSE KDE LiveCD (RC2)
Kubuntu 10.04

The command line version requires far less libraries and should work on most distributions.


For a more comprehensive list, please refer to:
http://www.passmark.com/support/bitlinux_faq.htm#software_requirement

To aid us in making the software better for you, please e-mail to
help@passmark.com if you have tested successfully in another Linux distribution
of if you encountered issues with running BurnInTest for Linux
on your system.


Version History
===============
Here is a summary of changes that have been made in each version of BurnInTest Linux:

Version					Date			Author
--------------------------------------------------------------------------------
Comments (latest top, oldest bottom)

BurnInTest v3.1 (1002) Linux		28 October 2013		Timr	
--------------------------------------------------------------------------------
 - Made some changes to the USB test so on some systems that don't have 
   "/proc/bus/usb" information the test will now start correctly
 - Made some changes to the USB3 test start process, on some systems the USB3 
   plugs are slow to re-enumerate after BurnInTest configures them and could cause
   a connection error while the test was starting, this was more apparent when running on a 
   live system (eg USB boot)
 - Fixed a bug in the GUI versions where scripts were not being launched correctly
   from the menu item after BurnInTest was running (scripts launched from the 
   command line were unaffected)
 - Fixed a bug where a very large number of available network ports could cause a crash
 - Added a new error message and fixed a crash when libusb fails to start, BurnInTest
   will now run but the USB tests will be disabled if libusb is unable to be accessed
 - Added a -B command line flag so the command line version can be run in the
   background (eg using &), this means all user input is turned off so if no 
   start/finish time is set BurnInTest will run indefinitely


BurnInTest v3.1 (1001) Linux		5 August 2013		Timr	
--------------------------------------------------------------------------------
 - Added benchmark mode to USB2 test as part of each cycle as well as a new 
   options to enable/disable the benchmark component of the test
 - Can now edit the "ttyS" edit field in the serial port setting in the GUI 
   versions to add differently named serial ports eg ttyUSB
 - Added sound loopback test
 - Made some changes to how parallel ports are detected and selected for testing
   will now scan the /proc/sys/dev/parport directory for available parallel ports
 - Fixed a bug that was preventing BurnIntest from getting the IPs of available 
   NICs  caused by changes in the way ifconfig displays NIC information (Fedora 18)
 - Fixed an issue where running the memory test in the 32bit build of BurnInTest
   when run in conjuction with other tests could fail with an 
   "Error allocating RAM" error.

BurnInTest v3.1 (1000) Linux		6 February 2013		Timr	
--------------------------------------------------------------------------------
 - Added USB3 loopback plug support 
 - Updated the USB library BurnInTest uses from libusb0.1 to libusb1
 - Changed behaviour so if the number of cpus/cores cannot be determined a warning
   will be logged and 1 CPU test thread will started by default
 - Fixed a crash on startup in the GUI version if "Error by category" under the
   "View" menu was enabled 
 - Fixed a bug in the network settings where the address for 4 & 5 were linked 
   to the wrong checkbox
 - Fixed a bug where raw hard disks were not being correctly counted and would not
   be displayed for selection in the test preferences or start the test as expected

BurnInTest v3.0 (1007) Linux		7 November 2012		Timr	
--------------------------------------------------------------------------------
 - Fixed a bug where the command line version could crash when a USB drive was 
   mounted at start up
 - Fixed a bug where using a long logging file path in the command line 
   configuration file could cause the BurnInTest command line version to stop working
 - Fixed a bug preventing the CD and serial tests from starting correctly
 - Added some extra information to trace level 1 logging when closing a serial 
   port fails

BurnInTest v3.0 (1006) Linux		17 September 2012		Timr	
--------------------------------------------------------------------------------
 - Added keywords so a memory test pattern can be specified in the command line
   configuration
 - Increased the amount of disk tests that can be run to 120
 - Added ability to test network drives (CIFS, NFS, SMBFS) 
 - Changed command line version to check for mount point or device when 
   specifying a disk test in the command line config file
 - Added %DATE% and %SYSTEMSERIAL% flags for use in creating log names and paths
 - Added "Test all raw disks" to disk test preferences and a new keyword for 
   the disk test section of the command line configuration
 - Added test pattern and file size settings for use with "Test all" options
 - Changed behaviour of BurnInTest when the configuration file can't be saved,
   instead of warning and exiting only the warning is displayed and BurnInTest 
   will continue to run
 - Fixed a bug where the filesize for the hard disk test could not be set below
   1% in the command line version
 - Fixed a bug where the number of CPUs in the system information could 
   be incorrect
 - Fixed a bug where the 32bit version of BurnInTest could try and allocate more
   RAM than 32buit process can access if there was more than 4GB of RAM on 
   the system
 - Fixed a bug in the command line version where if a hard disk was not mounted 
   the error was displayed in the user interface but not logged correctly
 - Fixed a crash when the disk test and text format logging is enabled and there 
   are no raw disks detected on the system
 - Fixed a bug where the incorrect disk name could be printed in the log file 
   when using text format logging
 - Fixed a bug where the memory pattern could be reset to cyclic each time 
   BurnInTest was started

BurnInTest v3.0 (1005) Linux		10  May 2012		Timr	
--------------------------------------------------------------------------------
 - Fixed a bug in memory information display where motherboards with multiple 
   banks of memory where being incorrectly parsed
 - Fixed a bug where error messages were not always displayed correctly in the 
   command line version 
 - Clarified USB test error to indicate root permissions are needed to run the  
   test
 - Changed how USB test threads are allocated a USB plug to test to avoid timing
   issues when the tests start
 - Changed how the available USB plugs are detected to fix a bug where some Linux
   systems no longer support usbdevfs (eg Fedora 16)


BurnInTest v3.0 (1004) Linux		15  March 2012		Timr	
--------------------------------------------------------------------------------
 - Fixed bug in the command line text configuration, the CPU test sections were 
   not being disabled when commented out
 - Fixed bug in command line config where more than 40 disk entries could cause 
   a crash
 - Fixed a bug in the disk test where when running multiple disk tests BurnInTest
   could occasionally fail to retrieve the available free space and report that 
   the drive was not mounted. 
 - Fixed a bug in the RAW disk test, random seeking pattern, (32 bit only) where
   a seek error could be reported incorrectly 
 - Fixed a bug in the 32bit versions where memory information was being reported
   incorrectly on system with more than 4GB of RAM

BurnInTest v3.0 (1003) Linux		5  October 2011		Timr	
--------------------------------------------------------------------------------
 - Changed how available disks are detected and displayed in the test preferences
   in order to display large numbers of available disks
 - Changed how disk test preferences are stored 
 - Fixed a bug in the command line version where the correct number of CPU tests
   were not started in some cases
 - Fixed a bug with the network test where in some situations a checksum error 
   could be logged even though no error occured.
 
BurnInTest v3.0 (1002) Linux		9  September 2011		Timr	
--------------------------------------------------------------------------------
- Fixed a bug with the scripting where when launching a script from the command
  line sometimes the script would launch the tests twice at the same time
- Changed the behaviour of the serial port test to prevent situations
  where the test could freeze rather than throw an error (only when using
  custom test plugs)
- Fixed a bug in the parallel test where if the port address was not set to a 
  default value the sent/received count would not be displayed correctly
- Some changes to the serial port test were made to match the windows behaviour, 
  if an error is encountered the test will now continue after closing and 
  re-opening the serial connection
- Some timeout changes were made in the serial test to prevent the test pausing
  rather then timing out in some cases
- Fixed a bug where the test configuration window could crash if there were more
  than 40 hard disks / paritions detected on the system
- Fixed a bug where multiple "Device" keywords could be added to the same 
  "<Test>" module of the disk test section of the command line configuration. 
  This would cause the disk test to start with incorrect parameters.
- Changed how the disk test files were deleted to improve the speed of deletions
  when cleaning up old test files

BurnInTest v3.0 (1001) Linux		10  June 2011		Timr	
--------------------------------------------------------------------------------
- When no system info is able to be retrieved a N/A is now displayed
- Removed incorrect warning message being shown before welcome dialog when 
  evaluation time has expired 
- Changed behaviour so disk test files will be created in the root directory
  '/' if startup disk is selected for testing 
- Fixed a bug in the command line version when using a non default serial port
- Fixed a bug in the command line version where raw disk tests could report 
  0 operations while the test was running
- Fixed a bug where the CPU test was not always creating the right amount of test
  threads
- Fixed a bug where an error message would sometimes not be displayed correctly
  if an invalid key was used
- Fixed a bug where some previously saved configuration options would not be
  loaded correctly next time configuration options were opened
- Removed some stderr output shown when running the gui version from a terminal


BurnInTest v3.0 (1000) Linux		17 August 2010		Timr	
--------------------------------------------------------------------------------
- New licence keys will be required for version 3 of BurnInTest Linux, please
  see http://www.passmark.com/products/bitlinux.htm to check if you qualify for
  a free upgrade
- Updated CPU tests to be more inline with current Windows version, including 
	general instructions, FPU, SSE, SSE2 and primes tests
- Updated user interface to use QT4 (4.6.2)
- Updated main window to included system information (where available), test 
  results and event log to allow easier access to these items
- Main window can now be resized
- Changed event log to color code information and error lines based on severity
- Added edit error classification function
- Changed some menu item names and location to be more consistent with the current
  Windows version
- Changed the optical CD/DVD/BD test so files should be minimally cached by the
  operating system during testing (previous versions resulted in much higher than
  expected read/verify speeds)
- Increased max limit for Memory test in 64bit version to 256GB and increased 
  the maximum amount locked for testing to 97% of free RAM
- Changed behaviour of -M (show machine ID and notes entry) command line parameter 
  when used with -R (auto-start tests) so the tests will not execute until the  
  machine ID and notes dialog is closed
- Added ext4 support for disk test 
- Added test certificate option to logging and HTML template file to the 
  download package 
- Added “Test all hard disk” option to test configuration options in GUI 
  version and new TestAllDisks option in command line config 
- Fixed a bug where the serial port test was not starting correctly in some 
  distributions of linux
- Fixed a bug in the USB test where a batch of recent USB2 test plugs were not
  correctly recognised by BurnInTest
- Fixed a bug in the CD "Data read and verify" test where the test could freeze
  during the checksum creation if it encountered a 0 length file
- Fixed a bug where when exiting from a script BurnInTest was not returning 
  the correct error/success code
- Changed how BiT detects the IP address for a network card to take into account
  aliased entries, eg when using an IPv6 and an IPv4 address with an aliased entry
  for the same network card, originally BiT would not pick up the IPv4 address
  from the alias


BurnInTest v2.0 (1006) Linux		10 July 2009 	Timr	
--------------------------------------------------------------------------------
 - Added NTFS to the list of recognised partition types for the disk test, please
   note that some Linux distribution might not support NTFS or writing to 
   NTFS so the test will not be able to run unless the Linux distribution
   support read/write for NTFS (for example those that use ntfs-3g)
 - Added -K command line option to keep disk test data files on disk when an
   error occurs (rather than delete them), best used with the "Stop on error"
   option
 - Added extra information to trace level 1 logging when a disk verification 
   error is detected
 - Removed disks from the disk test selection when using aufs/unionfs, so 
   BurnInTest won't select these virtual partitions for the disk test by default 
   in live environments
 - Fixed a bug where the CD/DVD test could generate a checksum error after the 
   test had finished when running the Data Checksum & Verify test and the test 
   finished halfway through check summing a file
 - Fixed a bug where the memory test could be run in the wrong mode and not generate
   any operations during the test, due to a corrupt config setting
 - Corrected some output for trace level 2 of the disk test where some information 
   was not being written out correctly

BurnInTest v2.0 (1005) Linux		3 Jun 2009 	Timr	
--------------------------------------------------------------------------------
 - Fixed a bug where running the CPU test on a machine with more than 16 CPUs
 	 could result in corruption of the results 
 - Fixed a bug where a corrupt config file could cause odd test behaviour, for 
   example an increasing cycle count but no increase in results or errors.
   BurnInTest was converting older versions of config files but not flagging them 
   as new, causing them to be converted again next run and therfore corrupting it. 
 
BurnInTest v2.0 (1004) Linux		24th Apr 2009 	TimR
--------------------------------------------------------------------------------
 - Removed the 2GB file limit for the disk test on 64bit versions
 - Fixed a bug where multiples warnings about having a floppy disk in the drive 
   could be displayed when testing a floppy drive and multiple disk partitions
 - Fixed a bug where opening the test preferences window and starting the tests 
   could add the USB test to the log file even if it wasn't selected to run in 
   the duty cycle / test selection options.
 - Removed CD drives from being listed in the disk test preferences
 - Increased number of disk tests that can be run from 20 to 40
 - Lowered minimum duty cycle for network test, when set to 1 will send 
   ~1 packet / second
 - Added -M command line option to display Machine ID and Notes dialog when 
   BurnInTest is started (GUI version only)
 - Added scrolling in command line version, use up arrow and down arrow 
   to scroll through the displayed test results in some display areas

BurnInTest v2.0 (1003) Linux		27th Feb 2009 		TimR
--------------------------------------------------------------------------------
 - Fixed a bug where some keys did not register correctly in the 64bit build
 
BurnInTest v2.0 (1002) Linux		11th Feb 2009 		TimR
--------------------------------------------------------------------------------

 - Added vmhgfs to the list of partitions types BurnInTest will recognise and
   display in the Disk tab
 - Fixed a bug where the Pre-Test option to hide/display the warning dialog
   had the opposite values
 - Fixed a bug where CD's mounted at certain points might not be recognised as
 	 a CD drive and not appear in the CD-RW/DVD tab
 - Fixed a bug in the memory test where the cycles count was incresed after
   the test was flagged to finish, making the final cycle count 1 higher than
   expected
 - Fixed a bug in the memory test where the One's pattern could sometimes be
   skipped when cycling through all test patterns
 - Fixed a bug in the command line version where the serial test could display
   the wrong operations count on the summary screen if there was a disk test
   running at the same time
 - Fixed a bug with the logging where RAW disk tests could log 0 operations
   in the command line version 
 - Fixed a bug with matching network cards to their IP if each network card
   isn't connected or doesn't have a current IP 
 - Fixed a bug where BurnInTest could exit if the disk test tried to create a 
   test file bigger than 2GB.

BurnInTest v2.0 (1001) Linux		 10th Dec 2008 TimR
--------------------------------------------------------------------------------
 - Fixed a bug in the random seeking disk test where the same block could be read/written 
   several times in a row instead of another random block
 - Fixed a bug in the random seeking disk test where a read verify error could occur, 
   more likely to happen in small partitions (<50mb) 
 - Fixed a bug with the scripting where multiple instances of the same test could 
   be launched 
 - Fixed a bug with the scripting where a segfault could occur when using logging 
 - Fixed a bug with key entry where extra spaces before/after user name were not 
   being ignored and causing some users name / key pairs to fail validation
 - Fixed a bug where BurnInTest would not launch on SUSE11
 - Removed some warning and message dialogs from the GUI version when running a script 

BurnInTest v2.0 (1000) Linux		 19th Nov 2008 TimR
--------------------------------------------------------------------------------

Converted help file to browser based html format
Added support for reiserfs and XFS in disk test (previously these were being ignored) and ext4
Added -F font size command line parameter
Added -D duration (minutes) command line parameter
Added -X duration (cycles) command line parameter
Added -S script command line paramter
Added -p command line parameter to command line version, allows update interval to be set
Added -d command line parameter, sets debug mode and creates debug.log file
Added command line parameters to command line version to match
Added USB2 loopback test for use with Passmark USB plugs

Removed the default behaviour of BurnInTest to create a debug log and print debug
information which reduces load times, on some systems this was the cause of a 
long pause when starting BurnInTest. Debug mode can be entered by using the -d command
line parameter.

Added scripting 
 - In command line version use command line flag
 - GUI version new menu item under Test menu

Memory Test
 - Improved memory test execution speed significantly
 - Added option for memory test to select test pattern

Disk Test:
 - Added ability to test hard disks that are un-partitioned (Raw hard disk test)
 - Changed disk test window design, added total drive capacity
 - Changed references of MBytes to MB
 - Added ability to display GB instead of MB when a drive is greater than 1 GB
 - Tweaked hard disk duty cycle effect so effect is more linear, decreasing by a small amount 
   from 100 will no longer result in a drastic cut to the speed of the test

Network Test:
 - Increases number of test IP slots to 6
 - Added option "Test All NICs" to bind each network card to an entered IP
 - Tweaked network duty cycle effect so effect is more linear, decreasing by a small amount 
   from 100 will no longer result in a drastic cut to the speed of the test
 - Changed MB sent/received to packets to give a clearer picture of how many packets are being
   sent/received
 - Changed flow rate MB/S to packets/s
 - Network test name will now include which eth device is being tested

Bug Fixes
 - Fixed a bug where tests could not automatically stop after a certain set amount of cycles
   when running the CPU test on multi core cpus
 - Fixed a bug with network test errors not displaying correctly
 - Fixed a bug with the 2D graphics test where the total operations count was incorrect and 
   being inflated each cycle resulting in a higher operations count than there actually were
 - Fixed a bug with command line version of disk test when testing multiple devices if the 
   underlying device block size differed the available and total space counts could be 
   calculated wrong and could lead to the disk test causing a "Device Full" error rather 
   than detecting when the device was running out of space and cleaning up files


BurnInTest v1.0 (1007) Linux		04th Oct 2006		sk
--------------------------------------------------------------------------------

1.	Hang reported when running 2D Graphics test, resulting in 2D Graphics thread and
	main thread hanging.  All windows will not being updated (grayed out) and remaining
	threads continue to run and needs to be killed.  This version should fix this issue.

2.	Fixed bug where number of CPU is not reported right.

3.	Limit maximum file size of Disk test to 2GB.

4.	Fixed a bug in Memory test whereby if your attempted test buffer size is less than 128MB,
	memory test does not run.

5.	If RTS/CTS is disabled, hardware flow control will not be turned on in Serial Port testing.
	
BurnInTest v1.0 (1006) Linux		05th July 2006		sk
--------------------------------------------------------------------------------
1.	Removed paintEvent function from 2DGraphicsTest.  Function is not in used but is being called
	everytime the widget needs to paint itself.

2.	Removed a while loop in bitmainapp.cpp, whereby it is calling Sleep and processEvent for 1 sec
	once memory test thread is created.

3.	We now compute parameter for OpenGL redraw outside of the paintGL function.  Previously,
	if user were to drag a window over the Open GL widget (window), you will see a "speed-up"
	effect whereby the spheres will be moving faster.  This is now no longer the case.

4.	Commented InitSignalHandling() from InitEnv_Main().

5.	We show() newly created child test window before we create the thread for the test
	(Before, we show() after the thread creation).
			
6.	Re-implemented main thread's paintEvent().  Previously, it is checking to see which thread is
	suppose to run and then updating each test window.  This is a bug because suppose only 1 thread
	has been created so far (and 5 threads are suppose to run), and system wants to update the
	main window, it will attempt to update a 5 child windows even though only the 1st window has
	been created.  Individual child window is now being updated outside the paintEvent function.
				

BurnInTest v1.0 (1005) Linux		26th Apr 2006		sk
--------------------------------------------------------------------------------
1.	Corrected bug whereby the 2D Graphics Test is updating its windows (window->update())
	from the main GUI thread!
2.	Added optional argument for -R option.
	-R:	optional argument
		Auto-start after delay_msecs.  Minimum (and default) is 3000, i.e. 3 secs.
		If you specify anything less than 3000 msecs, it will default to 3000 msecs.
		
Example:		
	./burnintest -R 10000
		Auto-start after 10 secs
	./burnintest -R
		Auto-start after 3 secs (default)			
	

BurnInTest v1.0 (1004) Linux		03rd Mar 2006		sk
--------------------------------------------------------------------------------
1.	Changed behaviour of how burnintest reports devices.  Before, it attempts to
	parse the mount point and the mount name to try and extract the last token after "/".
	Example, if it is mounted as "/dev/fd0" at "/media/floppy", burnintest reports it
	as Media floppy [fd0].  It now reports the full path, i.e. Media (/media/floppy) [/dev/fd0].
	There is no gurantee that the monunt point or mount name has a "/" in its path.
	
2.	Added "-R" (or "--autostart") and "-C" (or "--config") command line option.
	-R:	(no argument)
		Auto start without needing to press "Start Test".
	-C:	(argument needed)
		Determines which config file to use.

Example:
	burnintest -R -C testall.cfg
	burnintest --autostart --config=testall.cfg

3.	Removed "-d" (or "--debugmode") option.  "debug.log" is always created in executable's
	directory for debugging purposes.  If there is no write permission in executable's
	directory, an error prompt will be displayed (instead of segfault).		
	

BurnInTest v1.0 (1003) Linux		09th Feb 2006		sk
--------------------------------------------------------------------------------
1.	Changed default settings for Serial Test.  Default speed is now 9600baud
	and default timeout is 3500 ms.
2.	Changed default settings for Network Test.  Default error mode is now by ratio.	
3.	Standardized data type used for RAM.
4.	Added glFlush in OpenGL test to force execution of OpenGL commands in finite time.
5.	Fixed Pre-Test warning that prompts for Serial Loopback Plugs to be attached to
	test unit even though it is a "Detect Only" test.
6.	Added texture to 3D Graphics' Spheres.
7.	Adjusted material properties and lighting to enhance shadows on spheres for
	3D Graphics Test.
8.	Changed step size for displacement and rotation so spheres move faster in OpenGL Test.
9.	Light source is now rotated to enhance effects.
10.	Fixed bug in Preferences: CD-RW/DVD whereby even if a CD/DVD drive is not tested,
	it will appear in the main window (not suppose to).
11.	Put in extra trace logging for memory test.
12.	Put in extra debug logging for memory reporting and system resource limits during startup.
13.	Memory test now probes available physical RAM as well as available high RAM.

BurnInTest v1.0 (1002) Linux
--------------------------------------------------------------------------------
1.	Released BurnInTest for Linux Version 1.0 (build 1002)
2.	Removes excessive debug messages.

BurnInTest v1.0b2 (1001) Linux
--------------------------------------------------------------------------------
1.	Included collect application to help collect debug log for start-up errors.
2.	Fixed bug in Disk Test where files are not deleted properly after test finished.
3.	#include <X11/Xthreads.h> instead of <pthread.h>
4.	Added "Thank you" dialog once user enter correct username/key.
5.	Fixed negative cycle number for serial detect test.
6.	Fixed floppies failing because of limited number of files at root directory of floppy.
7.	Added build date/time in -v option
8.	Added Linux Distribution name in system header log...whatever appear in your login screen will be here.
9.	Fixed bug whereby accumulate log and machine id files were saved in current working directory,
	which may or may not be the application's directory.
10.	Fixed bug where in SUSE 10.0, "Clear all results" only clear if "No" was clicked.
11.	Synchronized icons with Performance Test as much as possible.

BurnInTest v1.0b1 (1000) Linux
--------------------------------------------------------------------------------
1.	Included "LastUsed.cfg" configuration file that will load the default preferences.
	Note that previous configuration files are not compatible with this version.
	BurnInTest Linux's config file have header "BITCFGL" to check for incompatibility
	between Windows and Linux version.
2.	As this is a beta version, debug mode is used by default when you launch the
	application by double-clicking or when running in terminal with no arguments.
	A file "debug.log" will be created in the destination_folder
	Again, please make sure you have read/write permission for the destination folder.
3.	Clean up reporting of hard-disks and cd/floppy drives with tested systems.
	If your system is not reporting it's peripherals right (or if you think it is not reporting
	right), please e-mail to help@passmark.com.
4.	Added Pre-Test preferences that enable you to disable "Warning" dialog everytime
	we start a test.
5.	When viewing log from "View Event Log" menu, new log entries will be updated.
6.	Added "Save Test Log" option to save as text file or html file.
7.	Updated "BITErrorClassification.txt", synchronized with Windows version, corrected typo,
	updated to user-oriented error messages.
8.	Fixed bug in CDROM error message reporting.
9.	Updated costs of software in Welcome Window to US$49.  "Order Online Now" redirects
	to PassMark's sales site.
10.	Corrected bug where user enters 0.x value for Auto-Stop time and it becomes 0.
11.	Disk Test's "Speed" value is now updated.
12.	Added boundary values checking for preferences when user clicks "OK".
13.	Updated auto-scrolling of log viewing when new entry is added.
14.	Load/Save config cleaned up.
15.	Auto-adjust column width for last error string in main test window.
16.	Machine ID, serial and notes now truncates to fixed crashes of long string.
17.	Fixed truncation of "HTML" in Preferences:Logging.
18.	Synchronized system info reporting between HTML and ASCII log (as well as correct reporting
	in HTML format for video info).
19.	"debug.log" dumps packages information for system including kde versions, gcc versions and qt versions.
	It also dumps various crticial files and command line tools that system info is collected.
	Files:
	a)	/etc/fstab: cdroms, floppies and potential mount points for file-systems
	b)	/etc/mtab: mounted medias and file-systems
	c)	/etc/x11/xorg.conf: video card info
	d)	/proc/cpuinfo: cpu speed, cache size, etc
	Tools:
	e)	xdpyinfo: display info
	f)	glxinfo: openGL capabilities
	g)	printenv: collecting environment variables to understand various unix platforms
	h)	uname -a: host and system build info
20.	Fixed bug where 2 CDROMs does not quite set their preferences right from "Test Preferences:CDROM".
21.	Removed unneccessary blank lines in the logs.
22.	Fixed bug where load/save config files are not behaving quite as planned.
23.	Added -v option to display BurnInTest for Linux's version.

Release BIT_Linux_v0.9b2
--------------------------------------------------------------------------------
1.	Updated key.dat file to fix installation time issue.
	Installation time will now be the first launch of the app.
2.	Included debug option.  To enable debug mode, launch application with:
	# ./BIT_Linux --debugmode
	(that is, on the command line, type in ./BIT_Linux --debugmode)
	A file called "debug.log" will be output to collect any start-up errors.

Release BIT_Linux_v0.9b1
--------------------------------------------------------------------------------
1.	Released for initial testing.
2.	Tests include:
	- Memory
	- Disks
	- Network
	- 2D Graphics
	- 3D Graphics (Open GL)
	- Serial Port
	- Parallel Port
	- CD-ROM/DVD
	- CPU-Maths


Documentation
=============
All the documentation is included in HTML format in the help directory in the
32bit and 64bit folders. It can be accessed from the help menu in the GUI version.


Support
=======
For technical support, questions, suggestions, please check the help file for 
our email address or visit our web page at http://www.passmark.com


FAQs
=======
Visit our web page at http://www.passmark.com/support/bitlinux_faq.htm
for the BurnInTest Linux FAQ page.


Ordering / Registration
=======================
All the details are in the help file documentation
or you can visit our sales information page
http://www.passmark.com/sales


Compatibility issues with the BurnInTest Linux
===========================================================
You need to have administrator privileges to run the following test:
1.	Serial Port Test:
	Linux character devices are usually root access only.
	For this test, we might be accessing /dev/ttyS0 - /dev/ttyS63 depending on your configuration.
2.	Parallel Port Test:
	Root access is required to access memory location for the parallel ports.
	(lp0 @ 0x378, p1 @ 0x278 or lp2 @ 0x3BC)
3.	Memory Test:
	As we are locking physical memory to prevent caching, root access is needed to call this function.
4.	Network Test:
	Root access is required to create raw sockets for the address family AF_INET.


Enjoy..
The PassMark Development team
