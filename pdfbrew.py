#!/usr/bin/python
import time
import pickle
import logging
import argparse
import yaml
import json
import magic
import inotify.adapters



def main ():


    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    parser = argparse.ArgumentParser(description = 'Monitor folder for ps files and convert them to pdf')
    parser.add_argument('--loglevel', default = 'INFO', help='FATAL, ERROR, WARNING, INFO, DEBUG')
    parser.add_argument('--logfile', default = 'pdfbrew.log', help='Logfile to store messages (Default: pdfbrew.log)')
    parser.add_argument('--configfile', default = 'pdfbrew.yaml', help='Config file in json or yaml format')
    parser.add_argument('--configfmt', default = 'yaml', help="Configfile format - json or yaml. Default json.")
    parser.add_argument('--quiet', action='store_true', help='Do not print logging to stdout')

    args = parser.parse_args()

    loglevel = levels.get(args.loglevel, logging.NOTSET)
    logging.basicConfig(
        level= args.loglevel,
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M',
        filename= args.logfile,
        filemode='a')

    root = logging.getLogger()
    if args.quiet is False: 
        console = logging.StreamHandler()
        console.setLevel(args.loglevel)
        
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        root.addHandler(console)
    
	notifier = inotify.adapters.Inotify()
	notifier.add_watch('/tmp/in')

	for event in notifier.event_gen():
		if event is not None:
			if 'IN_CREATE' in event[1]:

				file = event[2] + '/' + event[3]
				ftype = False
				
				with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
					ftype = m.id_filename(file)
					if (ftype is not False and ftype == 'application/postscript'):
						ps2pdf(file, '/tmp/out')

def ps2pdf(src, dst) :
    logging.info('converting file' + src + ' to ' + dst )

def parse_config(configfile, fmt) :
    f = open(configfile,'r')
    txt = f.read()
    logging.debug(txt)

    if fmt == "json" :
        return json.loads(txt)

    return yaml.load(txt)

if __name__ == "__main__":
	main()
