import os,sys
from JMTTools import *
from mkDetConfig import *


run_num = run_from_argv()
run_dir = os.path.join(POS_OUTPUT_DIRS,'Run_0','Run_%d'%run_num)
config='tbm'

tbmNewVersion = mkNewConfigVersion(config)
tbmNewDir = os.path.join(PIXELCONFIGURATIONBASE,config,str(tbmNewVersion))
tbmDatList = glob(os.path.join(run_dir,'TBM_module_FPix*.dat'))
if len(tbmDatList)==0:
    print 'WRONG run number/ NO new config generated!!\n Exit now...'
    os.system('rmdir %s'%tbmNewDir)
    sys.exit(0)

cmd = 'cp %s %s' %(os.path.join(run_dir,'TBM_module_FPix*.dat'),tbmNewDir)
print cmd
os.system(cmd)

save = raw_input("Do you want to set new version <%s/%d> as default? (y/N)?\n"%(config,tbmNewVersion))

if save.lower() in ['n','no']:
    save = False
elif save.lower() in ['y','yes']:
    save = True
                                                                                                    
if save:
    setAsDefault(config, tbmNewVersion)
