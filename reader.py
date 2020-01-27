#!/usr/bin/python
from common import *
import random
from time import sleep

myS3Tester = MyS3Tester()

runDelete = (myS3Tester.getArgv(1, "") == 'delete')

if (runDelete):
    for i in range(myS3Tester.getCount(2)):
        key = myS3Tester.makeKey(myS3Tester.getTestFilename(), myS3Tester.getPrefix(), str(i))
        if (myS3Tester.isDeletable(key)):
            print("Delete " + key + "...")
            res = myS3Tester.s3cli.delete_object(Bucket=myS3Tester.bucketName, Key=key)
            # A 204 is returned whether the object exists or not
            # print res['ResponseMetadata']['HTTPStatusCode']
    exit()


while True:
    #sleep(random.random())
    k = myS3Tester.dequeue()
    if (k != None):
        try:
            obj = myS3Tester.s3cli.get_object(Bucket=myS3Tester.bucketName, Key=k)
            myS3Tester.s3cli.download_file(myS3Tester.bucketName, k, "/tmp/"+k)
            print(k + " --> " + str(obj['Metadata']))
        except:
            print(" *** Download error for " + k)
