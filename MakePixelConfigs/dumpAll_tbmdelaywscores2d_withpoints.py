import sys, os
from pprint import pprint
from JMTTools import *
from JMTROOTTools import *
from cablemap import *
set_style()

run = run_from_argv()
run_dir = run_dir(run)
in_fn = os.path.join(run_dir, 'TBMDelay.root')
if not os.path.isfile(in_fn):
    raise RuntimeError('no file at %s' % in_fn)
out_dir = os.path.join(run_dir, 'dump_tbmdelaywscores')
os.system('mkdir -p %s' % out_dir)

f = ROOT.TFile(in_fn)

# JMT need ROOT os.walk...
all_graphs = defaultdict(dict)

c = ROOT.TCanvas('c', '', 1300, 1000)
c.Divide(3,3)
c.cd(0)
pdf_fn = os.path.join(out_dir, '2d.pdf')
c.Print(pdf_fn + '[')
hs=[]
mksN=[]
mksO=[]
#lgds=[]

for ikey, key in enumerate(f.GetListOfKeys()):
    obj = key.ReadObj()
    c.cd(ikey % 9 + 1)
    h = ROOT.TH2F('-'.join(obj.GetName().split('_')[0:2]),'',8,0,8,8,0,8)
    h.GetXaxis().SetTitle('160 MHz')
    h.GetYaxis().SetTitle('400 MHz')
    h.SetStats(False)
    h.SetTitle('-'.join(obj.GetName().split('_')[0:2]))
    h.SetMinimum(197)
    h.SetMaximum(200)
    hs.append(h)
    for x in range(64):
        y = obj.GetBinContent(x+1)
        col = x>>3
        row = x&7
        h.SetBinContent(col+1, row+1, y) 
    colors = array("i",[51+i for i in range(50)])
    ROOT.gStyle.SetPalette(len(colors), colors)
    hs[-1].Draw('colz')
    c.Update()

    fed= obj.GetName().split('_')[0].replace('FED','')                  
    if 'Fb' in obj.GetName():
        ch = str(2*int(obj.GetName().split('_')[1].replace('Fb','')))
    else:
        ch = obj.GetName().split('_')[1].replace('Ch','').lstrip("0") 
    module = findmodule(fed,ch)                                       
    tbmfile = 'TBM_module_'+module+'.dat'                            
    newTBMParam = tbmdelays(os.path.join(run_dir,tbmfile))                        
    if newTBMParam is None:
        continue
    else:
        configDict = findconfigversions(findkey(run_dir))
        tbmVersion = configDict['tbm']
        oldTBMParam = tbmdelays(os.path.join(PIXELCONFIGURATIONBASE,'tbm',str(tbmVersion),tbmfile))
        
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

        #lgd = ROOT.TLegend(0.4,0.7,0.9,0.9)
        #lgd.SetBorderSize(0)
        #lgd.SetFillColorAlpha(1, 0)
        #lgd.SetTextSize(0.06)
        #lgd.AddEntry(np,'New Setting','p')
        #lgds.append(lgd)
        #lgds[-1].Draw()
    
    if ikey % 9 == 8:
        c.cd(0)
        c.Print(pdf_fn)
c.cd(0)
c.Print(pdf_fn + ']')
os.system('evince %s'%pdf_fn)
