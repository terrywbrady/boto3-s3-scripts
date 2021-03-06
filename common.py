#!/usr/bin/python
import boto3
#import ConfigParser
import configparser
import sys
import glob
import os
import redis
from threading import Lock
from botocore.config import Config

class MyS3Tester:
    def __init__(self):
        #self.config = ConfigParser.RawConfigParser()
        self.config = configparser.RawConfigParser()
        self.config.read('service.ini')
        self.queue = redis.Redis(
            self.getConfigVal("redis", "host", "localhost"),
            self.getConfigIntVal("redis", "port", 6379)
        )
        self.storage = self.getStorageService()
        self.s3cli = self.getClient(self.storage)
        self.bucketName = self.getBucket(self.storage)
        self.sleepFactor = self.getConfigFloatVal("driver", "sleep-factor", .1)
        self.lock = Lock()

        os.makedirs("/tmp/" + self.getPrefix(), exist_ok=True)

    def getConfigIntVal(self, section, key, defval):
        return int(self.getConfigVal(section, key, defval))

    def getConfigFloatVal(self, section, key, defval):
        return float(self.getConfigVal(section, key, defval))

    def getConfigVal(self, section, key, defval):
        v = self.config.get(section, key)
        if v:
            return v
        return defval

    def getDefCount(self):
        return self.getConfigIntVal("driver", "default-count", 10)

    def getTestFilename(self):
        return self.getConfigVal("driver", "test-filename", "common.py")

    # get object count from command line, default to config value
    def getCount(self, argindex):
        return int(self.getArgv(argindex, self.getDefCount()))

    def getArgv(self, argindex, defval):
        if len(sys.argv) > argindex:
            return sys.argv[argindex]
        return defval

    def getPrefix(self):
        return self.getConfigVal("driver", "prefix", "test-prefix")

    def getStorageService(self):
        return self.getConfigVal("driver", "storage", "minio")

    def isDeletable(self, key):
        if (key.startswith(self.getPrefix())):
            return self.getConfigVal("driver", "deletable-prefix", "test-prefix")
        return False

    def getClient(self, storage):
        opts = {'config': Config(
            retries = dict(
                max_attempts = 1
            )
        )}
        #opts = {}
        if (storage == "minio"):
            opts['aws_access_key_id']=self.config.get(storage, "accessKey")
            opts['aws_secret_access_key']=self.config.get(storage, "secretKey")
            opts['endpoint_url']=self.config.get(storage, "endpointUrl")
        cli = boto3.client('s3', **opts)
        return cli

    def getBucket(self, storage):
        return self.getConfigVal(storage, "bucket", "test-bucket")

    def updateMetadata(self, key, mk, mv):
        #obj = self.s3cli.get_object(Bucket=self.bucketName, Key=key)
        objhead = self.s3cli.head_object(Bucket = self.bucketName, Key = key)
        m = objhead["Metadata"]
        m[mk] = mv
        self.s3cli.copy_object(
            Bucket = self.bucketName,
            Key = key,
            CopySource = self.bucketName + '/' + key,
            Metadata = m,
            MetadataDirective='REPLACE'
        )

    def makeKey(self, filename, prefix, suffix):
        return prefix + "/" + filename + "." + suffix

    def upload(self, filename, prefix, suffix):
        key = self.makeKey(filename, prefix, suffix)
        self.s3cli.upload_file(filename, self.bucketName, key,
            ExtraArgs={
                "Metadata":{
                    "state":"initial"
                }
            })
        self.enqueue(key)
        self.updateMetadata(key, "foo", "bar")

    def enqueue(self, key):
        self.queue.lpush("queue", key)
        print("Creating " + key)

    def dequeue(self):
        with self.lock:
            k = self.queue.rpop("queue")
            if k:
                return k.decode("utf-8")
        return None

    def listObjects(self, prefix, maxObj):
        if (maxObj == 0):
            return

        list = self.s3cli.list_objects_v2(
            Bucket=self.bucketName,
            MaxKeys=maxObj,
            Prefix=prefix
        )

        if ('Contents' in list):
            for lobj in list['Contents']:
                key=lobj['Key']
                obj = self.s3cli.get_object(Bucket=self.bucketName, Key=key)
                print(key + " --> " + str(obj['Metadata']))

    def randomPause(self):
        if (self.sleepFactor > 0):
            sleep(random.random() * self.sleepFactor)

    def download(self, k):
        osize = -1
        try:
            obj = self.s3cli.get_object(Bucket=self.bucketName, Key=k)
            status = obj['ResponseMetadata']['HTTPStatusCode']
            pre = "   " if (status == 200) else " * "
            print(pre + str(status) + " " + k + " --> " + str(obj['Metadata']))
            osize = obj['ContentLength']
        except Exception as e:
            print(" *** Object Retrieval error for " + k)
            print(e)
            return
        try:
            fname = "/tmp/" + k
            self.s3cli.download_file(self.bucketName, k, fname)
            if (osize != os.path.getsize(fname)):
              print(" * File size mismatch for " + fname)
        except Exception as e:
            print(" *** Download error for " + k)
            print(e)
