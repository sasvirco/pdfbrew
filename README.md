# Pdfbrew
Pdfbrew is a simple python app to replace some of the functionality of PDF Distiller. It monitors folders for new postscript files and converts them into pdf in output folder using ps2pdf.

# Configuration
Configuration is in yaml format.
 * watch - pairs of input:output folders to watch for files and convert
 * loglevel - the logging level for the application
 * logfile - self explanatory
 * delete_original - True or False - delete original file after converting
 * copy_original - True or False - copy the original file in the output_folder (sets delete_original to True)
 * convert_onstart - True or False - convert all files in input folder before starting the watch (skiped if       delete_original is false). Useful to clean up files in the queue if service was stoped for maintenance
 * ps2pdf_opts - additional arguments that can be specified when running ps2pdf. In case your option is a password
                 you can use the special string RANDOMPASS and it will be replaced with random password
 
 ```yaml
---
# which folder to watch for changes
# containts pairs of input and output folders
watch : 
  /home/sas/in1 : /home/sas/out1
  /home/sas/in2 : /home/sas/out2

# delete original file after converting
delete_original : yes

# convert all files in input queue
# before starting the watch 
convert_onstart : yes

# copy original file in the output_folder 
# alongside the converted one 
# resets delete_original to True
copy_original: yes

# debug level 
loglevel: INFO

# logfile
logfile : pdfbrew.log

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
