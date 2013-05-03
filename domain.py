from __future__ import with_statement
from urlparse import urlparse

# load tlds, ignore comments and empty lines:
with open("effective_tld_names.dat.txt") as tldFile:
    tlds = [line.strip() for line in tldFile if line[0] not in "/\n"]

class DomainParts(object):
    def __init__(self, domain_parts, tld):
        self.domain = None
        self.subdomains = None
        self.tld = tld
        if domain_parts:
            self.domain = domain_parts[-1]
            if len(domain_parts) > 1:
                self.subdomains = domain_parts[:-1]

def get_domain_parts(url, tlds):
    urlElements = urlparse(url).hostname.split('.')
    # urlElements = ["abcde","co","uk"]
    for i in range(-len(urlElements),0):
        lastIElements = urlElements[i:]
        #    i=-3: ["abcde","co","uk"]
        #    i=-2: ["co","uk"]
        #    i=-1: ["uk"] etc

        candidate = ".".join(lastIElements) # abcde.co.uk, co.uk, uk
        wildcardCandidate = ".".join(["*"]+lastIElements[1:]) # *.co.uk, *.uk, *
        exceptionCandidate = "!"+candidate

        # match tlds: 
        if (exceptionCandidate in tlds):
            return ".".join(urlElements[i:])
        if (candidate in tlds or wildcardCandidate in tlds):
            return DomainParts(urlElements[:i], '.'.join(urlElements[i:]))
            # returns ["abcde"]

    raise ValueError("Domain not in global list of TLDs")

