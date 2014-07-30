'''
Created on Feb 20, 2013

@author: stefanotranquillini

ONLY TO TEST PIECES

'''
from executor.forms import BidForm
from general.models import Task
from general.utils import mergeData, splitObjects, filterData, joinObjects
from lxml import etree
from test.test_descrtut import defaultdict
from django.contrib.databrowse.plugins import objects

def testBidForm():
    form_data = {'amount': 20.2}
    form = BidForm(data=form_data)
    task = Task()
def test_mergeData():
    obj1=[{'id':'1','a':'a'},{'id':'2','a':'a'}]
    obj2={'id':'1','b':'b'}
    res=mergeData([obj1,obj2])
    res_o = None
    if res[0]['id']=='1':
        res_o=res[0]
    else:
        res_o=res[1]
    print res_o
        
CONVERSION = (('CCM', 1),('USD', 1.16), ('EUR', 0.9), ('COF', 2))

def convertReward(r_type,r_quantity):
    for k, v in CONVERSION:
        if k==r_type:
            return r_quantity*v
    raise Exception('Reward type does not exists')

''' 
This flats out the list
example:
input [[a,b],[c,d]]
output [a,b,c,d]
'''
def mergeResults(instances):
    ret = []
    for instance in instances:
        value =instance
#        print 'value '+str(value)
#        if list then concat element
        if isinstance(value, list):
#            joinTasks('id', ret)
            for v in value:
                ret.append(v)
##        if not append the element
        else:
            ret.append(value)
    return ret

''' 
merges the fields of two object, if the objects share a field, the merging will be a list
example
input: {'id':'1','tag':'good'} and {'id':'1','tag':'nice', 'note':'cool pic bro'}
output: {'id':'1','tag':['nice','good'], 'note':'cool pic bro'}
'''
def mergeFields(field,d1,d2):
    ret = {}
    processed=[]
#    set the id of the result
    ret[field]=d1[field]
#        for all the field inside the element {'id':'1','tag':'fgh'} -> id, tag
    for el in d1:
#        if it is not the id
        if el is not field:
#            if elelemti s laso in d2
            if el in d2:
#                print '%s vs %s' % (d1[el],d2[el])
#                then merge them
                ret[el]=mergeResults([d1[el],d2[el]])
            else:
#                add just the one that has the element
                ret[el]=d1[el]
#           this for not processing the data tiwce     
            processed.append(el)
#    do the same with the fields of d2.
    for el in d2:
        if el is not field:
            if el not in processed:
                if el in d1:
#                    print '%s vs %s' % (d1[el],d2[el])
                    ret[el]=mergeResults([d1[el],d2[el]])
                else:
                    ret[el]=d2[el]

    return ret

''' 
join the results of a task, keeping the input sets separated : set of set
ex:
input: [
        [{'id':'1','tag':'abc'},{'id':'2','tag':'abc'}],
        [{'id':'1','tag':'efg'},{'id':'2','tag':'efg'}],
        [{'id':'3','tag':'abc'},{'id':'4','tag':'abc'}],
        [{'id':'3','tag':'efg'},{'id':'4','tag':'efg'}]
       ]
output:[
        [
        [{'tag': ['efg', 'abc'], 'id': '1'}, {'tag': ['efg', 'abc'], 'id': '2'}],
        [{'tag': ['efg', 'abc'], 'id': '3'}, {'tag': ['efg', 'abc'], 'id': '4'}]
        ]


'''
def joinResult(field, lst):
#    loads the dict
    res=defaultdict(dict)
#    init the list of input. this is used to keep track of what lists have to be made as output
    il = []
    for task in lst:
#        init the list of index for the item
        ll=[]

        for obj in task:
#            insert the id
            ll.append(obj[field])
#           search in the map the object with the same 'field' value
            idx = obj[field]
            t_obj=res[idx]
#           merge the two objects
            res[idx]=mergeFields(field,obj,t_obj)
#       if the list is not alreay in the ll, insert it 
        if ll not in il:
            il.append(ll)
    r=[]

#   create the output lists
    for ll in il:
        rl=[]
        for i in ll:
            rl.append(res[i])
        r.append(rl)
    return r

    
def addTasks(process):
    tree = etree.parse(process)
    root = tree.getroot()
    
    print(etree.tostring(root, pretty_print=True))
    
def processStuff():
    tree = etree.parse("Video.bpmn")
    processes = tree.findall('{http://www.omg.org/spec/BPMN/20100524/MODEL}process')  
    process = processes[0]
    print process.attrib['name']

def aggregateData(data,field): 
    ret = []
    res = {}
#    defaultdict(dict)
    for obj in data:
#        find the index
        idx = obj[field]
#        find the object
        if idx in res:
            t_obj = res[idx]
        else:
            t_obj = {}
            
        for k,v in obj.iteritems():
#            if key is the field don't do anything
            if k is not field:
                if k in t_obj:
#                    if it's a list then append it, so we avoid list into lists
                    if isinstance(t_obj[k], list):
                        t_obj[k].append(v)
                    else:
                        t_obj[k]=[v]+data
                else:
                    if isinstance(v, list):
                        t_obj[k]=v
                    else:
                        t_obj[k]=[v]
            else:
                t_obj[k]=v  
#            store in the map
        res[idx] = t_obj
    r = []
#    for all the elements in the list (which are dict)
    for k, v in res.iteritems():
        obj={}
#        take all the fields of an element
        for k1,v1 in v.iteritems():
            if isinstance(v1, list):
                if len(v1)==1:
                    obj[k1]=v1[0]
                else:
                    obj[k1]=v1
            else:
                obj[k1]=v1
        r.append(obj)
    return r   

def opsTest():
    u1 = [{'id':1,'tag':['ciao1','ciao2'],'smt':"else"}],[{'id':2,'tag':['ciao1','ciao2','ciao3']}]  
    split = splitObjects(u1, ["id"], ['tag'])
    print split
#    aggregated=aggregateData(merged,'id')
#    print("aggregated %s"%aggregated)

def findBest():
    r=[1,8,2,3,8,9,9,10,1]
    bests=[]
    not_bests=[]
    best_v=None;
    for e in r:
        if best_v is None:
            best_v=e
            bests.append(e)
        elif e>best_v:
            for b in bests:
                bests.remove(b)
                not_bests.append(b)
            bests.append(e)
            best_v=e
        elif e==best_v:
            bests.append(e) 
    print bests
    print not_bests
    
if __name__ == "__main__":
    findBest()
#    objects=[]
#    for i in range(1,10):
#        item={}
#        item['id']=i
#        item['a']=i
#        item['b']=i
#        item['c']=i
#        objects.append(item)
#        
#    condition={}
#    condition['field']='a'
#    condition['value']='3'
#    condition['operator']='<'
#    condition2={}
#    condition2['field']='a'
#    condition2['value']='8'
#    condition2['operator']='>'
#    condition3={}
#    condition3['field']='a'
#    condition3['value']='5'
#    condition3['operator']='=='
#    print filterData(objects,[condition,condition2,condition3])

