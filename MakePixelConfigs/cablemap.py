# list of keys
# {'DOH A/B': '', '': '', 'POH SN': '', 'mfecchannel': '', 'CCU': '03 (v1)', 'PC position Mirror': '', 'internal disk name': '', 'POH fiber color': '', 'FEC position': '', 'PP0 Adapter/FED': 'CCU+tFEC', 'DCDC channel': '', 'flex cable': '', 'PP0 Adapter/FEC': '-z up left 1', 'PC position phi': '', 'POH board': '', 'PC port': '', 'internal POH no': '', 'FED receiver': '', 'FED position': '', 'FED channel': '', 'channel': '', 'internal naming per Disk': '', 'DCDC name': '', 'POH Bundle': '', 'DCDC J11/J12': '', 'PC name': '', 'Official name of position': '', 'FEC ID': '', 'DOH bundle': '17', 'FED ID': '', 'Filterboard DCS': '', 'Filterboard module power': 'CI-B 008', 'DCDC': '', 'PP0 Ad.Slot/FEC': '1', 'PP0 Ad.Slot/FED': '', 'PC identifier': '', 'Module': '', 'HubID': '', 'mfec': '', 'FEC/FED crate': '', 'DOH QR': '30201210004685'}

import csv
import math

def getdict(filename='cablingmap_fpixphase1_BmI.csv'):
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
    portcardmapfile.write("# Portcard              Module                     AOH channel") 

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

def mapDOHbundle(bundlenumber):
    dictionary = getdict('csv/cablingmap_fpixphase1_BpO.csv')
    for row in dictionary:
        if len(row['POH SN'].split('/'))<2:continue
        if bundlenumber is int(row['POH SN'].split('/')[1].strip("0")):
           print 'bundlenumber:'+str(bundlenumber)+ ':FED position:'+row['FED position']+':FED receiver:'+row['FED receiver']
           break

def main():
   #printnametranslation('cablingmap_fpixphase1_BmI.csv')
   #printnametranslation('cablingmap_fpixphase1_BpO.csv')
    printportcardmap('cablingmap_fpixphase1_BpO.csv')
if __name__ == "__main__":
    main()
    

