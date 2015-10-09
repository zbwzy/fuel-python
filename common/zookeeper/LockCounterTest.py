'''
Created on Oct 8, 2015

@author: zhangbai
'''
import sys

sys.path.append("/Users/zhangbai/Documents/AptanaWorkspace/fuel-python")

import time
from common.zookeeper.ZooKeeperLock import ZooKeeperLock
from common.zookeeper.ZooKeeperCounter import ZooKeeperCounter

if __name__ == '__main__':
    print "start test==============="
    print "startTime=%s" % time.strftime('%Y-%m-%d %H:%M:%S')
    
    zookeeper_hosts = "54.205.0.210:2181"
    lock_name = "glance_weight_lock"
 
    lock = ZooKeeperLock(zookeeper_hosts, "myid is 1", lock_name)
    ###########################
    ret = lock.acquire() #get lock
    print "getLockTime=%s" % time.strftime('%Y-%m-%d %H:%M:%S')
     
    if not ret:
        print "Can't get lock! Ret: %s" % ret
#         return
 
    print "Get lock! Do something! Sleep 10 secs!"
    for i in range(1, 11):
        time.sleep(1)
        print str(i)
        pass
     
    print 'counter========='
    counter_name = 'glance_weight_counter'
    zk_counter = ZooKeeperCounter(hosts=zookeeper_hosts, counter_name=counter_name)
    print "getCounterTime=%s" % time.strftime('%Y-%m-%d %H:%M:%S')
    
    zk_counter.create_zk_client()
    counter = zk_counter.get_counter()
    print 'curValue=%s' % counter.value
    counter -= 1
#     counter += (300 - counter.value)
    print 'After substract 1, curValue=%s' % counter.value
#     zk_counter.destroy()
    print "releaseCounterTime=%s" % time.strftime('%Y-%m-%d %H:%M:%S')
    print 'counter#######'
    
    print "releaseLockTime=%s" % time.strftime('%Y-%m-%d %H:%M:%S')
    lock.release() #release lock
    
    print "endTime=%s" % time.strftime('%Y-%m-%d %H:%M:%S')
    
    print "test done###########"
    pass




    pass