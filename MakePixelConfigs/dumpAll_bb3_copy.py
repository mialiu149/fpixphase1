import sys, os
from pprint import pprint
from JMTTools import *
from JMTROOTTools import *
import moduleSummaryPlottingTools as FNAL
from trysomething_write_other_hc_configs import doer, HC, module_sorter_by_portcard_phi
set_style(light=True)
ROOT.gStyle.SetOptStat(111110)
ROOT.gStyle.SetOptFit(1111)

#if len(sys.argv) < 3:
#    print 'usage: bb3.py disk in_fn out_fn'
#    sys.exit(1)

#disk = int(sys.argv[1])
#in_fn = sys.argv[1]
#out_fn = sys.argv[2]

run = run_from_argv()
run_dir = run_dir(run)
in_fn = glob(os.path.join(run_dir, 'TrimOutputFile_Fed_*.dat'))
if not in_fn:
    raise RuntimeError('Generate root file first!')
if len(in_fn)>1:
    raise RuntimeError('too many .dat files, check please!')
in_fn = in_fn[0]
out_dir = os.path.join(run_dir,'dump_bb3')
if not os.path.isdir(out_dir):
    os.system('mkdir -p %s' %out_dir) 

roc_fits_out_fn = os.path.join(out_dir,'bb3_roc_fits.pdf')

the_doer = doer()
t = trim_dat(in_fn)

raw  = defaultdict(lambda: [None]*4160)
norm = defaultdict(lambda: [None]*4160)

c = ROOT.TCanvas('c', '', 1920, 1000)
c.Divide(3,2)
c.cd(0)
c.SaveAs(roc_fits_out_fn + '[')

for iroc, (roc, l) in enumerate(t.ls.iteritems()):
    #print iroc, roc
    #if iroc % 10 != 0:
    #    continue

    d = [[], []]
    means = [0., 0.]
    mins = [1e99, 1e99]
    maxs = [-1e99, -1e99]
    for i,e in enumerate(l):
        #assert type(e) != int
        if type(e) == int:
            continue
        col = i / 80
        row = i % 80
        j = col % 2
        d[j].append((col, row, e.th, e.sg))
        means[j] += e.th
        mins[j] = min(e.th, mins[j])
        maxs[j] = max(e.th, maxs[j])

    for j in (0,1):
        mins[j] = max(mins[j], 0.)
        maxs[j] = min(maxs[j], 200.)

    n = [len(d[0]), len(d[1])]
    rmses = [0., 0.]
    ws = [0., 0.]
    ranges = [None, None]
    nbins = [0, 0]
    medians = [0.,0.]
    fit_ranges = [None, None]
    for j in (0,1):
        means[j] /= n[j]
        ths = [th for col, row, th, sg in d[j]]
        ths.sort()
        medians[j] = ths[n[j]/2]
        fit_ranges[j] = [ths[n[j]/20], ths[19*n[j]/20]]
        ws[j] = 0.5
        #for th, _ in d[j]:
        #    rmses[j] += (th - means[j])**2
        #rmses[j] = (rmses[j] / (n[j] - 1))**0.5
        ##ws[j] = 3.49 * rmses[j] / n[j]**(1./3)
        extra = (maxs[j] - mins[j]) * 0.1
        ranges[j] = [mins[j] - extra, maxs[j] + extra]
        nbins[j] = int(round((ranges[j][1] - ranges[j][0]) / ws[j]))
        #print 'roc %s j=%i mean %f rms %f w %f nbins %i range %s' % (roc, j, means[j], rmses[j], ws[j], nbins[j], ranges[j])

    hs = []
    for j, x in enumerate(['even', 'odd']):
        hs.append({
                'raw':   ROOT.TH1F('h_%s_raw_%s'   % (x, roc), '%s on %s, threshold;VcThr units;pixels/0.8' % (x.capitalize() + 's', roc), nbins[j], ranges[j][0], ranges[j][1]),
                'noise': ROOT.TH1F('h_%s_noise_%s' % (x, roc), '%s on %s, width;VcThr units;pixels/0.2'     % (x.capitalize() + 's', roc), 100,  0, 10),
                'norm':  ROOT.TH1F('h_%s_norm_%s'  % (x, roc), '%s on %s, normed2;VcThr units;pixels/0.16'  % (x.capitalize() + 's', roc), 100, -10, 10),
                })

    for j in (0,1):
        for col, row, th, sg in d[j]:
            hs[j]['raw'].Fill(th)
            hs[j]['noise'].Fill(sg)

    fits = [None, None]
    for j in (0,1):
        for ix, x in enumerate(['raw', 'noise']):
            c.cd(1+j*3+ix)
            h = hs[j][x]
            h.Draw()
            if x == 'raw':
                f = ROOT.TF1('f', 'gaus', fit_ranges[j][0], fit_ranges[j][1])
                res = h.Fit(f, 'QRS')
                assert fits[j] is None
                fits[j] = (res.Parameter(1), res.Parameter(2))

    for j,(mean,sigma) in enumerate(fits):
        h = hs[j]['norm']
        for col, row, th, sg in d[j]:
            raw [roc][col*80 + row] = th
            norm[roc][col*80 + row] = v = (th - mean)/sigma
            h.Fill(v)
        c.cd(1+j*3+2)
        #h.Fit('gaus', 'q')
        h.Draw()

    c.cd(0)
    c.SaveAs(roc_fits_out_fn)

c.SaveAs(roc_fits_out_fn + ']')
del c

assert set(raw.keys()) == set(norm.keys())

map_c = None #ROOT.TCanvas('c', '', 1920, 1000)
#this_out_fn = out_fn + '.module_maps.pdf'
module_maps_out_fn = os.path.join(out_dir,'bb3_module_maps.pdf')

bad_counts = defaultdict(lambda: [0]*16) #defaultdict(int)

#min_pcnum = 2 if disk == 2 else 1
min_pcnum = 1
max_pcnum = 4
for pcnum in xrange(min_pcnum,max_pcnum+1):
    print pcnum

    #modules = [m for m in sorted(the_doer.modules, key=module_sorter_by_portcard_phi)]
    modules = [m for m in sorted(the_doer.modules, key=module_sorter_by_portcard_phi) if the_doer.moduleOK(m) and m.portcardnum == pcnum]

    for module in modules:
        #print module.name
        for label, d in [('raw', raw), ('norm', norm), ('bad', norm)]:
            lists = []
            any_ok = False
            for i in xrange(16):
                roc = module.name + '_ROC' + str(i)
                if not d.has_key(roc):
                    continue
                any_ok = True
                lists.append(d[roc])

            if not any_ok:
                continue

            def xform(label, module_name, rocnum, col, row, val):
                global bad_counts
                if val is None:
                    if label == 'norm':
                        val = 6
                    elif label == 'bad':
                        val = 2
                elif label == 'bad':
                    val = 1 if val>5 else 0

                #if label == 'bad' and disk == 3 and pcnum in (1,2,4) and row in (58,59):
                #    val = 0

                if label == 'bad' and val != 0:
                    bad_counts[module_name][rocnum] += 1
                else:
                    bad_counts[module_name][rocnum] += 0
                return val

            if module.name in 'FPix_BmO_D2_BLD3_PNL2_RNG1':
                print "skip FPix_BmO_D2_BLD3_PNL2_RNG1"
                continue
            else:
                hs = flat_to_module(label, module.name, lists, xform)

            z_range = None
            if label == 'raw':
                z_range = (0,100)
            elif label == 'norm':
                z_range = (-5, 6.1)

            title = label + '   ' + m.portcard + ' ' + m.portcard_hj[1] + ' ' + str(m.portcard_connection) + '   ' + module.name + '   ' + module.module + '   ' + module.internal_name

            h, fc, pt = fnal_pixel_plot(hs, module.name, title, z_range=z_range, existing_c=map_c)
            #fc.SaveAs(module.name + '_' + label + '.pdf')
            if map_c is None:
                map_c = fc
                map_c.SaveAs(module_maps_out_fn + '[')
            map_c.SaveAs(module_maps_out_fn)

map_c.SaveAs(module_maps_out_fn + ']')

out_dp_fn = os.path.join(out_dir,'deadPixelBySigma.txt')
if os.path.isfile(out_dp_fn):
    cmd = 'mv %s %s' %(out_dp_fn,out_dp_fn+'.old')
    os.system(cmd)

print 'bad by module/roc:'
for m, rl in bad_counts.iteritems():
    outline = '{0:30}{1:3d}  {2}\n'.format(m,sum(rl),str(rl)) 
    with open(out_dp_fn,'a+') as output:
        output.write(outline)


os.system('cat %s' %out_dp_fn)
os.system('wc -l %s' %out_dp_fn)
os.system('evince %s'%module_maps_out_fn)
