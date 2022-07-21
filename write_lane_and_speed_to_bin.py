from lxml import etree
#import translate
import numpy as np
import xpinyin
import numpy as np
import pandas as pd
import re
import time
import copy
P = xpinyin.Pinyin()
# block size: 277
# lanes start (0 based): 40, 4 bytes
# speed start (0 based): 36, 4 bytes
# name start (0 based): 4, nameLen bytes
# osmid start (0 based): 104, 20 bytes

# blockSize = 343
# lanesStart = 77-1
# speedStart = 73-1
# nameStart = 9-1
# nameLen = 64
# osmidStart = 171-1
# isonewayStart = 5-1

blockSize = 313
lanesStart = 73-1
speedStart = 77-1
nameStart = 5-1
nameLen = 64
osmidStart = 141-1
isonewayStart = 69-1
bin_filename = "all_links.bin"
with open("simplified_node_way_region.osm", 'rb') as f:
    osm_bin = f.read()
with open(f"zhengzhou\\{bin_filename}", "rb") as f:
    bin = f.read()
osm = etree.XML(osm_bin)
bin = np.frombuffer(bin, np.uint8).copy()
it = osm.iterchildren()
way_dict = {}
for item in it:
    if(item.tag == 'way'):
        way_dict[item.get('id')] = copy.deepcopy(item)
for i in range(bin.size//blockSize):
    id = bin[i*blockSize+osmidStart:i*blockSize+osmidStart+20].tobytes().decode('utf-8').strip(' ')


    li = way_dict[id].xpath("./tag[@k='name:en']")
    if(len(li) == 1):
        name = np.frombuffer(li[0].get('v').encode('utf-8'), np.uint8)
        name32 = 32*np.ones((nameLen,))
        name32[:len(name)] = name
        bin[i*blockSize+nameStart:i*blockSize+nameStart+nameLen] = name32[:]
    else:
        li = way_dict[id].xpath("./tag[@k='name']")
        if(len(li) == 1):
            name =  li[0].get('v')
            name = P.get_pinyin(name, ' ').title()
            name = np.frombuffer(name.encode('utf-8'), np.uint8)
            if(len(name)>nameLen):
                name = P.get_initials(li[0].get('v'), ' ')
                name = np.frombuffer(name.encode('utf-8'), np.uint8)
            name32 = 32*np.ones((nameLen,), dtype=np.uint8)
            name32[:len(name)] = name
            bin[i*blockSize+nameStart:i*blockSize+nameStart+nameLen] = name32[:]
        else:
            li = way_dict[id].xpath("./tag[@k='ref']")
            if(len(li) != 1):
                name = np.frombuffer("Ramp".encode('utf-8'), np.uint8)
            else:
                name = np.frombuffer(li[0].get('v').encode('utf-8'), np.uint8)
            name32 = 32*np.ones((nameLen,))
            name32[:len(name)] = name
            bin[i*blockSize+nameStart:i*blockSize+nameStart+nameLen] = name32[:]

    li = way_dict[id].xpath("./tag[@k='maxspeed']")
    if(len(li) == 1):
        speed = np.frombuffer(int(li[0].get('v')).to_bytes(4, 'little'), np.uint8)
    else:
        speed = np.frombuffer(int(0).to_bytes(4, 'little'), np.uint8)
    bin[i*blockSize+speedStart:i*blockSize+speedStart+4] = speed[:]

    li = way_dict[id].xpath("./tag[@k='lanes']")
    if(len(li) == 1):
        lanes = 2*np.frombuffer(int(li[0].get('v')).to_bytes(4, 'little'), np.uint8)
    else:
        
        lanes = np.frombuffer(int(0).to_bytes(4, 'little'), np.uint8)
    bin[i*blockSize+lanesStart:i*blockSize+lanesStart+4] = lanes[:]

    #######
    li = way_dict[id].xpath("./tag[@k='oneway']")
    if(len(li) == 1):
        if(li[0].get('v') == 'yes'):
            isoneway = np.frombuffer(int(1).to_bytes(4, 'little'), np.uint8)
        else:
            isoneway = np.frombuffer(int(0).to_bytes(4, 'little'), np.uint8)
    else:
        isoneway = np.frombuffer(int(0).to_bytes(4, 'little'), np.uint8)
    bin[i*blockSize+isonewayStart:i*blockSize+isonewayStart+4] = isoneway[:]
    
bin.tofile(f"zhengzhou\\{bin_filename}")
print("Done!")

    

