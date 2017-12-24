#!/usr/bin/env python
import logging

class ErrorCounter:
    def __init__(self):
        self.tracker = {}
    def get_error(self, filename):
        if filename in self.tracker:
            logging.info('Got '+ filename + " " + str(self.tracker[filename]))
            return self.tracker[filename]
        else:
            logging.info('Got None')
            return None
    def set_error(self, filename):
        if filename in self.tracker:
            self.tracker[filename] += 1
            logging.info('Set '+ filename + " " + str(self.tracker[filename]))
        else:
            self.tracker[filename] = 1
            logging.info('Set '+ filename + " " + str(self.tracker[filename]))
    def delete_error(self, filename):
        if filename in self.tracker:
            del self.tracker[filename]
            logging.info('Del '+ filename )

def main():
    logging.basicConfig(
        level='DEBUG',
        #format='%(asctime)s %(name)-12s %(funcName)20s() %(levelname)-8s %(message)s',
        format="%(levelname) -10s %(asctime)s %(module)s:%(lineno)s %(funcName)s %(message)s",
        datefmt='%m-%d %H:%M',
        filename='test.log',
        filemode='a')

    logger = logging.getLogger()
    console = logging.StreamHandler()
    console.setLevel('DEBUG')
    formatter = logging.Formatter(
                '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logger.addHandler(console)

    err = ErrorCounter()
    filename = '/tmp/sas'
    err.set_error(filename)
    err.get_error(filename)
    err.set_error(filename)
    err.get_error(filename)
    err.delete_error(filename)
    err.get_error(filename)

if __name__ == "__main__":
    main()
