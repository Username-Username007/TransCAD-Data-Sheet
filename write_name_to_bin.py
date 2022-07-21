from lxml import etree
import translate
import numpy as np
import xpinyin
import numpy as np
import pandas as pd
import re
import time
P = xpinyin.Pinyin()
with open("simplified_node_way_region.osm", "rb") as f:
    osm_data = f.read()
osm = etree.XML(osm_data)
with open("full_dazhou\\roads.bin.bak", "rb") as f:
    origin = np.frombuffer(f.read(), dtype=np.byte).copy()

print(f"{len(origin)=}")
df = pd.read_excel('full_dazhou\\line_id.xlsx', na_filter = False)
i = 0
start = time.time()
it = osm.iterchildren()
for item in it:
    if(item.tag == 'way'):
        way = item
        break

for tag in df['OSMID']:
    has_en_name = False
    has_ref_name = False
    has_ch_name = False
    #way = osm.xpath(f"./way[@id='{df['osm_id'].iloc[i]}']")[0]
    
    li = way.xpath("./tag[@k='name:zh']")
    if(len(li)):
        ch_name = li[0].attrib['v']
        has_ch_name = True

    li = way.xpath("./tag[@k='name']")
    if(len(li)):
        ch_name = li[0].attrib['v']
        has_ch_name = True

    li = way.xpath("./tag[@k='name:en']")
    if(len(li)):
        en_name = li[0].attrib['v']
        has_en_name = True
    li = way.xpath("./tag[@k='ref']")
    if(len(li)):
        ref_name = li[0].attrib['v']
        has_ref_name = True
    for item in it:
        if(i+1 >= df.shape[0]):
            break
        if(int(item.attrib['id']) == df['OSMID'].iloc[i+1]):
            way = item
            break

    if(has_en_name):
        #print(ch_name, end = ',')
        name = en_name
    elif(has_ch_name):
        name = P.get_pinyin(ch_name).replace('-', ' ').title()
        #name = P.get_pinyin(ch_name)
        #time.sleep(0.1)
        #print("Translate", ch_name, 'to', name)
    elif(has_ref_name):
        name = ref_name
    else:
        name = ''
    # name = name.replace('Zhong Lu', 'Mid')
    # name = name.replace('Xi Lu', 'West')
    # name = name.replace('Dong Lu', 'East')
    # name = name.replace('Nan Lu', 'South')
    # name = name.replace('Bei Lu', 'North')
    # name = name.replace('Gao Su', 'Expres.')
    # name = name.replace('Lu', "Rd.")
    # name = name.replace('Da Dao', 'Rev.')
    # name = name.replace('Xiang', 'Alley')
    if(len(name)>32):
            name = ' '.join([i[:3 if 3<len(i) else len(i)] for i in name.split(' ')])
    if(len(name)>32):
            name = ' '.join([i[0] for i in name.split(' ')])
    try:
        name32 = 32*np.ones((32,), dtype=np.int8)
        name_buf = np.frombuffer(name.encode('gbk'), dtype = np.int8)
        name32[:len(name_buf)] = name_buf
    except:
        print(name, ch_name)
        name = input("Input a name:")
        name32 = 32*np.ones((32,), dtype=np.int8)
        name_buf = np.frombuffer(name.encode('gbk'), dtype = np.int8)
        name32[:len(name_buf)] = name_buf
    ind = int.from_bytes(origin[i*45:i*45+4].tobytes(), 'little')

    origin[i*104+4:i*104+4+32] = name32
    i+=1
    end = time.time()
    if(end-start>1):
        start = end
        print(f"{i} of {df.shape[0]}")
origin.tofile("full_dazhou\\roads.BIN" )
print("Done!")
    # roads.bin file format:
    # each line occupies 3*16 = 48 bytes
    # the following indices are 1-based index
    # 1~4 bytes for each line is little-endian ID (or index) in int32(or uint32) 
    # 5~9 bytes is "LINES" charactersm
    # 10~13 bytes is an unknown attribute
    # 14~(14+32-1) = 45 is the name of the road

