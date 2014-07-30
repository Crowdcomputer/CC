"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from utils import mergeData

#from general.test_utils import createProcess, createTasks, createTaskInstance,lenInsOut,\
#    addTaskInstance
#from general.models import Data
import logging
from django.utils import unittest

log=logging.getLogger(__name__)

def findObject(list,id):
    for obj in list:
        if obj['id']==id:
            return obj

class DataFunctionTest(unittest.TestCase):
    
    def test_mergeData(self):
        obj1=[{'id':'1','a':'a'},{'id':'2','a':'a'}]
        obj2={'id':'1','b':'b'}
        res=mergeData([obj1,obj2])
        res_o = findObject(res,'1')
        self.assertEqual(res_o, {'id':'1','a':'a'}, 'Nope %s'%res_o)
        res=mergeData([obj1,obj2],'id')
        res_o = findObject(res,'1')
        self.assertEqual(res_o, {'id':'1','a':'a','b':'b'}, 'Nope %s'%res_o)

#class TestUtilTask(TestCase):
#    
#    def test_merge(self):
#        self.process=createProcess('test')
#        self.task=createTasks('test',self.process)
#        createTaskInstance(self.task,[{'resource_id':'kqtiwtiely2p0fskwigv','resource_url':'http://univerius.com/view/static/files/resources/kqtiwtiely2p0fskwigv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/mjqbri0gvnlqray4sd09'}] )
#        createTaskInstance(self.task, [{'resource_id':'ead4sugsro2wuon74rxh','resource_url':'http://univerius.com/view/static/files/resources/ead4sugsro2wuon74rxh'},{'resource_id':'tuujhzr8hhea30lqqbod','resource_url':'http://univerius.com/view/static/files/resources/tuujhzr8hhea30lqqbod'}])
#        createTaskInstance(self.task, [{'resource_id':'kqtiwtiely2p0fskwigv','resource_url':'http://univerius.com/view/static/files/resources/sdfsadfv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/dsfad'}])
#        totlen=lenInsOut(self.task)
#        ret = mergeResults(self.task)
#        self.assertEqual(len(ret), totlen, 'merged lenght is not 1')
#
#    def test_join(self):
#        inputs=[]
#        self.process=createProcess('test')
#        self.task0=createTasks('test0',self.process)
#        createTaskInstance(self.task0,[{'resource_id':'kqtiwtiely2p0fskwigv','resource_url':'http://univerius.com/view/static/files/resources/kqtiwtiely2p0fskwigv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/mjqbri0gvnlqray4sd09'}] )
#        createTaskInstance(self.task0, [{'resource_id':'ead4sugsro2wuon74rxh','resource_url':'http://univerius.com/view/static/files/resources/ead4sugsro2wuon74rxh'},{'resource_id':'tuujhzr8hhea30lqqbod','resource_url':'http://univerius.com/view/static/files/resources/tuujhzr8hhea30lqqbod'}])
#        createTaskInstance(self.task0, [{'resource_id':'kqtiwasdfasguu','resource_url':'http://univerius.com/view/static/files/resources/kqtiwtiely2p0fskwigv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/mjqbri0gvnlqray4sd09'}])
#        inputs.append(mergeResults(self.task0))
#        self.task1=createTasks('test1',self.process)
#        createTaskInstance(self.task1,[{'resource_id':'kqtiwtiely2p0fskwigv','resource_url_1':'a1'}] )
#        createTaskInstance(self.task1, [{'resource_id':'ead4sugsro2wuon74rxh','resource_url_1':'b1'}])
#        createTaskInstance(self.task1, [{'resource_id':'kqtiwasdfasguu','resource_url_1':'c1'}])
#        inputs.append(mergeResults(self.task1))
#        ret = joinTasks('resource_id', inputs)
##        the merge of the prev input should be 5
#        self.assertEqual(len(ret), 5, 'join len is not correct')
#
#    def test_split(self):
#        inputs=[]
#        self.process=createProcess('test')
#        self.task0=createTasks('test0',self.process)
#        createTaskInstance(self.task0,[{'resource_id':'kqtiwtiely2p0fskwigv','resource_url':'http://univerius.com/view/static/files/resources/kqtiwtiely2p0fskwigv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/mjqbri0gvnlqray4sd09'}] )
#        createTaskInstance(self.task0, [{'resource_id':'ead4sugsro2wuon74rxh','resource_url':'http://univerius.com/view/static/files/resources/ead4sugsro2wuon74rxh'},{'resource_id':'tuujhzr8hhea30lqqbod','resource_url':'http://univerius.com/view/static/files/resources/tuujhzr8hhea30lqqbod'}])
#        createTaskInstance(self.task0, [{'resource_id':'kqtiwasdfasguu','resource_url':'http://univerius.com/view/static/files/resources/kqtiwtiely2p0fskwigv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/mjqbri0gvnlqray4sd09'}])
#        inputs.append(mergeResults(self.task0))
#        self.task1=createTasks('test1',self.process)
#        createTaskInstance(self.task1,[{'resource_id':'kqtiwtiely2p0fskwigv','resource_url_1':'a1'}] )
#        createTaskInstance(self.task1, [{'resource_id':'ead4sugsro2wuon74rxh','resource_url_1':'b1'}])
#        createTaskInstance(self.task1, [{'resource_id':'kqtiwasdfasguu','resource_url_1':'c1'}])
#        inputs.append(mergeResults(self.task1))
#        ret = joinTasks('resource_id', inputs)
#        c=combinations(ret,2)
##        if it's 5 elements-> 5!/(2!*3!)
#        self.assertEqual(len(c),10,'Combinations are wrong %s ' %c )
#        s1=splitNM(ret,3,1)
##        if it's 5 elements
#        self.assertEqual(len(s1),2,'Overlap length is wrong %s ' %s1 )
#        self.assertEqual(s1[0][2],s1[1][0],'No overlapping of the first and last %s ' %s1 )
#        s2=splitN(ret,2)
#        self.assertEqual(len(s2),3,'SplitN length is wrong %s ' %s2 )
##        the merge of the prev input should be 5
#
#
#
#class ProcessTest(TestCase):
#    
#    def testT1toT2(self):
#        log.info('--------------------------------------')
#        log.info('testT1toT2')
##        create process
#        process=createProcess('test')
##        create task T1, with 2 output needed and no input
#        T1=createTasks('T1',process)
#        T1.instances_required=2
#        T1.save()
#        
##        create task T2 with T1 Input
#        T2=createTasks('T2',process)
#        T2.instances_required=1
##        no split, all in one
#        T2.split=1
#        T2.input_task=[T1]
#        T2.save()
##        start the process
##        control the status of T1 and instances created
#        startProcess(process)
#        self.assertEqual(process.status, 'PR', 'Process Not started')
#        self.assertEqual(T1.taskinstance_set.all().count(), 2, 'T1 instances are wrong')
#        self.assertEqual(T1.taskinstance_set.filter(output=None).count(), 2, 'T1 instances have outputs')
##        print ('T1.status = %s . is PR? %s' % (self.T1.status,(self.T1.status=='PR')))
##        self.assertEqual(T1.status, 'PR', 'T1 Not started.Status is %s'%(T1.status))
##        T1 status is ST!
#        addTaskInstance(T1,[{'resource_id':'kqtiwtiely2p0fskwigv','resource_url':'http://univerius.com/view/static/files/resources/kqtiwtiely2p0fskwigv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/mjqbri0gvnlqray4sd09'}] )
#        addTaskInstance(T1, [{'resource_id':'ead4sugsro2wuon74rxh','resource_url':'http://univerius.com/view/static/files/resources/ead4sugsro2wuon74rxh'},{'resource_id':'tuujhzr8hhea30lqqbod','resource_url':'http://univerius.com/view/static/files/resources/tuujhzr8hhea30lqqbod'}])
#        triggerTasks(process)
##        self.assertEqual(T1.status, 'FN', 'T1 Not finished. Status is %s'%(T1.status))
##        self.assertEqual(T2.status, 'PR', 'T2 Not started. Status is %s'%(T2.status))
#        self.assertEqual(T2.taskinstance_set.all().count(), 1, 'T2 instances are wrong')
#
#
#    
#    def testT1andT2(self):
#        log.info('--------------------------------------')
#        log.info('testT1andT2toT3')
##        create process
#        process=createProcess('test')
#        
#        T1=createTasks('T1',process)
#        T1.instances_required=2
#        T1.save()
#        
#        T2=createTasks('T2',process)
#        T2.instances_required=2
#        T2.save()
#        
#        T3=createTasks('T3',process)
#        T3.instances_required=1
#        T3.input_task=[T1,T2]
#        T3.input_task_field='resource_id'
#        T3.split=1
#        T3.save()
#        
#        T4=createTasks('T4',process)
#        T4.instances_required=1
#        T4.input_task=[T1,T2]
#        T4.input_task_field='resource_id'
#        T4.split=2
#        T4.split_field_N=1
#        T4.save()
#        
#        T5=createTasks('T5',process)
#        T5.instances_required=1
#        T5.input_task=[T1,T2]
#        T5.input_task_field='resource_id'
#        T5.split=3
#        T5.split_field_N=2
#        T5.split_field_M=1
#        T5.save()
#        
#        T6=createTasks('T6',process)
#        T6.instances_required=1
#        T6.input_task=[T1,T2]
#        T6.input_task_field='resource_id'
#        T6.split=4
#        T6.split_field_N=2
#        T6.save()
#        
#        
##        start the process
##        control the status of T1 and instances created
#        startProcess(process)
#        self.assertEqual(process.status, 'PR', 'Process Not started')
#        self.assertEqual(T1.taskinstance_set.all().count(), 2, 'T1 instances are wrong')
#        self.assertEqual(T1.taskinstance_set.filter(output=None).count(), 2, 'T1 instances have outputs')
##        print ('T1.status = %s . is PR? %s' % (T1.status,(T1.status=='PR')))
##        assertEqual(T1.status, 'PR', 'T1 Not started')
##        T1 status is ST!
#        addTaskInstance(T1,[{'resource_id':'kqtiwtiely2p0fskwigv','resource_url':'http://univerius.com/view/static/files/resources/kqtiwtiely2p0fskwigv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/mjqbri0gvnlqray4sd09'}] )
#        addTaskInstance(T1, [{'resource_id':'ead4sugsro2wuon74rxh','resource_url':'http://univerius.com/view/static/files/resources/ead4sugsro2wuon74rxh'},{'resource_id':'tuujhzr8hhea30lqqbod','resource_url':'http://univerius.com/view/static/files/resources/tuujhzr8hhea30lqqbod'}])
#        addTaskInstance(T2,[{'resource_id':'kqtiwtiely2p0fskwigv','resource_url_1':'a1'}] )
#        addTaskInstance(T2, [{'resource_id':'ead4sugsro2wuon74rxh','resource_url_1':'b1'}])
#        triggerTasks(process)
##        input is 4
##        if no split then 1
#        self.assertEqual(T3.taskinstance_set.all().count(), 1, 'T3 instances are wrong')
##        if split in set of 1 then 4
#        self.assertEqual(T4.taskinstance_set.all().count(), 4, 'T4 instances are wrong')
##        if split in set of 2 with 1 overlapp then 3 -> (1,2) (2,3) (3,4)
#        self.assertEqual(T5.taskinstance_set.all().count(), 3, 'T5 instances are wrong')
##        if combination of 2 then -> 4!/2!*2! = 6
#        self.assertEqual(T6.taskinstance_set.all().count(), 6, 'T6 instances are wrong')
#
#
#class TestMachineTask(TestCase):
#    
#    def testcall(self):
#        import requests
#        import json
#        process=createProcess('test')
#        task=createTasks('test',process)
#        createTaskInstance(task,[{'resource_id':'kqtiwtiely2p0fskwigv','resource_url':'http://univerius.com/view/static/files/resources/kqtiwtiely2p0fskwigv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/mjqbri0gvnlqray4sd09'}] )
#        createTaskInstance(task, [{'resource_id':'ead4sugsro2wuon74rxh','resource_url':'http://univerius.com/view/static/files/resources/ead4sugsro2wuon74rxh'},{'resource_id':'tuujhzr8hhea30lqqbod','resource_url':'http://univerius.com/view/static/files/resources/tuujhzr8hhea30lqqbod'}])
#        createTaskInstance(task, [{'resource_id':'kqtiwtiely2p0fskwigv','resource_url':'http://univerius.com/view/static/files/resources/kqtiwtiely2p0fskwigv'},{'resource_id':'mjqbri0gvnlqray4sd09','resource_url':'http://univerius.com/view/static/files/resources/mjqbri0gvnlqray4sd09'}])
#        ret = mergeResults(task)
#        log.debug("params %s"%ret)
##        r = requests.get("http://localhost:8888/view.php",params=params)
##        log.debug("response %s"%r.text)
#        data={}
#        data['data']=json.dumps(ret)
#        r = requests.post("http://resource.eu01.aws.af.cm/push",data)
#        log.debug("response %s"%r.text)
#        self.assertEqual(r.status_code, 200, "status code is not 200")

