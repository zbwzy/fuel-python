'''
Created on Sep 30, 2015

@author: zhangbai
'''
import os, time
from kazoo.client import KazooClient
from kazoo.client import KazooState

import logging
logging.basicConfig()

class ZooKeeperCounter():
    def __init__(self, hosts, counter_name, init_counter_value=300, timeout=10):
        self.hosts = hosts
        self.zk_client = None
        self.timeout = timeout
        self.counter_name = counter_name
        self.init_counter_value = init_counter_value
        
        if init_counter_value == None :
            self.init_counter_value = 300
            pass

        pass

    def create_zk_client(self):
        try:
            zk_availability = False
            self.zk_client = KazooClient(hosts=self.hosts, timeout=self.timeout)
            self.zk_client.start(timeout=self.timeout)
            
            if self.zk_client.state == 'CONNECTED':
                zk_availability = True
                pass

            if zk_availability:
                print "zookeeper is available!"
                pass
        except Exception, ex:
            self.init_ret = False
            self.err_str = "Create KazooClient failed! Exception: %s" % str(ex)
            print self.err_str
            return
        
    def get_counter(self):
        counter = self.zk_client.Counter("/counter/%s" % self.counter_name, default=self.init_counter_value)
#         counter -= 1
#         curValue = counter.value
#         counter += (300-curValue)
        print 'currentCounterValue=%s' % counter.value 
        return counter
    
    def destroy(self):
        self.zk_client.stop()
        self.zk_client = None
        pass
        
    def __del__(self):
        print 'ZooKeeperCounter.__del__======='
        self.destroy()
        print 'ZooKeeperCounter.__del__#######'
        pass


def main():
    #zk hosts
    zookeeper_hosts = "54.205.0.210:2181"
    
    ##################
    print 'counter========='
    counter_name = 'keystone_weight'
    zk_counter = ZooKeeperCounter(hosts=zookeeper_hosts, counter_name=counter_name)
    
    zk_counter.create_zk_client()
    counter = zk_counter.get_counter()
    value = counter.value
    print 'curValue=%s' % value
    
    counter -= 1
    print 'After substract 1, curValue=%s' % counter.value
#     zk_counter.destroy()
    print 'counter#######'
    pass

if __name__ == "__main__":
    try:
        print "Start to test zk counter============="
        main()
        print "DONE test zk counter######"
    except Exception, ex:
        print "Exception: %s" % str(ex)
        quit()
        
