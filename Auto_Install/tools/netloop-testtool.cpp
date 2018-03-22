//Compile with "g++ netloop-testtool.cpp -luuid -lssl -lpthread"
//Dependencies: -
//  ping
//  iperf
//  ifconfig
//  ethtool
//  iptables
//  ip
//  ftp
//  crc32
//  sh

#ifdef __linux__
#       define _REENTRANT
#       define _POSIX_SOURCE
#endif

#ifdef __linux__
#       define _P __P
#endif

#include <stdio.h>
#include <termios.h>
#include <fcntl.h>
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
#include <arpa/inet.h>
#include <pthread.h>
#include <signal.h>
#include <unistd.h>

using namespace std;

struct ifconfig_Output_Info
{
  string DeviceName;
  string Bus;
  string BusN;
  string LinkEncap;
  string HWaddr;
  string InetAddr;
  string Bcast;
  string Mask;
  string State;
  string MTU;
  string RXPackets;
  string RxErrors;
  string RxDropped;
  string RxOverruns;
  string RxFrames;
  string TXPackets;
  string TxErrors;
  string TxDropped;
  string TxOverruns;
  string TxCarrier;
  string Collisions;
  string TxQueueLen;
  string RxBytes;
  string TxBytes;
};

bool FindIPMacAddress(string& name, string& macaddress);
bool FindPCIAddress(string& name, string& pciaddress);
bool FindDevice(string& d1, string& d2, ifconfig_Output_Info& startup_d1_ifconfig, ifconfig_Output_Info& startup_d2_ifconfig, bool showdevices);
bool Get_ifconfig_infos(vector<string>& values, vector<ifconfig_Output_Info>& infos);
bool Get_ifconfig_info(vector<string>& values, ifconfig_Output_Info& info);
bool ParseFirstLine(string line, string& DeviceName, string& LinkEncap, string& HWaddr);
bool Parse_inet_addr_Line(string line, string& InetAddr, string& Bcast, string& Mask);
bool Parse_MTU_Line(string line, string& State, string& MTU);
bool Parse_Rx_Packets_Line(string line, string& RXPackets, string& Errors, string& Dropped, string& Overruns, string& Frame);
bool Parse_Tx_Packets_Line(string line, string& TXPackets, string& Errors, string& Dropped, string& Overruns, string& Carrier);
bool Parse_collision_txqueuelen_Line(string line, string& collision, string& txqueuelen);
bool Parse_RX_bytes_TX_bytes_Line(string line, string& rxbytes, string& txbytes);
string GetFormatedSubString(string s, string leading);

bool CreateNatMapping(string d1, string d2, string mtu, string physicalip1, string physicalip2, string virtualip1, string virtualip2, string macaddress1, string macaddress2);
bool RemoveNatMapping(string d1, string d2, string physicalip1, string physicalip2, string virtualip1, string virtualip2, string macaddress1, string macaddress2);

bool RunPing(string sourceip, string targetip);

bool RunLEDs(string physicalip1, string physicalip2, string virtualip1, string virtualip2);
int kbhit(void);


void *iperfServerThread(void *arg);
bool RunIperf(string physicalip1, string physicalip2, string virtualip1, string virtualip2, string runtime, double speed, string dual);

bool CalculateStatistic(ifconfig_Output_Info startup_ifconfig, ifconfig_Output_Info current_ifconfig, long& accumrxpackets, long& accumrxtotalerrors,  long& accumtxpackets, long& accumtxtotalerrors);

bool RunProcessGetExitCode(string command, vector<string>& outlines, int& exitcode);
bool RunProcessGetExitCodePrint(string command, vector<string>& outlines, int& exitcode);
bool RunProcessGetExitCodeDirectPrint(string command, int& exitcode);

string& trim(string& s);
string ToString(int value);
string ToStringWithComma(int value);

bool IsDirectoryExist(string pathname);
bool IsFileExist(string pathname);

string GetExecutableDirectory();
void WriteConsole(string value);
void WriteConsoleLine(string value);
void Syntax();

bool GetLongValue(string value, long& ret);

bool CreateLocalRandomFile(string param_tmpdirectory, long size, string& filename, string& local_filename_fullpath, string& crc32);
string GenerateRandomMd5();
string ComputeMD5(string str);
bool GetCrc32(string filename, string& crc32);

bool FtpDeleteRemoteFile(string param_remoteip, string param_remoteuser, string param_remotepassword, string param_remotedirectory, string filename);
bool FtpLocalFileToRemote(string param_remoteip, string param_remoteuser, string param_remotepassword, string param_remotedirectory, 
                          string param_localdirectory, string local_filename, string remote_filename);
bool FtpRemoteFileToLocal(string param_remoteip, string param_remoteuser, string param_remotepassword, string param_remotedirectory, 
                          string param_localdirectory, string local_filename, string remote_filename);

string workingdirectory;
ofstream logsw;
bool verboseftp = false;

int main(int argc, char *argv[])
{
  if(argc == 1)
  {
    Syntax();
    return 1;
  }
  
  workingdirectory = GetExecutableDirectory();
  workingdirectory = workingdirectory.substr(0, workingdirectory.rfind("/") + 1);
  
  string param_physicalip1 = "10.50.0.1";
  string param_physicalip2 = "10.50.1.1";
  string param_virtualip1 = "10.60.0.1";
  string param_virtualip2 = "10.60.1.1";
  
  string param_d1;
  string param_d2;
  
  string param_mtu;
  
  string param_iperfspeed;
  double min_iperfspeed = 0;
  string param_iperftime = "10";
  string param_iperfdual;

  string param_tmpdirectory = "/tmp/";

  string param_ftpdirectory = "/tmp/";
  string param_ftpuser;
  string param_ftppassword;
  string param_ftpsize;
  
  string param_leds;
  
  string param_maxerror;
  string param_loopcount;
  string param_runtime;

  string logfilename;

  long ftpsize = 100 * 1024;
  int ftploop = 1;
  long maxerror = 1;
  int loopcount = 1;
  long runtime = 0;

  bool testhasrun = false;

  int i = 1;
  while(i < argc)
  {
    //-log
    if(string(argv[i]) == "-log")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      if(string(argv[i]).find("/") != string::npos)
        logfilename = string(argv[i]);
      else
        logfilename = workingdirectory + argv[i];
      //cout << "log filename = " << logfilename << endl;
    }
    //-d1
    else if(string(argv[i]) == "-d1")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_d1= string(argv[i]);
    }
    //-d2
    else if(string(argv[i]) == "-d2")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_d2 = string(argv[i]);
    }
    //-mtu
    else if(string(argv[i]) == "-mtu")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_mtu = string(argv[i]);
    }
    //-iperfspeed
    else if(string(argv[i]) == "-iperfspeed")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_iperfspeed = string(argv[i]);
    }
    //-iperftime
    else if(string(argv[i]) == "-iperftime")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_iperftime = string(argv[i]);
    }
    //-iperdual
    else if(string(argv[i]) == "-iperfdual")
    {
      param_iperfdual = " -d";
    }

    //-tmpdirectory
    else if(string(argv[i]) == "-tmpdirectory")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_tmpdirectory = string(argv[i]);
      if(param_tmpdirectory[param_tmpdirectory.length() - 1] != '/')
        param_tmpdirectory = param_tmpdirectory + "/";
    }

    //-ftpdirectory
    else if(string(argv[i]) == "-ftpdirectory")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_ftpdirectory = string(argv[i]);
      if(param_ftpdirectory[param_ftpdirectory.length() - 1] != '/')
        param_ftpdirectory = param_ftpdirectory + "/";
    }
    //-ftpuser
    else if(string(argv[i]) == "-ftpuser")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_ftpuser = string(argv[i]);
    }
    //-ftppassword
    else if(string(argv[i]) == "-ftppassword")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_ftppassword = string(argv[i]);
    }
    //-ftpsize
    else if(string(argv[i]) == "-ftpsize")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_ftpsize = string(argv[i]);
    }
    //-leds
    else if(string(argv[i]) == "-leds")
    {
      param_leds = string(argv[i]);
    }
    //-maxerror
    else if(string(argv[i]) == "-maxerror")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_maxerror = string(argv[i]);
      maxerror = strtol(argv[i], NULL, 0);
    }
    else if(string(argv[i]) == "-i0")
    {
      param_physicalip1 = "10.50.0.1";
      param_physicalip2 = "10.50.1.1";
      param_virtualip1 = "10.60.0.1";
      param_virtualip2 = "10.60.1.1";
    }
    else if(string(argv[i]) == "-i1")
    {
      param_physicalip1 = "10.51.0.1";
      param_physicalip2 = "10.51.1.1";
      param_virtualip1 = "10.61.0.1";
      param_virtualip2 = "10.61.1.1";
    }
    else if(string(argv[i]) == "-i2")
    {
      param_physicalip1 = "10.52.0.1";
      param_physicalip2 = "10.52.1.1";
      param_virtualip1 = "10.62.0.1";
      param_virtualip2 = "10.62.1.1";
    }
    else if(string(argv[i]) == "-i3")
    {
      param_physicalip1 = "10.53.0.1";
      param_physicalip2 = "10.53.1.1";
      param_virtualip1 = "10.63.0.1";
      param_virtualip2 = "10.63.1.1";
    }
    else if(string(argv[i]) == "-i4")
    {
      param_physicalip1 = "10.54.0.1";
      param_physicalip2 = "10.54.1.1";
      param_virtualip1 = "10.64.0.1";
      param_virtualip2 = "10.64.1.1";
    }
    else if(string(argv[i]) == "-i5")
    {
      param_physicalip1 = "10.55.0.1";
      param_physicalip2 = "10.55.1.1";
      param_virtualip1 = "10.65.0.1";
      param_virtualip2 = "10.65.1.1";
    }
    else if(string(argv[i]) == "-i6")
    {
      param_physicalip1 = "10.56.0.1";
      param_physicalip2 = "10.56.1.1";
      param_virtualip1 = "10.66.0.1";
      param_virtualip2 = "10.66.1.1";
    }
    else if(string(argv[i]) == "-i7")
    {
      param_physicalip1 = "10.57.0.1";
      param_physicalip2 = "10.57.1.1";
      param_virtualip1 = "10.67.0.1";
      param_virtualip2 = "10.67.1.1";
    }
    else if(string(argv[i]) == "-i8")
    {
      param_physicalip1 = "10.58.0.1";
      param_physicalip2 = "10.58.1.1";
      param_virtualip1 = "10.68.0.1";
      param_virtualip2 = "10.68.1.1";
    }
    else if(string(argv[i]) == "-i9")
    {
      param_physicalip1 = "10.59.0.1";
      param_physicalip2 = "10.59.1.1";
      param_virtualip1 = "10.69.0.1";
      param_virtualip2 = "10.69.1.1";
    }

    /*
    //-loopcount
    else if(string(argv[i]) == "-loopcount")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_loopcount = string(argv[i]);
    }
    //-runtime
    else if(string(argv[i]) == "-runtime")
    {
      i += 1;
      if(i == argc)
      {
        Syntax();
        return 1;
      }
      param_runtime = string(argv[i]);
    }
    */
    //-v
    else if(string(argv[i]) == "-v")
    {
      verboseftp = true;
    }
    //-?
    else if(string(argv[i]) == "-?")
    {
      Syntax();
      return 1;
    }
    else
    {
      WriteConsoleLine("Error: Invalid argument " + string(argv[i]));
      return 1;
    }
   
    i += 1;
  }

  //Create log file stream
  if(logfilename.length() > 0)
    logsw.open(logfilename.c_str(), ios::out);

  //Show header
  WriteConsoleLine("network test tool");
  WriteConsoleLine("Version 1.4 Copyright Flextronics Penang");
  WriteConsoleLine("");
  
  //Check valid param_d1 & param_d2
  if(param_d1.length() == 0)
  {
    WriteConsoleLine("Error: No device #1 specified");
    return 1;
  }
  if(param_d2.length() == 0)
  {
    WriteConsoleLine("Error: No device #2 specified");
    return 1;
  }
  
  if(param_iperfspeed.size() > 0)
  {
    min_iperfspeed = atof(param_iperfspeed.c_str());
    if(min_iperfspeed == 0)
    {
      WriteConsoleLine("Error: Invalid iperf speed specified");
      return 1;
    }
  }

  if(param_ftpsize.size() > 0)
  {
    //Check valid tmp directory
    if((param_tmpdirectory.length() == 0) || (IsDirectoryExist(param_tmpdirectory) == false))
    {
      WriteConsoleLine("Error: Invalid tmp directory specified");
      return 1;
    }

    //Check valid user & password
    if(param_ftpuser.length() == 0)
    {
      WriteConsoleLine("Error: No ftp username specified");
      return 1;
    }
    if(param_ftppassword.length() == 0)
    {
      WriteConsoleLine("Error: No ftp password specified");
      return 1;
    }
  
    //Check valid size
    if(param_ftpsize.length() == 0)
    {
      WriteConsoleLine("Error: No ftp file size specified");
      return 1;
    }
    else if(GetLongValue(param_ftpsize, ftpsize) == false)
    {
      WriteConsoleLine("Error: Invalid file size specified");
      return 1;
    }
    //cout << "size = " << size << endl;
  }

  //------------------------------------------------------------------
  //2. Find local device, determine current packet count & dropped count
  //------------------------------------------------------------------
  ifconfig_Output_Info startup_d1_ifconfig;
  ifconfig_Output_Info startup_d2_ifconfig;
  if(FindDevice(param_d1, param_d2, startup_d1_ifconfig, startup_d2_ifconfig, true) == false)
    return 1;
  
  //------------------------------------------------------------------
  //3. Create nat mapping
  //------------------------------------------------------------------
  if(CreateNatMapping(param_d1, param_d2, param_mtu, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                   startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr) == false)
  {
    return 1;
  }
  else
  {
    bool pingresult = false;
    int pingcount = 0;
    WriteConsoleLine("Action: Run ping");
    while((pingresult == false) && (pingcount < 10))
    {
      sleep(1);
      if(RunPing(param_physicalip1, param_virtualip2) == true)
      {
        pingresult = true;
        break;
      }
      else
      {
        pingcount += 1;
      }
    }
    if(pingresult == false)
    {
      WriteConsoleLine("Error: Ping with 100% packet loss");
      RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                       startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
      return 1;
    }
  }
  //Run ifconfig again to get current statictic
  if(FindDevice(param_d1, param_d2, startup_d1_ifconfig, startup_d2_ifconfig, false) == false)
    return 1;

  //------------------------------------------------------------------
  //4. Test with iperf
  //------------------------------------------------------------------
  if(param_iperfspeed.size() > 0)
  {
    bool iperfresult = false;
    int iperfcount = 0;
    while((iperfresult == false) && (iperfcount < 5))
    {
      if(RunIperf(param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, param_iperftime, min_iperfspeed, param_iperfdual) == true)
      {
        iperfresult = true;
        break;
      }
      else
      {
        RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                         startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
        CreateNatMapping(param_d1, param_d2, param_mtu, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                   startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
        bool pingresult = false;
        int pingcount = 0;
        WriteConsoleLine("Action: Run ping");
        while((pingresult == false) && (pingcount < 10))
        {
          sleep(1);
          if(RunPing(param_physicalip1, param_virtualip2) == true)
          {
            pingresult = true;
            break;
          }
          else
          {
            pingcount += 1;
          }
        }
        if(pingresult == false)
        {
          WriteConsoleLine("Error: Ping with 100% packet loss");
          RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                           startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
          return 1;
        }
        iperfcount += 1;
      }
    }
    if(iperfresult == false)
    {
      RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                       startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
      return 1;
    }
    testhasrun = true;
  }

  //------------------------------------------------------------------
  //5. Test ftp
  //------------------------------------------------------------------
  if(param_ftpsize.size() > 0)
  {
    //------------------------------------------------------------------
    //5.1. Create local random file, get crc32
    //------------------------------------------------------------------
    string local_filename = GenerateRandomMd5();
    string local_filename_fullpath;
    string remote_filename= GenerateRandomMd5();
    string crc32;
    if(CreateLocalRandomFile(param_tmpdirectory, ftpsize, local_filename, local_filename_fullpath, crc32) == false)
    {
      WriteConsoleLine("Error: Failed to create random file");
      RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                       startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
      return 1;
    }
    WriteConsoleLine("Info: crc32 = " + crc32);

    //------------------------------------------------------------------
    //5.2. Delete remote file, ftp file to remote
    //------------------------------------------------------------------
    if(FtpDeleteRemoteFile(param_virtualip2, param_ftpuser, param_ftppassword, param_ftpdirectory, remote_filename) == false)
    {
      //WriteConsoleLine("Action: Remove " + local_filename_fullpath);
      remove(local_filename_fullpath.c_str());
      RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                       startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
      return 1;
    }
    
    int loopcount = 0;
    bool ftphasfailed = false;
    while((loopcount < ftploop) && (ftphasfailed == false))
    {
      if(FtpLocalFileToRemote(param_virtualip2, param_ftpuser, param_ftppassword, param_ftpdirectory, 
                              param_tmpdirectory, local_filename, remote_filename) == false)
      {
        //WriteConsoleLine("Action: Remove " + local_filename_fullpath);
        remove(local_filename_fullpath.c_str());
        RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                         startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
        return 1;
      }
    
      //------------------------------------------------------------------
      //5.3. Delete local file, ftp remote file to local, remove remote file
      //------------------------------------------------------------------
      WriteConsoleLine("Action: Remove " + local_filename_fullpath);
      remove(local_filename_fullpath.c_str());
      if(FtpRemoteFileToLocal(param_virtualip2, param_ftpuser, param_ftppassword, param_ftpdirectory, 
                              param_tmpdirectory, local_filename, remote_filename) == false)
      {
        FtpDeleteRemoteFile(param_virtualip2, param_ftpuser, param_ftppassword, param_ftpdirectory, remote_filename);
        RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                         startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
        return 1;
      }
      if(FtpDeleteRemoteFile(param_virtualip2, param_ftpuser, param_ftppassword, param_ftpdirectory, remote_filename) == false)
      {
        RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                         startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
        return 1;
      }
      
      //------------------------------------------------------------------
      //5.4. get crc32 of copied file, compare to original crc32
      //------------------------------------------------------------------
      string tempcrc32;
      if(GetCrc32(local_filename_fullpath, tempcrc32) == false)
      {
        WriteConsoleLine("Error: Failed to get crc32 value");
        //WriteConsoleLine("Action: Remove " + local_filename_fullpath);
        remove(local_filename_fullpath.c_str());
        RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                         startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
        return 1;
      }
      WriteConsoleLine("Info: crc32 = " + tempcrc32);
      if(tempcrc32 != crc32)
      {
        WriteConsoleLine("Error: Failed crc32 check");
        //WriteConsoleLine("Action: Remove " + local_filename_fullpath);
        remove(local_filename_fullpath.c_str());
        RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                         startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
        return 1;
      }

      loopcount += 1;
    }

    //WriteConsoleLine("Action: Remove " + local_filename_fullpath);
    remove(local_filename_fullpath.c_str());
    WriteConsoleLine("Info: crc32 matches");

    testhasrun = true;  
  }
  
  //------------------------------------------------------------------
  //6. LEDs
  //------------------------------------------------------------------
  if(param_leds.size() > 0)
  {
    RunLEDs(param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2);
  }

      //system(("ifconfig " + startup_d1_ifconfig.DeviceName).c_str());
      //system(("ethtool " + startup_d1_ifconfig.DeviceName).c_str());
      //system(("ifconfig " + startup_d2_ifconfig.DeviceName).c_str());
      //system(("ethtool " + startup_d2_ifconfig.DeviceName).c_str());

  //------------------------------------------------------------------
  //7. Determine current packet count & dropped count
  //------------------------------------------------------------------
  ifconfig_Output_Info current_d1_ifconfig;
  ifconfig_Output_Info current_d2_ifconfig;
  if(FindDevice(param_d1, param_d2, current_d1_ifconfig, current_d2_ifconfig, false) == false)
  {
    RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                     startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);
    return 1;
  }
  
  //------------------------------------------------------------------
  //8. Remove nat mapping
  //------------------------------------------------------------------
  RemoveNatMapping(param_d1, param_d2, param_physicalip1, param_physicalip2, param_virtualip1, param_virtualip2, 
                   startup_d1_ifconfig.HWaddr, startup_d2_ifconfig.HWaddr);

  //------------------------------------------------------------------
  //9. Check statistic
  //------------------------------------------------------------------
  //Check d1 statistic
  long d1_TXPackets = 0;
  long d1_RXPackets = 0;
  long d1_TXTotalErrors = 0;
  long d1_RXTotalErrors = 0;

  if(CalculateStatistic(startup_d1_ifconfig, current_d1_ifconfig, 
                        d1_RXPackets, d1_RXTotalErrors, d1_TXPackets, d1_TXTotalErrors) == false)
    return 1;
  if((d1_TXPackets == 0) || (d1_RXPackets == 0))
  {
      WriteConsoleLine("Error: Insufficient packets transmitted or received in device #1");
      WriteConsoleLine("  Packets transmitted = " + ToStringWithComma(d1_TXPackets));
      WriteConsoleLine("  Packets received = " + ToStringWithComma(d1_RXPackets));
      return 1;
  }

  //Check d2 statistic
  long d2_TXPackets = 0;
  long d2_RXPackets = 0;
  long d2_TXTotalErrors = 0;
  long d2_RXTotalErrors = 0;

  if(CalculateStatistic(startup_d2_ifconfig, current_d2_ifconfig, 
                        d2_RXPackets, d2_RXTotalErrors, d2_TXPackets, d2_TXTotalErrors) == false)
    return 1;
  if((d2_TXPackets == 0) || (d2_RXPackets == 0))
  {
      WriteConsoleLine("Error: Insufficient packets transmitted or received in device #2");
      WriteConsoleLine("  Packets transmitted = " + ToStringWithComma(d2_TXPackets));
      WriteConsoleLine("  Packets received = " + ToStringWithComma(d2_RXPackets));
      return 1;
  }

  if(param_maxerror.size() > 0)
  {
    string msg = "";
    msg += "Info: " + startup_d1_ifconfig.DeviceName + ": TX = " + ToStringWithComma(d1_TXPackets);
    msg += ", TX error = " + ToStringWithComma(d1_TXTotalErrors);
    msg += " packets. RX = " + ToStringWithComma(d1_RXPackets);
    msg += ", RX error = " + ToStringWithComma(d1_RXTotalErrors);
    msg += " packets";
    WriteConsoleLine(msg);

    msg = "";
    msg += "Info: " + startup_d2_ifconfig.DeviceName + ": TX = " + ToStringWithComma(d2_TXPackets);
    msg += ", TX error = " + ToStringWithComma(d2_TXTotalErrors);
    msg += " packets. RX = " + ToStringWithComma(d2_RXPackets);
    msg += ", RX error = " + ToStringWithComma(d2_RXTotalErrors);
    msg += " packets";
    WriteConsoleLine(msg);

    if(d1_TXTotalErrors > maxerror)
    {
        WriteConsoleLine("Error:Device #1 TX error rate exceeded limit");
        WriteConsoleLine("  Total TX errors = " + ToStringWithComma(d1_TXTotalErrors));
        return 1;
    }
    if(d1_RXTotalErrors > maxerror)
    {
        WriteConsoleLine("Error:Device #1 RX error rate exceeded limit");
        WriteConsoleLine("  Total RX errors = " + ToStringWithComma(d1_RXTotalErrors));
        return 1;
    }
    if(d2_TXTotalErrors > maxerror)
    {
        WriteConsoleLine("Error:Device #2 TX error rate exceeded limit");
        WriteConsoleLine("  Total TX errors = " + ToStringWithComma(d2_TXTotalErrors));
        return 1;
    }
    if(d2_RXTotalErrors > maxerror)
    {
        WriteConsoleLine("Error:Device #2 RX error rate exceeded limit");
        WriteConsoleLine("  Total RX errors = " + ToStringWithComma(d2_RXTotalErrors));
        return 1;
    }
  }
  
  if(testhasrun == true)
  {
    WriteConsoleLine("");
    WriteConsoleLine("******************");
    WriteConsoleLine("*** All Passed ***");
    WriteConsoleLine("******************");
    return 0;
  }
  else
  {
    return 1;
  }
}

string GetExecutableDirectory()
{
  char buff[1024];
  ssize_t len = readlink("/proc/self/exe", buff, sizeof(buff) - 1);
  if (len != -1) 
  {
    buff[len] = '\0';
    return string(buff);
  }
  else
  {
    cout << "!!! readlink /proc/self/exe failed" << endl;
    return string("");
  }
}

void WriteConsole(string value)
{
  cout << value << flush;
  if(logsw.is_open())
    logsw << value;
}

void WriteConsoleLine(string value)
{
  cout << value << endl << flush;
  if(logsw.is_open())
    logsw << value << endl;
}

void Syntax()
{
  ////////////////("--------------------------------------------------------------------------------")
  WriteConsoleLine("Syntax: -");
  WriteConsoleLine("  -d1 <device identifier for device #1>");
  WriteConsoleLine("  -d2 <device identifier for device #2>");
  WriteConsoleLine("Device identifier can be one of the following: -");
  WriteConsoleLine("  Device name from ifconfig -a output, example eth0, eth1");
  WriteConsoleLine("  Mac address from ifconfig -a output, example 00:11:22:AA:BB:CC");
  WriteConsoleLine("  Bus number from ethtool -i output, example 0000:1c:01.0");
  WriteConsoleLine("  Bus number from ethtool -i output with 0-base #, example 0000:1c:01.0/0");
  WriteConsoleLine("  -mtu <mtu size>");
  WriteConsoleLine("iperf test option: -");
  WriteConsoleLine("  -iperfspeed <speed in Mbits/sec>");
  WriteConsoleLine("  -iperftime <time in seconds, default is 10 seconds>");
  WriteConsoleLine("  -iperfdual");
  WriteConsoleLine("ftp test option: -");
  WriteConsoleLine("  -tmpdirectory <tmp directory>");
  WriteConsoleLine("  -ftpdirectory <ftp directory>");
  WriteConsoleLine("  -ftpuser <ftp username>");
  WriteConsoleLine("  -ftppassword <ftp password>");
  WriteConsoleLine("  -ftpsize <ftp test file size in k, M, G>");
  WriteConsoleLine("    Note: Add \"pasv_promiscuous=YES\" & \"port_promiscuous=YES\"");
  WriteConsoleLine("          to /etc/vsftp/vsftp.conf");
  WriteConsoleLine("Additional checking option: -");
  WriteConsoleLine("  -maxerror <maximum allowed errors>");
  WriteConsoleLine("Turn on LEDs option: -");
  WriteConsoleLine("  -leds");
  WriteConsoleLine("Use alternate IP addresses option: -");
  WriteConsoleLine("  -i0 use 10.50.0.1, 10.50.1.1, 10.60.0.1, 10.60.1.1 IP addresses (default)");
  WriteConsoleLine("  -i1 use 10.51.0.1, 10.51.1.1, 10.61.0.1, 10.61.1.1 IP addresses");
  WriteConsoleLine("  -i2 use 10.52.0.1, 10.52.1.1, 10.62.0.1, 10.62.1.1 IP addresses");
  WriteConsoleLine("  -i3 use 10.53.0.1, 10.53.1.1, 10.63.0.1, 10.63.1.1 IP addresses");
  WriteConsoleLine("  -i4 use 10.54.0.1, 10.54.1.1, 10.64.0.1, 10.64.1.1 IP addresses");
  WriteConsoleLine("  -i5 use 10.55.0.1, 10.55.1.1, 10.65.0.1, 10.65.1.1 IP addresses");
  WriteConsoleLine("  -i6 use 10.56.0.1, 10.56.1.1, 10.66.0.1, 10.66.1.1 IP addresses");
  WriteConsoleLine("  -i7 use 10.57.0.1, 10.57.1.1, 10.67.0.1, 10.67.1.1 IP addresses");
  WriteConsoleLine("  -i8 use 10.58.0.1, 10.58.1.1, 10.68.0.1, 10.68.1.1 IP addresses");
  WriteConsoleLine("  -i9 use 10.59.0.1, 10.59.1.1, 10.69.0.1, 10.69.1.1 IP addresses");
}

bool RunPing(string sourceip, string targetip)
{
  string command = "ping -I " + sourceip + " -w 1 " + targetip;
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  vector<string> outlines = vector<string>();
  int exitcode;
  bool bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to start ping");
    return false;
  }
  for(int i = 0; i < outlines.size(); i++)
  {
    if(outlines[i].find("100% packet loss") != string::npos)
    {
      //WriteConsoleLine("Error: Ping with 100% packet loss");
      return false;
    }
  }
  return true;
}

void *iperfServerThread(void *arg)
{
  string *bindip = (string*) arg;
  string command = "iperf -B " + *bindip + " -s -f M -x CDMSV";
  WriteConsoleLine("Action: Run \"" + command + "\"");
  system(command.c_str());
  
}

bool RunLEDs(string physicalip1, string physicalip2, string virtualip1, string virtualip2)
{
  pthread_t iperf_server_thread;
  string bindip = physicalip2;
  pthread_create(&iperf_server_thread, NULL, iperfServerThread, &bindip);
  //cout << "iperf speed = " << min_iperfspeed << endl;
  sleep(1);
    
  string command = "iperf -B " + physicalip1 + " -c " + virtualip2 + " -t 1 -f m";
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  vector<string> outlines = vector<string>();
  int exitcode;
  while( ! kbhit())
  {
    bool bret = RunProcessGetExitCodePrint(command, outlines, exitcode);
  }
  pthread_cancel(iperf_server_thread);
  pthread_join(iperf_server_thread, NULL);

  return true;  
}

int kbhit(void)
{
  struct termios oldt, newt;
  int ch;
  int oldf;
 
  tcgetattr(STDIN_FILENO, &oldt);
  newt = oldt;
  newt.c_lflag &= ~(ICANON | ECHO);
  tcsetattr(STDIN_FILENO, TCSANOW, &newt);
  oldf = fcntl(STDIN_FILENO, F_GETFL, 0);
  fcntl(STDIN_FILENO, F_SETFL, oldf | O_NONBLOCK);
 
  ch = getchar();
 
  tcsetattr(STDIN_FILENO, TCSANOW, &oldt);
  fcntl(STDIN_FILENO, F_SETFL, oldf);
 
  if(ch != EOF)
  {
    ungetc(ch, stdin);
    return 1;
  }
 
  return 0;
}

bool RunIperf(string physicalip1, string physicalip2, string virtualip1, string virtualip2, string runtime, double speed, string dual)
{
  pthread_t iperf_server_thread;
  string bindip = physicalip2;
  pthread_create(&iperf_server_thread, NULL, iperfServerThread, &bindip);
  //cout << "iperf speed = " << min_iperfspeed << endl;
  sleep(1);
    
  string command = "iperf -B " + physicalip1 + " -c " + virtualip2 + " -t " + runtime + " -f m" + dual;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  vector<string> outlines = vector<string>();
  int exitcode;
  bool bret = RunProcessGetExitCodePrint(command, outlines, exitcode);
    
  pthread_cancel(iperf_server_thread);
  pthread_join(iperf_server_thread, NULL);

  string realspeedstring;
  for(int i = 0; i < outlines.size(); i++)
  {
    //WriteConsoleLine(outlines[i]);
    if(outlines[i].find("Mbits/sec") != string::npos)
      realspeedstring = outlines[i];
  }

  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }
    
  int index = realspeedstring.find("Mbits/sec");
  if(index == string::npos)
  {
    WriteConsoleLine("Error: Failed to get speed");
    return false;
  }

  index -= 1;
  while(realspeedstring[index] == 32)
    index -= 1;
  while(realspeedstring[index] != 32)
    index -= 1;
  index += 1;
  //cout << realspeedstring[index] << endl;
  realspeedstring = realspeedstring.substr(index);
  //cout << "[" << realspeedstring << "]" << endl;
  double realspeed = atof(realspeedstring.c_str());
  //cout << realspeed << endl;
  if(realspeed >= speed)
  {
    WriteConsoleLine("Info: iperf speed test passed");
    return true;
  }
  else
  {
    WriteConsoleLine("Error: iperf speed test failed");
    return false;
  }
}

bool CreateNatMapping(string d1,
                      string d2,
                      string mtu,
                      string physicalip1,
                      string physicalip2,
                      string virtualip1,
                      string virtualip2,
                      string macaddress1,
                      string macaddress2)
{
  WriteConsoleLine("Info: Setup NAT route");
  
  string command;
  if(mtu.size() == 0)
    command= "ifconfig " + d1 + " " + physicalip1 + "/24";
  else
    command= "ifconfig " + d1 + " " + physicalip1 + "/24 mtu " + mtu;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  vector<string> outlines = vector<string>();
  int exitcode;
  bool bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  if(mtu.size() == 0)
    command = "ifconfig " + d2 + " " + physicalip2 + "/24";
  else
    command = "ifconfig " + d2 + " " + physicalip2 + "/24 mtu " + mtu;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "iptables -t nat -A POSTROUTING -s " + physicalip1 + " -d " + virtualip2 + " -j SNAT --to-source " + virtualip1;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "iptables -t nat -A PREROUTING -d " + virtualip1 + " -j DNAT --to-destination " + physicalip1;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "iptables -t nat -A POSTROUTING -s " + physicalip2 + " -d " + virtualip1 + " -j SNAT --to-source " + virtualip2;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "iptables -t nat -A PREROUTING -d " + virtualip2 + " -j DNAT --to-destination " + physicalip2;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "ip route add " + virtualip2 + " dev " + d1;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  //command = "arp -i " + d1 + " -s " + virtualip2 + " " + macaddress2;
  command = "ip neigh add " + virtualip2 + " lladdr " + macaddress2 + " nud permanent dev " + d1;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "ip route add " + virtualip1 + " dev " + d2;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  //command = "arp -i " + d2 + " -s " + virtualip1 + " " + macaddress1;
  command = "ip neigh add " + virtualip1 + " lladdr " + macaddress1 + " nud permanent dev " + d2;
  WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  return true;
}

bool RemoveNatMapping(string d1,
                      string d2,
                      string physicalip1,
                      string physicalip2,
                      string virtualip1,
                      string virtualip2,
                      string macaddress1,
                      string macaddress2)
{
  WriteConsoleLine("Info: Clean up NAT route");
  
  //string command = "arp -i " + d2 + " -d " + virtualip1 ;
  string command = "ip neigh delete " + virtualip1 + " dev " + d2;
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  vector<string> outlines = vector<string>();
  int exitcode;
  bool bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }
  
  command = "ip route del " + virtualip1 + " dev " + d2;
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  //command = "arp -i " + d1 + " -d " + virtualip2;
  command = "ip neigh delete " + virtualip2 + " dev " + d1;
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "ip route del " + virtualip2 + " dev " + d1;
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "iptables -t nat -D PREROUTING -d " + virtualip2 + " -j DNAT --to-destination " + physicalip2;
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "iptables -t nat -D POSTROUTING -s " + physicalip2 + " -d " + virtualip1 + " -j SNAT --to-source " + virtualip2;
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "iptables -t nat -D PREROUTING -d " + virtualip1 + " -j DNAT --to-destination " + physicalip1;
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  command = "iptables -t nat -D POSTROUTING -s " + physicalip1 + " -d " + virtualip2 + " -j SNAT --to-source " + virtualip1;
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }
  
  command = "ifconfig " + d2 + " 0.0.0.0 0.0.0.0 down";
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }
  
  command = "ifconfig " + d1 + " 0.0.0.0 0.0.0.0 down";
  //WriteConsoleLine("Action: Run \"" + command + "\"");
  outlines.clear();
  bret = RunProcessGetExitCode(command, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute \"" + command + "\"");
    return false;
  }

  return true;
}

bool CalculateStatistic(ifconfig_Output_Info startup_ifconfig, ifconfig_Output_Info current_ifconfig,
                        long& accumrxpackets, long& accumrxtotalerrors, 
                        long& accumtxpackets, long& accumtxtotalerrors)
{
  accumrxpackets = 0;
  accumrxtotalerrors = 0;
  accumtxpackets = 0;
  accumtxtotalerrors = 0;
  
  long startuprxppackets;
  long startuprxerrors;
  long startuprxdropped;
  long startuprxframes;
  long startuprxoverruns;
  startuprxppackets = atol(startup_ifconfig.RXPackets.c_str());
  if(startup_ifconfig.RxErrors.length() > 0)
    startuprxerrors = atol(startup_ifconfig.RxErrors.c_str());
  if(startup_ifconfig.RxDropped.length() > 0)
    startuprxdropped = atol(startup_ifconfig.RxDropped.c_str());
  if(startup_ifconfig.RxFrames.length() > 0)
    startuprxframes = atol(startup_ifconfig.RxFrames.c_str());
  if(startup_ifconfig.RxOverruns.length() > 0)
    startuprxoverruns = atol(startup_ifconfig.RxOverruns.c_str());
  long startuprxtotalerrors = startuprxerrors + startuprxdropped + startuprxframes + startuprxoverruns;

  long startuptxppackets;
  long startuptxerrors;
  long startuptxdropped;
  long startuptxcarrier;
  long startuptxoverruns;
  startuptxppackets = atol(startup_ifconfig.TXPackets.c_str());
  if(startup_ifconfig.TxErrors.length() > 0)
    startuptxerrors = atol(startup_ifconfig.TxErrors.c_str());
  if(startup_ifconfig.TxDropped.length() > 0)
    startuptxdropped = atol(startup_ifconfig.TxDropped.c_str());
  if(startup_ifconfig.TxCarrier.length() > 0)
    startuptxcarrier = atol(startup_ifconfig.TxCarrier.c_str());
  if(startup_ifconfig.TxOverruns.length() > 0)
    startuptxoverruns = atol(startup_ifconfig.TxOverruns.c_str());
  long startuptxtotalerrors = startuptxerrors + startuptxdropped + startuptxcarrier + startuptxoverruns;

  long currentrxppackets;
  long currentrxerrors;
  long currentrxdropped;
  long currentrxframes;
  long currentrxoverruns;
  currentrxppackets = atol(current_ifconfig.RXPackets.c_str());
  if(current_ifconfig.RxErrors.length() > 0)
    currentrxerrors = atol(current_ifconfig.RxErrors.c_str());
  if(current_ifconfig.RxDropped.length() > 0)
    currentrxdropped = atol(current_ifconfig.RxDropped.c_str());
  if(current_ifconfig.RxFrames.length() > 0)
    currentrxframes = atol(current_ifconfig.RxFrames.c_str());
  if(current_ifconfig.RxOverruns.length() > 0)
    currentrxoverruns = atol(current_ifconfig.RxOverruns.c_str());
  long currentrxtotalerrors = currentrxerrors + currentrxdropped + currentrxframes + currentrxoverruns;
  long currenttxppackets;
  long currenttxerrors;
  long currenttxdropped;
  long currenttxcarrier;
  long currenttxoverruns;
  currenttxppackets = atol(current_ifconfig.TXPackets.c_str());
  if(current_ifconfig.TxErrors.length() > 0)
    currenttxerrors = atol(current_ifconfig.TxErrors.c_str());
  if(current_ifconfig.TxDropped.length() > 0)
    currenttxdropped = atol(current_ifconfig.TxDropped.c_str());
  if(current_ifconfig.TxCarrier.length() > 0)
    currenttxcarrier = atol(current_ifconfig.TxCarrier.c_str());
  if(current_ifconfig.TxOverruns.length() > 0)
    currenttxoverruns = atol(current_ifconfig.TxOverruns.c_str());
  long currenttxtotalerrors = currenttxerrors + currenttxdropped + currenttxcarrier + currenttxoverruns;
    
  accumrxpackets = currentrxppackets - startuprxppackets;
  accumrxtotalerrors = currentrxtotalerrors - startuprxtotalerrors;
  //WriteConsole("Info: Local RX packets = " + ToString(accumrxpackets));
  //WriteConsoleLine(", RX errors = " + ToString(accumrxtotalerrors));

  accumtxpackets = currenttxppackets - startuptxppackets;
  accumtxtotalerrors = currenttxtotalerrors - startuptxtotalerrors;
  //WriteConsole("Info: Local TX packets = " + ToString(accumtxpackets));
  //WriteConsoleLine(", TX errors = " + ToString(accumtxtotalerrors));

  return true;
}

bool FindPCIAddress(string& name, string& pciaddress)
{
  pciaddress = "";
  //WriteConsoleLine("Action: Run \"ethtool -i " + name + "\"");
  vector<string> outlines = vector<string>();
  int exitcode;
  bool bret = RunProcessGetExitCode("ethtool -i " + name, outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute ethtool -i " + name);
    return false;
  }
  if(outlines.size() < 0)
  {
    WriteConsoleLine("Error: No output from ethtool -i " + name);
    return false;
  }
  int i;
  for(i = 0; i < outlines.size(); i++)
  {
    if(outlines[i].find("bus-info: ") != string::npos)
    {
      pciaddress = outlines[i].substr(outlines[i].find("bus-info: ") + string("bus-info: ").size());
      //WriteConsoleLine(pciaddress);
      return true;
    }
  }
  return false;
}

bool FindIPMacAddress(string& name, string& macaddress)
{
  //Run ip addr show <name>
  vector<string> outlines = vector<string>();
  int exitcode;
  bool bret = RunProcessGetExitCode("ip addr show " + name, outlines, exitcode);
  if(bret == false)
  {
    //WriteConsoleLine("Error: Failed to execute ip addr show " + name + " locally");
    return false;
  }
  if(outlines.size() == 0)
  {
    //WriteConsoleLine("Error: Failed to execute ip addr show " + name + " locally");
    return false;
  }
  for(int i = 0; i < outlines.size(); i++)
  {
    outlines[i] = trim(outlines[i]);
    if((outlines[i].find("link/") != string::npos) && (outlines[i].find("link/") == 0))
    {
      if(outlines[i].find(" ") != string::npos) 
      {
        outlines[i]=outlines[i].substr(outlines[i].find(" "));
        outlines[i] = trim(outlines[i]);
        if(outlines[i].find(" ") != string::npos) 
        {
          outlines[i]=outlines[i].substr(0, outlines[i].find(" "));
          outlines[i] = trim(outlines[i]);
          macaddress = outlines[i];
          return true;
        }
      }
    }
  }
  //WriteConsoleLine("Error: Cannot find \"link/<type> <mac address> brd <mask>\" pattern from ip addr show " + name + " locally");
  return false;
}

bool FindDevice(string& d1,
                string& d2,
                ifconfig_Output_Info& startup_d1_ifconfig, 
                ifconfig_Output_Info& startup_d2_ifconfig,
                bool showdevices
               )
{
  //Run ifconfig -a
  //WriteConsoleLine("Action: Run \"ifconfig -a\"");
  vector<string> outlines = vector<string>();
  int exitcode;
  bool bret = RunProcessGetExitCode("ifconfig -a", outlines, exitcode);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to execute ifconfig -a locally");
    return false;
  }
  
  //Parse output into ifconfig_output_info
  vector<ifconfig_Output_Info> startup_local_ifconfig_list = vector<ifconfig_Output_Info>();
  if(Get_ifconfig_infos(outlines, startup_local_ifconfig_list) == false)
  {
    WriteConsoleLine("Error: Failed to parse ifconfig output");
    return false;
  }

  for(int index = 0; index < startup_local_ifconfig_list.size(); index++)
  {
    //Check whether mac address is IB 
    FindIPMacAddress(startup_local_ifconfig_list[index].DeviceName, startup_local_ifconfig_list[index].HWaddr);
    
    //Find PCI address
    string pciaddress;
    if(FindPCIAddress(startup_local_ifconfig_list[index].DeviceName, pciaddress) == true)
    {
      startup_local_ifconfig_list[index].Bus = pciaddress;
      int counter = 0;
      for(int tmpindex = 0; tmpindex < index; tmpindex++)
        if(startup_local_ifconfig_list[tmpindex].Bus == pciaddress)
          counter += 1;
      char tmpbuffer[20];
      sprintf(tmpbuffer, "%d", counter);
      startup_local_ifconfig_list[index].BusN = pciaddress + "/" + string(tmpbuffer);
    }
  }

  //Find ifconfig_output_info matching d1
  bool devicefound = false;
  for(int index = 0; index < startup_local_ifconfig_list.size(); index++)
  {
    if((startup_local_ifconfig_list[index].DeviceName == d1) ||
       (startup_local_ifconfig_list[index].HWaddr == d1) || 
       (startup_local_ifconfig_list[index].Bus == d1) ||
       (startup_local_ifconfig_list[index].BusN == d1))
    {
      if(showdevices == true)
        WriteConsoleLine("Info: Using " + startup_local_ifconfig_list[index].DeviceName + " as device #1");
      startup_d1_ifconfig = startup_local_ifconfig_list[index];
      d1 = startup_d1_ifconfig.DeviceName;
      devicefound = true;
      break;
    }
  }
  if(devicefound == false)
  {
    WriteConsoleLine("Error: Cannot find ethernet device " + d1);
    return false;
  }
  else
  {
    //WriteConsoleLine("Info: Found " + startup_d1_ifconfig.DeviceName);
    if((startup_d1_ifconfig.RXPackets.length() == 0) ||
       ((startup_d1_ifconfig.RxErrors.length() == 0) && (startup_d1_ifconfig.RxDropped.length() == 0) &&
        (startup_d1_ifconfig.RxOverruns.length() == 0) && (startup_d1_ifconfig.RxFrames.length() == 0)))
    {
      WriteConsoleLine("Error: Cannot find get RX packet count or error count for " + startup_d1_ifconfig.DeviceName);
      return false;
    }
    if((startup_d1_ifconfig.TXPackets.length() == 0) ||
       ((startup_d1_ifconfig.TxErrors.length() == 0) && (startup_d1_ifconfig.TxDropped.length() == 0) &&
        (startup_d1_ifconfig.TxOverruns.length() == 0) && (startup_d1_ifconfig.TxCarrier.length() == 0)))
    {
      WriteConsoleLine("Error: Cannot find get TX packet count or error count for " + startup_d1_ifconfig.DeviceName);
      return false;
    }
  }
  
  //Find ifconfig_output_info matching d2
  devicefound = false;
  for(int index = 0; index < startup_local_ifconfig_list.size(); index++)
  {
    if((startup_local_ifconfig_list[index].DeviceName == d2) ||
       (startup_local_ifconfig_list[index].HWaddr == d2) || 
       (startup_local_ifconfig_list[index].Bus == d2) ||
       (startup_local_ifconfig_list[index].BusN == d2))
    {
      if(showdevices)
        WriteConsoleLine("Info: Using " + startup_local_ifconfig_list[index].DeviceName + " as device #2");
      startup_d2_ifconfig = startup_local_ifconfig_list[index];
      d2 = startup_d2_ifconfig.DeviceName;
      devicefound = true;
      break;
    }
  }
  if(devicefound == false)
  {
    WriteConsoleLine("Error: Cannot find ethernet device " + d2);
    return false;
  }
  else
  {
    //WriteConsoleLine("Info: Found " + startup_d2_ifconfig.DeviceName);
    if((startup_d2_ifconfig.RXPackets.length() == 0) ||
       ((startup_d2_ifconfig.RxErrors.length() == 0) && (startup_d2_ifconfig.RxDropped.length() == 0) &&
        (startup_d2_ifconfig.RxOverruns.length() == 0) && (startup_d2_ifconfig.RxFrames.length() == 0)))
    {
      WriteConsoleLine("Error: Cannot find get RX packet count or error count for " + startup_d2_ifconfig.DeviceName);
      return false;
    }
    if((startup_d2_ifconfig.TXPackets.length() == 0) ||
       ((startup_d2_ifconfig.TxErrors.length() == 0) && (startup_d2_ifconfig.TxDropped.length() == 0) &&
        (startup_d2_ifconfig.TxOverruns.length() == 0) && (startup_d2_ifconfig.TxCarrier.length() == 0)))
    {
      WriteConsoleLine("Error: Cannot find get TX packet count or error count for " + startup_d2_ifconfig.DeviceName);
      return false;
    }
  }
  
  return true;
}

bool RunProcessGetExitCode(string command, vector<string>& outlines, int& exitcode)
{
  exitcode = -1;
  outlines.clear();
  string fullcommand = command + " 2>&1";
  FILE *read_fp;
  char buffer[256];
  int chars_read;
  memset(buffer, '\0', sizeof(buffer));
  read_fp = popen(fullcommand.c_str(), "re");
  if(read_fp == NULL)
    return false;
  string outline;
  while(fgets(buffer, sizeof(buffer), read_fp) != NULL)
  {
    outline += string(buffer);
  }
  exitcode = pclose(read_fp);
  //cout << "exit code = " << exitcode << endl;
  //cout << outline;
  istringstream iss(outline);
  string s;
  while(getline(iss, s))
  {
    outlines.push_back(s);
    //cout << "[" << s << "]" << endl;
  }
  
  return true;
}

bool RunProcessGetExitCodePrint(string command, vector<string>& outlines, int& exitcode)
{
  exitcode = -1;
  outlines.clear();
  string fullcommand = command + " 2>&1";
  FILE *read_fp;
  char buffer[256];
  int chars_read;
  memset(buffer, '\0', sizeof(buffer));
  read_fp = popen(fullcommand.c_str(), "re");
  if(read_fp == NULL)
    return false;
  string outline;
  while(fgets(buffer, sizeof(buffer), read_fp) != NULL)
  {
    outline += string(buffer);
    WriteConsole(buffer);
  }
  exitcode = pclose(read_fp);
  //cout << "exit code = " << exitcode << endl;
  //cout << outline;
  istringstream iss(outline);
  string s;
  while(getline(iss, s))
  {
    outlines.push_back(s);
    //cout << "[" << s << "]" << endl;
  }
  
  return true;
}

bool RunProcessGetExitCodeDirectPrint(string command, int& exitcode)
{
  //string fullcommand = command + " 2>&1";
  //exitcode = system(fullcommand.c_str());
  ///*
  exitcode = -1;
  string fullcommand = command + " 2>&1";
  FILE *read_fp;
  //char buffer[256];
  char buffer[2];
  int chars_read;
  memset(buffer, '\0', sizeof(buffer));
  read_fp = popen(fullcommand.c_str(), "r");
  if(read_fp == NULL)
    return false;
  while(fgets(buffer, sizeof(buffer), read_fp) != NULL)
  {
    WriteConsole(string(buffer));
  }
  exitcode = pclose(read_fp);
  //*/
  return true;
}


bool Get_ifconfig_infos(vector<string>& values, vector<ifconfig_Output_Info>& infos)
{
  infos.clear();
  if(values.size() == 0)
  {
    WriteConsoleLine("Error: Nothing to parse");
    return false;
  }
   
  vector< vector<string> > devicestext = vector< vector<string> >();
  vector<string> devicetext = vector<string>();
  for(int index = 0; index < values.size(); index++)
  {
    string value = values[index];
    trim(value);
    if(value.length() > 0)
    {
      if(values[index][0] != ' ')
      {
        if(devicetext.empty() == false)
        {
          devicestext.push_back(devicetext);
          devicetext = vector<string>();
        }
        devicetext.push_back(value);
      }
      else
      {
          devicetext.push_back(value);
      }
    }
  }
  if(devicetext.empty() == false)
  {
    devicestext.push_back(devicetext);
  }

  if(devicestext.size() == 0)
  {
    WriteConsoleLine("Error: Not enough text to parse");
    return false;
  }

  for(int index = 0; index < devicestext.size(); index++)
  {
    ifconfig_Output_Info device;
    bool ret = Get_ifconfig_info(devicestext[index], device);
    if(ret == true)
      infos.push_back(device);
  }
  return true;
}

bool Get_ifconfig_info(vector<string>& values, ifconfig_Output_Info& info)
{
  int i;
  if(values.size() == 0)
    return false;
  if(ParseFirstLine(values[0], info.DeviceName, info.LinkEncap, info.HWaddr) == false)
    return false;
  if(values.size() == 1)
    return true;
  for(int i = 1; i < values.size(); i++)
  {
    if((values[i].find("inet addr:") != string::npos) ||
       (values[i].find("Bcast:") != string::npos) ||
       (values[i].find("Mask:") != string::npos))
    {
      if(Parse_inet_addr_Line(values[i], info.InetAddr, info.Bcast, info.Mask) == false)
        return false;
    }
    else if(values[i].find("MTU:") != string::npos)
    {
      if(Parse_MTU_Line(values[i], info.State, info.MTU) == false)
        return false;
    }
    else if(values[i].find("RX packets:") == 0)
    {
      if(Parse_Rx_Packets_Line(values[i], info.RXPackets, info.RxErrors, info.RxDropped, info.RxOverruns, info.RxFrames) == false)
        return false;
    }
    else if(values[i].find("TX packets:") == 0)
    {
      if(Parse_Tx_Packets_Line(values[i], info.TXPackets, info.TxErrors, info.TxDropped, info.TxOverruns, info.TxCarrier) == false)
        return false;
    }
    else if((values[i].find("collisions:") != string::npos) ||
            (values[i].find("txqueuelen:") != string::npos))
    {
      if(Parse_collision_txqueuelen_Line(values[i], info.Collisions, info.TxQueueLen) == false)
        return false;
    }
    else if((values[i].find("RX bytes:") != string::npos) ||
            (values[i].find("TX bytes:") != string::npos))
    {
      if(Parse_RX_bytes_TX_bytes_Line(values[i], info.RxBytes, info.TxBytes) == false)
        return false;
    }
  }
  return true;
}

bool ParseFirstLine(string line, string& DeviceName, string& LinkEncap, string& HWaddr)
{
  DeviceName.clear();
  LinkEncap.clear();
  HWaddr.clear();
  
  trim(line);
  if(line.length() == 0)
    return false;
  string s = line;
  if(s.find(" ") != string::npos)
  {
    DeviceName = s.substr(0, s.find(" "));
    s = s.substr(DeviceName.length());
    trim(s);
  }
  else
  {
    DeviceName = s;
    return true;
    
  }
  LinkEncap = GetFormatedSubString(line, "Link encap:");
  HWaddr = GetFormatedSubString(line, "HWaddr ");

  return true;
}

bool Parse_inet_addr_Line(string line, string& InetAddr, string& Bcast, string& Mask)
{
  InetAddr.clear();
  Bcast.clear();
  Mask.clear();
  
  trim(line);
  if(line.length() == 0)
    return false;

  InetAddr = GetFormatedSubString(line, "inet addr:");
  Bcast = GetFormatedSubString(line, "Bcast:");
  Mask = GetFormatedSubString(line, "Mask:");

  return true;
}

bool Parse_MTU_Line(string line, string& State, string& MTU)
{
  State.clear();
  MTU.clear();
  
  trim(line);
  if(line.length() == 0)
    return false;

  MTU = GetFormatedSubString(line, "MTU:");
  //RUNNING
  if(line.find("RUNNING ") != string::npos)
    State = "RUNNING";

  return true;
}

bool Parse_Rx_Packets_Line(string line, string& RXPackets, string& Errors, string& Dropped, string& Overruns, string& Frame)
{
  RXPackets.clear();
  Errors.clear();
  Dropped.clear();
  Overruns.clear();
  Frame.clear();
  
  trim(line);
  if(line.length() == 0)
    return false;

  //RX packets:3101 errors:0 dropped:0 overruns:0 frame:0
  RXPackets = GetFormatedSubString(line, "RX packets:");
  Errors = GetFormatedSubString(line, "errors:");
  Dropped = GetFormatedSubString(line, "dropped:");
  Overruns = GetFormatedSubString(line, "overruns:");
  Frame = GetFormatedSubString(line, "frame:");
  return true;
}

bool Parse_Tx_Packets_Line(string line, string& TXPackets, string& Errors, string& Dropped, string& Overruns, string& Carrier)
{
  TXPackets.clear();
  Errors.clear();
  Dropped.clear();
  Overruns.clear();
  Carrier.clear();
  
  trim(line);
  if(line.length() == 0)
    return false;

  //TX packets:379 errors:0 dropped:0 overruns:0 carrier:0
  TXPackets = GetFormatedSubString(line, "TX packets:");
  Errors = GetFormatedSubString(line, "errors:");
  Dropped = GetFormatedSubString(line, "dropped:");
  Overruns = GetFormatedSubString(line, "overruns:");
  Carrier = GetFormatedSubString(line, "carrier:");
  return true;
}

bool Parse_collision_txqueuelen_Line(string line, string& collision, string& txqueuelen)
{
  collision.clear();
  txqueuelen.clear();
  
  trim(line);
  if(line.length() == 0)
    return false;

  //collisions:0 txqueuelen:1000
  collision = GetFormatedSubString(line, "collisions:");
  txqueuelen = GetFormatedSubString(line, "txqueuelen:");
  return true;
}


bool Parse_RX_bytes_TX_bytes_Line(string line, string& rxbytes, string& txbytes)
{
  rxbytes.clear();
  txbytes.clear();
  
  trim(line);
  if(line.length() == 0)
    return false;
  
  //RX bytes:656 (656.0 b)  TX bytes:8581 (8.3 Kb)
  rxbytes = GetFormatedSubString(line, "RX bytes:");
  txbytes = GetFormatedSubString(line, "TX bytes:");
  return true;
}

string GetFormatedSubString(string s, string leading)
{
  string ret;
  if(s.length() == 0)
    return ret;
  if(s.find(leading) != string::npos)
  {
    string s2 = s.substr(s.find(leading) + leading.length());
    if(s2.find(" ") != string::npos)
      ret = s2.substr(0, s2.find(" "));
    else
      ret = s2;
  }
  return ret;
}

bool CreateLocalRandomFile(string param_tmpdirectory, long size, string& local_filename, string& local_filename_fullpath, string& crc32)
{
  local_filename_fullpath = param_tmpdirectory + local_filename;
  WriteConsoleLine("Action: Create random file \"" + local_filename_fullpath + "\"");
  
  ofstream fs;
  fs.open (local_filename_fullpath.c_str(), ios::out | ios::binary);
  if(fs.is_open() == false)
  {
    WriteConsoleLine("Error: Failed to open " + local_filename_fullpath + " for writing\n");
    return false;
  }
  long count = 0;
    
  char randgroup[10][1024];
  FILE *fp;
  fp = fopen("/dev/urandom", "r");
  if(fp == NULL)
  {
    WriteConsoleLine("Error: Failed to /dev/urandom\n");
    fs.close();
    remove(local_filename_fullpath.c_str());
    return false;
  }

  for(int tmpi = 0; tmpi < 10; tmpi++)
  {
    fread(&randgroup[tmpi], 1, 1024, fp);
    while(randgroup[tmpi][0] == 0)
      fread(&randgroup[tmpi], 1, 1024, fp);
  }
  fclose(fp);
  
  int block_count = size / 1024;
  for(int tmpi = 0; tmpi < block_count; tmpi++)
  {
    fs.write(randgroup[rand() % 10], 1024);
    count += 1024;
  }
  if(fs.bad() == true)
  {
    WriteConsoleLine("Error: Failed to write to " + local_filename_fullpath + "\n");
    fs.close();
    remove(local_filename_fullpath.c_str());
    return false;
  }
  
  fs.close();    

  WriteConsoleLine("Info: File size is " + ToStringWithComma(count) + " bytes");

  //Get random file crc32
  crc32.clear();
  if(GetCrc32(local_filename_fullpath, crc32) == false)
  {
    WriteConsoleLine("Error: Failed to get crc32 value");
    //WriteConsoleLine("Action: Remove " + local_filename_fullpath);
    remove(local_filename_fullpath.c_str());
    return false;
  }
  
  return true;
}

bool FtpDeleteRemoteFile(string param_remoteip, string param_remoteuser, string param_remotepassword, string param_remotedirectory, string filename)
{
  char tmpfile1[] = "/tmp/ftp-testtool.XXXXXX";
  int fd = mkstemp(tmpfile1);
  if (fd == -1) 
    return false;
  //cout << "tmpfile1 = " << tmpfile1 << endl;
  FILE *out = fdopen(fd, "wt");
  fprintf(out, "#!/bin/sh\n");
  if(verboseftp)
    fprintf(out, string("ftp -inv " + param_remoteip + " << EOF\n").c_str());
  else
    fprintf(out, string("ftp -in " + param_remoteip + " << EOF\n").c_str());
  fprintf(out, string("quote USER " + param_remoteuser + "\n").c_str());
  fprintf(out, string("quote PASS " + param_remotepassword + "\n").c_str());
  fprintf(out, string("cd \"" + param_remotedirectory + "\"\n").c_str());
  fprintf(out, string("delete \"" + filename + "\"\n").c_str());
  fprintf(out, "bye\n");
  fprintf(out, "EOF\n");
  fclose(out);
  close(fd);
  
  WriteConsoleLine("Action: Delete file on remote system");
  int exitcode;
  bool bret = RunProcessGetExitCodeDirectPrint("sh " + string(tmpfile1), exitcode);
  remove(tmpfile1);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to delete file on remote system");
    return false;
  }
  if(exitcode != 0)
  {
    WriteConsoleLine("Error: Exit code is " + ToString(exitcode));
    return false;
  }
  return true;
}

bool FtpLocalFileToRemote(string param_remoteip, string param_remoteuser, string param_remotepassword, string param_remotedirectory, 
                          string param_localdirectory, string local_filename, string remote_filename)
{
  char tmpfile1[] = "/tmp/ftp-testtool.XXXXXX";
  int fd = mkstemp(tmpfile1);
  if (fd == -1) 
    return false;
  //cout << "tmpfile1 = " << tmpfile1 << endl;
  FILE *out = fdopen(fd, "wt");
  fprintf(out, "#!/bin/sh\n");
  if(verboseftp)
    fprintf(out, string("ftp -inpv " + param_remoteip + " << EOF\n").c_str());
  else
    fprintf(out, string("ftp -inp " + param_remoteip + " << EOF\n").c_str());
  fprintf(out, string("quote USER " + param_remoteuser + "\n").c_str());
  fprintf(out, string("quote PASS " + param_remotepassword + "\n").c_str());
  fprintf(out, "passive\n");
  fprintf(out, string("cd \"" + param_remotedirectory + "\"\n").c_str());
  fprintf(out, string("lcd \"" + param_localdirectory + "\"\n").c_str());
  fprintf(out, "bin\n");
  fprintf(out, string("put \"" + local_filename + "\" \""+ remote_filename + "\"\n").c_str());
  fprintf(out, "bye\n");
  fprintf(out, "EOF\n");
  fclose(out);
  close(fd);
  
  WriteConsoleLine("Action: ftp file to remote system");
  int exitcode;
  bool bret = RunProcessGetExitCodeDirectPrint("sh " + string(tmpfile1), exitcode);
  remove(tmpfile1);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to ftp file to remote system");
    return false;
  }
  if(exitcode != 0)
  {
    WriteConsoleLine("Error: Exit code is " + ToString(exitcode));
    return false;
  }
  return true;
}

bool FtpRemoteFileToLocal(string param_remoteip, string param_remoteuser, string param_remotepassword, string param_remotedirectory, 
                          string param_localdirectory, string local_filename, string remote_filename)
{
  char tmpfile1[] = "/tmp/ftp-testtool.XXXXXX";
  int fd = mkstemp(tmpfile1);
  if (fd == -1) 
    return false;
  //cout << "***tmpfile1 = " << tmpfile1 << endl;
  FILE *out = fdopen(fd, "wt");
  fprintf(out, "#!/bin/sh\n");
  if(verboseftp)
    fprintf(out, string("ftp -inpv " + param_remoteip + " << EOF\n").c_str());
  else
    fprintf(out, string("ftp -inp " + param_remoteip + " << EOF\n").c_str());
  fprintf(out, string("quote USER " + param_remoteuser + "\n").c_str());
  fprintf(out, string("quote PASS " + param_remotepassword + "\n").c_str());
  fprintf(out, "passive\n");
  fprintf(out, string("cd \"" + param_remotedirectory + "\"\n").c_str());
  fprintf(out, string("lcd \"" + param_localdirectory + "\"\n").c_str());
  fprintf(out, "bin\n");
  fprintf(out, string("get \"" + remote_filename + "\" \"" + local_filename + "\"\n").c_str());
  fprintf(out, "bye\n");
  fprintf(out, "EOF\n");
  fclose(out);
  close(fd);
  
  WriteConsoleLine("Action: ftp file from remote system");
  int exitcode;
  bool bret = RunProcessGetExitCodeDirectPrint("sh " + string(tmpfile1), exitcode);
  remove(tmpfile1);
  if(bret == false)
  {
    WriteConsoleLine("Error: Failed to ftp file from remote system");
    return false;
  }
  if(exitcode != 0)
  {
    WriteConsoleLine("Error: Exit code is " + ToString(exitcode));
    return false;
  }
  return true;
}

string GenerateRandomMd5()
{
  uuid_t uuid;
  char str[64];
  uuid_generate(uuid);
  uuid_unparse(uuid, str);
  //cout << str << endl;
  return ComputeMD5(string(str));
}

string ComputeMD5(string str) 
{
  MD5_CTX ctx;
  MD5_Init(&ctx);
  MD5_Update(&ctx, str.c_str(), str.length());
  unsigned char digest[16];
  MD5_Final(digest, &ctx);
  char md5string[33];
  for(int i = 0; i < 34; ++i)
    md5string[i] = 0;
  for(int i = 0; i < 16; ++i)
    sprintf(&md5string[i*2], "%02x", (unsigned int)digest[i]);
  return string(md5string);
}

bool GetCrc32(string filename, string& crc32)
{
  crc32.clear();
  vector<string> outlines = vector<string>();
  int exitcode;
  if((RunProcessGetExitCode("crc32 " + filename , outlines, exitcode) == false) ||
     (exitcode != 0) ||
     (outlines.size() == 0) ||
     (outlines[0].find("No such file or directory") != string::npos))
  {
    return false;
  }
  else
  {
    crc32 = trim(outlines[0]);
    return true;
  }
}

string& trim_right_inplace(string& s, const string& delimiters = " \f\n\r\t\v")
{
  return s.erase(s.find_last_not_of(delimiters) + 1);
}

string& trim_left_inplace(string& s, const string& delimiters = " \f\n\r\t\v")
{
  return s.erase( 0, s.find_first_not_of( delimiters ) );
}

string& trim(string& s, const string& delimiters = " \f\n\r\t\v")
{
  return trim_left_inplace(trim_right_inplace(s, delimiters), delimiters);
}

string& trim(string& s)
{
  const string delimiters = " \f\n\r\t\v";
  return trim_left_inplace(trim_right_inplace(s, delimiters), delimiters);
}

string ToString(int value)
{
  ostringstream convert;
  convert << value;
  return convert.str();
}

class comma_numpunct : public std::numpunct<char>
{
  protected:
    virtual char do_thousands_sep() const
    {
        return ',';
    }

    virtual std::string do_grouping() const
    {
        return "\03";
    }
};

string ToStringWithComma(int value)
{
  stringstream ss;
  locale comma_locale(locale(), new comma_numpunct());
  ss.imbue(locale(comma_locale));
  ss << fixed << value;
  //cout << ss.str() << endl;
  return ss.str();
}

bool IsDirectoryExist(string pathname)
{
  struct stat sb;
  return (stat(pathname.c_str(), &sb) == 0 && S_ISDIR(sb.st_mode));
}

bool IsFileExist(string pathname)
{
  struct stat sb;
  return (stat(pathname.c_str(), &sb) == 0 && S_ISREG(sb.st_mode));
}

bool GetLongValue(string value, long& ret)
{
  ret = 0;
  string s = value;
  for(int i = 0; i < s.length(); i++)
    s[i] = tolower(s[i]);
  //cout << "s = " << s << endl;
  long multiplier = 1;
  if(s[s.length() - 1] == 'k')
  {
    s = s.substr(0,s.length() - 1);
    multiplier = 1024;
  }
  else if(s[s.length() - 1] == 'm')
  {
    s = s.substr(0,s.length() - 1);
    multiplier = 1024 * 1024;
  }
  else if(s[s.length() - 1] == 'g')
  {
    s = s.substr(0,s.length() - 1);
    multiplier = 1024 * 1024 * 1024;
  }
  ret = atol(s.c_str());
  ret = ret * multiplier;
  return true;
}

