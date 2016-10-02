# list of keys
# {'DOH A/B': '', '': '', 'POH SN': '', 'mfecchannel': '', 'CCU': '03 (v1)', 'PC position Mirror': '', 'internal disk name': '', 'POH fiber color': '', 'FEC position': '', 'PP0 Adapter/FED': 'CCU+tFEC', 'DCDC channel': '', 'flex cable': '', 'PP0 Adapter/FEC': '-z up left 1', 'PC position phi': '', 'POH board': '', 'PC port': '', 'internal POH no': '', 'FED receiver': '', 'FED position': '', 'FED channel': '', 'channel': '', 'internal naming per Disk': '', 'DCDC name': '', 'POH Bundle': '', 'DCDC J11/J12': '', 'PC name': '', 'Official name of position': '', 'FEC ID': '', 'DOH bundle': '17', 'FED ID': '', 'Filterboard DCS': '', 'Filterboard module power': 'CI-B 008', 'DCDC': '', 'PP0 Ad.Slot/FEC': '1', 'PP0 Ad.Slot/FED': '', 'PC identifier': '', 'Module': '', 'HubID': '', 'mfec': '', 'FEC/FED crate': '', 'DOH QR': '30201210004685'}

import csv
import math

def getdict(filename='csv/cablingmap_fpixphase1_BmI.csv'):
    rows = []
    with open(filename, mode='r') as infile:
         reader = csv.DictReader(infile)
         for row in reader:  
             rows.append(row)
    return rows

def printnametranslation(xmlfilename):
    dictionary = getdict(xmlfilename)
    nametranslationfile = open("ConfigDat/translation.dat","w")
    nametranslationfile.write("#name                              A/B   FEC       mfec      mfecch    hubid     port      rocid     FEDid     FEDch     roc# \n")
  
    for row in dictionary:
        fedch=''
        fedchs=row['FED channel'].split('/')
        if len(fedchs)<2:continue
        for x in range(16):
            tbmcore = 'A'
            rocn=0
            if x < 8:
               tbmcore= 'A'
               fedch=fedchs[0]
               rocn=x
            else:
               tbmcore= 'B'
               fedch=fedchs[1]
               rocn=x-8
            
            i,d = math.modf(float(x)/4.0)
            towrite=row['Official name of position']+'_ROC%s'%str(x)+'         '+tbmcore +'        '+row['FEC position']+'      '+row['mfec']+'     '+row['mfecchannel'] +'     '+row['HubID']+'      '+ '%i'%d +'      '+ str(x) + '      '+row['FED ID']+'       '+ fedch+'     '+str(rocn)+'\n'
            nametranslationfile.write(towrite)

def printportcardmap(xmlfilename):
    dictionary = getdict(xmlfilename)
    portcardmapfile=open("ConfigDat/portcardmap.dat","w")
    portcardmapfile.write("# Portcard             Module                     AOH channel") 

    for row in dictionary:
        fedch=''
        fedchs=row['FED channel'].split('/')
        if len(fedchs)<2:continue
        portcard=list(row['PC position Mirror'])[-1]
        print portcard
        towrite='FPix_BpO_D1_PRT'+'           '+row['Official name of position']  
 
def mapfedidPOHbundle(bundlenumber):
    dictionary = getdict('csv/cablingmap_fpixphase1_BpO.csv')
    for row in dictionary:
        if len(row['POH SN'].split('/'))<2:continue
        if bundlenumber is int(row['POH SN'].split('/')[1].strip("0")):
           print 'bundlenumber:'+str(bundlenumber)+ ':FED position:'+row['FED position']+':FED receiver:'+row['FED receiver']
           break
        else:
           print 'test'
           break

def mapDOHbundle(bundlenumber):
    dictionary = getdict('csv/cablingmap_fpixphase1_BpO.csv')
    for row in dictionary:
        if len(row['POH SN'].split('/'))<2:continue
        if bundlenumber is int(row['POH SN'].split('/')[1].strip("0")):
           print 'bundlenumber:'+str(bundlenumber)+ ':FED position:'+row['FED position']+':FED receiver:'+row['FED receiver']
           break

def printfecconfig(xmlfilename):
    dictionary = getdict(xmlfilename)
    portcardmapfile=open("ConfigDat/fecconfig.dat","w")
    portcardmapfile.write("#FEC number    crate     vme base address     type    URI")
    portcardmapfile.write('\n')
    portcardmapfile.write("1               1         0x60000000           CTA     chtcp-2.0://cmsuppixch:10203?target=devpxfec:50001")
    
def printdetconfig(xmlfilename):
    dictionary =  getdict(xmlfilename)
    detconfigfile=open("ConfigDat/detconfig.dat","w")
    for row in dictionary:
        if row['Official name of position']=='':
            break;
        for x in range(16):
            towrite=row['Official name of position']+'_ROC%s'%str(x)+'\n'
            detconfigfile.write(towrite)
    
def printfedconfig(xmlfilename):
    dictionary =  getdict(xmlfilename)
    fedconfigfile=open("ConfigDat/fedconfig.dat","w")
    fedconfigfile.write("#FED number     crate     vme base address     type    URI")
    fedconfigfile.write('\n')
    elements_fedID=[]
    for row in dictionary:
        if(row['FED ID'] not in elements_fedID):
            elements_fedID.append(row['FED ID'])
    host=raw_input("Please input host computer in format 'localhost:10203'for FED:")
    target=raw_input("Please input target fed in format 'fed' (assuming port is 50001 for debug info):") 
    for x in elements_fedID:
        if x=='':
            continue;    
        towrite=str(x)+'     '+row['FEC/FED crate']+'     '+str(x)+'     '+'CTA'+'chtcp-2.0://'+host+'?target='+target+str(x)+':50001'+'\n'
        fedconfigfile.write(towrite)

def printBmIdcdc():
    for x in range(3):
       for y in range(4):
           dcdcconfigfilename='ConfigDat/dcdc/dcdc_FPix_BmI_D%s'%str(x+1)+"_PRT%s"%str(y+1)+".dat"
           dcdcconfigfile=open(dcdcconfigfilename,"w")
           dcdcconfigfile.write("Enabled: no"+"\n"+"CCUAddressEnable: 0x7e"+"\n"+"CCUAddressPgood: 0x7d"+"\n"+"PIAChannelAddress: 0x30"+"\n"+"PortNumber: 2"+'\n')

def printtbm(xmlfilename):
    dictionary =  getdict(xmlfilename)
    elements_tbmdelay=[]
    for row in dictionary:
        tbm_row=row['Official name of position']
        if tbm_row=='':
            continue;
        FPix, B_PorM_IorO, Disk,BLD,PNL, Ring=tbm_row.split('_')
        tbm_related=B_PorM_IorO+'_'+Disk+'_'+BLD+'_'+PNL
        if tbm_related not in elements_tbmdelay:
            elements_tbmdelay.append(tbm_related)

    for x in elements_tbmdelay:
        if x=='':
            continue;
        tbmfilename='ConfigDat/tbm/TBM_module_Pilt_'+str(x)+'.dat'
        tbmfile=open (tbmfilename,"w")
        towrite='Pilt'+'_'+B_PorM_IorO+'_'+Disk+'_'+BLD+'_'+PNL+'_'+'ROC0'+'\n'+\
        "TBMABase0: 0\n"+\
        "TBMBBase0: 0\n"+\
        "TBMAAutoReset: 0\n"+\
        "TBMBAutoReset: 0\n"+\
        "TBMANoTokenPass: 0\n"+\
        "TBMBNoTokenPass: 0\n"+\
        "TBMADisablePKAMCounter: 0\n"+\
        "TBMBDisablePKAMCounter: 0\n"+\
        "TBMAPKAMCount: 5\n"+\
        "TBMBPKAMCount: 5\n"+\
        "TBMPLLDelay: 132\n"+\
        "TBMADelay: 73\n"+\
        "TBMBDelay: 73"
        tbmfile.write(towrite)

def main():
   #printnametranslation('cablingmap_fpixphase1_BmI.csv')
   #printnametranslation('csv/cablingmap_fpixphase1_BpO.csv')
   # printportcardmap('csv/cablingmap_fpixphase1_BpO.csv')
   #printfecconfig('csv/cablingmap_fpixphase1_BpO.csv')
   printtbm('csv/cablingmap_fpixphase1_BpO.csv')
if __name__ == "__main__":
    main()
 

