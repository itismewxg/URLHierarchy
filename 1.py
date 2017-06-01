import sys 
import os
import argparse
import json
import base64
import random
from copy import copy
from kafka import KafkaConsumer
from kafka.errors import KafkaError
import signals_pb2
from google.protobuf.descriptor import FieldDescriptor
from protobuf_to_dict import protobuf_to_dict, TYPE_CALLABLE_MAP
import geoip2.database
from ua_parser import user_agent_parser

import log

LOGGER = log.get_logger()

user_agent_parser.MAX_CACHE_SIZE = 10000

def show_pb(pb):
    type_callable_map = copy(TYPE_CALLABLE_MAP)
    # convert TYPE_BYTES to a Python bytestring
    type_callable_map[FieldDescriptor.TYPE_BYTES] = str 
                                    
    # my_message is a google.protobuf.message.Message instance
    dm = protobuf_to_dict(pb, type_callable_map=type_callable_map)
    print json.dumps(dm)


class mergemeta:
    """
        metafile stored 2 parts in the metafile:
            1. checkpoint of the consumer 
            2. the leftover dict of the joiner message
        
        1st line is the commited consumed offsets by merger's outputer
        e.g.
        ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
            <json dump of partition: [{1:1000],[2,12020],[3,787]}]>
        ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        from the 2nd line, line by line
        b64 for each line: <serialized pb message1>
            -- initilization from leftover serialized data of the join dict
            -- b64 for such string easy to be kept from reading
    """
    def __init__(self, mfile):
        self.meta_file = mfile
        if not os.path.exists(mfile):
            self.partition_offsets = {}
            self.leftover_messages = {}
            return
        else:
            read_offset = False
            with open("r", mfile) as f:
                for l in f:
                    l = l.strip()
                    if not read_offset:
                        self.partition_offsets = json.read_from_string(l)
                        read_offset = True
                    else:
                        sm = base64.b64decode(l)
                        pb_msg = signals_pb2.Telemetry()
                        pb_msg.ParseFromString(m)
                        self.leftover_messages[pb_msg.sessionToken] = pb_msg


    def get_partition_offsets(self):
        return self.partition_offsets

    def get_leftover_pbmsg(self):
        return self.leftover_messages

    def update_partition_offset(self, p, o):
        self.partition_offsets[p] = o

    def save(self, partoffsets, leftover):
        f = open("w", self.meta_file)
        f.write("%s\n" % json.dumps(self.partition_offsets))
        for k, v in self.leftover_message:
            b64smsg = base64.b64encode(smessage.SerializeToString(v))
            f.write("%s\n", b64smsg)
        f.close()


class hashjoin:
    @staticmethod
    def apply(leftover, pb):
        stoken = pb.sessionToken
        uv = pb.uniqv[0]
        if stoken in leftover.keys():
            if uv in leftover[stoken].uniqv:
                LOGGER.warning("send twice message", {"stoken":stoken, "uniqv":uniqv})
                return
            else:
                leftover[stoken].merge(pb)
                show_pb(leftover[stoken])
        else:
            """  """
            leftover[pb.sessionToken] = pb
            show_pb(pb)

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
    def __init__(self):
        self.asnReader = geoip2.database.Reader('/home/osprey/workspace/osprey/apiserver/GeoLite2-ASN_20170523/GeoLite2-ASN.mmdb') 
        self.locReader = geoip2.database.Reader('/home/osprey/workspace/osprey/apiserver/GeoLite2-City_20170502/GeoLite2-City.mmdb')

    def enrich_pb_msg(self, pb):
        """
            sequencely enrich message
            1) ua
            2) ip
        """
        ua = pb.httpReqInfo.ua
        pb.httpReqInfo.parsedUaInfo.os.family = uap["os"].family
        pb.httpReqInfo.parsedUaInfo.os.major = uap["os"].major
        pb.httpReqInfo.parsedUaInfo.os.minor = uap["os"].minor
        pb.httpReqInfo.parsedUaInfo.os.patch = uap["os"].patch
        pb.httpReqInfo.parsedUaInfo.os.patch_minor = uap["os"].patch_minor
        pb.httpReqInfo.parsedUaInfo.browser.family = uap["browser"].family
        pb.httpReqInfo.parsedUaInfo.os.major = uap["browser"].major
        pb.httpReqInfo.parsedUaInfo.os.minor = uap["browser"].minor
        pb.httpReqInfo.parsedUaInfo.os.patch = uap["browser"].patch
        pb.httpReqInfo.parsedUaInfo.os.patch_minor = uap["browser"].patch_minor
        pb.httpReqInfo.parsedUaInfo.device.family = uap["browser"].family
        pb.httpReqInfo.parsedUaInfo.device.brand = uap["browser"].brand
        pb.httpReqInfo.parsedUaInfo.device.model = uap["browser"].model
        
    def _get_parsed_uainfo(ua):
        uap = {}
        try:
            uap["os"] = user_agent_parser.ParseOS(ua)
            uap["device"] = user_agent_parser.ParseDevice(ua)
            uap["browser"] = user_agent_parser.ParseUserAgent(ua)
        except Exception as e:
            print e
        return uap 

    def _get_geoip_info(ip):
        geoip = {}
        try:
            asnRsp = asnReader.asn(ip)
            geoip["asn_num"] = asnRsp.autonomous_system_number
            geoip["asn"] = asnRsp.autonomous_system_organization
            locRsp = locReader.city(ip)
            geoip["country"] = locRsp.country.name
            geoip["city"] = locRsp.city.name
            geoip["location"] = {}
            geoip["location"]["lon"] = locRsp.location.longitude
            geoip["location"]["lat"] = locRsp.location.latitude
            geoip["postalcode"] = locRsp.postal.code
        except Exception as e:
            print e
        return geoip




class kreader:
    """ 
        initialze and prepare the reader
        get the infinite loop iterator to get the message
    """
    def __init__(self, topic, group, brokers, offsets):
        self.consumer = KafkaConsumer(topic, group_id=group, bootstrap_servers=brokers, auto_offset_reset='latest')
        for offset in offsets:
            consumer.seek(offset['offset'], whence=0, partition=offset['partition'])

    def msg_iterator(self):
        return self.consumer

def build_arg_parser():
    parser = argparse.ArgumentParser(description="Parquet Loader")
    parser.add_argument("-f", "--conf", type=file, help="", required=True)
    parser.add_argument("-c", "--customer", type=str, help="", default="group")
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    return parser

def main():

    meta = mergemeta("metafile")
    enrich = enricher() 
    # To consume latest messages and auto-commit offsets
    r = kreader('osprey', 'merger', ['localhost:9092'], meta.get_partition_offsets())

    for message in r.msg_iterator():
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        LOGGER.warning("get message", {"topic": message.topic, "part" : message.partition,
            "offset": message.offset, "key":message.key})
        
        print message
        print len(message.value)
        
        try:
            pb_msg = signals_pb2.Telemetry()
            pb_msg.ParseFromString(message.value)
            hashjoin.apply(meta.get_leftover_pbmsg(), pb_msg)
        except Exception as e:
            print e

if __name__ == '__main__':
    main()


#!/usr/local/bin/python

import sys 
import signals_pb2
import base64
import random
from copy import copy
from google.protobuf.descriptor import FieldDescriptor
from protobuf_to_dict import protobuf_to_dict, TYPE_CALLABLE_MAP
import json
from elasticsearch import Elasticsearch
import urllib2

ES_HOST = {
    "host" : "localhost", 
    "port" : 9200
}

INDEX_NAME = 'enriched-osprey-test'
TYPE_NAME = 'event'

ID_FIELD = 'sessionToken'

def get_dict_of_message(bm):
    m = base64.b64decode(bm)
    smessage = signals_pb2.Telemetry()
    smessage.ParseFromString(m)
    
    type_callable_map = copy(TYPE_CALLABLE_MAP)
    # convert TYPE_BYTES to a Python bytestring
    type_callable_map[FieldDescriptor.TYPE_BYTES] = str 
    
    # my_message is a google.protobuf.message.Message instance
    dm = protobuf_to_dict(smessage, type_callable_map=type_callable_map)
    print json.dumps(dm)
    #return dm

def main():
    # create ES client, create index
    es = Elasticsearch(hosts = [ES_HOST])

    if es.indices.exists(INDEX_NAME):
        print("deleting '%s' index..." % (INDEX_NAME))
        res = es.indices.delete(index = INDEX_NAME)
        print(" response: '%s'" % (res))

    request_body = {
        "settings" : {
            "number_of_shards": 1,
            "number_of_replicas": 0
        }
    }

    print("creating '%s' index..." % (INDEX_NAME))
    res = es.indices.create(index = INDEX_NAME, body = request_body)
    print(" response: '%s'" % (res))

    f = open('enriched_message.json','r')
    bulk_data = []
    send2Es = False
    toSend = 0
    for l in f:
        if send2Es:
            # bulk index the data
            print("bulk indexing...")
            res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = True)
            print(" response: '%s'" % (res))
            toSend = 0
            send2Es = False
            bulk_data = []
        l = l.strip()
        j = json.loads(l)
        dmsg = j
        #d = j['d']
        #dmsg = get_dict_of_message(d)
        op_dict = {
            "index": {
                "_index": INDEX_NAME, 
        	"_type": TYPE_NAME, 
        	"_id": dmsg[ID_FIELD]
            }
        }
        bulk_data.append(op_dict)
        bulk_data.append(dmsg)
        toSend += 1
        if toSend == 50:
            send2Es = True
    if len(bulk_data) > 0:
        print("bulk indexing...")
        res = es.bulk(index = INDEX_NAME, body = bulk_data, refresh = True)
        print(" response: '%s'" % (res))


    # sanity check
    print("searching...")
    res = es.search(index = INDEX_NAME, size=2, body={"query": {"match_all": {}}})
    print(" response: '%s'" % (res))

    print("results:")
    for hit in res['hits']['hits']:
        print(hit["_source"])

if __name__ == '__main__':
    main()
