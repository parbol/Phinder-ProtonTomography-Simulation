import json, sys, optparse




if __name__=='__init__':

    parser = optparse.OptionParser(usage='usage: %prog [options] path', version='%prog 1.0')
    parser.add_option('-i', '--input', action='store', type='string', dest='inputFile', default='confExample.json', help='Configuration file template')
    parser.add_option('-o', '--output', action='store', type='string', dest='configurationFile', default='conf.json', help='Final configuration file')

    (opts, args) = parser.parse_args()

    with open(opts.inputFile, 'r') as file:
        data = json.load(file)

    