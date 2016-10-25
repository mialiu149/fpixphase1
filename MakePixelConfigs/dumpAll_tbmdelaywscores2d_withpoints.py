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
mks=[]
lgds=[]

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
    tbmfile = '/TBM_module_'+module+'.dat'                            
    print fed, ch, module                                                  
    tbmdelayParam = tbmdelays(run_dir+tbmfile)                        
    print tbmdelayParam
    if tbmdelayParam is None:
        continue
    else:
        npx = [float(tbmdelayParam['pll']>>5)+0.5]
        npy = [float((tbmdelayParam['pll']&28)>>2)+0.5]
        print npx, npy
        np = ROOT.TGraph(1, array('d',npx), array('d',npy))
        np.SetMarkerStyle(21)
        np.SetMarkerColor(1)
        np.SetMarkerSize(1.5)
        mks.append(np)
        mks[-1].Draw('P same')
        c.Update()
        lgd = ROOT.TLegend(0.4,0.7,0.9,0.9)
        lgd.SetBorderSize(0)
        lgd.SetFillColorAlpha(1, 0)
        lgd.SetTextSize(0.06)
        lgd.AddEntry(np,'New Setting','p')
        lgds.append(lgd)
        #lgds[-1].Draw()
    
    if ikey % 9 == 8:
        c.cd(0)
        c.Print(pdf_fn)
c.cd(0)
c.Print(pdf_fn + ']')
os.system('evince %s'%pdf_fn)
