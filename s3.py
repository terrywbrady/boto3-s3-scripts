#!/usr/bin/python
from common import *
from time import sleep

myS3Tester = MyS3Tester()

count = myS3Tester.getCount(1)
myS3Tester.listObjects(myS3Tester.getPrefix(), count + 100)

print("==============")

for i in range(count):
  myS3Tester.upload(myS3Tester.getTestFilename(), myS3Tester.getPrefix(), str(i))
  #sleep(.1)

myS3Tester.listObjects(myS3Tester.getPrefix(), count)
