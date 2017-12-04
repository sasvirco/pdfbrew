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
from apscheduler.schedulers.background import BackgroundScheduler

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

    newconf = parse_config(args.configfile)

    config = {'polling_interval' : 15, 'purge_age' : 300, 'purge_int' : 120,
              'purge_err_int': 120, 'num_workers' : 4, 'delete_onfail': True,
              'filetypes' : ['application/postscript', 'application/pdf',
                             'text/plain', 'application/octet-stream'],
              'copy_original': True, 'loglevel': 'INFO',
              'logfile': 'pdfbrew.log', 'fail_tries': 10}

    config.update(newconf)

    if args.logfile:
        config['logfile'] = args.logfile

    if args.loglevel:
        config['loglevel'] = args.loglevel

    logging.basicConfig(
        level=config['loglevel'],
        #format='%(asctime)s %(name)-12s %(funcName)20s() %(levelname)-8s %(message)s',
        format="%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s",
        datefmt='%m-%d %H:%M',
        filename=config['logfile'],
        filemode='a')

    pdfbrew = logging.getLogger()

    if args.quiet is False:
        console = logging.StreamHandler()
        console.setLevel(config['loglevel'])

        formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        pdfbrew.addHandler(console)


    queue = Queue.Queue()
    num_workers = config['num_workers']
    pool = [threading.Thread(target=process_queue,
                             args=(queue, config)) for _ in range(num_workers)]


    for worker in pool:
        worker.daemon = True
        worker.start()

    scheduler = BackgroundScheduler(daemon=True)
    scheduler.start()

    scheduler.add_job(purge_old_files, 'interval', seconds=int(config['purge_int']),
                      args=[queue, config])
    scheduler.add_job(purge_old_errors, 'interval', seconds=int(config['purge_err_int']),
                      args=[queue, config])
    scheduler.add_job(poll_folders, 'interval', seconds=int(config['polling_interval']),
                      args=[queue, config])
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        sys.exit(0)

def poll_folders(queue, config):
    """ poll watched folders and put files in the process queue"""

    for indir in config['watch']:
        logging.debug('scaning '+ indir + ' for new files')
        paths = [os.path.join(indir, fn) for fn in next(os.walk(indir))[2]]
        for path in paths:
            queue.put([path, 'convert'])

def process_queue(queue, config):
    """ process event queue """
    while True:
        filename, action = queue.get()
        if action == 'convert':
            path = os.path.dirname(filename)
            convert_file(filename, config['watch'][path], config)
        if action == 'delete':
            delete_file(filename)
        time.sleep(1)


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
        logging.debug("cannot convert file: " + src)
        logging.debug(stderr)

        #cleanup broken file from output if convertion failed
        if os.path.exists(out_file):
            delete_file(out_file)

        return {'success' : False, 'error': stderr}
    else:
        logging.info('converted file ' + src + ' to ' + out_file)
        return {'success' : True, 'error': None}


def convert_file(fname, outdir, config):
    """validate files and start conversion"""

    if os.path.exists(fname) is False:
        return

    name, ext = os.path.splitext(fname)
    out_file = outdir + '/' + os.path.basename(name) + '.pdf'
    errstr = {'error': None, 'num_tries': 0}

    if os.path.exists(out_file + ".err"):
        errfile = open(out_file + ".err")
        err = yaml.load(errfile.read())
        logging.debug('Previous error detected for ' + fname
                      + ' try ' + str(err['num_tries'])
                      + '/' + str(config['fail_tries']))

        errstr.update(err)

    if errstr['num_tries'] > config['fail_tries']:
        logging.error('Exceeding number of attempts to convert '
                      + fname)
        if config['delete_onfail']:
            delete_file(fname)
            delete_file(out_file + ".err")
            return

    with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
        ftype = m.id_filename(fname)

        logging.debug("filename: " + fname + " is type  " + ftype)
        ret = {'success' : False, 'error': None}

        if ftype is not False and ftype in config['filetypes']:
            ret = ps2pdf(fname, outdir, config['ps2pdf_opts'])

        if ret['success'] and config['copy_original']:
            logging.info("Copy original file " + fname +
                         " to destination " + outdir)
            shutil.copy2(fname, outdir)

<<<<<<< HEAD
=======
        if ret and config['delete_original']:
            try : 
                os.remove(fname)
            except Exception as e:
                loggin.error("Failed to delete "+ fname + " Exception: " + e)
            else :
                logging.info("Deleting " + fname)
>>>>>>> 5f2892795eacc109b86e7a291921aae4e3dc20e3

        if ret['success'] is False:
            errstr['num_tries'] = errstr['num_tries'] + 1
            errstr['error'] = ret['error']
            errfile = open(out_file + ".err", "w")
            errfile.write(yaml.dump(errstr))
        else:
            delete_file(fname) #remove original
            delete_file(out_file + ".err")


def parse_config(configfile):
    """parse configuration yaml file"""

    cnf = open(configfile, 'r')
    txt = cnf.read()

    return yaml.load(txt)

def delete_file(filename):
    """delete file and catch any exceptions while doing it"""
    try:
        if os.path.exists(filename):
            os.remove(filename)
            logging.debug("Deleting " + filename)
    except Exception as e:
        logging.error("Cannot delete file "+ filename)
        logging.exception(e)


def purge_old_files(queue, config):
    """purge old files after predefined period"""
    logging.debug('Purging old files')

    now = time.time()
    i = 0
    for indir in config['watch']:
        logging.debug('scaning '+ indir + ' for stale error files')
        paths = [os.path.join(config['watch'][indir], fn)
                 for fn in next(os.walk(config['watch'][indir]))[2]]
        for filename in paths:
            creation_time = os.path.getctime(filename) + int(config['purge_age'])
            if now > creation_time:
                queue.put([filename, 'delete'])
                i += 1
        logging.info('Purging ' + str(i) + " old files in " + config['watch'][indir])

def purge_old_errors(queue, config):
    """purge stale errors files"""
    logging.debug('Purging stale error files')

    i = 0
    for indir in config['watch']:
        logging.debug('scaning '+ config['watch'][indir] + ' for stale error files')
        paths = [os.path.join(config['watch'][indir], fn)
                 for fn in next(os.walk(config['watch'][indir]))[2]]
        for filename in paths:
            if os.path.exists(filename) and os.path.exists(filename + ".err"):
               queue.put([filename+".err", 'delete'])
               i += 1
        logging.info('Purging '+ str(i) + ' stale error files in' + config['watch'][indir])

if __name__ == "__main__":
    main()
