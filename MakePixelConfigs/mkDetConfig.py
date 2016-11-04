import os
from cablemap import *
from optparse import OptionParser

class MyParser(OptionParser):
    def format_epilog(self, formatter):
        return self.epilog
epi = '''
EXAMPLE:
    > python mkDetConfig.py --fed='1287 1289 1293'
    > python mkDetConfig.py --prt='1TA 1BD 2TB'
    > python mkDetConfig.py --dsk='1 3'
    > python mkDetConfig.py --exclude='FPix_BpO_D1_BLD6_PNL2_RNG1 FPix_BpO_D1_BLD7_PNL1_RNG1'
    > python mkDetConfig.py --fed='1290 1291' --prt='1BD 3TA' --exclude='FPix_BpO_D1_BLD6_PNL2_RNG1'
'''

parser = MyParser(epilog=epi)
parser.add_option('','--fed',dest='feds',help='Input fed list as string.')
parser.add_option('','--prt',dest='prts',help='Input portcard list as string.')
parser.add_option('','--dsk',dest='dsks',help='Input disk list as string')
parser.add_option('','--exclude',dest='ex',help='Input name list of module to be excluded as string')
parser.add_option('','--include',dest='icld',help='Input name list of module to be included as string')

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
    cdb = "~tif/TriDAS/pixel/PixelConfigDBInterface/test/bin/linux/x86_64_slc6/PixelConfigDBCmd.exe "
    args = "--insertVersionAlias "+configName+" "+str(version)+" Default"
    print cdb+args
    os.system(cdb+args)



def main():
    cableMap_Fn='cablingmap_fpixphase1_BpO.csv'
    dictionary = getdict(filename='csv/'+cableMap_Fn)
     
    moduleListByFed = []
    moduleListByPrt = []
    moduleListByDsk = []
    includelist = []
    
    if opts.feds:
         fedlist = opts.feds.split(' ')
         moduleListByFed=[item['Official name of position'] for item in dictionary if item['FED ID'] in fedlist]
    if opts.prts:
        prtlist = opts.prts.split(' ')
        moduleListByPrt=[item['Official name of position'] for item in dictionary if item['PC position Mirror'] in prtlist]
    if opts.dsks:
        dsklist = opts.dsks.split(' ')
        moduleListByDsk=[item['Official name of position'] for item in dictionary if len(item['Official name of position'].split('_'))>3 and item['Official name of position'].split('_')[2][-1] in dsklist]
    
    if opts.icld:
        includelist = opts.icld.split(' ')

    moduleList = moduleListByFed + moduleListByPrt + moduleListByDsk + includelist
    moduleList = sorted(set(moduleList))

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
