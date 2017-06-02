import sys 
import os
import argparser
import json
import base64
import random
from copy import copy
import signals_pb2
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from google.protobuf.descriptor import FieldDescriptor
from protobuf_to_dict import protobuf_to_dict, TYPE_CALLABLE_MAP
from common.logger import logger as LOGGER
from elasticsearch import Elasticsearch
import urllib2

#-- defaul log file name
ENRICHED_LOGFILE = "enriched.log"

#-- convert pb preparing stuff
type_callable_map = copy(TYPE_CALLABLE_MAP)
type_callable_map[FieldDescriptor.TYPE_BYTES] = str 

def show_pb(pb):
    # my_message is a google.protobuf.message.Message instance
    dm = protobuf_to_dict(pb, type_callable_map=type_callable_map)
    print json.dumps(dm)

#-- elastic search conf
DEFAULT_ES_HOST = {
    "host" : "localhost", 
    "port" : 9200
}
ES_INDEX_PREFIX = 'enriched-osprey-test'
TYPE_NAME = 'event'
ID_FIELD = 'sessionToken'

class es_piper:
    def __init__(self):
        self.es_client = None
        try:
            es_client = elasticsearch.Elasticsearch(
                hosts=[ES_HOST], 
                timeout=120, 
                max_retries=5, 
                retry_on_timeout=True)
        except Exception as e:
            logger.error("cannot connect to ES", {"err":e})
        if self.es_client == None:
            return
        self.bulk_data = {}

    def pipe_msg(msg):

        date = msg["@timestamp"]
        suffix = "%s-%s%s" % (h.hexdigest(), suffix, datetime.datetime.now().strftime("%Y%m%d"))
        es_index = "cpq-%s-%s-%s" % ("TEST" if label == None else label, retention, suffix)
        es_index_type = "%s/%s" % (es_index, estype)
        es_client = elasticsearch.Elasticsearch(hosts=[{"host": esnode, "port": 9200}], timeout=120, max_retries=5, retry_on_timeout=True)


        if es.indices.exists(INDEX_NAME):
            print("deleting '%s' index..." % (INDEX_NAME))
            res = es.indices.delete(index = INDEX_NAME)
            print(" response: '%s'" % (res))

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

    def create_index(es_client, es_index_type, schema):
       if es_client.indices.exists(index=es_index):
            logger.warn("index %s already exists remove" % es_index)
            es_client.indices.delete(index=es_index, ignore=[400, 404])
        try:
            with open(ES_SETTINGS, 'r') as settings_file:
                settings_value = settings_file.read()
            with open(ES_MAPPINGS, 'r') as mappings_file:
                mappings_value = mappings_file.read()
            mv = json.loads(mappings_value)
            exclude_keys = []
            for k in mv['_default_']['properties']:
                if k not in schema.keys():
                    exclude_keys.append(k)
            for k in exclude_keys:
                mv['_default_']['properties'].pop(k)
            index_body = { 
                    'aliases': {}, 
                    'mappings': mv, 
                    'settings': json.loads(settings_value),
                    'warmers': {}
            }   
            es_client.indices.create(index=es_index, body=index_body, master_timeout="120s", timeout="120s")
        except elasticsearch.exceptions.TransportError as err:
            return None



def build_arg_parser():
    parser = argparse.ArgumentParser(description="Merger Consumer")
    parser.add_argument("-e", "--elastic", type=str, help="Specify the Elasticsearch Server", required=True)
    parser.add_argument("-f", "--conf", type=file, help="Specify the config file of Merger Consumer", required=True)
    parser.add_argument("-v", "--verbosity", action="count", default=0)
    return parser


def claim(owner, zookeeper):
    return True 

def main():
    parser = build_arg_parser()
    args = parser.parse_args()
    owner = socket.gethostname()+"-"+randomword(8)
    print('[%s] start a new Round Parquet Pusher' % (strftime("%Y%m%d %H:%M:%S", gmtime()), ))
    # prepare parameter for the job
    label = args.label
    # fetch the config
    config = yaml.load(args.conf)
    config = pusher_config.build_config_map(config)

    # claim to have the authority to run the job
    if args.zookeeper != None:
        zookeeper = {'host':args.zookeeper.split(':')[0], 'port':args.zookeeper.split(':')[1]}
    else:
        zookeeper = config['clusters']['zookeeper']
    if (not claim(owner, zookeeper)):
        print('Cannot be coordinated to start the %s parquet loader' % owner)
        exit(1)

    # make a logger
    log_file = "%s/%s/%s/%s-%s" % (config['logging']['directory'], args.customer, label, owner, ENRICHED_LOGFILE)
    if not os.path.exists(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))
    log_level = args.verbosity
    LOGGER.set_file_logger(__name__, log_level, log_file)

    es_piper = es_piper()

    r = kreader('mergedEnrichRequest', 'piper', ['localhost:9092'], meta.get_partition_offsets())
    if es_client == None:
        print "Cannot connect to ElasticSearch"
        exit(0)

    for message in r.msg_iterator():
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        logger.warning("get message", {"topic": message.topic, "part" : message.partition,
            "offset": message.offset, "key":message.key})
        
        print message
        print len(message.value)
        
        try:
            pb_msg = signals_pb2.Telemetry()
            pb_msg.ParseFromString(message.value)
        except Exception as e:
            print e

        # after get the merged message, simply pipe into the ES in bulk mode
        dmsg = protobuf_to_dict(pb_msg, type_callable_map=type_callable_map)
        es_piper.pipe_msg(dmsg)

if __name__ == '__main__':
    main()

