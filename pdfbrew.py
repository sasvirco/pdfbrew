#!/usr/bin/python
import time
import pickle
import logging
import argparse
import yaml
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class NewFileHandler(FileSystemEventHandler):
    def on_created(self, event):
        logging.info(event.__class__.__name__ + ' ' + event.src_path )
        ps2pdf(event.src_path, event.src_path)


if __name__ == "__main__":


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
    
    event_handler = NewFileHandler()
    observer = Observer()
    observer.schedule(event_handler, path='/devel/in', recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    
    observer.join()

def ps2pdf(src, dst) :
    logging.info('converting file' + src + ' to ' + dst )

def parse_config(configfile, fmt) :
    f = open(configfile,'r')
    txt = f.read()
    logging.debug(txt)

    if fmt == "json" :
        return json.loads(txt)

    return yaml.load(txt)
