# Pdfbrew
Pdfbrew is a simple python app to replace some of the functionality of PDF Distiller. It monitors folders for new postscript files and converts them into pdf in output folder using ps2pdf.

# Configuration
Configuration is in yaml format.
 * watch - pairs of input:output folders to watch for files and convert
 * loglevel - the logging level for the application
 * logfile - self explanatory
 * delete_original - True or False - delete original file after converting
 * copy_original - True or False - copy the original file in the output_folder (sets delete_original to True)
 * ps2pdf_opts - additional arguments that can be specified when running ps2pdf. Please note that the pdfbrew always runs ps2pdf with -sOwnerPassword=randomString to prevent files from modification.
 
 ```yaml
 ---
# which folder to watch for chaanges (it works recursively)
---
# which folder to watch for changes
# containts pairs of input and output folders
watch :
  /home/az023377/in1 : /home/az023377/out1
  /home/az023377/in2 : /home/az023377/out2

# delete original file after converting
delete_original : True

# copy original file in the output_folder 
# alongside the converted one 
# resets delete_original to True
copy_original: True

# debug level 
loglevel: INFO

# logfile
logfile : pdfbrew.log

# ps2pdf args
ps2pdf_opts : -dCompatibility=1.4

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
