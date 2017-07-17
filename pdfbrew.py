#!/usr/bin/python
import logging
import argparse
import yaml
import magic
import inotify.adapters
import sys
from subprocess import Popen, PIPE
import os
import uuid
import shutil

def main():


    levels = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }

    parser = argparse.ArgumentParser(description = 'Monitor folder for ps files and convert them to pdf')
    parser.add_argument('--loglevel', help='CRITICAL, ERROR, WARNING, INFO, DEBUG')
    parser.add_argument('--logfile', default = 'pdfbrew.log', help='Logfile to store messages (Default: pdfbrew.log)')
    parser.add_argument('--configfile', default = 'pdfbrew.yaml', help='Config file in json or yaml format')
    parser.add_argument('--quiet', action='store_true', help='Do not print logging to stdout')

    args = parser.parse_args()

    config = parse_config(args.configfile)
    
    if (args.logfile):
        config['logfile'] = args.logfile

    if (args.loglevel):
        config['loglevel'] = args.loglevel

    loglevel = levels.get(args.loglevel, logging.NOTSET)
    logging.basicConfig(
        level= config['loglevel'],
        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
        datefmt='%m-%d %H:%M',
        filename= config['logfile'],
        filemode='a')

    root = logging.getLogger()
    if args.quiet is False: 
        console = logging.StreamHandler()
        console.setLevel(config['loglevel'])
        
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        console.setFormatter(formatter)
        root.addHandler(console)

        
    notifier = inotify.adapters.Inotify()

    for w in config['watch']:
        if (os.path.isdir(w)) :
            notifier.add_watch(w)
            root.info("started watching " + w)
        else :
            root.critical("cannot watch "+ w + " it is not a directory")
            sys.exit(1)
        
        if (not os.access(config['watch'][w], os.W_OK) 
            and not os.path.isdir(config['watch'][w])) :
            root.critical("Can't write to output_folder "+config['watch'][w]+ " or it does not exist")
            sys.exit(1)
            
    try:
        for event in notifier.event_gen():
            
            root.debug(event)
            
            if event is not None:
                if 'IN_CLOSE_WRITE' in event[1]:

                    file = event[2] + '/' + event[3]
                                
                    with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
                        ftype = m.id_filename(file)
                        rc = None
                        if (ftype is not False and ftype == 'application/postscript'):
                            rc = ps2pdf(file, config['watch'][event[2]], config['ps2pdf_opts'])
                        
                        if (rc and config['copy_original']) :
                            root.info("Copy original file "+ file + " to destination "+config['watch'][event[2]])
                            config['delete_original'] = True
                            shutil.copy2(file, config['watch'][event[2]])

                        if (rc and config['delete_original']) :
                            os.remove(file)
                            root.info("Deleting "+ file )

    
    except KeyboardInterrupt:
        root.fatal('keyboard interrupt')
        sys.exit(0)

def ps2pdf(src, dst, ps2pdf_args):

    name, ext = os.path.splitext(src)
    out_file = dst + '/' + os.path.basename(name) + '.pdf'
    cmd = ["ps2pdf"]
    
    if ps2pdf_args :
        # replace string RANDOM12 with random password
        ps2pdf_args = ps2pdf_args.replace("RANDOMPASS",str(uuid.uuid4().get_hex().upper()[0:12]) )
        cmd = cmd + ps2pdf_args.split(' ')

    proc = Popen(cmd + [ src, out_file] , stderr=PIPE, stdout=PIPE)

    logging.debug("executing "+ " ".join(str(x) for x in cmd) + ' ' + src + ' '+ out_file)
    
    (stdout, stderr) = proc.communicate()
    if proc.returncode :
        logging.error(stderr)
        return False
    else :
        logging.info('converted file ' + src + ' to ' + out_file )
        return True



def parse_config(configfile):
    f = open(configfile,'r')
    txt = f.read()

    return yaml.load(txt)

if __name__ == "__main__":
    main()
