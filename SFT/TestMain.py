#!/usr/bin/env python

import sys,os

if len( sys.argv ) == 1:
    sku_name = "SYS_EVT.sku"
    #home_dir = os.environ['Zuari_BFT']
elif len( sys.argv ) == 2:
    sku_name = sys.argv[1]
    #home_dir = "/root/Zuari-"+sku_name.split('_')[1].split('.')[0]
else:
    sys.exit('Usage: TestEngine.py sku_name')
home_dir = '/root/Zuari-EVT'
print sku_name
print home_dir

#if home_dir == '/root/Zuari-cDVT' or home_dir == '/root/Zuari-DVT':
#   home_dir = '/root'
#TestEinge.py also need to modify, and fixture changed, so unmeaning.

print sys.path
sys.path.insert(0, home_dir+'/TestConfig')
sys.path.insert(0, home_dir+'/Common')
sys.path.insert(0, home_dir+'/BFT')
print sys.path
#from ScanBarCode import *
#from PowerControl import *
#from RelayControl import *
#from Log import *
#from EventManager import *
#from Comm232 import *
from TestEngine import *

config = Configure()
config.Put('HOME_DIR', home_dir)
config.Load(home_dir + '/TestConfig/' + sku_name)

ScanBarCode(config)
testMain = TestEngine(config, sku_name)
result = testMain.Run()
if result[0:4] == 'FAIL':
    InvokeMessagePopup(result, 'Exit', True)
elif result == 'PASS':
    InvokeMessagePopup("Test Pass!!", 'Exit', True)
else:
    print "Shouldn't reach here"
testMain.End()
