'''
Created on Sep 29, 2015

@author: zhangbai
'''
import os, time
from kazoo.client import KazooClient
from kazoo.client import KazooState
from kazoo.recipe.lock import Lock


class ZooKeeperLock():
    def __init__(self, hosts, id_str, lock_name, timeout=10):
        self.hosts = hosts
        self.id_str = id_str
        self.zk_client = None
        self.timeout = timeout
        self.name = lock_name
        self.lock_handler = None

        self.create_lock()
        pass

    def create_lock(self):
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

        try:
            lock_path = os.path.join("/", "locks", self.name)
            self.lock_handler = Lock(self.zk_client, lock_path)
        except Exception, ex:
            self.init_ret = False
            self.err_str = "Create lock failed! Exception: %s" % str(ex)
            print self.err_str
            return

    def destroy_lock(self):
        #self.release()

        if self.zk_client != None:
            self.zk_client.stop()
            self.zk_client = None

    def acquire(self, blocking=True, timeout=None):
        if self.lock_handler == None:
            return None

        try:
            return self.lock_handler.acquire(blocking=blocking, timeout=timeout)
        except Exception, ex:
            self.err_str = "Acquire lock failed! Exception: %s" % str(ex)
            print self.err_str
            return None

    def release(self):
        if self.lock_handler == None:
            print "release.lock_handler is None!"
            return None
        return self.lock_handler.release()


    def __del__(self):
        print 'ZooKeeperLock.__del__======='
        self.destroy_lock()
        print 'ZooKeeperLock.__del__#######'
        pass


def main():
    #zk hosts
    zookeeper_hosts = "54.205.0.210:2181"
    lock_name = "test"

    lock = ZooKeeperLock(zookeeper_hosts, "myid is 1", lock_name)
    ret = lock.acquire()
    if not ret:
        print "Can't get lock! Ret: %s" % ret
        return

    print "Get lock! Do something! Sleep 10 secs!"
    for i in range(1, 11):
        time.sleep(1)
        print str(i)
        pass

    lock.release()
    
    ##################
    print 'counter========='
    zk_client = KazooClient(hosts=zookeeper_hosts, timeout=10)
    print zk_client.start(timeout=10)
    print 'zkSTATE=%s' % zk_client.state
    
    zk_client.stop()
    print 'couter#######'
    
    
    pass

if __name__ == "__main__":
    try:
        print "Start to test zk lock============="
        main()
        print "DONE acquire zk lock!"
    except Exception, ex:
        print "Exception: %s" % str(ex)
        quit()
        
