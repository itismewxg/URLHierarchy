#coding:utf8

from __future__ import with_statement
"""
author: wangxingang
contact: itismewxg@gmail.com

This script will take the domain name as the input and detect the URL hierarchy which 
can be found by HTTP GET command

Be sure, the url which can only be connected by more than 2 times POST Httprequest
cannot be detected in our detection

Need to be enhanced by "js embedded" like GA, Quancast, baidu Statistics 

"""
import os
import getopt
import sys
import traceback
import httplib
from urlparse import urlparse
from HTMLParser import HTMLParser
from collections import deque
import domain
import log
import pickle
import copy
import re

LOGGER = log.get_logger()

"""
	my html parser, just print out the <a href>, the anchor of the ref link in 
	the page, this link will analysed
	0) the root is the domain
	1) only the subdomain: 		aaa.site.com/org
	2) and the url under the site and subdomain:
		www.site.com/org or aaa.site.com/org | [path] 
	   will be left, and record in the tree-like 
	3) this url hierarchy will be recorded the specific url log output
"""

BAD_LINK = ""

# load tlds, ignore comments and empty lines:
with open("effective_tld_names.dat.txt") as tldFile:
    tlds = [line.strip() for line in tldFile if line[0] not in "/\n"]

"""
	define the customed html parser which get all the href from the current page
"""
class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.hrefList = set()
    
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            for attr in attrs:
                if attr[0]=='href':
                    self.hrefList.add(attr[1])
        
    def get_containing_links(self):
            return self.hrefList

"""
	initialize with the Domain, the 1st access to the website, and
	its site name
	this class will then try to scan in a tree traversal of all the links
	which can be accessed from GET and 1st level POST and no forbidden
	redirection multi-level POST

"""
class URLHierarchy:
    def __init__(self, domain, site):
        self.domain = domain
        self.site = site

	"""
		scan the url and get all the href in the url	
	"""
    def scan(self, url):
        parsed_url = urlparse(url)
        hostname = parsed_url.hostname
        path = parsed_url.path
        LOGGER.info("get to scan", {'url':url, 'hostname':hostname, 'path':path})
        conn = httplib.HTTPConnection(hostname, timeout=15)
        conn.request("GET", path)
        res = conn.getresponse()
        LOGGER.info("connected then, ", {'status':res.status, 'reason':res.reason})
        if res.status == 200:
            ctype = res.getheader("Content-type")
            if "text/html" not in ctype:
                return None
            data = res.read()
            #print data
            html = MyHTMLParser()
            html.feed(data)
            #return _filter_and_complete(html.get_containing_links())
            links = html.get_containing_links() 
            ret_links = set()
            for l in links:
                try:
                    parsed_link = urlparse(l)
                    if parsed_link.hostname == None:
                        if parsed_link.path == l:
                            ret_links.add(self.domain+'/'+l)
                    else:
                        hsite = domain.get_domain_parts(l, tlds).domain
                        if hsite == self.site:
                            ret_links.add(l)
                except:
                    pass
            return ret_links
        elif (res.status == 301 or res.status == 302) :
            data = res.read()
            html = MyHTMLParser()
            html.feed(data)
            redirect_link = html.get_containing_links()[0]
            LOGGER.info("url redirect",{'redir_link':redirect_link})
            return scan(redirect_link)
        else:
            print res.status, res.reason
            return BAD_LINK

    def detect(self):
        scanned_links = set()
        scanning_links = set()
        scanning_links.add(self.domain)

        while len(scanning_links) != 0:
            checking_links = copy.deepcopy(scanning_links)
            scanned_links = scanned_links | checking_links # to be scanned
            scanning_links.clear()
            for link in checking_links:
                print "to be checking:"+link
                try:
                    print link
                    outlinks = self.scan(link)
                    if outlinks != None:
                        print outlinks
                    if outlinks != None and len(outlinks) != 0:
                        newlinks = outlinks - scanned_links
                        scanning_links = scanning_links | newlinks 
                    else:
                        print "no links in page " + link
                except Exception as e:
                    print e
                    pass
            print str(len(scanning_links))
        print "print out all the scanned links"
        sorted(scanned_links)
        filename = self.site + ".urls"
        f = open(filename, "w")
        pickle.dump(scanned_links, f)

def usage():
    print ' -------------------------------------------------------------------------------'
    print ' scan a website from its entry domain'
    print ' '
    print ' example: python detectURLHiearchy -d http://www.example.com'
    print ' -------------------------------------------------------------------------------'
    sys.exit(' ')	

def main(): 
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hd:", ["help","domain="])
    except getopt.GetoptError, err:
        # print help information and exit:
        print str(err) # will print something like "option -a not recognized
        usage()
        sys.exit(2)
    entry_domain = None
    site = None
    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage() 
            sys.exit()
        elif o in ("-d", "--domain"):
            entry_domain = a
        else:
            assert False, "unhandled option"
        if (entry_domain == None):
            usage()
            sys.exit()
    site = domain.get_domain_parts(entry_domain, tlds).domain
    LOGGER.info("start to detect in the site", {'entry_domain':entry_domain, 'site':site})
    url_hierarchy = URLHierarchy(entry_domain, site)
    url_hierarchy.detect()	

if __name__ == "__main__":
    main()



	

