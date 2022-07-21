from lxml import etree
from time import time
import os
import copy

def timeit(func, text=None):
    start = time()
    func()
    end = time()
    print(f"{text} Time consumed: {end-start:.3f}s")
filename = input("Input the osm file (with suffix):")
if(not os.path.exists(filename)):
    print(f"{filename} does not exist!")
    input("Press Enter to exist the program")
    os._exit()

def read_file():
    global data
    with open(filename, 'rb') as f:
        data = f.read()

timeit(read_file, "File has been read!")
def parse_xml():
    global osm
    osm = etree.XML(data)

timeit(parse_xml, "XML data have been parsed!")
print("The program is simplifying your data. This might take a long time (an hour or so).")


n_way = 0
n_node = 0
n_region = 0


newosm = etree.XML("<osm></osm>")
it = osm.iterchildren()
for item in it:
    if(item.tag == 'node'):
        break
    else:
        newosm.append(item)
        
it = osm.iterchildren()
dependency_way_id = []
start = time()
timer =  time()
node_dict = {}
# delete redundant regions, and find redundant ways
for item in it:
    
    if(item.tag == 'way'):
        n_way+=1
        child_it = item.iterchildren()
        for child in child_it:
            if(child.tag == 'tag'):
                if(child.attrib['k'] == 'highway'\
                    and (child.attrib['v'] == 'motorway' or 'link' in child.attrib['v'])):
                    dependency_way_id.append(item.get('id'))
                    break
                if(child.attrib['k'] == 'ref' and \
                    (child.attrib['v'][0] in 'GSgs') ):
                    dependency_way_id.append(item.get('id'))
                    break
    #if(item.attrib['id'] == '4566400'):
        #print("金水区!")
    if(item.tag == 'relation'):
        #print(item.get('id'))
        n_region+=1
        no_del = False
        child_it = item.iterchildren()
        for child in child_it:
            if(child.tag == 'tag'):
                if(child.attrib['k'] == 'name' and child.attrib['v'][-1] in '市县区'):
                    no_del = True
                    newosm.append(copy.deepcopy(item))
        if(no_del):
            child_it = item.iterchildren()
            for child in child_it:
                if(child.tag == 'member' and child.attrib['type']=='relation'):
                    li = osm.xpath(f"/osm/relation[@id='{child.attrib['ref']}']")
                    if(len(li) != 1):
                        print(f"Region {child.attrib['ref']} is referred but no data source exists!")
                        item.remove(child)
                    else:
                        newosm.append(copy.deepcopy(li[0]))
                if(child.tag == 'member' and child.attrib['type']=='way'):
                    dependency_way_id.append(child.attrib['ref'])
                if(child.tag == 'member' and child.attrib['type']=='node'):
                    item.remove(child)
                    #pass
            
    if(item.tag == 'node'):
        n_node+=1
        node_dict[item.get('id')] = copy.deepcopy(item)
    end = time()
    if(end-timer>3):
        print(f"{end-start:.3f}s used.")
        timer = end

print(f"Number of nodes:{n_node}")
print(f"Number of ways:{n_way}")
print(f"Number of regions:{n_region}")

print(f"Number of useful ways:{len(dependency_way_id)}")



# delete redundant ways
first_region = newosm.xpath("/osm/relation[1]")[0]
bounds_ele = newosm.xpath("/osm/bounds")[0]
dependency_node_id = []
I = 0
it = osm.iterchildren()
for item in it:
    end = time()
    if(end-timer>3):
        print(f"{end-start:.3f}s used.")
        print(f"Deleting redundant ways and nodes, process: {I/(n_node+n_way+n_region)*100:.3f}%")
        timer = end
    if(item.tag == 'way'):
        if(item.get('id') in dependency_way_id):
            child_it = item.iterchildren()
            for child in child_it:
                if(child.tag == 'nd'):
                    bounds_ele.addnext(node_dict[child.get('ref')])

            first_region.addprevious(item)
    I+=1

#print(f"Redundant ways and regions have been removed. The results are saved to ")
print(f"Done! Time consumed: {time()-start:.3f}s")
newosm.getroottree().write("simplified_node_way_region.osm", encoding = 'utf-8')
print("Data have been dumped to file \"simplified_node_way_region.osm\"")