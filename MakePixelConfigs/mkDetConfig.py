import os
from cablemap import *
from optparse import OptionParser

parser = OptionParser()
parser.add_option('','--fed',dest='feds',help='Input fed list as string')
parser.add_option('','--prt',dest='prts',help='Input portcard list as string')
parser.add_option('','--dsk',dest='dsks',help='Input disk list as string')
parser.add_option('-e','--exclude',dest='ex',help='Input name list of module to be excluded as string')

(opts, args) = parser.parse_args()

def list2dat(lst,fn):
    with open(fn, 'w') as output:
        output.write('Rocs:\n')
        for element in lst:
            for x in range(16):
                line = element+'_ROC%s'%str(x)+'\n'
                output.write(line)

def mkNewConfigVersion(configName):
    configBaseDir = os.environ['PIXELCONFIGURATIONBASE']
    os.chdir(os.path.join(configBaseDir, configName))
    subdirs = [int(x) for x in os.walk('.').next()[1]]
    subdirs.sort()
    lastVersion = subdirs[-1]
    print "Last %s version: "%configName, lastVersion
    newVersion = subdirs[-1]+1
    os.system('mkdir %d'%newVersion)
    os.chdir('%d'%newVersion)
    print "New %s version: "%configName, newVersion
    return newVersion

def setAsDefault(configName, version):
    args = "--insertVersionAlias "+configName+" "+str(version)+" Default"
    os.system(cdb+args)



def main():
    cableMap_Fn='cablingmap_fpixphase1_BpO.csv'
    dictionary = getdict(filename='csv/'+cableMap_Fn)
     
    moduleListByFed = []
    moduleListByPrt = []
    moduleListByDsk = []
    
    if opts.feds:
         fedlist = opts.feds.split(' ')
         moduleListByFed=[item['Official name of position'] for item in dictionary if item['FED ID'] in fedlist]
    if opts.prts:
        prtlist = opts.prts.split(' ')
        moduleListByPrt=[item['Official name of position'] for item in dictionary if item['PC position Mirror'] in prtlist]
    if opts.dsks:
        dsklist = opts.dsks.split(' ')
        moduleListByDsk=[item['Official name of position'] for item in dictionary if len(item['Official name of position'].split('_'))>3 and item['Official name of position'].split('_')[2][-1] in dsklist]
    
    moduleList = moduleListByFed + moduleListByPrt + moduleListByDsk
    
    if opts.ex:
        exlist = opts.ex.split(' ')
        moduleList = [module for module in moduleList if module not in exlist]
    
    config = 'detconfig'
    newVersion = mkNewConfigVersion(config)
    
    list2dat(moduleList, 'detectconfig.dat')
    save = raw_input("Do you want to set new version <%s/%d> as default? (y/N)?\n"%(config,newVersion))
    
    if save.lower() in ['n','no']:
        save = False
    elif save.lower() in ['y','yes']:
        save = True

    if save:
        setAsDefault(config, newVersion)

if __name__ == "__main__":
    main()
