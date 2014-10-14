import threatexpert_parser as teparser
from maec.package.package import Package

___version__ = "0.0.0.1"

proxies = {}
    
def generate_package_from_report_filepath(input_path, options = None):
    "Take a file path to a ThreatExpert report and return a MAEC package object"
    parser = teparser.parser()
    open_file = parser.open_file(input_path)
    
    if not open_file:
        print('\nError: Error in parsing input file. Please check to ensure that it is valid XML and conforms to the ThreatExpert output schema.')
        return
    
    return generate_package_from_parser(parser)

def generate_package_from_binary_filepath(input_path, options = None):
    "Take a file path to a binary file, try to look up its ThreatExpert report by MD5, and return a MAEC package object if a report is found"
    import hashlib
    # create MD5
    blocksize = 65536
    fd = open(input_path, "rb")
    hasher = hashlib.md5()
    buf = fd.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = fd.read(blocksize)
    
    return generate_package_from_md5(hasher.hexdigest())

def generate_package_from_md5(input_md5, options = None):
    "Take an MD5 string, try to look up its ThreatExpert report, and return a MAEC package object if a report is found"
    global proxies
    import requests
    parameters = { "md5": input_md5, "xml": 1 }
    response = requests.get("http://threatexpert.com/report.aspx", params=parameters, proxies=proxies)
    
    return generate_package_from_report_string(response.content)

def generate_package_from_report_string(input_string, options = None):
    "Take a ThreatExpert report as a string and return a MAEC package object"
    parser = teparser.parser()
    parser.use_input_string(input_string)
    
    return generate_package_from_parser(parser)

def generate_package_from_parser(input_parser, options = None):
    "Take a populated ThreatExpert parser object and return a MAEC package object"
    #Parse the file to get the actions and processes
    input_parser.parse_document()

    #Create the MAEC Package
    package = Package()
    
    #Add the analysis
    for malware_subject in input_parser.maec_subjects:
        
        if options:
            if options.normalize_bundles:
                malware_subject.normalize_bundles()
            if options.deduplicate_bundles:
                malware_subject.deduplicate_bundles()
            if options.dereference_bundles:
                malware_subject.dereference_bundles()
        
        package.add_malware_subject(malware_subject)
        
    return package

def set_proxies(proxy_dict={}):
    "Take a dictionary of proxies to use for network fetches, where keys are protocol names and values are proxy addresses; e.g., { 'http':'http://example.com:80', ... }"
    global proxies
    proxies = proxy_dict
    