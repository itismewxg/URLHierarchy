import sys 
import os
import argparser
import json
import base64
import random
from copy import copy
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import sample_pb2
from google.protobuf.descriptor import FieldDescriptor
from protobuf_to_dict import protobuf_to_dict, TYPE_CALLABLE_MAP

class hashjoin:
    """ 
        hashjoin: hold the dict(map) of the token and its merge or partial merge message
            -- initilization from leftover serialized data of the join dict
            -- in journel, write the serialized data into the leftover in a time policy 
    """
    __init__(self, leftover):



class enricher:
    """ 
        initialization to get enrich handlers
        to do the enrich in a sequence and execute all the active handlers
        e.g. so far,
            -- the maxmind geoip handler
            -- the uaparser for th ua parsing handler
            -- url pattern to application-type
            -- claculate out the 
    """

class kreader:
    """ 
        initialze and prepare the reader
        get the infinite loop iterator to get the message
    """
    __init__(self, topic, group, brokers, offsets):
        self.consumer = KafkaConsumer(topic, group_id=group, bootstrap_servers=brokers)
        for offset in offsets:
            consumer.seek(offset['offset'], whence=0, partition=offset['partition'])

    msg_iterator(self):
        return self.consumer

def build_arg_parser():
    parser = argparse.ArgumentParser(description="Parquet Loader")
    parser.add_argument("-f", "--conf", type=file, help="", required=True)
    parser.add_argument("-c", "--customer", type=str, help="", default="group")
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    return parser

def main():

    # To consume latest messages and auto-commit offsets
    consumer = KafkaConsumer('my-topic',
                         group_id='my-group',
                         bootstrap_servers=['localhost:9092'])
    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))

if __name__ == '__main__':
    main()


