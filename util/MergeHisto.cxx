#include <iostream>

#include <TROOT.h>
#include <TFile.h>
#include <TH1F.h>
#include <TLegend.h>
#include <TCanvas.h>
#include <TPad.h>
#include <TString.h>
#include <TSystem.h>
#include <TGraphAsymmErrors.h>


#include <PMGValidation/AtlasStyle.h>
#include <PMGValidation/AtlasLabels.h>

#include <vector>
using namespace std;

int main( int argc, char* argv[] ) {

  if( argc != 6 ) {
      cout<<"usage :"<<endl
          <<"MergeHisto input1.root label1 input2.root label2 output.pdf"<<endl;
    return 0;
  }

  SetAtlasStyle();
  bool normalize = true;

  TString file1  = argv[1];
  TString label1 = argv[2];
  TString file2  = argv[3];
  TString label2 = argv[4];
  TString outputFilename = argv[5];

  TFile *f1 = new TFile( file1 );
  TFile *f2 = new TFile( file2 );

  vector<TString> h_names = {"h_jetN","h_jetPt","h_jetE","h_jetEta","h_jetPhi",
                             "h_bjetN","h_bjetPt","h_bjetE","h_bjetEta","h_bjetPhi",
                             "h_electronN","h_electronPt","h_electronE","h_electronEta","h_electronPhi","h_electronQ",
                             "h_muonN","h_muonPt","h_muonE","h_muonEta","h_muonPhi","h_muonQ",
                             "h_met","h_metPhi","h_meff"};
  size_t histo_counter = 0;
  for(auto &h_name : h_names){

    TH1F  *h1 = static_cast<TH1F*>(f1->Get( h_name ));
    h1->SetLineColor(kBlue+2);
    h1->GetXaxis()->SetLabelOffset(0.05);

    TH1F  *h2 = static_cast<TH1F*>(f2->Get( h_name ));
    h2->SetMarkerStyle(1);
    h2->SetLineColor(kRed+2);

    double integral_h1 = h1->Integral();
    double integral_h2 = h2->Integral();
    if(normalize && integral_h1 && integral_h2) {
        h1->Scale(1.0/integral_h1);
        h2->Scale(1.0/integral_h2);
    }

    TLegend *legend=new TLegend(0.90,0.90,0.80,0.80);
    legend->SetTextFont(62);
    legend->SetTextSize(0.035);
    legend->AddEntry(h1, label1,"l");
    legend->AddEntry(h2, label2,"l");

    TCanvas *c = new TCanvas( h_name , h_name );
    TPad* p1 = new TPad("p1","p1",0.0,0.25,1.0,1.0,-22);
    TPad* p2 = new TPad("p2","p2",0.0,0.0,1.0,0.25,-21);
    p1->SetBottomMargin(0.02);
    p2->SetTopMargin(0.05);
    p2->SetBottomMargin(0.5);
    p1->Draw();
    p2->Draw();

    // First Pad
    p1->cd();
    h1->Draw("HIST");
    h2->Draw("HIST E SAME");
    legend->Draw();

    // Second Pad
    p2->cd();

    TH1F* href = (TH1F*)h2->Clone("ref");
    for (Int_t ik = 1; ik <= href->GetXaxis()->GetNbins(); ik++) href->SetBinContent( ik , 1. );

    href->SetLineColor(kBlack);
    href->SetLineWidth(1);
    href->SetLineStyle(2);

    href->SetMaximum(1.25);
    href->SetMinimum(0.75);

    href->GetYaxis()->SetTitle(label1+" / "+label2);

    href->GetXaxis()->SetLabelSize(0.17);
    href->GetYaxis()->SetNdivisions(505);
    href->GetYaxis()->SetLabelSize(0.12);

    href->GetXaxis()->SetTitleSize(0.17);
    href->GetXaxis()->SetTitleOffset(1.35);
    href->GetYaxis()->SetTitleSize(0.12);
    href->GetYaxis()->SetTitleOffset(0.5);

    href->Draw("HIST");

    TH1F* hR = (TH1F*)h2->Clone("ratio");
    hR->Divide(h1);
    hR->SetMarkerStyle(1);

    for (Int_t ik = 1; ik <= hR->GetXaxis()->GetNbins(); ik++) {
        if(h1->GetBinContent(ik)>0. && h2->GetBinContent(ik)>0.)
        hR->SetBinError( ik ,
                         hR->GetBinContent(ik) *
                         ( (h1->GetBinError(ik)/h1->GetBinContent(ik)) +
                           (h2->GetBinError(ik)/h2->GetBinContent(ik)) ) );
    }

    hR->Draw("HIST E SAME");

    // Write
    bool outputPdf = outputFilename.EndsWith(".pdf");
    bool outputPng = outputFilename.EndsWith("/"); // if given out dir, save individual png
    if(outputPdf) {
        bool first_histo = histo_counter==0;
        bool last_histo = histo_counter==h_names.size()-1;
        c->Print(outputFilename+(first_histo ? "(" :
                                 last_histo ? ")" :  ""));
    } else if (outputPng) {
        TString outputDir = outputFilename;
        c->Print(outputDir + h_name + ".png");

    } else {
        cout<<"Invalid output choice '"<<outputFilename<<"'"<<endl
            <<"must be either a '*.pdf' or a directory '*/' (-> save png)"<<endl;
    }
    histo_counter++;
  } // for(h_name)

}
