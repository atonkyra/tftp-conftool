#!/usr/bin/env python
import logging
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)-15s %(levelname)-8s %(name)-20s %(message)s'
)
import tftpy
import StringIO
import argparse
import sys
import json

logger = logging.getLogger('conftool-tftp')
logger.setLevel(logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--format', required=True)
parser.add_argument('-d', '--datasource', required=True)
parser.add_argument('-t', '--template', required=True)
parser.add_argument('-n', '--hostname', required=True)
args = parser.parse_args()

replace_data = None

fd = open('%s' % (args.datasource), 'r')
for line in fd.readlines():
    line = line.strip()
    if line == '':
        continue
    linedict = dict(zip(args.format.split(','),line.split()))
    if 'hostname' in linedict and linedict['hostname'] == args.hostname:
        replace_data = linedict
        break
fd.close()

if replace_data is None:
    logger.info('failed to find %s in datasource %s', args.hostname, args.datasource)
    sys.exit(1)
logger.info('prepared to config %s', args.hostname)
logger.info('data: %s', json.dumps(replace_data))

fd = open('%s' % (args.template), 'r')
template = fd.read()
fd.close()

class ConfigFile(StringIO.StringIO):
    def close(self):
        logger.info("config upload finished, allow switch to think it through :)")
        return StringIO.StringIO.close(self)

def serve_file(name):
    if name == 'network-confg':
        logger.info("returning network config to switch")
        return ConfigFile(template % replace_data)
    logger.info("switch requested file: %s, returning empty file", name)
    return StringIO.StringIO()

srv = tftpy.TftpServer(tftproot='/dev/null', dyn_file_func=serve_file)
srv.listen()
