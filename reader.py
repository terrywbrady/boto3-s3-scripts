#!/usr/bin/python
from common import *
import random
from time import sleep

myS3Tester = MyS3Tester()

param = myS3Tester.getArgv(1, "")
runDelete = (param == 'delete')

if (runDelete):
    for i in range(myS3Tester.getCount(2)):
        key = myS3Tester.makeKey(myS3Tester.getTestFilename(), myS3Tester.getPrefix(), str(i))
        if (myS3Tester.isDeletable(key)):
            print("Delete " + key + "...")
            res = myS3Tester.s3cli.delete_object(Bucket=myS3Tester.bucketName, Key=key)
            # A 204 is returned whether the object exists or not
            # print res['ResponseMetadata']['HTTPStatusCode']
    exit()

if (param != ""):
    myS3Tester.download(param)
else:
    try:
        while True:
            myS3Tester.randomPause()
            k = myS3Tester.dequeue()
            if (k != None):
                myS3Tester.download(k)
    except KeyboardInterrupt as e:
        print(" *** User interrupt, ending read")
