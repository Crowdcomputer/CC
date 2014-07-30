'''
Created on Jul 19, 2013

@author: stefanotranquillini
'''
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
            not_bests+=bests
            bests=[]
            bests.append(e)
            best_v=e
        elif e==best_v:
            bests.append(e)
        else:
            not_bests.append(e) 
    print bests
    print not_bests
    
if __name__ == "__main__":
    findBest()