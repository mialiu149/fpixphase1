import sys, os
from pprint import pprint
from JMTTools import *
from JMTROOTTools import *
from cablemap import *
set_style()

def numConvert(x):
    return (8+x)&7

def getAroundedCoords((x, y)):
    nearest = [-1,0,1]
    ptList = [(numConvert(x+i), numConvert(y+j)) for i in nearest for j in nearest if (i or j)]
    return ptList

def findOptimalPoints(h, maxVal):
    hd={}
    for x in range(h.GetNbinsX()):
        for y in range(h.GetNbinsY()):
            hd[(x,y)] = h.GetBinContent(x+1,y+1)
    nd = {}
    for wp in hd.items():
        if wp[1] < maxVal:
            continue
        wp_x, wp_y = wp[0]
        scores = 0.
        for ptAround in getAroundedCoords((wp_x, wp_y)):
            scores += hd[ptAround]
        nd[(wp_x, wp_y)] = scores
    if not nd.values():
        return None
    bestScore = sorted(nd.values(), reverse=True)[0]
    optimalPoints = [k for k,v in nd.items() if v==bestScore]
    return optimalPoints

def getModuleList(detconfig_Fn):
    modulelist = []
    with open(detconfig_Fn) as inf:
        for line in inf:
            if len(line.split(' '))>1:
                continue
            if line.split(' ')[0].startswith('FPix'):
                x = line.split(' ')[0]
                modulelist.append('_'.join(x.split('_')[:-1]))
    return modulelist

run = run_from_argv()
run_dir = run_dir(run)
in_fn = os.path.join(run_dir, 'TBMDelay.root')
if not os.path.isfile(in_fn):
    raise RuntimeError('no file at %s' % in_fn)
out_dir = os.path.join(run_dir, 'dump_tbmdelaywscores')
os.system('mkdir -p %s' % out_dir)

f = ROOT.TFile(in_fn)

configDict = findconfigversions(findkey(run_dir))
detconfigVersion = configDict['detconfig']
moduleONList = getModuleList(os.path.join(PIXELCONFIGURATIONBASE,'detconfig',str(detconfigVersion),'detectconfig.dat'))

c = ROOT.TCanvas('c', '', 1300, 1000)
c.Divide(3,3)
c.cd(0)
pdf_fn = os.path.join(out_dir, 'test.pdf')
c.Print(pdf_fn + '[')

scaleMax = 200
scaleMin = 197
hs = []
mksN = []
mksO = []
mksE = []
#lgds=[]

for ikey, key in enumerate(f.GetListOfKeys()):
    obj = key.ReadObj()
    c.cd(ikey % 9 + 1)
    fedN = obj.GetName().split('_')[0]
    fedNum = fedN[3:]
    if 'Ch' in obj.GetName().split('_')[1]:
        chN = obj.GetName().split('_')[1]
        chNum = str(int(chN[2:]))
        module = findmodule(fedNum, chNum)
    else:
        fbN = obj.GetName().split('_')[1]
        chNum = str(int(fbN[2:])*2)
        module = findmodule(fedNum, chNum)
    if module not in moduleONList:
        continue
    
    h = ROOT.TH2F(fedN+' '+chN+' '+module,'',8,0,8,8,0,8)
    h.GetXaxis().SetTitle('160 MHz')
    h.GetYaxis().SetTitle('400 MHz')
    h.SetStats(False)
    h.SetTitle(fedN+' '+chN+' '+module)
    h.SetMinimum(scaleMin)
    h.SetMaximum(scaleMax)
    
    for x in range(obj.GetNbinsX()):
        y = obj.GetBinContent(x+1)
        col = x>>3
        row = x&7
        h.SetBinContent(col+1, row+1, y) 
    hs.append(h)

colors = array("i",[51+i for i in range(50)])
ROOT.gStyle.SetPalette(len(colors), colors)

for index, h in enumerate(hs):
    c.cd(index%9+1)
    moduleN = h.GetTitle().split(' ')[-1]
    tbm_Fn = 'TBM_module_'+moduleN+'.dat'
    newTBMParam = getTBMDelayParam(os.path.join(run_dir,tbm_Fn))
    hs[index].Draw('colz')
    c.Update()
    
    if newTBMParam is None:
        continue
    else:
        tbmVersion = configDict['tbm']
        oldTBMParam = getTBMDelayParam(os.path.join(PIXELCONFIGURATIONBASE,'tbm',str(tbmVersion),tbm_Fn))
        npx = [float(newTBMParam['pll']>>5)+0.5]
        npy = [float((newTBMParam['pll']&28)>>2)+0.5]
        opx = [float(oldTBMParam['pll']>>5)+0.5]
        opy = [float((oldTBMParam['pll']&28)>>2)+0.5]

        np = ROOT.TGraph(1, array('d',npx), array('d',npy))
        np.SetMarkerStyle(29)
        np.SetMarkerColor(1)
        np.SetMarkerSize(1.5)
        mksN.append(np)
        mksN[-1].Draw('P same') # solid black star for NEW
        c.Update()
        
        op = ROOT.TGraph(1, array('d',opx), array('d',opy))
        op.SetMarkerStyle(26)
        op.SetMarkerColor(1)
        op.SetMarkerSize(1.2)
        mksO.append(op)
        mksO[-1].Draw('P same') # triangle for OLD
        c.Update()

        ep = findOptimalPoints(h, scaleMax)
        if ep:
            if (int(npx[0]-0.5),int(npy[0]-0.5)) in ep:
                epx = npx
                epy = npy
            else:
                epx = [float(ep[0][0])+0.5]
                epy = [float(ep[0][1])+0.5]

            ep = ROOT.TGraph(1, array('d',epx), array('d',epy))
            ep.SetMarkerStyle(28)
            ep.SetMarkerColor(1)
            ep.SetMarkerSize(1.2)
            mksE.append(ep)
            mksE[-1].Draw('P same') # cross for EYE
            c.Update()

        #lgd = ROOT.TLegend(0.4,0.7,0.9,0.9)
        #lgd.SetBorderSize(0)
        #lgd.SetFillColorAlpha(1, 0)
        #lgd.SetTextSize(0.06)
        #lgd.AddEntry(np,'New Setting','p')
        #lgds.append(lgd)
        #lgds[-1].Draw()


    if index%9+1 == 9 or index+1==len(hs):
        c.cd(0)
        c.Print(pdf_fn)
        for i in range(9):
            c.cd(i+1).Clear()
    
c.cd(0)
c.Print(pdf_fn + ']')
os.system('evince %s'%pdf_fn)
