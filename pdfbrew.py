#!/usr/bin/python
import logging
import argparse
import yaml
import magic
import inotify.adapters
import sys
import ghostscript
import os
import uuid

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
	parser.add_argument('--quiet', action='store_true', help='Do not print logging to stdout')

	args = parser.parse_args()

	config = parse_config(args.configfile)
	
	if (args.logfile) :
		config['logfile'] = args.logfile

	if (args.loglevel) :
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
		console.setLevel(args.loglevel)
		
		formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
		console.setFormatter(formatter)
		root.addHandler(console)

		
	notifier = inotify.adapters.InotifyTree(config['watch'])
	root.info("started watching " + config['watch'])

	try :
		for event in notifier.event_gen():
			
			root.debug(event)
			
			if event is not None:
				if 'IN_CLOSE_WRITE' in event[1]:

					file = event[2] + '/' + event[3]
								
					with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
						ftype = m.id_filename(file)
						if (ftype is not False and ftype == 'application/postscript'):
							ps2pdf(file, config['output_folder'], config['ps2pdf_args'])
	
	except KeyboardInterrupt:
		root.fatal('keyboard interrupt')
		sys.exit(0)

def ps2pdf(src, dst, ps2pdf_args) :

	name, ext = os.path.splitext(src)
	out_file = dst + '/' + os.path.basename(name) + '.pdf'

	gs_args = [
		"ps2pdf",
		"-dSAFER", "-dNOPAUSE", "-dQUIET", "-dBATCH",
		"-sDEVICE=pdfwrite",
		"-sOutputFile=" + out_file,
		"-sOwnerPassword=" + str(uuid.uuid4().get_hex().upper()[0:6]),
		"-c",".setpdfwrite",
		"-f", src
	]

	#if (ps2pdf_args) :
	#	for k in ps2pdf_args :
	#		gs_args.append(k)

	logging.debug(gs_args)
	logging.info('converting file' + src + ' to ' + out_file )
	ghostscript.Ghostscript(*gs_args)


def parse_config(configfile) :
	f = open(configfile,'r')
	txt = f.read()

	return yaml.load(txt)

if __name__ == "__main__":
	main()
