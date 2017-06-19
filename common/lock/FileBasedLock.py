'''
Created on May 12, 2017

@author: zhangbai
'''

import time
import os
import fcntl

from common.file.FileUtil import FileUtil

class FileBasedLock(object):
    '''
    classdocs
    '''


    def __init__(self, lockFilePath=None):
        '''
        Constructor
        '''
        self.lockFilePath = lockFilePath
        pass
    
    def acquire(self, acquireTimeout=60):
        #acquireTimeout Unit is sec
        self.createLocFileIfNotExist()
        self.lockFile= open(self.lockFilePath, 'w')
        acquired = False
        try:
            print ("Try to get lock...")
            fcntl.lockf(self.lockFile, fcntl.LOCK_EX | fcntl.LOCK_NB)
            print ("Get lock successfully!")
            acquired = True
        except Exception, e:
            print (e)
            print ("Fail to get lock!")
            acquired = False
        
        if acquired :
            iLockTime=time.time()
            lock_time=str(iLockTime)
            self.lockFile.write(lock_time)
            return True
        else :
            acquireTime = time.time()
            while time.time() - acquireTime < acquireTimeout :
                pollingInterval = 5
                time.sleep(pollingInterval)
                try:
                    print ("Try to get lock...")
                    fcntl.lockf(self.lockFile, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    print ("Get lock successfully!")
                    acquired = True
                    break
                except Exception, e:
                    print (e)
                    print ("Fail to get lock!")
                    
                acquired = False
        return acquired
    
    def createLocFileIfNotExist(self):
        try:
            dir_path = os.path.dirname(self.lockFilePath)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
                pass
            
            if not os.path.exists(self.lockFilePath):
                cmd = "touch {lock_file_path}".format(lock_file_path=self.lockFilePath)
                os.system(cmd)
                pass
        except Exception, e:
            print 'ERROR:%s' % e
    
    def release(self):
        try:
            print ("Release lock...")
            fcntl.flock(self.lockFile, fcntl.LOCK_UN) 
            print ("Release lock successfully!")
        except Exception, e :
            print 'ERROR:%s' % e
            print ("Release lock exception=%s" % str(e))
        finally :
            try:
                self.lockFile.close()
            except Exception, e :
                print 'ERROR:%s' % e
                print ("lockFile.close exception=%s" % str(e))
                pass
            pass
        pass
    
    
