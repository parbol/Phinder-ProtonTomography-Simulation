import json, sys, optparse
import copy



if __name__=='__init__':

    parser = optparse.OptionParser(usage='usage: %prog [options] path', version='%prog 1.0')
    parser.add_option('-i', '--input', action='store', type='string', dest='inputFile', default='confExample.json', help='Configuration file template')
    parser.add_option('-o', '--output', action='store', type='string', dest='configurationFile', default='conf.json', help='Final configuration file')

    (opts, args) = parser.parse_args()

    with open(opts.inputFile, 'r') as file:
        data = json.load(file)

    #Modify world directly in data
    data['theWorld']['xSizeWorld'] = 100
    data['theWorld']['ySizeWorld'] = 100
    data['theWorld']['zSizeWorld'] = 100
    #Modify beam directly in data
    data['theBeam']['xBeamPosition'] = 0
    data['theBeam']['yBeamPosition'] = 0
    data['theBeam']['zBeamPosition'] = 125
    data['theBeam']['xBeamSigma'] = 0.1
    data['theBeam']['yBeamSigma'] = 0.1
    data['theBeam']['xDir'] = 0
    data['theBeam']['yDir'] = 0
    data['theBeam']['zDir'] = 1
    data['theBeam']['maxOpenAngle'] = 0.02
    data['theBeam']['nStep'] = 100
    data['theBeam']['nParticles'] = 1
    data['theBeam']['nParticlesDistribution'] = "Constant"
    data['theBeam']['energy'] = 250.0
    data['theBeam']['energyDistribution'] = "Constant"
    data['theBeam']['energySigma'] = 1.0
    data['theBeam']['tBeamSigma'] = 1.0
    #Modify phantoms directly in data
    data['thePhantoms'][0]['name'] = "lung"
    data['thePhantoms'][0]['xPos'] = 0
    data['thePhantoms'][0]['yPos'] = 0
    data['thePhantoms'][0]['zPos'] = 0
    data['thePhantoms'][0]['xDir'] = 0
    data['thePhantoms'][0]['yDir'] = 0
    data['thePhantoms'][0]['zDir'] = 1
    data['thePhantoms'][0]['zsize'] = 1
    data['thePhantoms'][0]['radius'] = 1
    data['thePhantoms'][0]['material'] = "lung"
    #Modify the detectors
    detector = copy.copy(data['Detectors'][0]
    layer = copy.copy(data['Detectors'][0]['Layers'][0])
    fiber = copy.copy(data['Detectors'][0]['Layers'][0]['Fibers'][0])
    
    fillDetector(xpos, ypos, zpos, xdir, ydir, zdir, xsize, ysize, zsize)

    data['Detectors'][0]['xPosDetector'] = "tracker"