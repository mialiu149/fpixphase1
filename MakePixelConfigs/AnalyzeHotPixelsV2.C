#include <string> 
#include <sstream>

using namespace std;

//std::string to_string(int myfavoriteINT){     std::stringstream ss;     ss << myfavoriteINT;     string intasastring = ss.str();     return intasastring; }

//note that V2 does not work for the most early runs
void AnalyzeHotPixelsV2(int runnumber){

  float max = 100;//more than max hit to be considered hot
    //try something more meaningful, see l.45
  unsigned int PotentialHotCounter = 0;
  unsigned int PotentialHotPixels = 0;
  unsigned int NotHotCounter = 0;
  string filename = "DQM_V0001_PixelPhase1_R000"+to_string(runnumber)+".root";
  string basedir = "DQMData/Run "+to_string(runnumber)+"/PixelPhase1/Run summary/Phase1_MechanicalView/PXForward/";
  string newname = "PotentialHot_R000"+to_string(runnumber)+".root";
    TFile *f = TFile::Open(filename.c_str());
    int runnumber2 = atoi(to_string(runnumber).substr(0, 2).c_str());
    int runnumber4 = atoi(to_string(runnumber).substr(0, 4).c_str());
    if(f==NULL){
        cout << "Download DQM file from" << endl << "https://cmsweb.cern.ch/dqm/online/data/browse/Original/000" << runnumber2 << "xxxx/000" << runnumber4 << "xx/" << filename << endl;
        cout << "If file does not exist there, the run does not exist or is not finished yet." << endl;
        return;
    }
    TFile *fsearch = new TFile(newname.c_str(),"RECREATE");
    //cout << filename << endl;
    //cout << f->GetName() << endl;
    f->cd();
    string summaryfilename = basedir + "digi_occupancy_per_SignedDiskCoord_per_SignedBladePanelCoord_PXRing_1";
    TH2F *hsummary1 = (TH2F*)f->Get(summaryfilename.c_str());
    summaryfilename = basedir + "digi_occupancy_per_SignedDiskCoord_per_SignedBladePanelCoord_PXRing_2";
    TH2F *hsummary2 = (TH2F*)f->Get(summaryfilename.c_str());
    float sumoccupancy = 0;
    float numofoccupantROCs = 0;
    for(int ix = 1; ix<=hsummary1->GetNbinsX();++ix){
        for(int iy = 1; iy<=hsummary1->GetNbinsX();++iy){
            if(hsummary1->GetBinContent(ix,iy)>0){
                sumoccupancy += hsummary1->GetBinContent(ix,iy);
                ++numofoccupantROCs;
            }
        }
    }
    for(int ix = 1; ix<=hsummary2->GetNbinsX();++ix){
        for(int iy = 1; iy<=hsummary2->GetNbinsX();++iy){
            if(hsummary2->GetBinContent(ix,iy)>0){
                sumoccupancy += hsummary2->GetBinContent(ix,iy);
                ++numofoccupantROCs;
            }
        }
    }
    max = 10.*sumoccupancy/numofoccupantROCs;
    cout << "Choose maximal occupancy to be " << max << " (which is 10x the average)" << endl;
    string hc[4] = {"mI", "mO", "pI", "pO"};
    for(unsigned int ih = 0; ih<4; ++ih){
      for(unsigned int ir = 1; ir<=2; ++ir){
	string ring = to_string(ir);
	for(unsigned int id = 1; id<=3; ++id){
	  string disk = to_string(id);
	  if(ih<2) disk = "-"+to_string(id);
	  else     disk = "+"+to_string(id);
	  for(unsigned int ib = 1; ib<=17; ++ib){
	    if(ir==1&&ib>11) continue;//inner ring has only 11 blades
	    string blade = to_string(ib);
	    if(ih==1||ih==3) blade = "-" + to_string(ib);
	    //else             blade = "+" + to_string(ib);
	    for(unsigned int ip = 1; ip<=2; ++ip){
	      f->cd();
	      string histodir = basedir + "HalfCylinder_"+hc[ih]+"/PXRing_"+ring+"/PXDisk_"+disk+"/SignedBlade_"+blade+"/";
	      string modulename = "FPix_B"+hc[ih]+"_D"+to_string(id)+"_BLD"+to_string(ib)+"_PNL"+to_string(ip)+"_RNG"+to_string(ir);
	      string histoname = histodir + "digi_occupancy_per_col_per_row_"+modulename;
	      //cout << filename << " " << histoname << endl;
	      //cout << modulename << " " << histoname << endl;
	      TH2F *h = (TH2F*)f->Get(histoname.c_str());
	      if(h==NULL) {
		cout << "Module " << modulename << " is not in DQM file" << endl;
		continue;
	      }
	      if(h->GetMaximum()>max) {
		//cout << "Maximum of module " << modulename << " is " << h->GetMaximum() << endl;
		++PotentialHotCounter;
		for(int x = 1; x<=h->GetNbinsX(); ++x){
		  for(int y = 1; y<=h->GetNbinsY(); ++y){
		    float xc = h->GetXaxis()->GetBinCenter(x);
		    float yc = h->GetYaxis()->GetBinCenter(y);
		    //ROCs 0-7: yc 0-79
		    //ROC0:  xc 415-->364
		    //ROC1:  xc 363-->312
		    //ROC2:  xc 311-->260
		    //ROC3:  xc 259-->208
		    //ROC4:  xc 207-->156
		    //ROC5:  xc 155-->104
		    //ROC6:  xc 103-->52
		    //ROCs 8-15: yc 159-->80
		    //ROC8:  xc 0-->51
		    //ROC9:  xc 52-->103
		    //ROC10: xc 104-->155
		    //ROC11: xc 156-->207
		    //ROC12: xc 208-->259
		    //ROC13: xc 260-->311
		    //ROC14: xc 312-->363
		    //ROC15: xc 364-->415
		    int mycol;
		    int myroc;
		    int myrow;
		    if(yc<80){
		      myrow = yc;
		      if(xc<52){       myroc =  7; mycol = abs(xc- 51); }
		      else if(xc<104){ myroc =  6; mycol = abs(xc-103); }
		      else if(xc<156){ myroc =  5; mycol = abs(xc-155); }
		      else if(xc<208){ myroc =  4; mycol = abs(xc-207); }
		      else if(xc<260){ myroc =  3; mycol = abs(xc-259); }
		      else if(xc<312){ myroc =  2; mycol = abs(xc-311); }
		      else if(xc<364){ myroc =  1; mycol = abs(xc-363); }
		      else if(xc<416){ myroc =  0; mycol = abs(xc-415); }
		    }
		    else{
		      myrow = abs(yc-159);
		      if(xc<52){       myroc =  8; mycol = abs(xc-  0); }
		      else if(xc<104){ myroc =  9; mycol = abs(xc- 52); }
		      else if(xc<156){ myroc = 10; mycol = abs(xc-104); }
		      else if(xc<208){ myroc = 11; mycol = abs(xc-156); }
		      else if(xc<260){ myroc = 12; mycol = abs(xc-208); }
		      else if(xc<312){ myroc = 13; mycol = abs(xc-260); }
		      else if(xc<364){ myroc = 14; mycol = abs(xc-312); }
		      else if(xc<416){ myroc = 15; mycol = abs(xc-364); }
		    }
		    if(h->GetBinContent(x,y)>max) {
		      cout << "Module " << modulename << " ROC " << myroc << " row " << myrow << " col " << mycol << " is hot: " <<h->GetBinContent(x,y) << endl;
		      ++PotentialHotPixels;
		    }
		  }//y
		}//x
		fsearch->cd();
		h->Write(modulename.c_str(),TObject::kOverwrite);
		f->cd();
	      }
	      else
		++NotHotCounter;
	    }//ip
	  }//ib
	}//id
      }//ir
    }//ih
    cout << "Found " << float(PotentialHotCounter)<<"/" <<float(PotentialHotCounter+NotHotCounter) << " modules with potential hot pixels, Npixels = " << PotentialHotPixels << endl;
    fsearch->Close();
}//AnalyzeHotPixels
