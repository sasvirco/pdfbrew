#!/usr/bin/env python

import logging
import argparse
import sys
import Queue
import threading
from subprocess import Popen, PIPE
import os
import uuid
import shutil
import time
import yaml
import magic
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver as Observer

class BrewHandler(FileSystemEventHandler):
    """ capture file created event and brew pdf """
    def __init__(self, queue, config):
        self.config = config
        self.queue = queue

    def on_created(self, event):
        if event.is_directory is False:
            self.queue.put(event)

def process_queue(queue, config):
    """ process event queue """
    while True:
        event = queue.get()
        logging.info(event)
        fname = event.src_path
        src_dir = os.path.dirname(event.src_path)
        convert_file(fname, config['watch'][src_dir], config)

def main():
    """main"""

    parser = argparse.ArgumentParser(
        description='Monitor folder for ps files and convert them to pdf')
    parser.add_argument('-l', '--loglevel',
                        help='CRITICAL, ERROR, WARNING, INFO, DEBUG')
    parser.add_argument('-o', '--logfile',
                        help='Logfile to store messages (Default: pdfbrew.log)')
    parser.add_argument('-c', '--configfile', default='pdfbrew.yaml',
                        help='Config file yaml format')
    parser.add_argument('-q', '--quiet', action='store_true',
                        help='Do not print logging to stdout')

    args = parser.parse_args()

    config = parse_config(args.configfile)

    if args.logfile:
        config['logfile'] = args.logfile

    if args.loglevel:
        config['loglevel'] = args.loglevel

    logging.basicConfig(
        level=config['loglevel'],
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M',
        filename=config['logfile'],
        filemode='a')

    root = logging.getLogger()
    if args.quiet is False:
        console = logging.StreamHandler()
        console.setLevel(config['loglevel'])

        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        root.addHandler(console)

    # clean up input folders before watch
    if config['convert_onstart']:
        convert_onstart(config)

    queue = Queue.Queue()
    num_workers = config['num_workers']
    pool = [threading.Thread(target=process_queue,
                             args=(queue, config)) for _ in range(num_workers)]
    for worker in pool:
        worker.daemon = True
        worker.start()

    observer = Observer(timeout=config['polling_interval'])
    observer.event_queue_maxsize = 20
    event_handler = BrewHandler(queue, config)

    for indir in config['watch']:
        if os.path.isdir(indir):
            observer.schedule(event_handler, indir, recursive=False)
            root.info("started watching " + indir +
                      " with output at " + config['watch'][indir])
        else:
            root.critical("cannot watch " + indir + " it is not a directory")
            sys.exit(1)

        if (not os.access(config['watch'][indir], os.W_OK)
                and not os.path.isdir(config['watch'][indir])):
            root.critical("Can't write to output_folder " + config['watch'][indir] +
                          " or does not exist")
            sys.exit(1)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        root.fatal('keyboard interrupt')
        sys.exit(0)

    observer.join()


def ps2pdf(src, dst, ps2pdf_args):
    """spawns ps2pdf process"""

    name, ext = os.path.splitext(src)
    out_file = dst + '/' + os.path.basename(name) + '.pdf'
    cmd = ["ps2pdf"]

    if ps2pdf_args:
        # replace string RANDOMPASS with random password
        ps2pdf_args = ps2pdf_args.replace(
            "RANDOMPASS", str(uuid.uuid4().get_hex().upper()[0:12]))
        cmd = cmd + ps2pdf_args.split(' ')

    proc = Popen(cmd + [src, out_file], stderr=PIPE, stdout=PIPE)

    logging.debug("executing " + " ".join(str(x)
                                          for x in cmd) + ' ' + src + ' ' + out_file)

    (stdout, stderr) = proc.communicate()
    if proc.returncode:
        logging.error("cannot convert file: " + src)
        logging.error(stderr)
        #cleanup broken file from output if convertion failed
        if os.path.exists(out_file):
            os.remove(out_file)
        return False
    else:
        logging.info('converted file ' + src + ' to ' + out_file)
        return True

def convert_onstart(config):
    """empty input queue on start before watch"""

    if not config['delete_original']:
        logging.warn('Cannot convert queue on start, delete_original is False')
        return

    logging.info('Converting files in queue before starting watch')

    for indir in config['watch']:
        if os.path.isdir(indir):
            paths = [os.path.join(indir, fn) for fn in next(os.walk(indir))[2]]
            for filename in paths:
                convert_file(filename, config['watch'][indir], config)


def convert_file(fname, outdir, config):
    """validate files and start conversion"""

    with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
        ftype = m.id_filename(fname)
        ret = False

        logging.debug("filename: " + fname + " is type  " + ftype)

        if ftype is not False and ftype in config['filetypes']:
            ret = ps2pdf(fname, outdir, config['ps2pdf_opts'])

        if ret and config['copy_original']:
            logging.info("Copy original file " + fname +
                         " to destination " + outdir)
            config['delete_original'] = True
            shutil.copy2(fname, outdir)

        if ret and config['delete_original']:
            os.remove(fname)
            logging.info("Deleting " + fname)

        return


def parse_config(configfile):
    """parse configuration yaml file"""

    cnf = open(configfile, 'r')
    txt = cnf.read()

    return yaml.load(txt)


if __name__ == "__main__":
    main()
