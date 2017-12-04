# Pdfbrew
Pdfbrew is a simple python app to replace some of the functionality of PDF Distiller. It monitors folders for new postscript files and converts them into pdf in output folder using ps2pdf.

# Configuration
Configuration is in yaml format.
 * watch - pairs of input:output folders to watch for files and convert
 * loglevel - the logging level for the application
 * logfile - self explanatory
 * delete_onfail: If the file fails to convert after the predefined number of attempts, delete it. Setting it to false will keep trying to convert the file indefinetly.
 * copy_original - True or False - copy the original file in the output_folder (sets delete_original to True)
 * polling_interval - how often remote folders should be checked for changes
 * fail_tries - Number of tries to convert a file before it fails
 * purge_age - delete converted file after predefined period of time (2 weeks)
 * purge_int - interval in seconds to run the purge job for the old files (24 hours)
 * purge_err_int - interval in seconds to run the purge job for stale error files (1 hour)
 * num_workers - number of worker threads to process convert/delete events
 * ps2pdf_opts - additional arguments that can be specified when running ps2pdf. In case your option is a password
                 you can use the special string RANDOMPASS and it will be replaced with random password
 
 ```yaml
# which folder to watch for new files
# containts pairs of input and output folders
watch : 
  /home/sas/in1 : /home/sas/out1
  /home/sas/in2 : /home/sas/out2

# delete original file if it fails to convert for
# the specified number of tries
# if set to no it will continue trying indefinetly
delete_onfail : yes

# copy original file in the output_folder 
# alongside the converted one 
# resets delete_original to True
copy_original: no

# debug level 
loglevel: INFO

# logfile
logfile : pdfbrew.log

# directory polling interval
polling_interval: 15

# number of tries for failed attempts
fail_tries:  10

# how long to keep converted files (default 2 weeks in seconds)
purge_age: 1209600

# how often to run purge old files job (default 1 day in seconds) 
purge_int : 86400

# how often to remove stale error files (default 1 hour in seconds)
purge_err_int: 3600

# number of convert worker threads
num_workers: 4


# filetypes to convert from
# ignores other files in input dir
filetypes: 
  - application/postscript
  - application/pdf
  - text/plain
  - application/octet-stream

# ps2pdf args 
# string RANDOMPASS will be replaced with a random password
# use for g.g. -sOwnerPassword if you want to have a random one
ps2pdf_opts : -dCompatibility=1.4 -sOwnerPassword=RANDOMPASS
```
# Command line arguments

```
usage: pdfbrew.py [-h] [--loglevel LOGLEVEL] [--logfile LOGFILE]
                  [--configfile CONFIGFILE] [--quiet]

Monitor folder for ps files and convert them to pdf

optional arguments:
  -h, --help            show this help message and exit
  --loglevel LOGLEVEL   FATAL, ERROR, WARNING, INFO, DEBUG
  --logfile LOGFILE     Logfile to store messages (Default: pdfbrew.log)
  --configfile CONFIGFILE
                        Config file in json or yaml format
  --quiet               Do not print logging to stdout
```
