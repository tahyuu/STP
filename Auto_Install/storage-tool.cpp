//Version: 2.5, 2014-10-20 By QG Chong
//Compile with "g++ storage-tool.cpp -luuid -lpthread -lssl -o storage-tool-64"
//Dependencies: -
//  sg_scan
//  sg_map
//  sginfo
//  sg_readcap
//  sg_read
//  sg_dd
//  readlink
//  lspci
//  fdisk
//  smartctl
//  crc32

#ifdef __linux__
#       define _REENTRANT
#       define _POSIX_SOURCE
#endif

#ifdef __linux__
#       define _P __P
#endif

#include <iostream>
#include <sstream>
#include <iomanip>
#include <fstream>
#include <string>
#include <stddef.h>
#include <sys/types.h>
#include <dirent.h>
#include <vector>
#include <sys/stat.h>
#include <string.h>
#include <stdlib.h>
#include <algorithm>
#include <pthread.h>
#include <cstdlib>
#include <uuid/uuid.h>
#include <openssl/md5.h>
#include <unistd.h>

using namespace std;

enum WriteReadCompareActionEnum {
	CreateRandomFile, TransferInAndOutAndCompare, RemoveTemporaryFiles
};

struct DeviceInfo {
	bool enabled;
	int driveindex;
	string sg_device_file;
	bool sg_removeable;
	bool sg_command_queuing;
	string sg_host_number;
	string sg_bus_number;
	string sg_scsi_id_number;
	string sg_lun_number;
	string sg_scsi_type;
	string sg_size;
	string sg_size_long_string;
	string block_device_file;
	string sg_vendor_string;
	string sg_product_string;
	string sg_revision_string;
	string sg_serial_number_string;
	string pci_path;
	string pci_vendor_device_id;
	string usb_path;
	string scsi_path;
	string pci_description_string;
	pthread_t sg_writeread_thread;
	int create_thread_ret;
	int join_thread_ret;
	string sg_writeread_if_filename;
	string sg_writeread_if_filename_crc;
	string sg_writeread_of_filename;
	string sg_writeread_of_filename_crc;
	string sg_writeread_blocksize_string;
	string sg_writeread_blockcount_string;
	string sg_writeread_offset_string;
	string sg_writeread_bpt_string;
	int sg_writeread_blocksize;
	long sg_writeread_blockcount;
	long sg_writeread_offset;
	bool sg_writeread_nosync;
	string sg_writeread_stdout;
	string sg_writeread_stderr;
	enum WriteReadCompareActionEnum sg_writeread_action;
	bool ignore_nak;
	bool sg_writeread_result;
};

vector<DeviceInfo> Devices = vector<DeviceInfo> ();

struct SgMapInfo {
	bool success;
	string sg_device_file;
	string sg_host_number;
	string sg_bus_number;
	string sg_scsi_id_number;
	string sg_lun_number;
	string sg_scsi_type;
	string block_device_file;
};

struct DevDiskByPathInfo {
	string filename;
	string fullfilename;
	string pcipath;
	string usbpath;
	string scsipath;
	string block_device_file;
};

bool DiscoverDevices();
bool Parse_sg_scan_i_Line1(string line, string& sg_divice_file);
bool Parse_sg_scan_i_Line2(string line, bool& sg_removeable, bool& sg_command_queuing);
SgMapInfo Parse_sg_map_x(string line);
bool ParseLsPciVVNNDFirstLineInfo(string value, string& domain, string& bus, string& device, string& func, string& devicetype, string& devicedescription, string& vendorid, string& deviceid, string& revision);
int FindIndexOfVendorIDBracket(string value);
bool CheckPartitionExist(string blockfile, bool& partitionexist, string& cpstdout);
bool ShowDevicesInfo(vector<string>& vendors, vector<string>& products, vector<string>& revisions, vector<string>& sns, vector<string>& sizes, bool& smart);
bool DoSgReads(string count, string bpt, string speed, string retries);
bool DoSingleSgRead(DeviceInfo& device, string count, string bpt, string speed, double minspeed, bool isretry);
bool DoSgWriteReadCompare(string blocksize, string bpt, string blockcount, bool nosync, string dir, bool clear, bool ignore_nak, string blockoffset);
void *PrintDotEvertSecondThread(void *arg);
void *WriteReadThread(void *arg);
bool GetIntegerValue(string value, int& ret);
bool GetLongValue(string value, long& ret);
string GenerateRandomMd5();
string ComputeMD5(string str);
bool DoCommand(string commandstring);
bool RunProcessGetExitCode(string command, vector<string>& outlines, int& exitcode);
void Syntax();
void WriteConsole(string value);
void WriteConsoleLine(string value);
string GetExecutableDirectory();
//string& trim(string& s, const string& delimiters = " \f\n\r\t\v");
string& trim(string& s);
bool IsDirectoryExist(string pathname);
bool IsFileExist(string pathname);
bool GetFilesInDirectory(string pathname, vector<string>& filenames);
vector<string> SplitStringByDelimiter(string line, char delimiter);
bool FindStringInVector(string value, vector<string>& strings);
string ToString(int value);
string ToStringWithComma(int value);
bool IsMD5Filename(string filename);

string lspcitool = "lspci";
string workingdirectory;
ofstream logsw;
bool verbose = false;

pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

int main(int argc, char *argv[]) {
	if (argc == 1) {
		Syntax();
		return 1;
	}

	workingdirectory = GetExecutableDirectory();
	workingdirectory = workingdirectory.substr(0, workingdirectory.rfind("/") + 1);
	//cout << "working directory = " << workingdirectory << endl;

	vector < string > limit_pciid = vector<string> ();
	vector < string > limit_pcipath = vector<string> ();
	vector < string > limit_usbpath = vector<string> ();
	vector < string > limit_scsipath = vector<string> ();
	vector < string > limit_host = vector<string> ();
	vector < string > limit_bus = vector<string> ();
	vector < string > limit_scsi = vector<string> ();
	vector < string > limit_lun = vector<string> ();
	vector < string > limit_type = vector<string> ();
	vector < string > limit_drive = vector<string> ();

	string devicecount;
	string action;

	string param_count = "100k";
	string param_offset;
	string param_bpt;
	string param_speed;
	string param_retries = "2";
	bool param_nosync = false;

	vector < string > param_check_vendor = vector<string> ();
	vector < string > param_check_product = vector<string> ();
	vector < string > param_check_revision = vector<string> ();
	vector < string > param_check_serialnumber = vector<string> ();
	vector < string > param_check_size = vector<string> ();
	bool param_check_smart = false;

	string param_exec_string;

	string param_directory = "/tmp/";
	bool param_clear = false;
	bool param_force = false;
	bool param_ignore_nak = false;
	string logfilename;

	int i = 1;
	while (i < argc) {
		//-log
		if (string(argv[i]) == "-log") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			if (string(argv[i]).find("/") != string::npos)
				logfilename = string(argv[i]);
			else
				logfilename = workingdirectory + argv[i];
			//cout << "log filename = " << logfilename << endl;
		}
		//-pciid
		else if (string(argv[i]) == "-pciid") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			limit_pciid.push_back(string(argv[i]));
		}
		//-pcipath
		else if (string(argv[i]) == "-pcipath") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			limit_pcipath.push_back(string(argv[i]));
		}
		//-usbpath
		else if (string(argv[i]) == "-usbpath") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			limit_usbpath.push_back(string(argv[i]));
		}
		//-scsipath
		else if (string(argv[i]) == "-scsipath") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			limit_scsipath.push_back(string(argv[i]));
		}
		//-host
		else if (string(argv[i]) == "-host") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			limit_host.push_back(string(argv[i]));
		}
		//-bus
		else if (string(argv[i]) == "-bus") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			limit_bus.push_back(string(argv[i]));
		}
		//-scsi
		else if (string(argv[i]) == "-scsi") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			limit_scsi.push_back(string(argv[i]));
		}
		//-lun
		else if (string(argv[i]) == "-lun") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			limit_lun.push_back(string(argv[i]));
		}
		//-type
		else if (string(argv[i]) == "-type") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			limit_type.push_back(string(argv[i]));
		}
		//-drive
		else if (string(argv[i]) == "-drive") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			string tmpdrive = string(argv[i]);
			if (tmpdrive.find("-") != string::npos) {
				string s1 = tmpdrive.substr(0, tmpdrive.find("-"));
				string s2 = tmpdrive.substr(tmpdrive.find("-") + 1);
				int drivestart = atoi(s1.c_str());
				int driveend = atoi(s2.c_str());
				//cout << "drive start = " << drivestart << endl;
				//cout << "drive end = " << driveend << endl;
				for (int tmpi = drivestart; tmpi <= driveend; tmpi++) {
					ostringstream convert;
					convert << tmpi;
					limit_drive.push_back(convert.str());
					//cout << "drive = " << convert.str() << endl;
				}
			} else {
				limit_drive.push_back(tmpdrive);
			}
		}
		//-devicecount
		else if (string(argv[i]) == "-devicecount") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			devicecount = string(argv[i]);
		}
		//-action
		else if (string(argv[i]) == "-action") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			if (string(argv[i]) == "info")
				action = "info";
			else if (string(argv[i]) == "testspeed")
				action = "testspeed";
			else if (string(argv[i]) == "writeread")
				action = "writeread";
			else if (string(argv[i]) == "exec")
				action = "exec";
			else {
				Syntax();
				return 1;
			}
		}
		//-vendor
		else if (string(argv[i]) == "-vendor") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_check_vendor.push_back(string(argv[i]));
		}
		//-product
		else if (string(argv[i]) == "-product") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_check_product.push_back(string(argv[i]));
		}
		//-revision
		else if (string(argv[i]) == "-revision") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_check_revision.push_back(string(argv[i]));
		}
		//-sn
		else if (string(argv[i]) == "-sn") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_check_serialnumber.push_back(string(argv[i]));
		}
		//-size
		else if (string(argv[i]) == "-size") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_check_size.push_back(string(argv[i]));
		}
		//-smart
		else if (string(argv[i]) == "-smart") {
			param_check_smart = true;
		}
		//-count
		else if (string(argv[i]) == "-count") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_count = string(argv[i]);
		}
		//-offset
		else if (string(argv[i]) == "-offset") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_offset = string(argv[i]);
		}
		//-bpt
		else if (string(argv[i]) == "-bpt") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_bpt = string(argv[i]);
		}
		//-speed
		else if (string(argv[i]) == "-speed") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_speed = string(argv[i]);
		}
		//-retries
		else if (string(argv[i]) == "-retries") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_retries = string(argv[i]);
		}
		//-nosync
		else if (string(argv[i]) == "-nosync") {
			param_nosync = true;
		}
		//-command
		else if (string(argv[i]) == "-command") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_exec_string = string(argv[i]);
		}
		//-directory
		else if (string(argv[i]) == "-directory") {
			i += 1;
			if (i == argc) {
				Syntax();
				return 1;
			}
			param_directory = string(argv[i]);
			if (param_directory[param_directory.length() - 1] != '/')
				param_directory = param_directory + "/";
			//cout << "param_directory = " << param_directory << endl;
		}
		//-clear
		else if (string(argv[i]) == "-clear") {
			param_clear = true;
		}
		//-force
		else if (string(argv[i]) == "-force") {
			param_force = true;
		}
		//-ignorenak
		else if (string(argv[i]) == "-ignorenak") {
			param_ignore_nak = true;
		}
		//verbose
		else if (string(argv[i]) == "-v") {
			verbose = true;
		} else if (string(argv[i]) == "-?") {
			Syntax();
			return 1;
		} else {
			WriteConsoleLine("Error: Invalid argument " + string(argv[i]));
			return 1;
		}

		i += 1;
	}

	//Create log file stream
	if (logfilename.length() > 0)
		logsw.open(logfilename.c_str(), ios::out);

	//Show header
	WriteConsoleLine("Storage test tool");
	WriteConsoleLine("Version 2.5 Copyright Flextronics Penang");
	WriteConsoleLine("");

	//Discover devices
	if (DiscoverDevices() == false) {
		WriteConsoleLine("Error: Failed to discover devices");
		return 1;
	}

	//Apply limits
	if (limit_pciid.size() > 0) {
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(Devices[device_index].pci_vendor_device_id, limit_pciid) == false))
				Devices[device_index].enabled = false;
	}
	if (limit_pcipath.size() > 0) {
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(Devices[device_index].pci_path, limit_pcipath) == false))
				Devices[device_index].enabled = false;
	}
	if (limit_usbpath.size() > 0) {
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(Devices[device_index].usb_path, limit_usbpath) == false))
				Devices[device_index].enabled = false;
	}
	if (limit_scsipath.size() > 0) {
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(Devices[device_index].scsi_path, limit_scsipath) == false))
				Devices[device_index].enabled = false;
	}
	if (limit_host.size() > 0) {
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(Devices[device_index].sg_host_number, limit_host) == false))
				Devices[device_index].enabled = false;
	}
	if (limit_bus.size() > 0) {
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(Devices[device_index].sg_bus_number, limit_bus) == false))
				Devices[device_index].enabled = false;
	}
	if (limit_scsi.size() > 0) {
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(Devices[device_index].sg_scsi_id_number, limit_scsi) == false))
				Devices[device_index].enabled = false;
	}
	if (limit_lun.size() > 0) {
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(Devices[device_index].sg_lun_number, limit_lun) == false))
				Devices[device_index].enabled = false;
	}
	if (limit_type.size() > 0) {
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(Devices[device_index].sg_scsi_type, limit_type) == false))
				Devices[device_index].enabled = false;
	}
	if (limit_drive.size() > 0) {
		i = 0;
		for (int device_index = 0; device_index < Devices.size(); device_index++) {
			if (Devices[device_index].enabled == true) {
				Devices[device_index].driveindex = i;
				i += 1;
			}
		}
		for (int device_index = 0; device_index < Devices.size(); device_index++)
			if ((Devices[device_index].enabled == true) && (FindStringInVector(ToString(Devices[device_index].driveindex), limit_drive) == false))
				Devices[device_index].enabled = false;
	}
	if (action == "writeread") {
		for (int device_index = 0; device_index < Devices.size(); device_index++) {
			if ((Devices[device_index].enabled == true) && (param_force == false)) {
				bool partitionexist = false;
				string outstring;
				if (CheckPartitionExist(Devices[device_index].block_device_file, partitionexist, outstring) == false) {
					WriteConsoleLine("Error: Failed to check partition on " + Devices[device_index].sg_device_file + " on block device file " + Devices[device_index].block_device_file);
					if (outstring.length() > 0)
						WriteConsoleLine(outstring);
					return 1;
				} else if (partitionexist == true) {
					WriteConsoleLine("Info: Ignoring " + Devices[device_index].sg_device_file + " becuase partition exist");
					if (outstring.length() > 0)
						WriteConsoleLine(outstring);
					Devices[device_index].enabled = false;
				}
			}
		}
	}

	//Check device count

	int limiteddevicecount = 0;
	for (int device_index = 0; device_index < Devices.size(); device_index++)
		if (Devices[device_index].enabled == true)
			limiteddevicecount += 1;

	if (devicecount.length() == 0) {
		vector < string > nothing = vector<string> ();
		bool smart = false;
		ShowDevicesInfo(nothing, nothing, nothing, nothing, nothing, smart);
		WriteConsoleLine("Info: Total device count is " + ToString(limiteddevicecount));
		WriteConsoleLine("Error: No device count specified");
		return 1;
	}

	int devicecountint = atoi(devicecount.c_str());

	if (devicecountint != limiteddevicecount) {
		vector < string > nothing = vector<string> ();
		bool smart = false;
		ShowDevicesInfo(nothing, nothing, nothing, nothing, nothing, smart);
		WriteConsoleLine("Info: Total device count is " + ToString(limiteddevicecount));
		WriteConsoleLine("Error: Device count mismatch");
		//Try to analyze missing drives
		//Case where no specific devices are specified
		if ((devicecountint > limiteddevicecount) && (limit_usbpath.size() == 0) && (limit_scsipath.size() == 0) && (limit_scsi.size() == 0) && (limit_drive.size() == 0) && (limit_host.size() <= 1) && (limit_bus.size() <= 1) && (limit_lun.size() <= 1)) {
			for (i = 0; i < devicecountint; i++) {
				bool deviceindexfound = false;
				string deviceindexstring = ToString(i);
				for (int tmpindex = 0; tmpindex < Devices.size(); tmpindex++) {
					if (Devices[tmpindex].enabled == true) {
						if (deviceindexstring == Devices[tmpindex].sg_scsi_id_number)
							deviceindexfound = true;
					}
				}
				if (deviceindexfound == false) {
					WriteConsoleLine("Info: Possible reason: scsi id " + deviceindexstring + " missing");
				}
			}
		}
		//Case where scsi id are specified
		else if ((devicecountint > limiteddevicecount) && (limit_scsi.size() > 0) && (limit_usbpath.size() == 0) && (limit_scsipath.size() == 0) && (limit_drive.size() == 0) && (limit_host.size() <= 1) && (limit_bus.size() <= 1) && (limit_lun.size() <= 1)) {
			for (i = 0; i < limit_scsi.size(); i++) {
				bool deviceindexfound = false;
				string deviceindexstring = limit_scsi[i];
				for (int tmpindex = 0; tmpindex < Devices.size(); tmpindex++) {
					if (Devices[tmpindex].enabled == true) {
						if (deviceindexstring == Devices[tmpindex].sg_scsi_id_number)
							deviceindexfound = true;
					}
				}
				if (deviceindexfound == false) {
					WriteConsoleLine("Info: Possible reason: scsi id " + deviceindexstring + " missing");
				}
			}
		}
		//Case where scsi path are specified
		else if ((devicecountint > limiteddevicecount) && (limit_scsipath.size() > 0) && (limit_usbpath.size() == 0) && (limit_scsi.size() == 0) && (limit_drive.size() == 0) && (limit_host.size() <= 1) && (limit_bus.size() <= 1) && (limit_lun.size() <= 1)) {
			for (i = 0; i < limit_scsipath.size(); i++) {
				bool deviceindexfound = false;
				string devicescsipathstring = limit_scsipath[i];
				for (int tmpindex = 0; tmpindex < Devices.size(); tmpindex++) {
					if (Devices[tmpindex].enabled == true) {
						if (devicescsipathstring == Devices[tmpindex].scsi_path)
							deviceindexfound = true;
					}
				}
				if (deviceindexfound == false) {
					WriteConsoleLine("Info: Possible reason: scsi path " + devicescsipathstring + " missing");
				}
			}
		}
		//Case where usb path are specified
		else if ((devicecountint > limiteddevicecount) && (limit_usbpath.size() > 0) && (limit_scsipath.size() == 0) && (limit_scsi.size() == 0) && (limit_drive.size() == 0) && (limit_host.size() <= 1) && (limit_bus.size() <= 1) && (limit_lun.size() <= 1)) {
			for (i = 0; i < limit_usbpath.size(); i++) {
				bool deviceindexfound = false;
				string deviceusbpathstring = limit_usbpath[i];
				for (int tmpindex = 0; tmpindex < Devices.size(); tmpindex++) {
					if (Devices[tmpindex].enabled == true) {
						if (deviceusbpathstring == Devices[tmpindex].usb_path)
							deviceindexfound = true;
					}
				}
				if (deviceindexfound == false) {
					WriteConsoleLine("Info: Possible reason: usb path " + deviceusbpathstring + " missing");
				}
			}
		}

		return 1;
	}
	if (devicecountint == 0) {
		WriteConsoleLine("Error: Nothing to do");
		return 1;
	}

	if (action == "info") {
		bool ret = ShowDevicesInfo(param_check_vendor, param_check_product, param_check_revision, param_check_serialnumber, param_check_size, param_check_smart);
		//cout << "ret = " << ret << endl;
		if ((ret == true) && (devicecountint == limiteddevicecount)) {
			WriteConsoleLine("****************************");
			WriteConsoleLine("*** Device count matches ***");
			WriteConsoleLine("****************************");
			ret = true;
		} else {
			WriteConsoleLine("**************************************");
			WriteConsoleLine("*** Error: Device count mismatches ***");
			WriteConsoleLine("**************************************");
			ret = false;
		}
		if (ret == true)
			return 0;
		else
			return 1;
	} else if (action == "testspeed") {
		bool ret = DoSgReads(param_count, param_bpt, param_speed, param_retries);
		if (ret == true)
			return 0;
		else
			return 1;
	} else if (action == "writeread") {
		bool ret = DoSgWriteReadCompare("512", param_bpt, param_count, param_nosync, param_directory, param_clear, param_ignore_nak, param_offset);
		if (ret == true)
			return 0;
		else
			return 1;
	} else if (action == "exec") {
		if (param_exec_string.length() == 0) {
			WriteConsoleLine("Error: Nothing to do");
			return 1;
		}
		bool ret = DoCommand(param_exec_string);
		if (ret == true)
			return 0;
		else
			return 1;
	} else {
		WriteConsoleLine("!!! Unknown action " + action);
		return 1;
	}
}

bool DiscoverDevices() {
	//'Do sg_scan -i
	//Get sg_device_file, sg_removeable, sg_command_queuing
	vector < string > outlines = vector<string> ();

	struct timeval start, end;
	long mtime, seconds, useconds;
	gettimeofday(&start, NULL);

	int exitcode;
	if ((RunProcessGetExitCode("sg_scan -i", outlines, exitcode) == false) || (exitcode != 0)) {
		WriteConsoleLine("  Error: Failed sg_scan -i");
		return false;
	}

	gettimeofday(&end, NULL);
	seconds = end.tv_sec - start.tv_sec;
	useconds = end.tv_usec - start.tv_usec;
	mtime = ((seconds) * 1000 + useconds / 1000.0) + 0.5;
	if ((mtime > 3000) || (verbose)) {
		WriteConsoleLine("Info: It takes " + ToString(mtime) + " ms to complete sg_scan -i");
	}

	int i = 0;
	while (i < outlines.size()) {
		DeviceInfo newdevice;
		newdevice.enabled = true;
		//cout << outlines[i] << endl;
		if (Parse_sg_scan_i_Line1(outlines[i], newdevice.sg_device_file) == false) {
			i += 1;
			continue;
		}
		i += 1;
		if (i == outlines.size())
			return false;
		//cout << outlines[i] << endl;
		if (Parse_sg_scan_i_Line2(outlines[i], newdevice.sg_removeable, newdevice.sg_command_queuing) == false) {
			i += 1;
			continue;
		}
		//cout << newdevice.sg_device_file << endl;
		//cout << newdevice.sg_removeable << endl;
		//cout << newdevice.sg_command_queuing << endl;
		Devices.push_back(newdevice);
		i += 1;
	}

	//Do sg_map -x
	//Get sg_host_number, sg_bus_number, sg_scsi_id_number, sg_lun_number, sg_scsi_type, block_device_file (with readlink)
	
	gettimeofday(&start, NULL);
	
	if ((RunProcessGetExitCode("sg_map -x", outlines, exitcode) == false) || (exitcode != 0)) {
		WriteConsoleLine("  Error: Failed sg_map -x");
		return false;
	}
	
	gettimeofday(&end, NULL);
	seconds = end.tv_sec - start.tv_sec;
	useconds = end.tv_usec - start.tv_usec;
	mtime = ((seconds) * 1000 + useconds / 1000.0) + 0.5;
	if ((mtime > 3000) || (verbose)) {
		WriteConsoleLine("Info: It takes " + ToString(mtime) + " ms to complete sg_map -x");
	}
	
	i = 0;
	while (i < outlines.size()) {
		SgMapInfo sgmap = Parse_sg_map_x(outlines[i]);
		if (sgmap.success == true) {
			for (int device_index = 0; device_index < Devices.size(); device_index++) {
				if (Devices[device_index].sg_device_file == sgmap.sg_device_file) {
					Devices[device_index].sg_host_number = sgmap.sg_host_number;
					Devices[device_index].sg_bus_number = sgmap.sg_bus_number;
					Devices[device_index].sg_scsi_id_number = sgmap.sg_scsi_id_number;
					Devices[device_index].sg_lun_number = sgmap.sg_lun_number;
					Devices[device_index].sg_scsi_type = sgmap.sg_scsi_type;
					if (sgmap.block_device_file.length() > 0) {
						vector < string > tmpoutlines = vector<string> ();
						
						gettimeofday(&start, NULL);
						
						if ((RunProcessGetExitCode("readlink -f " + sgmap.block_device_file, tmpoutlines, exitcode) == true) && (exitcode == 0) && (tmpoutlines.size() > 0) && (tmpoutlines[0].find("/dev/") == 0)) {
							Devices[device_index].block_device_file = tmpoutlines[0];
						} else {
							Devices[device_index].block_device_file = sgmap.block_device_file;
						}
						
						gettimeofday(&end, NULL);
						seconds = end.tv_sec - start.tv_sec;
						useconds = end.tv_usec - start.tv_usec;
						mtime = ((seconds) * 1000 + useconds / 1000.0) + 0.5;
						if ((mtime > 3000) || (verbose)) {
							WriteConsoleLine("Info: It takes " + ToString(mtime) + " ms to complete " + "readlink -f " + sgmap.block_device_file);
						}
					}
					//cout << "device_index = " << device_index << endl;
					//cout << "sg_device_file = " << Devices[device_index].sg_device_file << endl;
					//cout << "sg_host_number = " << Devices[device_index].sg_host_number << endl;
					//cout << "sg_bus_number = " << Devices[device_index].sg_bus_number << endl;
					//cout << "sg_scsi_id_number = " << Devices[device_index].sg_scsi_id_number << endl;
					//cout << "sg_lun_number = " << Devices[device_index].sg_lun_number << endl;
					//cout << "sg_scsi_type = " << Devices[device_index].sg_scsi_type << endl;
					//cout << "block_device_file = " << Devices[device_index].block_device_file << endl;
					break;
				}
			}
		}
		i += 1;
	}

	//Do sginfo -a /dev/sg#
	//Get sg_vendor_string, sg_product_string, sg_revision_string, sg_serial_number_string
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
	
		gettimeofday(&start, NULL);
		
		if (RunProcessGetExitCode("sginfo -a " + Devices[device_index].sg_device_file, outlines, exitcode) == false) {
			WriteConsoleLine("  Error: Failed sginfo -a " + Devices[device_index].sg_device_file);
			return false;
		}
		
		gettimeofday(&end, NULL);
		seconds = end.tv_sec - start.tv_sec;
		useconds = end.tv_usec - start.tv_usec;
		mtime = ((seconds) * 1000 + useconds / 1000.0) + 0.5;
		if ((mtime > 3000) || (verbose)) {
			WriteConsoleLine("Info: It takes " + ToString(mtime) + " ms to complete " + "sginfo -a " + Devices[device_index].sg_device_file);
		}
						
		i = 0;
		while (i < outlines.size()) {
			//cout << "[" << outlines[i] << "]" << endl;
			if (outlines[i].find("Vendor:") == 0) {
				Devices[device_index].sg_vendor_string = outlines[i].substr(string("Vendor:").length());
				trim(Devices[device_index].sg_vendor_string);
				//cout << "sg_vendor_string = [" << Devices[device_index].sg_vendor_string << "]" << endl;
			} else if (outlines[i].find("Product:") == 0) {
				Devices[device_index].sg_product_string = outlines[i].substr(string("Product:").length());
				trim(Devices[device_index].sg_product_string);
				//cout << "sg_product_string = [" << Devices[device_index].sg_product_string << "]" << endl;
			} else if (outlines[i].find("Revision level:") == 0) {
				Devices[device_index].sg_revision_string = outlines[i].substr(string("Revision level:").length());
				trim(Devices[device_index].sg_revision_string);
				//cout << "sg_revision_string = [" << Devices[device_index].sg_revision_string << "]" << endl;
			} else if (outlines[i].find("Serial Number ") == 0) {
				Devices[device_index].sg_serial_number_string = outlines[i].substr(string("Serial Number ").length());
				trim(Devices[device_index].sg_serial_number_string);
				if ((Devices[device_index].sg_serial_number_string.length() > 1) && (Devices[device_index].sg_serial_number_string[0] == '\'') && (Devices[device_index].sg_serial_number_string[Devices[device_index].sg_serial_number_string.length() - 1] == '\'')) {
					Devices[device_index].sg_serial_number_string = Devices[device_index].sg_serial_number_string.substr(1, Devices[device_index].sg_serial_number_string.length() - 2);
					trim(Devices[device_index].sg_serial_number_string);
				}
				//cout << "sg_serial_number_string = [" << Devices[device_index].sg_serial_number_string << "]" << endl;
			}
			i += 1;
		}
	}

	//Do sg_readcap /dev/sg#
	//Get sg_size_long_string, sg_size
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
	
		//Skip sg_readcap on virtual devices
		if ((Devices[device_index].sg_product_string.length() >= 7 ) && 
		    (Devices[device_index].sg_product_string.substr(0, 7) == "Virtual" )) {
			continue;
		}
	
		gettimeofday(&start, NULL);
		
		if (RunProcessGetExitCode("sg_readcap " + Devices[device_index].sg_device_file, outlines, exitcode) == false) {
			WriteConsoleLine("  Error: Failed sg_readcap " + Devices[device_index].sg_device_file);
			return false;
		}
		
		gettimeofday(&end, NULL);
		seconds = end.tv_sec - start.tv_sec;
		useconds = end.tv_usec - start.tv_usec;
		mtime = ((seconds) * 1000 + useconds / 1000.0) + 0.5;
		if ((mtime > 3000) || (verbose)) {
			WriteConsoleLine("Info: It takes " + ToString(mtime) + " ms to complete " + "sg_readcap " + Devices[device_index].sg_device_file);
		}		
		
		i = 0;
		while (i < outlines.size()) {
			if (outlines[i].find("Device size:") != string::npos) {
				//cout << "[" << outlines[i] << "]" << endl;
				string s = outlines[i].substr(outlines[i].find("Device size:") + string("Device size:").length());
				trim(s);
				Devices[device_index].sg_size_long_string = s;
				//cout << "sg_size_long_string = [" << Devices[device_index].sg_size_long_string << "]" << endl;
				if (s.find("bytes") != string::npos) {
					s = s.substr(0, s.find("bytes"));
					trim(s);
					Devices[device_index].sg_size = s;
					//cout << "sg_size = [" << Devices[device_index].sg_size << "]" << endl;
				}
			}
			i += 1;
		}
	}

	//List link files in /dev/disk/by-path/
	//Get pci-path, usb-path, scsi-path
	if (IsDirectoryExist("/dev/disk/by-path")) {
		vector<DevDiskByPathInfo> disksbypath = vector<DevDiskByPathInfo> ();
		vector < string > filenames = vector<string> ();
		if (GetFilesInDirectory("/dev/disk/by-path/", filenames) == true) {
			for (int file_index = 0; file_index < filenames.size(); file_index++) {
				DevDiskByPathInfo newdisk;
				newdisk.filename = filenames[file_index];
				//cout << "filename = " << newdisk.filename << endl;
				newdisk.fullfilename = "/dev/disk/by-path/" + filenames[file_index];
				//cout << "fullfilename = " << newdisk.fullfilename << endl;
				if (filenames[file_index].find("pci-") != string::npos) {
					string s = filenames[file_index].substr(filenames[file_index].find("pci-") + string("pci-").length());
					if (s.find("-") != string::npos)
						s = s.substr(0, s.find("-"));
					newdisk.pcipath = s;
					//cout << "pcipath = " << newdisk.pcipath << endl;
				}
				if (filenames[file_index].find("usb-") != string::npos) {
					string s = filenames[file_index].substr(filenames[file_index].find("usb-") + string("usb-").length());
					if (s.find("-") != string::npos)
						s = s.substr(0, s.find("-"));
					newdisk.usbpath = s;
					//cout << "usbpath = " << newdisk.usbpath << endl;
				}
				if (filenames[file_index].find("scsi-") != string::npos) {
					string s = filenames[file_index].substr(filenames[file_index].find("scsi-") + string("scsi-").length());
					if (s.find("-") != string::npos)
						s = s.substr(0, s.find("-"));
					newdisk.scsipath = s;
					//cout << "scsipath = " << newdisk.scsipath << endl;
				}

				vector < string > tmpoutlines = vector<string> ();
				
				gettimeofday(&start, NULL);
				
				if ((RunProcessGetExitCode("readlink -f " + newdisk.fullfilename, tmpoutlines, exitcode) == false) || (exitcode != 0) || (tmpoutlines.size() == 0) || (tmpoutlines[0].find("/dev/") != 0)) {
					WriteConsoleLine("  Error: Failed readlink -f " + newdisk.fullfilename);
					continue;
				}
				
				gettimeofday(&end, NULL);
				seconds = end.tv_sec - start.tv_sec;
				useconds = end.tv_usec - start.tv_usec;
				mtime = ((seconds) * 1000 + useconds / 1000.0) + 0.5;
				if ((mtime > 3000) || (verbose)) {
					WriteConsoleLine("Info: It takes " + ToString(mtime) + " ms to complete " + "readlink -f " + newdisk.fullfilename);
				}		
		
				if (tmpoutlines[0] != newdisk.fullfilename)
					newdisk.block_device_file = tmpoutlines[0];
				disksbypath.push_back(newdisk);
			}

			if (disksbypath.size() > 0) {
				for (int disk_index = 0; disk_index < disksbypath.size(); disk_index++) {
					for (int device_index = 0; device_index < Devices.size(); device_index++) {
						if (disksbypath[disk_index].block_device_file == Devices[device_index].block_device_file) {
							Devices[device_index].pci_path = disksbypath[disk_index].pcipath;
							Devices[device_index].usb_path = disksbypath[disk_index].usbpath;
							Devices[device_index].scsi_path = disksbypath[disk_index].scsipath;
							//cout << "device_index = " << device_index << endl;
							//cout << "pci_path = " << Devices[device_index].pci_path << endl;
							//cout << "usb_path = " << Devices[device_index].usb_path << endl;
							//cout << "scsi_path = " << Devices[device_index].scsi_path << endl;
							break;
						}
					}
				}
			}
		}
	}

	//Do lspci -s pci-path -nnvvD
	//Get pci_description_string, pci_vendor_device_id
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].pci_path.length() > 0) {
		
			gettimeofday(&start, NULL);
			
			if ((RunProcessGetExitCode("lspci -s " + Devices[device_index].pci_path + " -nnvvD", outlines, exitcode) == false) || (outlines.size() == 0)) {
				WriteConsoleLine("  Error: Failed lspci -s " + Devices[device_index].pci_path);
				continue;
			}
			
			gettimeofday(&end, NULL);
			seconds = end.tv_sec - start.tv_sec;
			useconds = end.tv_usec - start.tv_usec;
			mtime = ((seconds) * 1000 + useconds / 1000.0) + 0.5;
			if ((mtime > 3000) || (verbose)) {
				WriteConsoleLine("Info: It takes " + ToString(mtime) + " ms to complete " + "lspci -s " + Devices[device_index].pci_path + " -nnvvD");
			}				
			
			//cout << "[" << outlines[0] << "]" << endl;
			string domain;
			string bus;
			string dev;
			string func;
			string devicetype;
			string devicedescription;
			string vendorid;
			string deviceid;
			string revision;
			bool ret = ParseLsPciVVNNDFirstLineInfo(outlines[0], domain, bus, dev, func, devicetype, devicedescription, vendorid, deviceid, revision);
			if ((ret == true) && (devicedescription.length() > 0))
				Devices[device_index].pci_description_string = devicedescription;
			//cout << "pci_description_string = " << Devices[device_index].pci_description_string << endl;
			if ((ret == true) && (vendorid.length() > 0) && (deviceid.length() > 0))
				Devices[device_index].pci_vendor_device_id = vendorid + ":" + deviceid;
			//cout << "pci_vendor_device_id = " << Devices[device_index].pci_vendor_device_id << endl;
		}
	}

	return true;
}

bool Parse_sg_scan_i_Line1(string line, string& sg_divice_file) {
	sg_divice_file.clear();
	if (line.find("/dev/sg") != 0)
		return false;
	if (line.find(":") == string::npos)
		return false;
	sg_divice_file = line.substr(0, line.find(":", 0));
	return true;
}

bool Parse_sg_scan_i_Line2(string line, bool& sg_removeable, bool& sg_command_queuing) {
	sg_removeable = false;
	sg_command_queuing = false;
	if (line.find("[") == string::npos)
		return false;
	if (line.find("]", line.find("[")) == string::npos)
		return false;
	string attrstring = line.substr(line.find("[") + 1);
	attrstring = attrstring.substr(0, attrstring.find("]"));
	if (attrstring.find("rmb=") >= 0) {
		string substring = attrstring.substr(attrstring.find("rmb=") + string("rmb=").length());
		if ((substring.length() > 0) && (substring[0] == '1'))
			sg_removeable = true;
	}
	if (attrstring.find("cmdq=") >= 0) {
		string substring = attrstring.substr(attrstring.find("cmdq=") + string("cmdq=").length());
		if ((substring.length() > 0) && (substring[0] == '1'))
			sg_removeable = true;
	}
	return true;
}

SgMapInfo Parse_sg_map_x(string line) {
	SgMapInfo ret;
	ret.success = false;
	vector < string > ss = SplitStringByDelimiter(line, ' ');
	if (ss.size() < 6)
		return ret;
	ret.success = true;
	ret.sg_device_file = ss[0];
	ret.sg_host_number = ss[1];
	ret.sg_bus_number = ss[2];
	ret.sg_scsi_id_number = ss[3];
	ret.sg_lun_number = ss[4];
	ret.sg_scsi_type = ss[5];
	if (ss.size() > 6)
		ret.block_device_file = ss[6];
	return ret;
}

bool ParseLsPciVVNNDFirstLineInfo(string value, string& domain, string& bus, string& device, string& func, string& devicetype, string& devicedescription, string& vendorid, string& deviceid, string& revision) {
	domain.clear();
	bus.clear();
	device.clear();
	func.clear();
	devicetype.clear();
	devicedescription.clear();
	vendorid.clear();
	deviceid.clear();
	revision.clear();

	//Get domain:bus:device:function
	if (value.find(" ") == string::npos)
		return false;
	string s1 = value.substr(0, value.find(" "));
	string remain = value.substr(value.find(" ") + 1);
	//cout << "[" << s1 << "]" << endl;
	//cout << "[" << remain << "]" << endl;
	//Get domain, bus, device, function
	vector < string > ss = SplitStringByDelimiter(s1, ':');
	if (ss.size() != 3)
		return false;
	domain = ss[0];
	bus = ss[1];
	ss = SplitStringByDelimiter(ss[2], '.');
	if (ss.size() != 2)
		return false;
	device = ss[0];
	func = ss[1];
	//cout << "domain = [" << domain << "]" << endl;
	//cout << "bus = [" << bus << "]" << endl;
	//cout << "device = [" << device << "]" << endl;
	//cout << "func = [" << func << "]" << endl;
	//Get device type
	if (remain.find(":") == string::npos)
		return false;
	devicetype = remain.substr(0, remain.find(":"));
	//cout << "devicetype = [" << devicetype << "]" << endl;
	remain = remain.substr(remain.find(":") + 1);
	int vidindex = FindIndexOfVendorIDBracket(remain);
	if (vidindex < 0)
		return false;
	devicedescription = remain.substr(0, vidindex);
	trim(devicedescription);
	//cout << "devicedescription = [" << devicedescription << "]" << endl;
	remain = remain.substr(vidindex + 1);
	if (remain.find(":") == string::npos)
		return false;
	vendorid = remain.substr(0, remain.find(":"));
	trim(vendorid);
	//cout << "vendorid = [" << vendorid << "]" << endl;
	remain = remain.substr(remain.find(":") + 1);
	if (remain.find("]") == string::npos)
		return false;
	deviceid = remain.substr(0, remain.find("]"));
	trim(deviceid);
	//cout << "deviceid = [" << deviceid << "]" << endl;
	remain = remain.substr(remain.find("]") + 1);
	if (remain.find("(") != string::npos) {
		if (remain.find("(") == string::npos)
			return false;
		remain = remain.substr(remain.find("(") + 1);
		if (remain.find(")") == string::npos)
			return false;
		revision = remain.substr(0, remain.find(")"));
		trim(revision);
		if (revision.find("rev ") == 0)
			revision = revision.substr(string("rev ").length());
	} else {
		revision = "N.A.";
	}
	//cout << "revision = [" << revision << "]" << endl;
	return true;
}

int FindIndexOfVendorIDBracket(string value) {
	string s1 = value;
	string s2;
	string s3;
	int index = -1;
	while (s1.find("[") != string::npos) {
		index = s1.find("[");
		s2 = s1.substr(0, index);
		s3 = s1.substr(index + 1);
		if ((s3.length() >= 10) && (s3[4] == ':') && (s3[9] == ']'))
			return value.find(s3) - 1;
		else
			s1 = s3;
	}
	return -1;
}

bool CheckPartitionExist(string blockfile, bool& partitionexist, string& cpstdout) {
	cpstdout.clear();
	partitionexist = false;
	if (blockfile.length() == 0)
		return true;
	vector < string > outlines = vector<string> ();
	int exitcode;
	
	struct timeval start, end;
	long mtime, seconds, useconds;
	gettimeofday(&start, NULL);
	
	if (RunProcessGetExitCode("fdisk -l " + blockfile, outlines, exitcode) == false) {
		cpstdout += "  fdisk -l " + blockfile + " returns " + ToString(exitcode) + "\n";
		return false;
	}
	
	gettimeofday(&end, NULL);
	seconds = end.tv_sec - start.tv_sec;
	useconds = end.tv_usec - start.tv_usec;
	mtime = ((seconds) * 1000 + useconds / 1000.0) + 0.5;
	if ((mtime > 3000) || (verbose)) {
		WriteConsoleLine("Info: It takes " + ToString(mtime) + " ms to complete " + "fdisk -l " + blockfile);
	}
			
	for (int i = 0; i < outlines.size(); i++) {
		if (outlines[i].find("doesn't contain a valid partition table") != string::npos) {
			cpstdout += "    " + outlines[i] + "\n";
			return true;
		} else if (outlines[i].find(blockfile) == 0) {
			cpstdout += "    " + outlines[i] + "\n";
			partitionexist = true;
		}
	}
	return true;
}

bool ShowDevicesInfo(vector<string>& vendors, vector<string>& products, vector<string>& revisions, vector<string>& sns, vector<string>& sizes, bool& smart) {
	bool haserror = false;
	bool isanychecked = false;
	//Print all device info
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		DeviceInfo device = Devices[device_index];
		if (device.enabled == true) {
			WriteConsoleLine("Device info for " + device.sg_device_file);
			if (device.sg_removeable == true)
				WriteConsoleLine("  Removable");
			if (device.sg_command_queuing == true)
				WriteConsoleLine("  Command queuing supported");
			if (device.sg_host_number.length() > 0)
				WriteConsoleLine("  Host#=" + device.sg_host_number);
			if (device.sg_bus_number.length() > 0)
				WriteConsoleLine("  Bus#=" + device.sg_bus_number);
			if (device.sg_scsi_id_number.length() > 0)
				WriteConsoleLine("  SCSI Id#=" + device.sg_scsi_id_number);
			if (device.sg_lun_number.length() > 0)
				WriteConsoleLine("  LUN#=" + device.sg_lun_number);
			if (device.sg_scsi_type.length() > 0)
				WriteConsoleLine("  Type=" + device.sg_scsi_type);
			if (device.sg_size_long_string.length() > 0)
				WriteConsoleLine("  Size=" + device.sg_size_long_string);
			if (device.block_device_file.length() > 0)
				WriteConsoleLine("  Block device=" + device.block_device_file);
			if (device.sg_vendor_string.length() > 0)
				WriteConsoleLine("  Vendor=" + device.sg_vendor_string);
			if (device.sg_product_string.length() > 0)
				WriteConsoleLine("  Product=" + device.sg_product_string);
			if (device.sg_revision_string.length() > 0)
				WriteConsoleLine("  Revision=" + device.sg_revision_string);
			if (device.sg_serial_number_string.length() > 0)
				WriteConsoleLine("  Serial number=" + device.sg_serial_number_string);
			if (device.pci_description_string.length() > 0)
				WriteConsoleLine("  Controller=" + device.pci_description_string);
			if (device.pci_vendor_device_id.length() > 0)
				WriteConsoleLine("  Controller PCI vendorID:deviceID=" + device.pci_vendor_device_id);
			if (device.pci_path.length() > 0)
				WriteConsoleLine("  Controller PCI path=" + device.pci_path);
			if (device.usb_path.length() > 0)
				WriteConsoleLine("  Controller USB path=" + device.usb_path);
			if (device.scsi_path.length() > 0)
				WriteConsoleLine("  Controller SCSI path=" + device.scsi_path);

			if (vendors.size() > 0) {
				bool ischecked = false;
				bool isvalid = false;
				for (int index = 0; index < vendors.size(); index++) {
					ischecked = true;
					if (vendors[index] == device.sg_vendor_string) {
						isvalid = true;
						break;
					}
				}
				if (ischecked == true)
					isanychecked = true;
				if ((ischecked == true) && (isvalid == true)) {
					WriteConsoleLine("    Info: Vendor string matches");
				} else if (ischecked == true) {
					WriteConsoleLine("    Error: Vendor string mismatches");
					haserror = true;
				}
			}

			if (products.size() > 0) {
				bool ischecked = false;
				bool isvalid = false;
				for (int index = 0; index < products.size(); index++) {
					ischecked = true;
					if (products[index] == device.sg_product_string) {
						isvalid = true;
						break;
					}
				}
				if (ischecked == true)
					isanychecked = true;
				if ((ischecked == true) && (isvalid == true)) {
					WriteConsoleLine("    Info: Product string matches");
				} else if (ischecked == true) {
					WriteConsoleLine("    Error: Product string mismatches");
					haserror = true;
				}
			}

			if (revisions.size() > 0) {
				bool ischecked = false;
				bool isvalid = false;
				for (int index = 0; index < revisions.size(); index++) {
					ischecked = true;
					if (revisions[index] == device.sg_revision_string) {
						isvalid = true;
						break;
					}
				}
				if (ischecked == true)
					isanychecked = true;
				if ((ischecked == true) && (isvalid == true)) {
					WriteConsoleLine("    Info: Revision string matches");
				} else if (ischecked == true) {
					WriteConsoleLine("    Error: Revision string mismatches");
					haserror = true;
				}
			}

			if (sns.size() > 0) {
				bool ischecked = false;
				bool isvalid = false;
				for (int index = 0; index < sns.size(); index++) {
					ischecked = true;
					if (sns[index] == device.sg_serial_number_string) {
						isvalid = true;
						break;
					}
				}
				if (ischecked == true)
					isanychecked = true;
				if ((ischecked == true) && (isvalid == true)) {
					WriteConsoleLine("    Info: Serial number string matches");
				} else if (ischecked == true) {
					WriteConsoleLine("    Error: Serial number string mismatches");
					haserror = true;
				}
			}

			if (sizes.size() > 0) {
				bool ischecked = false;
				bool isvalid = false;
				for (int index = 0; index < sizes.size(); index++) {
					ischecked = true;
					if (sizes[index] == device.sg_size) {
						isvalid = true;
						break;
					}
				}
				if (ischecked == true)
					isanychecked = true;
				if ((ischecked == true) && (isvalid == true)) {
					WriteConsoleLine("    Info: Size string matches");
				} else if (ischecked == true) {
					WriteConsoleLine("    Error: Size string mismatches");
					haserror = true;
				}
			}

			if (smart == true) {
				vector < string > outlines = vector<string> ();
				int exitcode;
				WriteConsoleLine("    Info: smartctl -a " + device.sg_device_file);
				
				struct timeval start, end;
				long mtime, seconds, useconds;
				gettimeofday(&start, NULL);
				
				if ((RunProcessGetExitCode("smartctl -a " + device.sg_device_file, outlines, exitcode) == false) || (exitcode != 0) || (outlines.size() == 0)) {
					WriteConsoleLine("      Error: Failed smartctl -a " + device.sg_device_file);
					WriteConsoleLine("      Exit code is " + ToString(exitcode));
					for (int tmpi = 0; tmpi < outlines.size(); tmpi++)
						WriteConsoleLine("      " + outlines[tmpi]);
					haserror = true;
				} else {
					WriteConsoleLine("      Pass smartctl -a " + device.sg_device_file + ", return code is 0");
				}
				
				gettimeofday(&end, NULL);
				seconds = end.tv_sec - start.tv_sec;
				useconds = end.tv_usec - start.tv_usec;
				mtime = ((seconds) * 1000 + useconds / 1000.0) + 0.5;
				if ((mtime > 3000) || (verbose)) {
					WriteConsoleLine("Info: It takes " + ToString(mtime) + " ms to complete " + "smartctl -a " + device.sg_device_file);
				}
	
				isanychecked = true;
			}
		}
	}

	if (isanychecked == true) {
		if (haserror == false) {
			WriteConsoleLine("*******************************");
			WriteConsoleLine("*** Info check status: Pass ***");
			WriteConsoleLine("*******************************");
			return true;
		} else {
			WriteConsoleLine("*******************************");
			WriteConsoleLine("*** Info check status: Fail ***");
			WriteConsoleLine("*******************************");
			return false;
		}
	} else {
		return true;
	}
}

bool DoSgReads(string count, string bpt, string speed, string retries) {
	//Enable dio
	if (IsFileExist("/proc/scsi/sg/allow_dio") == true) {
		ifstream infile;
		infile.open("/proc/scsi/sg/allow_dio", ifstream::in);
		char ch = infile.get();
		infile.close();
		//cout << "ch = " << ch << endl;
		if (ch == '0') {
			ofstream outfile;
			outfile.open("/proc/scsi/sg/allow_dio", ofstream::out);
			outfile.put('1');
			outfile.close();
		}
	}

	if (speed.length() == 0) {
		WriteConsoleLine("Error: No speed value specified");
		return false;
	}
	double minspeed = atof(speed.c_str());
	//cout << "minspeed = " << minspeed << endl;

	int maxcount = atoi(retries.c_str());
	//cout << "maxcount = " << maxcount << endl;
	bool haserror = false;
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			int countremains = maxcount + 1;
			bool ret = false;
			while ((countremains > 0) && (ret == false)) {
				ret = DoSingleSgRead(Devices[device_index], count, bpt, speed, minspeed, (countremains < maxcount + 1));
				countremains -= 1;
			}
			if (ret == false)
				haserror = true;
		}
	}
	if (haserror == false) {
		WriteConsoleLine("*******************************");
		WriteConsoleLine("*** Speed test status: Pass ***");
		WriteConsoleLine("*******************************");
		return true;
	} else {
		WriteConsoleLine("*******************************");
		WriteConsoleLine("*** Speed test status: Fail ***");
		WriteConsoleLine("*******************************");
		return false;
	}
}

bool DoSingleSgRead(DeviceInfo& device, string count, string bpt, string speed, double minspeed, bool isretry) {
	if (isretry == false) {
		WriteConsoleLine("Test bus speed on " + device.sg_device_file);
	} else {
		WriteConsoleLine("Retry test bus speed on " + device.sg_device_file);
		sleep(0.5);
	}

	vector < string > outlines = vector<string> ();
	int exitcode;
	string param = "if=" + device.sg_device_file + " bs=512 time=2 blk_sgio=1 dio=1 count=" + count;
	if (bpt.length() > 0)
		param = param + " bpt=" + bpt;
	WriteConsoleLine("  Info: sg_read " + param);

	if ((RunProcessGetExitCode("sg_read " + param, outlines, exitcode) == false) || (exitcode != 0) || (outlines.size() == 0) || (outlines[0].find("Time from second SCSI READ command to end was ") == string::npos)) {
		WriteConsoleLine("  Error: Failed sg_read " + param);
		if (exitcode != 0) {
			WriteConsoleLine("    Exit code is " + ToString(exitcode));
			for (int tmpi = 0; tmpi < outlines.size(); tmpi++)
				WriteConsoleLine("    " + outlines[tmpi]);
		}
		return false;
	}

	string s = outlines[0].substr(outlines[0].find("Time from second SCSI READ command to end was "));
	if (s.find(", ") == string::npos) {
		WriteConsoleLine("  Error: Failed to get speed from [" + outlines[0] + "]");
		return false;
	}
	s = s.substr(s.find(", ") + string(", ").length());
	if (s.find("MB/sec") == string::npos) {
		WriteConsoleLine("  Error: Failed to get speed from [" + outlines[0] + "]");
		return false;
	}
	s = s.substr(0, s.find("MB/sec"));
	trim(s);
	double speeddouble = atof(s.c_str());
	//cout << "outlines[0] = " << outlines[0] << endl;
	//cout << "speeddouble = " << speeddouble << endl;
	if (speeddouble < minspeed) {
		WriteConsoleLine("  Fail: Speed is " + s + " MB/sec, less then " + speed + " MB/sec");
		return false;
	} else {
		WriteConsoleLine("  Pass: Speed is " + s + " MB/sec, more then " + speed + " MB/sec");
		return true;
	}
}

bool DoSgWriteReadCompare(string blocksize, string bpt, string blockcount, bool nosync, string dir, bool clear, bool ignore_nak, string blockoffset) {
	int bs = 0;
	if (GetIntegerValue(blocksize, bs) == false)
		return false;
	//cout << "bs = " << bs << endl;
	long count = 0;
	if (GetLongValue(blockcount, count) == false)
		return false;
	//cout << "count = " << count << endl;

	long offset = 0;
	if (GetLongValue(blockoffset, offset) == false)
		return false;
	//cout << "offset = " << offset << endl;

	//Clear directory
	if (clear == true) {
		vector < string > existingfiles = vector<string> ();
		if (GetFilesInDirectory(dir, existingfiles) == true) {
			for (int tmpi = 0; tmpi < existingfiles.size(); tmpi++) {
				if (IsMD5Filename(existingfiles[tmpi]) == true) {
					WriteConsoleLine("Removing existing file " + dir + existingfiles[tmpi]);
					remove((dir + existingfiles[tmpi]).c_str());
				}
			}
		}
	}

	//Create random files
	WriteConsole("Creating random files");
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			pthread_mutex_lock(&mutex);
			Devices[device_index].sg_writeread_action = CreateRandomFile;
			Devices[device_index].sg_writeread_blockcount = count;
			Devices[device_index].sg_writeread_blockcount_string = blockcount;
			Devices[device_index].sg_writeread_offset = offset;
			Devices[device_index].sg_writeread_offset_string = blockoffset;
			Devices[device_index].sg_writeread_blocksize = bs;
			Devices[device_index].sg_writeread_blocksize_string = blocksize;
			Devices[device_index].sg_writeread_bpt_string = bpt;
			Devices[device_index].sg_writeread_if_filename = dir + GenerateRandomMd5();
			//cout << Devices[device_index].sg_writeread_if_filename << endl;
			Devices[device_index].sg_writeread_of_filename = dir + GenerateRandomMd5();
			//cout << Devices[device_index].sg_writeread_of_filename << endl;
			Devices[device_index].sg_writeread_stdout.clear();
			Devices[device_index].sg_writeread_stderr.clear();
			Devices[device_index].ignore_nak = ignore_nak;
			Devices[device_index].sg_writeread_result = false;
			//Devices[device_index].sg_writeread_thread = New Threading.Thread(AddressOf WriteReadThread)
			Devices[device_index].create_thread_ret = pthread_create(&Devices[device_index].sg_writeread_thread, NULL, WriteReadThread, &Devices[device_index]);
			pthread_mutex_unlock(&mutex);
		}
	}

	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  *** Check thread for creating random files");
		// pthread_mutex_unlock(&mutex);
	// }

	//Check all threads created successfully
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			if (Devices[device_index].create_thread_ret) {
				WriteConsoleLine("failed to create thread");
				WriteConsoleLine("");
				WriteConsoleLine("********************************************");
				WriteConsoleLine("*** Write-Read-Compare test status: Fail ***");
				WriteConsoleLine("********************************************");
				return false;
			}
		}
	}

	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  *** Create dot thread for creating random files");
		// pthread_mutex_unlock(&mutex);
	// }

	//Create print dot thread;
	pthread_t print_dot_thread;
	pthread_create(&print_dot_thread, NULL, PrintDotEvertSecondThread, NULL);

	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  *** Join thread for creating random files");
		// pthread_mutex_unlock(&mutex);
	// }

	//Join and close all threads
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			Devices[device_index].join_thread_ret = pthread_join(Devices[device_index].sg_writeread_thread, NULL);
		}
	}

	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  *** Cancel dot thread for creating random files");
		// pthread_mutex_unlock(&mutex);
	// }

	//Cancel thread;
	pthread_mutex_lock(&mutex);
	pthread_cancel(print_dot_thread);
	pthread_detach(print_dot_thread);
	pthread_mutex_unlock(&mutex);
	WriteConsoleLine(" done.");

	//Check all threads joined successfully
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			if (Devices[device_index].join_thread_ret) {
				WriteConsoleLine("failed to join thread");
				WriteConsoleLine("");
				WriteConsoleLine("********************************************");
				WriteConsoleLine("*** Write-Read-Compare test status: Fail ***");
				WriteConsoleLine("********************************************");
				return false;
			}
		}
	}

	//Check for errors
	bool haserror = false;
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			if (Devices[device_index].sg_writeread_result == false)
				haserror = true;
		}
	}
	if (haserror == true) {
		for (int device_index = 0; device_index < Devices.size(); device_index++) {
			if (Devices[device_index].enabled == true) {
				WriteConsoleLine("\nWrite-Read-Compare status for " + Devices[device_index].sg_device_file);
				if (Devices[device_index].sg_writeread_stdout.length() > 0)
					WriteConsoleLine(Devices[device_index].sg_writeread_stdout);
				if (Devices[device_index].sg_writeread_stderr.length() > 0)
					WriteConsoleLine(Devices[device_index].sg_writeread_stderr);
				Devices[device_index].sg_writeread_action = RemoveTemporaryFiles;
				WriteReadThread(&Devices[device_index]);
			}
		}
		WriteConsoleLine("An error has occured while creating random file");
		WriteConsoleLine("");
		WriteConsoleLine("********************************************");
		WriteConsoleLine("*** Write-Read-Compare test status: Fail ***");
		WriteConsoleLine("********************************************");
		return false;
	}

	//Do sg_dd & compare
	WriteConsole("Transfer data to device, read back, and compare");

	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			pthread_mutex_lock(&mutex);
			Devices[device_index].sg_writeread_action = TransferInAndOutAndCompare;
			Devices[device_index].sg_writeread_nosync = nosync;
			Devices[device_index].sg_writeread_result = false;
			Devices[device_index].create_thread_ret = pthread_create(&Devices[device_index].sg_writeread_thread, NULL, WriteReadThread, &Devices[device_index]);
			pthread_mutex_unlock(&mutex);
		}
	}

	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  *** Check thread for write read");
		// pthread_mutex_unlock(&mutex);
	// }

	//Check all threads created successfully
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			if (Devices[device_index].create_thread_ret) {
				WriteConsoleLine("failed to create thread");
				WriteConsoleLine("");
				WriteConsoleLine("********************************************");
				WriteConsoleLine("*** Write-Read-Compare test status: Fail ***");
				WriteConsoleLine("********************************************");
				return false;
			}
		}
	}

	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  *** Check dot thread for write read");
		// pthread_mutex_unlock(&mutex);
	// }

	//Create print dot thread;
	pthread_create(&print_dot_thread, NULL, PrintDotEvertSecondThread, NULL);

	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  *** Join thread for write read");
		// pthread_mutex_unlock(&mutex);
	// }

	//Join and close all threads
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			Devices[device_index].join_thread_ret = pthread_join(Devices[device_index].sg_writeread_thread, NULL);
		}
	}

	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  *** Cancel dot thread for write read");
		// pthread_mutex_unlock(&mutex);
	// }

	//Cancel thread;
	pthread_mutex_lock(&mutex);
	pthread_cancel(print_dot_thread);
	pthread_detach(print_dot_thread);
	pthread_mutex_unlock(&mutex);
	WriteConsoleLine(" done.");

	//Check all threads joined successfully
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			if (Devices[device_index].join_thread_ret) {
				WriteConsoleLine("failed to join thread");
				WriteConsoleLine("");
				WriteConsoleLine("********************************************");
				WriteConsoleLine("*** Write-Read-Compare test status: Fail ***");
				WriteConsoleLine("********************************************");
				return false;
			}
		}
	}

	haserror = false;
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			if (Devices[device_index].sg_writeread_result == false)
				haserror = true;
		}
	}
	if (haserror == true) {
		for (int device_index = 0; device_index < Devices.size(); device_index++) {
			if (Devices[device_index].enabled == true) {
				WriteConsoleLine("\nWrite-Read-Compare status for " + Devices[device_index].sg_device_file);
				if (Devices[device_index].sg_writeread_stdout.length() > 0)
					WriteConsoleLine(Devices[device_index].sg_writeread_stdout);
				if (Devices[device_index].sg_writeread_stderr.length() > 0)
					WriteConsoleLine(Devices[device_index].sg_writeread_stderr);
				Devices[device_index].sg_writeread_action = RemoveTemporaryFiles;
				WriteReadThread(&Devices[device_index]);
			}
		}
		WriteConsoleLine("An error has occured while performing sg_dd");
		WriteConsoleLine("");
		WriteConsoleLine("********************************************");
		WriteConsoleLine("*** Write-Read-Compare test status: Fail ***");
		WriteConsoleLine("********************************************");
		return false;
	}

	//Remove files
	haserror = false;
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			Devices[device_index].sg_writeread_action = RemoveTemporaryFiles;
			WriteReadThread(&Devices[device_index]);
			if (Devices[device_index].sg_writeread_result == false)
				haserror = true;
		}
	}
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		if (Devices[device_index].enabled == true) {
			WriteConsoleLine("\nWrite-Read-Compare status for " + Devices[device_index].sg_device_file);
			if (Devices[device_index].sg_writeread_stdout.length() > 0)
				WriteConsoleLine(Devices[device_index].sg_writeread_stdout);
			if (Devices[device_index].sg_writeread_stderr.length() > 0)
				WriteConsoleLine(Devices[device_index].sg_writeread_stderr);
		}
	}

	if (haserror == true) {
		WriteConsoleLine("An unknown error has occured");
		WriteConsoleLine("");
		WriteConsoleLine("********************************************");
		WriteConsoleLine("*** Write-Read-Compare test status: Fail ***");
		WriteConsoleLine("********************************************");
		return false;
	} else {
		WriteConsoleLine("********************************************");
		WriteConsoleLine("*** Write-Read-Compare test status: Pass ***");
		WriteConsoleLine("********************************************");
		return true;
	}
}

void *PrintDotEvertSecondThread(void *arg) {
	while (true) {
		pthread_mutex_lock(&mutex);
		WriteConsole(".");
		pthread_mutex_unlock(&mutex);
		sleep(1);
	}
}

void *WriteReadThread(void *arg) {
	WriteReadCompareActionEnum action;

	pthread_mutex_lock(&mutex);
	DeviceInfo *device = (DeviceInfo*) arg;
	//cout << device->sg_writeread_if_filename << endl;
	action = device->sg_writeread_action;
	pthread_mutex_unlock(&mutex);

	if (action == CreateRandomFile) {
		//Create random file
		string filename;
		int blocksize = 0;
		long blockcount = 0;
		pthread_mutex_lock(&mutex);
		filename = device->sg_writeread_if_filename;
		blocksize = device->sg_writeread_blocksize;
		blockcount = device->sg_writeread_blockcount;
		pthread_mutex_unlock(&mutex);

		// if (verbose) {
			// pthread_mutex_lock(&mutex);
			// WriteConsoleLine("  *** Create random filename " + filename);
			// pthread_mutex_unlock(&mutex);
		// }

		//cout << "filename = " << filename << endl << flush;
		//cout << "blocksize = " << blocksize << endl << flush;
		//cout << "filename = " << blockcount << endl << flush;
		ofstream fs;
		fs.open(filename.c_str(), ios::out | ios::binary);
		if (fs.is_open() == false) {
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Error: Failed to open " + filename + " for writing\n";
			device->sg_writeread_result = false;
			pthread_mutex_unlock(&mutex);
			return NULL;
		}
		long i = 0;
		long count = 0;

		char randgroup[10][blocksize];
		char diskSignature[3];
		FILE *fp;
		fp = fopen("/dev/urandom", "r");
		if (fp == NULL) {
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Error: Failed to /dev/urandom\n";
			device->sg_writeread_result = false;
			pthread_mutex_unlock(&mutex);
			fs.close();
			return NULL;
		}

		for (int tmpi = 0; tmpi < 10; tmpi++) {
			fread(&randgroup[tmpi], 1, blocksize, fp);
			while (randgroup[tmpi][0] == 0)
				fread(&randgroup[tmpi], 1, blocksize, fp);
		}

		fread(&diskSignature, 1, 4, fp);

		fclose(fp);

		char zerobytes[blocksize];
		for (int tmpi = 0; tmpi < blocksize; tmpi++)
			zerobytes[tmpi] = 0;
		zerobytes[0x1b8] = diskSignature[3];
		zerobytes[0x1b9] = diskSignature[2];
		zerobytes[0x1ba] = diskSignature[1];
		zerobytes[0x1bb] = diskSignature[0];
		zerobytes[0x1fe] = 0x55;
		zerobytes[0x1ff] = 0xaa;

		char onebytes[blocksize];
		for (int tmpi = 0; tmpi < blocksize; tmpi++)
			onebytes[tmpi] = 1;
		char twobytes[blocksize];
		for (int tmpi = 0; tmpi < blocksize; tmpi++)
			twobytes[tmpi] = 2;
		char threebytes[blocksize];
		for (int tmpi = 0; tmpi < blocksize; tmpi++)
			threebytes[tmpi] = 3;

		fs.write(zerobytes, blocksize);
		count += blocksize;
		fs.write(onebytes, blocksize);
		count += blocksize;
		fs.write(twobytes, blocksize);
		count += blocksize;
		fs.write(threebytes, blocksize);
		count += blocksize;

		for (int tmpi = 4; tmpi < blockcount; tmpi++) {
			fs.write(randgroup[rand() % 10], blocksize);
			count += blocksize;
		}
		if (fs.bad() == true) {
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Error: Failed to write to " + filename + "\n";
			device->sg_writeread_result = false;
			pthread_mutex_unlock(&mutex);
			fs.close();
			return NULL;
		}

		fs.close();

		pthread_mutex_lock(&mutex);
		if (count > 0) {
			device->sg_writeread_stdout += "  Info: " + filename + " created with " + ToStringWithComma(count) + " bytes of random data\n";
			device->sg_writeread_result = true;
		} else {
			device->sg_writeread_stdout += "  Error: " + filename + " is zero file size\n";
			device->sg_writeread_result = false;
		}
		pthread_mutex_unlock(&mutex);
		return NULL;
	} else if (action == RemoveTemporaryFiles) {
		//Remove temporary files
		string file1;
		string file2;
		pthread_mutex_lock(&mutex);
		file1 = device->sg_writeread_if_filename;
		file2 = device->sg_writeread_of_filename;
		device->sg_writeread_result = true;
		pthread_mutex_unlock(&mutex);
		if (IsFileExist(file1) == true) {
			remove(file1.c_str());
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Info: " + file1 + " removed\n";
			pthread_mutex_unlock(&mutex);
		}
		if (IsFileExist(file2) == true) {
			remove(file2.c_str());
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Info: " + file2 + " removed\n";
			pthread_mutex_unlock(&mutex);
		}
		return NULL;
	} else if (action == TransferInAndOutAndCompare) {
		//Do read/write
		//Do crc32 <sg_writeread_if_filename>
		string infilename;
		pthread_mutex_lock(&mutex);
		infilename = device->sg_writeread_if_filename;
		;
		pthread_mutex_unlock(&mutex);
		string cmd = "crc32 " + infilename;
		vector < string > outlines = vector<string> ();
		int exitcode;
		if ((RunProcessGetExitCode(cmd, outlines, exitcode) == false) || (exitcode != 0) || (outlines.size() == 0)) {
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Error: " + cmd + " has error \n";
			device->sg_writeread_result = false;
			pthread_mutex_unlock(&mutex);
			return NULL;
		} else {
			pthread_mutex_lock(&mutex);
			device->sg_writeread_if_filename_crc = trim(outlines[0]);
			device->sg_writeread_stdout += "  Info: Input file crc = " + device->sg_writeread_if_filename_crc + "\n";
			pthread_mutex_unlock(&mutex);
		}

		//Do sg_dd if=<sg_writeread_if_filename> of=/dev/sg# bs=<blocksize> time=1 sync=1
		pthread_mutex_lock(&mutex);
		cmd = "sg_dd if=" + device->sg_writeread_if_filename + " of=" + device->sg_device_file + " bs=" + device->sg_writeread_blocksize_string + " time=1";
		if (device->sg_writeread_bpt_string.length() > 0)
			cmd += " bpt=" + device->sg_writeread_bpt_string;
		if (device->sg_writeread_nosync == false)
			cmd += " sync=1";
		if (device->sg_writeread_offset > 0)
			cmd += " seek=" + device->sg_writeread_offset_string;
		device->sg_writeread_stdout += "  Info: running " + cmd + "\n";
		pthread_mutex_unlock(&mutex);
		if ((RunProcessGetExitCode(cmd, outlines, exitcode) == false) || (exitcode != 0) || (outlines.size() == 0)) {
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Error: " + cmd + " returns " + ToString(exitcode) + "\n";
			for (int tmpi = 0; tmpi < outlines.size(); tmpi++)
				device->sg_writeread_stdout += "    " + outlines[tmpi] + "\n";
			device->sg_writeread_result = false;
			pthread_mutex_unlock(&mutex);
			return NULL;
		} else {
			bool hasextraerror = false;
			pthread_mutex_lock(&mutex);
			for (int tmpi = 0; tmpi < outlines.size(); tmpi++) {
				device->sg_writeread_stdout += "    " + outlines[tmpi] + "\n";
				if (outlines[tmpi].find("time to transfer data") != string::npos) {
					//ok
				} else if (outlines[tmpi].find("Synchronizing cache on ") != string::npos) {
					//ok
				} else if (outlines[tmpi].find("records in") != string::npos) {
					//ok
				} else if (outlines[tmpi].find("records out") != string::npos) {
					//ok
				} else if ((outlines[tmpi].find("reading: SCSI status: Check Condition") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else if ((outlines[tmpi].find("Fixed format, current;  Sense key: Aborted Command") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else if ((outlines[tmpi].find("Additional sense: Nak received") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else if ((outlines[tmpi].find("Info fld=") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else if ((outlines[tmpi].find("Aborted command, continuing (r)") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else {

					hasextraerror = true;
				}
			}
			if (hasextraerror) {
				device->sg_writeread_stdout += "  Error: " + cmd + " returns some unknown error\n";
				device->sg_writeread_result = false;
			}
			pthread_mutex_unlock(&mutex);
			if (hasextraerror)
				return NULL;
		}

		//Remove <sg_writeread_if_filename>
		if (IsFileExist(infilename) == true) {
			remove(infilename.c_str());
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Info: " + device->sg_writeread_if_filename + " removed\n";
			pthread_mutex_unlock(&mutex);
		}
		
		system("sync; echo 3 > /proc/sys/vm/drop_caches");

		//Do sg_dd if=/dev/sg# of=<sg_writeread_of_filename> bs=<blocksize> count=<count> time=1 sync=1
		string outfilename;
		pthread_mutex_lock(&mutex);
		outfilename = device->sg_writeread_of_filename;
		cmd = "sg_dd if=" + device->sg_device_file + " of=" + device->sg_writeread_of_filename + " bs=" + device->sg_writeread_blocksize_string + " time=1";
		if (device->sg_writeread_bpt_string.length() > 0)
			cmd += " bpt=" + device->sg_writeread_bpt_string;
		cmd += " sync=1";
		cmd += " count=" + device->sg_writeread_blockcount_string;
		if (device->sg_writeread_offset > 0)
			cmd += " skip=" + device->sg_writeread_offset_string;
		device->sg_writeread_stdout += "  Info: running " + cmd + "\n";
		pthread_mutex_unlock(&mutex);
		if ((RunProcessGetExitCode(cmd, outlines, exitcode) == false) || (exitcode != 0) || (outlines.size() == 0)) {
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Error: " + cmd + " returns " + ToString(exitcode) + "\n";
			for (int tmpi = 0; tmpi < outlines.size(); tmpi++)
				device->sg_writeread_stdout += "    " + outlines[tmpi] + "\n";
			device->sg_writeread_result = false;
			pthread_mutex_unlock(&mutex);
			return NULL;
		} else {
			bool hasextraerror = false;
			pthread_mutex_lock(&mutex);
			for (int tmpi = 0; tmpi < outlines.size(); tmpi++) {
				device->sg_writeread_stdout += "    " + outlines[tmpi] + "\n";
				if (outlines[tmpi].find("time to transfer data") != string::npos) {
					//ok
				} else if (outlines[tmpi].find("Synchronizing cache on ") != string::npos) {
					//ok
				} else if (outlines[tmpi].find("records in") != string::npos) {
					//ok
				} else if (outlines[tmpi].find("records out") != string::npos) {
					//ok
				} else if ((outlines[tmpi].find("reading: SCSI status: Check Condition") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else if ((outlines[tmpi].find("Fixed format, current;  Sense key: Aborted Command") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else if ((outlines[tmpi].find("Additional sense: Nak received") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else if ((outlines[tmpi].find("Info fld=") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else if ((outlines[tmpi].find("Aborted command, continuing (r)") != string::npos) && (device->ignore_nak == true)) {
					//ok
				} else {
					hasextraerror = true;
				}
			}
			if (hasextraerror) {
				device->sg_writeread_stdout += "  Error: " + cmd + " returns some unknown error\n";
				device->sg_writeread_result = false;
			}
			pthread_mutex_unlock(&mutex);
			if (hasextraerror)
				return NULL;
		}

		//Do crc32 <sg_writeread_of_filename>
		pthread_mutex_lock(&mutex);
		cmd = "crc32 " + device->sg_writeread_of_filename;
		pthread_mutex_unlock(&mutex);
		if ((RunProcessGetExitCode(cmd, outlines, exitcode) == false) || (exitcode != 0) || (outlines.size() == 0)) {
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Error: " + cmd + " has error \n";
			device->sg_writeread_result = false;
			pthread_mutex_unlock(&mutex);
			return NULL;
		} else {
			pthread_mutex_lock(&mutex);
			device->sg_writeread_of_filename_crc = trim(outlines[0]);
			device->sg_writeread_stdout += "  Info: Output file crc = " + device->sg_writeread_of_filename_crc + "\n";
			pthread_mutex_unlock(&mutex);
		}

		//Remove <sg_writeread_of_filename>
		if (IsFileExist(outfilename) == true) {
			remove(outfilename.c_str());
			pthread_mutex_lock(&mutex);
			device->sg_writeread_stdout += "  Info: " + device->sg_writeread_of_filename + " removed\n";
			pthread_mutex_unlock(&mutex);
		}

		//Compare crc32
		pthread_mutex_lock(&mutex);
		if (device->sg_writeread_if_filename_crc == device->sg_writeread_of_filename_crc) {
			device->sg_writeread_stdout += "  Info: CRC matches\n";
			device->sg_writeread_result = true;
		} else {
			device->sg_writeread_stdout += "  Error: CRC mismatch\n";
			device->sg_writeread_result = false;
		}
		pthread_mutex_unlock(&mutex);

		//cout << device->sg_writeread_stdout << endl << flush;

		return NULL;
	}
}

bool GetIntegerValue(string value, int& ret) {
	ret = 0;
	string s = value;
	for (int i = 0; i < s.length(); i++)
		s[i] = tolower(s[i]);
	//cout << "s = " << s << endl;
	int multiplier = 1;
	if (s[s.length() - 1] == 'k') {
		s = s.substr(0, s.length() - 1);
		multiplier = 1024;
	} else if (s[s.length() - 1] == 'm') {
		s = s.substr(0, s.length() - 1);
		multiplier = 1024 * 1024;
	} else if (s[s.length() - 1] == 'g') {
		s = s.substr(0, s.length() - 1);
		multiplier = 1024 * 1024 * 1024;
	}
	ret = atoi(s.c_str());
	ret = ret * multiplier;
	return true;
}

bool GetLongValue(string value, long& ret) {
	ret = 0;
	string s = value;
	for (int i = 0; i < s.length(); i++)
		s[i] = tolower(s[i]);
	//cout << "s = " << s << endl;
	long multiplier = 1;
	if (s[s.length() - 1] == 'k') {
		s = s.substr(0, s.length() - 1);
		multiplier = 1024;
	} else if (s[s.length() - 1] == 'm') {
		s = s.substr(0, s.length() - 1);
		multiplier = 1024 * 1024;
	} else if (s[s.length() - 1] == 'g') {
		s = s.substr(0, s.length() - 1);
		multiplier = 1024 * 1024 * 1024;
	}
	ret = atol(s.c_str());
	ret = ret * multiplier;
	return true;
}

string GenerateRandomMd5() {
	uuid_t uuid;
	char str[64];
	uuid_generate(uuid);
	uuid_unparse(uuid, str);
	//cout << str << endl;
	return ComputeMD5(string(str));
}

string ComputeMD5(string str) {
	MD5_CTX ctx;
	MD5_Init(&ctx);
	MD5_Update(&ctx, str.c_str(), str.length());
	unsigned char digest[16];
	MD5_Final(digest, &ctx);
	char md5string[33];
	for (int i = 0; i < 34; ++i)
		md5string[i] = 0;
	for (int i = 0; i < 16; ++i)
		sprintf(&md5string[i * 2], "%02x", (unsigned int) digest[i]);
	return string(md5string);
}

bool DoCommand(string commandstring) {
	for (int device_index = 0; device_index < Devices.size(); device_index++) {
		DeviceInfo device = Devices[device_index];
		if (device.enabled == true) {
			string cmd = commandstring;
			while (cmd.find("{}") != string::npos)
				cmd.replace(cmd.find("{}"), 2, device.sg_device_file);
			while (cmd.find("[]") != string::npos)
				cmd.replace(cmd.find("[]"), 2, device.block_device_file);
			//cout << "cmd = " << cmd << endl;

			WriteConsoleLine("Execute " + cmd);
			vector < string > outlines = vector<string> ();
			int exitcode;
			if (RunProcessGetExitCode(cmd, outlines, exitcode) == false) {
				WriteConsoleLine("  Error: Failed to execute " + cmd);
				return false;
			}
			WriteConsoleLine("  Info: Return code is " + ToString(exitcode));
			for (int tmpi = 0; tmpi < outlines.size(); tmpi++)
				WriteConsoleLine("    " + outlines[tmpi]);
		}
	}
	return true;
}

bool RunProcessGetExitCode(string command, vector<string>& outlines, int& exitcode) {
	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  *** Run \"" + command + "\"");
		// pthread_mutex_unlock(&mutex);
	// }
	exitcode = -1;
	outlines.clear();
	string fullcommand = command + " 2>&1";
	FILE *read_fp;
	char buffer[256];
	int chars_read;
	memset(buffer, '\0', sizeof(buffer));
	read_fp = popen(fullcommand.c_str(), "re");
	if (read_fp == NULL)
		return false;
	string outline;
	while (fgets(buffer, sizeof(buffer), read_fp) != NULL) {
		outline += string(buffer);
	}
	exitcode = pclose(read_fp);
	//cout << "exit code = " << exitcode << endl;
	//cout << outline;
	istringstream iss(outline);
	string s;
	while (getline(iss, s)) {
		outlines.push_back(s);
		//cout << "[" << s << "]" << endl;
	}
	// if (verbose) {
		// pthread_mutex_lock(&mutex);
		// WriteConsoleLine("  @@@ Completed \"" + command + "\"");
		// pthread_mutex_unlock(&mutex);
	// }
	return true;
}

void Syntax() {
	////////////////("--------------------------------------------------------------------------------")
	WriteConsoleLine("Syntax: -");
	WriteConsoleLine("[limiting options] -devicecount <#> -action <info/testspeed/writeread/exec> ");
	WriteConsoleLine("[action options] [-log <logfilename>]");
	WriteConsoleLine("");
	WriteConsoleLine("Limiting options: -");
	WriteConsoleLine("    -pciid <####:####>      -> limit to this vendor id:device id");
	WriteConsoleLine("    -pcipath <####:##:##.#> -> limit to this domain:bus:device.function");
	WriteConsoleLine("    -usbpath <#:#:#.#>      -> limit to this scsi usb path");
	WriteConsoleLine("    -scsipath <#:#:#:#>     -> limit to this scsi path");
	WriteConsoleLine("    -host <#>               -> limit to this host#");
	WriteConsoleLine("    -bus <#>                -> limit to this bus#");
	WriteConsoleLine("    -scsi <#>               -> limit to this scsi id#");
	WriteConsoleLine("    -lun <#>                -> limit to this lun#");
	WriteConsoleLine("    -type <#>               -> limit to this type");
	WriteConsoleLine("    -drive <x-y>            -> limit to drive x to y, 0 base");
	WriteConsoleLine("info action options: -");
	WriteConsoleLine("    -vendor <#>             -> check device vendor description");
	WriteConsoleLine("    -product <#>            -> check device product description");
	WriteConsoleLine("    -revision <#>           -> check device revision description");
	WriteConsoleLine("    -sn <#>                 -> check device serial number description");
	WriteConsoleLine("    -size <#>               -> check device size in bytes");
	WriteConsoleLine("    -smart <#>              -> check device SMART status");
	WriteConsoleLine("testspeed action options: -");
	WriteConsoleLine("    -count <#>              -> number of block, default = 100k");
	WriteConsoleLine("    -bpt <#>                -> block per transfer, default = 512");
	WriteConsoleLine("    -speed                  -> minimum speed in MB/sec");
	WriteConsoleLine("    -retries <#>            -> number of reries, default = 2");
	WriteConsoleLine("writeread action options: -");
	WriteConsoleLine("    -count <#>              -> number of block, default = 100k");
	WriteConsoleLine("    -offset <#>             -> number of block to skip, default = 0");
	WriteConsoleLine("    -nosync                 -> do not include sync=1 argument");
	WriteConsoleLine("    -directory              -> specify directory for temp files");
	WriteConsoleLine("    -clear                  -> clear directory before start write-read");
	WriteConsoleLine("    -force                  -> do not check partition before writing");
	WriteConsoleLine("    -ignorenak              -> ignore nak error");
	WriteConsoleLine("exec action options: -");
	WriteConsoleLine("    -command \"<commands {}>\" -> {} will be replaced with the /dev/sg#");
	WriteConsoleLine("    -command \"<commands []>\" -> [] will be replaced with the /dev/sd#");
}

void WriteConsole(string value) {
	cout << value << flush;
	if (logsw.is_open())
		logsw << value;
}

void WriteConsoleLine(string value) {
	cout << value << endl << flush;
	if (logsw.is_open())
		logsw << value << endl;
}

string GetExecutableDirectory() {
	char buff[1024];
	ssize_t len = readlink("/proc/self/exe", buff, sizeof(buff) - 1);
	if (len != -1) {
		buff[len] = '\0';
		return string(buff);
	} else {
		cout << "!!! readlink /proc/self/exe failed" << endl;
		return string("");
	}
}

string& trim_right_inplace(string& s, const string& delimiters = " \f\n\r\t\v") {
	return s.erase(s.find_last_not_of(delimiters) + 1);
}

string& trim_left_inplace(string& s, const string& delimiters = " \f\n\r\t\v") {
	return s.erase(0, s.find_first_not_of(delimiters));
}

string& trim(string& s, const string& delimiters = " \f\n\r\t\v") {
	return trim_left_inplace(trim_right_inplace(s, delimiters), delimiters);
}

string& trim(string& s) {
	const string delimiters = " \f\n\r\t\v";
	return trim_left_inplace(trim_right_inplace(s, delimiters), delimiters);
}

bool IsDirectoryExist(string pathname) {
	struct stat sb;
	return (stat(pathname.c_str(), &sb) == 0 && S_ISDIR(sb.st_mode));
}

bool IsFileExist(string pathname) {
	struct stat sb;
	return (stat(pathname.c_str(), &sb) == 0 && S_ISREG(sb.st_mode));
}

bool GetFilesInDirectory(string pathname, vector<string>& filenames) {
	DIR *dp;
	struct dirent *dirp;
	if ((dp = opendir(pathname.c_str())) == NULL)
		return false;
	while ((dirp = readdir(dp)) != NULL) {
		struct stat sb;
		string fullpathname = pathname + string(dirp->d_name);
		if ((stat(fullpathname.c_str(), &sb) == 0) && (!S_ISDIR(sb.st_mode))) {
			//cout << dirp->d_name << endl;
			filenames.push_back(string(dirp->d_name));
		}
	}
	closedir(dp);
	return true;
}

vector<string> SplitStringByDelimiter(string line, char delimiter) {
	istringstream iss(line);
	string s;
	vector < string > ss = vector<string> ();
	while (getline(iss, s, delimiter)) {
		if (s.length() > 0) {
			ss.push_back(s);
			//cout << "[" << s << "]" << endl;
		}
	}
	return ss;
}

bool FindStringInVector(string value, vector<string>& strings) {
	for (int i = 0; i < strings.size(); i++)
		if (value == strings[i])
			return true;
	return false;
}

string ToString(int value) {
	ostringstream convert;
	convert << value;
	return convert.str();
}

class comma_numpunct: public std::numpunct<char> {
protected:
	virtual char do_thousands_sep() const {
		return ',';
	}

	virtual std::string do_grouping() const {
		return "\03";
	}
};

string ToStringWithComma(int value) {
	stringstream ss;
	locale comma_locale(locale(), new comma_numpunct());
	ss.imbue(locale(comma_locale));
	ss << fixed << value;
	//cout << ss.str() << endl;
	return ss.str();
}

bool IsMD5Filename(string filename) {
	if (filename.length() != 32)
		return false;
	for (int i = 0; i < 32; i++) {
		if ((isdigit(filename[i]) == true) || (filename[i] == 'a') || (filename[i] == 'b') || (filename[i] == 'c') || (filename[i] == 'd') || (filename[i] == 'e') || (filename[i] == 'f')) {
			continue;
		} else {
			return false;
		}
	}
	return true;
}
