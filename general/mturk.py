'''
Created on Apr 22, 2013

@author: stefanotranquillini
'''


from boto.mturk.question import ExternalQuestion
from boto.mturk.connection import MTurkConnection, HIT       
import logging

log = logging.getLogger(__name__)

class mTurk():
    ACCESS_ID =''
    SECRET_KEY = ''
    HOST = ''
    mtc = None
    log=None
    def __init__(self,access_id,secret_key,debug=True):
        self.ACCESS_ID=access_id
        self.SECRET_KEY=secret_key
        if debug:
            self.HOST='mechanicalturk.sandbox.amazonaws.com'
        else:
            raise Exception('sure you want to spend money')
        
        self.mtc = MTurkConnection(aws_access_key_id=self.ACCESS_ID,
                              aws_secret_access_key=self.SECRET_KEY,
                              host=self.HOST)
        
    def getBalance(self):
        return self.mtc.get_account_balance()
    
    def hasEnoughMoney(self,cost):
        return cost<self.getBalance()
    
    
    def approveAssignemnt(self,a_id,feedback="Thanks for contribution"):
        assignment= self.mtc.get_assignment(a_id)[0]
        log.debug("%s",assignment.__dict__)

        if assignment.AssignmentStatus!="Approved":
            ret = self.mtc.approve_assignment(a_id, feedback)
            log.debug("approve ret: %s",ret)
        else:
            log.debug("already approvred")
            
    def rejectAssigment(self,a_id,feedback="Sorry, but your work was not satifactory"):
        ret = self.mtc.reject_assignment(a_id, feedback)
        log.debug("reject ret: %s",ret)

    
    def createExternalQuestion(self,title,description,keywords,url,duration,reward):
        ex_q=ExternalQuestion(url,1000)  
        res=self.mtc.create_hit(question=ex_q,max_assignments=1,title=title,description=description,keywords=keywords,duration = duration,reward=reward)   
        log.debug("created external question %s",res[0])
        return res[0]
    
    def getDataFromHit(self, assignmentId, workerId):
        assignment= self.mtc.get_assignment(assignmentId)[0]
        log.debug("Answers of the worker %s",  assignment.WorkerId)
        if assignment.WorkerId == workerId: 
            ret = {}
            for question_form_answer in assignment.answers[0]:
                if len(question_form_answer.fields)>1:
                    log.debug("answers are >1")
                    ret[question_form_answer.qid]=question_form_answer.fields
                else:
                    ret[question_form_answer.qid]=question_form_answer.fields[0]
                
        return ret
#                print question_form_answer.qid," - "," ".join(question_form_answer.fields)           
#        # for r in res:        
#            # print "Your hit ID is this %s -> https://workersandbox.mturk.com/mturk/preview?groupId=%s"%(r.HITId,r.HITTypeId))
#        
#    # def printAllHits(self):
#    #        hits=self.mtc.get_all_hits()
#    #        for hit in hits:
#    #            print printAtt(hit,'HITId')            
#            
#  #   def rejectAllHITs(self):
#  #         hits=self.mtc.get_all_hits()
#  #         for hit in hits:
#  #             assignements = self.mtc.get_assignments(hit.HITId)
#  #             for assignment in assignements:
#  #                 try:
#  #                     self.mtc.reject_assignment(assignment.AssignmentId, "i'm just testing this functionality")
#  #                     print "Rejected the assignment %s of HIT %s"%(assignment.AssignmentId,hit.HITId)
#  #                 except Exception:
#  #                     print "ERROR with the assignment %s of HIT %s"%(assignment.AssignmentId,hit.HITId)
#  # #           ret = self.mtc.disable_hit(hit.HITId, "HITDetail")
##            print ret   