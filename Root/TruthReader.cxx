#include <EventLoop/Job.h>
#include <EventLoop/StatusCode.h>
#include <EventLoop/Worker.h>
#include <PMGValidation/TruthReader.h>

#include "xAODRootAccess/Init.h"
#include "xAODRootAccess/TEvent.h"
#include "xAODTruth/TruthEvent.h"
#include "xAODTruth/TruthEventContainer.h"
#include "xAODRootAccess/tools/Message.h"
#include "xAODEventInfo/EventInfo.h"
#include "xAODTruth/TruthParticleContainer.h"
#include "xAODJet/JetContainer.h"
#include "xAODJet/JetAuxContainer.h"
#include "xAODMissingET/MissingETContainer.h"

#include <iostream>
using namespace std;

const double mev2gev = 1.0e-3;

/// Helper macro for checking xAOD::TReturnCode return values
#define EL_RETURN_CHECK( CONTEXT, EXP )			   \
  do {                                                     \
    if( ! EXP.isSuccess() ) {				   \
      Error( CONTEXT,					   \
	     XAOD_MESSAGE( "Failed to execute: %s" ),	   \
	     #EXP );					   \
      return EL::StatusCode::FAILURE;			   \
    }							   \
  } while( false )


// this is needed to distribute the algorithm to the workers
ClassImp(TruthReader)


TruthReader :: TruthReader():
    verbose(false),
    weightIndex(-1),
    printedEvents(0)
{
  // Here you put any code for the base initialization of variables,
  // e.g. initialize all pointers to 0.  Note that you should only put
  // the most basic initialization here, since this method will be
  // called on both the submission and the worker node.  Most of your
  // initialization code will go into histInitialize() and
  // initialize().
}



EL::StatusCode TruthReader :: setupJob (EL::Job& job)
{
  // Here you put code that sets up the job on the submission object
  // so that it is ready to work with your algorithm, e.g. you can
  // request the D3PDReader service or add output files.  Any code you
  // put here could instead also go into the submission script.  The
  // sole advantage of putting it here is that it gets automatically
  // activated/deactivated when you add/remove the algorithm from your
  // job, which may or may not be of value to you.

  // let's initialize the algorithm to use the xAODRootAccess package
  job.useXAOD ();
  EL_RETURN_CHECK( "setupJob()", xAOD::Init() ); // call before opening first file

  return EL::StatusCode::SUCCESS;
}



EL::StatusCode TruthReader :: histInitialize ()
{
  // Here you do everything that needs to be done at the very
  // beginning on each worker node, e.g. create histograms and output
  // trees.  This method gets called before any input files are
  // connected.
    SelectionHistograms &h = m_inclusive_histos;
  // Jet
  h.jetN   = new TH1F("h_jetN", "h_jetN", 25, 0, 25);
  h.jetPt  = new TH1F("h_jetPt", "h_jetPt", 50, 0, 1000);
  h.jetE   = new TH1F("h_jetE", "h_jetE", 50, 0, 1200);
  h.jetEta = new TH1F("h_jetEta", "h_jetEta", 50, -5, 5);
  h.jetPhi = new TH1F("h_jetPhi", "h_jetPhi", 20, 0, 3.14);
  // BJet
  h.bjetN   = new TH1F("h_bjetN", "h_bjetN", 8, 0, 8);
  h.bjetPt  = new TH1F("h_bjetPt", "h_bjetPt", 50, 0, 800);
  h.bjetE   = new TH1F("h_bjetE", "h_bjetE", 50, 0, 1000);
  h.bjetEta = new TH1F("h_bjetEta", "h_bjetEta", 50, -5, 5);
  h.bjetPhi = new TH1F("h_bjetPhi", "h_bjetPhi", 20, 0, 3.14);
  // Electron
  h.electronN   = new TH1F("h_electronN", "h_electronN", 7, 0, 7);
  h.electronPt  = new TH1F("h_electronPt", "h_electronPt", 50, 0, 300);
  h.electronE   = new TH1F("h_electronE", "h_electronE", 50, 0, 300);
  h.electronEta = new TH1F("h_electronEta", "h_electronEta", 50, -3, 3);
  h.electronPhi = new TH1F("h_electronPhi", "h_electronPhi", 20, 0, 3.14);
  h.electronQ   = new TH1F("h_electronQ", "h_electronQ", 2, -1, 1);
  // Muon
  h.muonN   = new TH1F("h_muonN", "h_muonN", 7, 0, 7);
  h.muonPt  = new TH1F("h_muonPt", "h_muonPt", 50, 0, 300);
  h.muonE   = new TH1F("h_muonE", "h_muonE", 50, 0, 300);
  h.muonEta = new TH1F("h_muonEta", "h_muonEta", 50, -3, 3);
  h.muonPhi = new TH1F("h_muonPhi", "h_muonPhi", 20, 0, 3.14);
  h.muonQ   = new TH1F("h_muonQ", "h_muonQ", 2, -1, 1);
  // Global Variable
  h.meff   = new TH1F("h_meff", "h_meff", 50, 0, 3000);
  h.met    = new TH1F("h_met", "h_met", 50, 0, 500);
  h.metPhi = new TH1F("h_metPhi", "h_metPhi", 20, 0, 3.14);
  h.numEvents = new TH1F("h_numEvents", "h_numEvents", 1, 0.5, 1.5);

  h.sumw2();
  h.add_histograms_to_output(wk());

  generateSrHistograms();

  return EL::StatusCode::SUCCESS;
}



EL::StatusCode TruthReader :: fileExecute ()
{
  // Here you do everything that needs to be done exactly once for every
  // single file, e.g. collect a list of all lumi-blocks processed
  return EL::StatusCode::SUCCESS;
}



EL::StatusCode TruthReader :: changeInput (bool firstFile)
{
  // Here you do everything you need to do when we change input files,
  // e.g. resetting branch addresses on trees.  If you are using
  // D3PDReader or a similar service this method is not needed.
  return EL::StatusCode::SUCCESS;
}



EL::StatusCode TruthReader :: initialize ()
{
  // Here you do everything that you need to do after the first input
  // file has been connected and before the first event is processed,
  // e.g. create additional histograms based on which variables are
  // available in the input files.  You can also create all of your
  // histograms and trees in here, but be aware that this method
  // doesn't get called if no events are processed.  So any objects
  // you create here won't be available in the output if you have no
  // input events.

  xAOD::TEvent* event = wk()->xaodEvent();

  // as a check, let's see the number of events in our xAOD
  Info("initialize()", "Number of events = %lli", event->getEntries() ); // print long long int

  return EL::StatusCode::SUCCESS;
}

template <class Container>
double sumPt(Container &container)
{
    double totPt = 0.0;
    for(const auto *e : container)
        totPt += (e->pt() * mev2gev);
    return totPt;
}

size_t count_samesign_leptons(const std::vector<xAOD::TruthParticle*> &electrons, const std::vector<xAOD::TruthParticle*> &muons)
{
    size_t number_of_leptons=0;
    std::vector<xAOD::TruthParticle*> leptons;
    leptons.reserve(electrons.size()+muons.size());
    leptons.insert(leptons.end(), electrons.begin(), electrons.end());
    leptons.insert(leptons.end(), muons.begin(), muons.end());
    size_t nplus = 0;
    size_t nminus = 0;
    for(auto l : leptons) {
        if(l->pt()*mev2gev>20.0) {
            if(l->charge()>0) nplus++;
            if(l->charge()<0) nminus++;
        }
    }
    bool samesign = (nplus>1 || nminus>1);
    if(samesign) { // count potential third leptons above 10GeV
        number_of_leptons=2;
        for(auto l : leptons) {
            double pt = l->pt()*mev2gev;
            if(pt<20.0 && pt>10.0) {
                number_of_leptons++;
            }
        }
    }
    return number_of_leptons;
}

EL::StatusCode TruthReader :: execute ()
{
  // Here you do everything that needs to be done on every single
  // events, e.g. read input variables, apply cuts, and fill
  // histograms and trees.  This is where most of your actual analysis
  // code will go.

  xAOD::TEvent* event = wk()->xaodEvent();
  double eventWeight = 1.0;

  //----------------------------
  // Event information
  //---------------------------
  const xAOD::EventInfo* eventInfo = 0;
  EL_RETURN_CHECK("execute",event->retrieve( eventInfo, "EventInfo"));
  // std::cout<<"run "<<eventInfo->runNumber()<<" event "<< eventInfo->eventNumber() << std::endl;
  eventWeight *= eventInfo->mcEventWeight();

  const xAOD::TruthEventContainer* truthEvents = 0;
  EL_RETURN_CHECK("execute()", event->retrieve(truthEvents, "TruthEvents"));
  if(false && truthEvents){
      xAOD::TruthEventContainer::const_iterator te_itr = truthEvents->begin();
      xAOD::TruthEventContainer::const_iterator te_end = truthEvents->end();
      cout<<"TruthEvents : ";
      for(; te_itr!=te_end; ++te_itr) {
          cout<<"TruthEvent::weights["<<(*te_itr)->weights().size()<<"] : ";
          for(auto w : (*te_itr)->weights())
              cout<<" "<<w;
          cout<<endl;
      }
  }
  if(truthEvents and weightIndex >= 0){
      if(truthEvents->size()!=1)
          Error("TruthReader::execute()", XAOD_MESSAGE( "do not know how to process %d 'TruthEvents'"),
                static_cast<int>(truthEvents->size()));
      xAOD::TruthEventContainer::const_iterator tec = truthEvents->begin();
      const vector<float> &weights = (*tec)->weights();
      int weightsSize = static_cast<int>(weights.size());
      if(weightIndex > weightsSize)
          Error("TruthReader::execute()", XAOD_MESSAGE( "invalid weightIndex %d (max %d)"), weightIndex, weightsSize);
      eventWeight = weights[weightIndex];
      const int maxPrintEvents = 10;
      if(verbose && printedEvents<maxPrintEvents) {
          cout<<"eventWeight "<<eventWeight<<endl;
          printedEvents++;
      }
  }

  //----------------------------
  // Jets
  //---------------------------
  const xAOD::JetContainer* jets = 0;
  EL_RETURN_CHECK("execute()",event->retrieve( jets, "AntiKt4TruthJets" ));

  std::vector<xAOD::Jet*> v_jet;

  xAOD::JetContainer::const_iterator jet_itr = jets->begin();
  xAOD::JetContainer::const_iterator jet_end = jets->end();
  for( ; jet_itr != jet_end; ++jet_itr ) {
    if(( (*jet_itr)->pt() * 0.001) < 20 ) continue;

    xAOD::Jet* jet = new xAOD::Jet();
    jet->makePrivateStore( **jet_itr );
    v_jet.push_back(jet);
  }

  //----------------------------
  // Electron
  //---------------------------
  const xAOD::TruthParticleContainer* electrons = 0;
  EL_RETURN_CHECK("execute",event->retrieve( electrons, "TruthElectrons" ));

  std::vector<xAOD::TruthParticle*> v_electron;

  xAOD::TruthParticleContainer::const_iterator electron_itr = electrons->begin();
  xAOD::TruthParticleContainer::const_iterator electron_end = electrons->end();
  for( ; electron_itr != electron_end; ++electron_itr ) {
    if(( (*electron_itr)->pt() * 0.001) < 10 ) continue;
    if( fabs((*electron_itr)->eta()) > 2.47 ) continue;

    xAOD::TruthParticle* electron = new xAOD::TruthParticle();
    electron->makePrivateStore( **electron_itr );
    v_electron.push_back(electron);
  }

  //----------------------------
  // Muons
  //---------------------------
  const xAOD::TruthParticleContainer* muons = 0;
  EL_RETURN_CHECK("execute",event->retrieve( muons, "TruthMuons" ));

  std::vector<xAOD::TruthParticle*> v_muon;

  xAOD::TruthParticleContainer::const_iterator muon_itr = muons->begin();
  xAOD::TruthParticleContainer::const_iterator muon_end = muons->end();
  for( ; muon_itr != muon_end; ++muon_itr ) {
    if(( (*muon_itr)->pt() * 0.001) < 10 ) continue;
    if( fabs((*muon_itr)->eta()) > 2.4 ) continue;

    xAOD::TruthParticle* muon = new xAOD::TruthParticle();
    muon->makePrivateStore( **muon_itr );
    v_muon.push_back(muon);
  }

  //----------------------------
  // MET
  //---------------------------
  const xAOD::MissingETContainer* met = 0;
  EL_RETURN_CHECK("execute()",event->retrieve( met, "MET_Truth" ));

  xAOD::MissingETContainer::const_iterator met_it = met->begin();

  //----------------------------
  // Overlap Removal
  //---------------------------

  // Jet Removal
  for(int i_jet = 0 ; i_jet < (int)v_jet.size() ; i_jet++ ){
    for(int i_el = 0 ; i_el < (int)v_electron.size() ; i_el++ ){
      if( v_jet.at(i_jet)->p4().DeltaR(v_electron.at(i_el)->p4()) < 0.2) { // Remove Jet element and move backward
        v_jet.erase( v_jet.begin()+i_jet);
        i_jet-- ;
        break;
      }
    }
  }

  // Electron Removal
  for(int i_el = 0 ; i_el < (int)v_electron.size() ; i_el++ ){
    for(int i_jet = 0 ; i_jet < (int)v_jet.size() ; i_jet++ ){
      if( v_electron.at(i_el)->p4().DeltaR(v_jet.at(i_jet)->p4()) < 0.4) { // Remove Electron element and move backward
        v_electron.erase( v_electron.begin()+i_el);
        i_el-- ;
        break;
      }
    }
  }

  // Muon Removal
  for(int i_mu = 0 ; i_mu < (int)v_muon.size() ; i_mu++ ){
    for(int i_jet = 0 ; i_jet < (int)v_jet.size() ; i_jet++ ){
      if( v_muon.at(i_mu)->p4().DeltaR(v_jet.at(i_jet)->p4()) < 0.4) { // Remove Muon element and move backward
        v_muon.erase( v_muon.begin()+i_mu);
        i_mu-- ;
        break;
      }
    }
  }

  // Leptons Removal
  for(int i_el = 0 ; i_el < (int)v_electron.size() ; i_el++ ){
    for(int i_mu = 0 ; i_mu < (int)v_muon.size() ; i_mu++ ){
      if( v_muon.at(i_mu)->p4().DeltaR(v_electron.at(i_el)->p4()) < 0.1) { // Remove electron element and move backward
	v_electron.erase( v_electron.begin()+i_el);
        i_el--;
	break;
      }
    }
  }
  std::vector<xAOD::Jet*> v_bjet;
  for(const auto jet : v_jet) {
      if(abs( jet->auxdata<int>("PartonTruthLabelID") ) == 5)
          v_bjet.push_back(jet);
  }

  double etmiss = (*met_it)->met() * mev2gev;
  double etmissPhi = (*met_it)->phi();
  double meff = etmiss + sumPt(v_jet) + sumPt(v_electron) + sumPt(v_muon);
  size_t num_ss_leptons = count_samesign_leptons(v_electron, v_muon);
  size_t num_jet20_b = std::count_if(v_bjet.begin(), v_bjet.end(),
                                     [](const xAOD::Jet* j) {return j->pt()*mev2gev >20.0;});
  size_t num_jet50 = std::count_if(v_jet.begin(), v_jet.end(),
                                   [](const xAOD::Jet* j) {return j->pt()*mev2gev >50.0;});

  //----------------------------
  // Fill Histograms
  //---------------------------

  struct FillJetHistos {
      void operator()(const std::vector<xAOD::Jet*> &jets, TH1 *n, TH1 *pt, TH1 *e, TH1 *eta, TH1 *phi, double weight) {
          n->Fill(jets.size(), weight);
          for(const auto jet : jets) {
              pt->Fill( ( jet->pt()) * mev2gev, weight);
              e->Fill( ( jet->e()) * mev2gev, weight);
              eta->Fill( jet->eta() , weight);
              phi->Fill( jet->phi() , weight);
          }
      }
  };

  struct FillLeptonHistos {
      void operator()(const std::vector<xAOD::TruthParticle*> &leptons,
                      TH1 *n, TH1 *pt, TH1 *e, TH1 *eta, TH1 *phi, TH1* q,
                      double weight) {
          n->Fill( leptons.size() , weight);
          for(const auto lep : leptons) {
              pt->Fill( ( lep->pt()) * mev2gev, weight);
              e->Fill( ( lep->e()) * mev2gev, weight);
              eta->Fill( lep->eta() , weight);
              phi->Fill( lep->phi() , weight);
              q->Fill( lep->charge()/2 , weight);
          }
      }
  };

  bool pass_sr3b   = (num_ss_leptons>=2 && num_jet20_b >=3                 && etmiss>100.0 && meff>600.0);
  bool pass_sr1b   = (num_ss_leptons>=2 && num_jet20_b >=1 && num_jet50>=4 && etmiss>100.0 && meff>600.0);
  bool pass_sr0b5j = (num_ss_leptons>=2 && num_jet20_b ==0 && num_jet50>=5 && etmiss>100.0 && meff>600.0);
  bool pass_sr0b3j = (num_ss_leptons>=3 && num_jet20_b ==0 && num_jet50>=3 && etmiss>100.0 && meff>600.0);

  struct FillHistos {
      void operator()(SelectionHistograms &h,
                      const std::vector<xAOD::Jet*> &jets,
                      const std::vector<xAOD::Jet*> &bjets,
                      const std::vector<xAOD::TruthParticle*> &electrons,
                      const std::vector<xAOD::TruthParticle*> &muons,
                      double &etmiss,
                      double &etmissPhi,
                      double &meff,
                      double &weight) {

      h.numEvents->Fill(weight);
      FillJetHistos()(jets, h.jetN, h.jetPt, h.jetE, h.jetEta, h.jetPhi, weight);
      FillJetHistos()(bjets, h.bjetN, h.bjetPt, h.bjetE, h.bjetEta, h.bjetPhi, weight);
      FillLeptonHistos()(electrons, h.electronN, h.electronPt, h.electronE, h.electronEta, h.electronPhi, h.electronQ, weight);
      FillLeptonHistos()(muons, h.muonN, h.muonPt, h.muonE, h.muonEta, h.muonPhi, h.muonQ, weight);
      h.met->Fill(etmiss, weight );
      h.metPhi->Fill(etmissPhi, weight );
      h.meff->Fill(meff , weight);
      }
  } fillHistos;

  if(true){
      fillHistos(m_inclusive_histos, v_jet, v_bjet, v_electron, v_muon, etmiss, etmissPhi, meff, eventWeight);
  }
  if(pass_sr3b){
      fillHistos(m_sr3b_histos, v_jet, v_bjet, v_electron, v_muon, etmiss, etmissPhi, meff, eventWeight);
  }
  if(pass_sr1b){
      fillHistos(m_sr1b_histos, v_jet, v_bjet, v_electron, v_muon, etmiss, etmissPhi, meff, eventWeight);
  }
  if(pass_sr0b5j){
      fillHistos(m_sr0b5j_histos, v_jet, v_bjet, v_electron, v_muon, etmiss, etmissPhi, meff, eventWeight);
  }
  if(pass_sr0b3j){
      fillHistos(m_sr0b3j_histos, v_jet, v_bjet, v_electron, v_muon, etmiss, etmissPhi, meff, eventWeight);
  }


  return EL::StatusCode::SUCCESS;
}



EL::StatusCode TruthReader :: postExecute ()
{
  // Here you do everything that needs to be done after the main event
  // processing.  This is typically very rare, particularly in user
  // code.  It is mainly used in implementing the NTupleSvc.
  return EL::StatusCode::SUCCESS;
}



EL::StatusCode TruthReader :: finalize ()
{
  // This method is the mirror image of initialize(), meaning it gets
  // called after the last event has been processed on the worker node
  // and allows you to finish up any objects you created in
  // initialize() before they are written to disk.  This is actually
  // fairly rare, since this happens separately for each worker node.
  // Most of the time you want to do your post-processing on the
  // submission node after all your histogram outputs have been
  // merged.  This is different from histFinalize() in that it only
  // gets called on worker nodes that processed input events.

  return EL::StatusCode::SUCCESS;
}



EL::StatusCode TruthReader :: histFinalize ()
{
  // This method is the mirror image of histInitialize(), meaning it
  // gets called after the last event has been processed on the worker
  // node and allows you to finish up any objects you created in
  // histInitialize() before they are written to disk.  This is
  // actually fairly rare, since this happens separately for each
  // worker node.  Most of the time you want to do your
  // post-processing on the submission node after all your histogram
  // outputs have been merged.  This is different from finalize() in
  // that it gets called on all worker nodes regardless of whether
  // they processed input events.

    SelectionHistograms &h = m_inclusive_histos;
  // Jet
  h.jetN->GetYaxis()->SetTitle(" # of events ");
  h.jetN->GetXaxis()->SetTitle(" Number of Jets ");
  h.jetN->SetLineColor( kBlue + 2);

  h.jetPt->GetYaxis()->SetTitle(" # of events ");
  h.jetPt->GetXaxis()->SetTitle(" Pt_{jet} [GeV] ");
  h.jetPt->SetLineColor( kBlue + 2);

  h.jetE->GetYaxis()->SetTitle(" # of events ");
  h.jetE->GetXaxis()->SetTitle(" E_{jet} [GeV] ");
  h.jetE->SetLineColor( kBlue + 2);

  h.jetEta->GetYaxis()->SetTitle(" # of events ");
  h.jetEta->GetXaxis()->SetTitle(" #eta_{jet} ");
  h.jetEta->SetLineColor( kBlue + 2);

  h.jetPhi->GetYaxis()->SetTitle(" # of events ");
  h.jetPhi->GetXaxis()->SetTitle(" #phi_{jet} ");
  h.jetPhi->SetMinimum(0.1);
  h.jetPhi->SetLineColor( kBlue + 2);

  // BJet
  h.bjetN->GetYaxis()->SetTitle(" # of events ");
  h.bjetN->GetXaxis()->SetTitle(" Number of b-jets");
  h.bjetN->SetLineColor( kBlue + 2);

  h.bjetPt->GetYaxis()->SetTitle(" # of events ");
  h.bjetPt->GetXaxis()->SetTitle(" Pt_{b-jet} [GeV] ");
  h.bjetPt->SetLineColor( kBlue + 2);

  h.bjetE->GetYaxis()->SetTitle(" # of events ");
  h.bjetE->GetXaxis()->SetTitle(" E_{b-jet} [GeV] ");
  h.bjetE->SetLineColor( kBlue + 2);

  h.bjetEta->GetYaxis()->SetTitle(" # of events ");
  h.bjetEta->GetXaxis()->SetTitle(" #eta_{b-jet} ");
  h.bjetEta->SetLineColor( kBlue + 2);

  h.bjetPhi->GetYaxis()->SetTitle(" # of events ");
  h.bjetPhi->GetXaxis()->SetTitle(" #phi_{b-jet} ");
  h.bjetPhi->SetMinimum(0.1);
  h.bjetPhi->SetLineColor( kBlue + 2);

  // Electron
  h.electronN->GetYaxis()->SetTitle(" # of events ");
  h.electronN->GetXaxis()->SetTitle(" Number of Electrons");
  h.electronN->SetLineColor( kBlue + 2);

  h.electronPt->GetYaxis()->SetTitle(" # of events ");
  h.electronPt->GetXaxis()->SetTitle(" Pt_{electron} [GeV] ");
  h.electronPt->SetLineColor( kBlue + 2);

  h.electronE->GetYaxis()->SetTitle(" # of events ");
  h.electronE->GetXaxis()->SetTitle(" E_{electron} [GeV] ");
  h.electronE->SetLineColor( kBlue + 2);

  h.electronEta->GetYaxis()->SetTitle(" # of events ");
  h.electronEta->GetXaxis()->SetTitle(" #eta_{electron} ");
  h.electronEta->SetLineColor( kBlue + 2);

  h.electronPhi->GetYaxis()->SetTitle(" # of events ");
  h.electronPhi->GetXaxis()->SetTitle(" #phi_{electron} ");
  h.electronPhi->SetMinimum(0.1);
  h.electronPhi->SetLineColor( kBlue + 2);

  h.electronQ->GetYaxis()->SetTitle(" # of events ");
  h.electronQ->GetXaxis()->SetTitle(" Charge_{electron} ");
  h.electronQ->SetMinimum(0.1);
  h.electronQ->SetLineColor( kBlue + 2);

  // Muon
  h.muonN->GetYaxis()->SetTitle(" # of events ");
  h.muonN->GetXaxis()->SetTitle(" Number of Muons");
  h.muonN->SetLineColor( kBlue + 2);

  h.muonPt->GetYaxis()->SetTitle(" # of events ");
  h.muonPt->GetXaxis()->SetTitle(" Pt_{muon} [GeV] ");
  h.muonPt->SetLineColor( kBlue + 2);

  h.muonE->GetYaxis()->SetTitle(" # of events ");
  h.muonE->GetXaxis()->SetTitle(" E_{muon} [GeV] ");
  h.muonE->SetLineColor( kBlue + 2);

  h.muonEta->GetYaxis()->SetTitle(" # of events ");
  h.muonEta->GetXaxis()->SetTitle(" #eta_{muon} ");
  h.muonEta->SetLineColor( kBlue + 2);

  h.muonPhi->GetYaxis()->SetTitle(" # of events ");
  h.muonPhi->GetXaxis()->SetTitle(" #phi_{muon} ");
  h.muonPhi->SetMinimum(0.1);
  h.muonPhi->SetLineColor( kBlue + 2);

  h.muonQ->GetYaxis()->SetTitle(" # of events ");
  h.muonQ->GetXaxis()->SetTitle(" Charge_{muon} ");
  h.muonQ->SetMinimum(0.1);
  h.muonQ->SetLineColor( kBlue + 2);

  //Global Variable
  h.met->GetYaxis()->SetTitle(" # of events ");
  h.met->GetXaxis()->SetTitle(" MET [GeV] ");
  h.met->SetLineColor( kBlue + 2);

  h.metPhi->GetYaxis()->SetTitle(" # of events ");
  h.metPhi->GetXaxis()->SetTitle(" PHI_{MET} ");
  h.metPhi->SetMinimum(0.1);
  h.metPhi->SetLineColor( kBlue + 2);

  h.meff->GetYaxis()->SetTitle(" # of events ");
  h.meff->GetXaxis()->SetTitle(" M_{eff} [GeV] ");
  h.meff->SetLineColor( kBlue + 2);

  h.numEvents->GetYaxis()->SetTitle(" # of events ");
  h.numEvents->GetXaxis()->SetTitle(" weight==1 ");
  h.numEvents->SetLineColor( kBlue + 2);

  return EL::StatusCode::SUCCESS;
}

void TruthReader::SelectionHistograms::clone_with_suffix(TruthReader::SelectionHistograms &input,
                                                         EL::Worker *worker,
                                                         TString name_suffix, TString title_suffix)
{
    struct Clone_histogram_with_suffix {
        TString ns, ts;
        Clone_histogram_with_suffix(TString name_suffix, TString title_suffix):
            ns(name_suffix),
            ts(title_suffix) {}
        TH1* operator()(const TH1* h_in) {
            TString h_name = h_in->GetName();
            TH1* h_out = static_cast<TH1*>(h_in->Clone(h_name+ns));
            h_out->SetTitle(h_in->GetTitle()+ts);
            return h_out;
            }
    } with_suffix(name_suffix, title_suffix);
    jetN           = with_suffix(input.jetN       );
    jetPt          = with_suffix(input.jetPt      );
    jetE           = with_suffix(input.jetE       );
    jetEta         = with_suffix(input.jetEta     );
    jetPhi         = with_suffix(input.jetPhi     );
    bjetN          = with_suffix(input.bjetN      );
    bjetPt         = with_suffix(input.bjetPt     );
    bjetE          = with_suffix(input.bjetE      );
    bjetEta        = with_suffix(input.bjetEta    );
    bjetPhi        = with_suffix(input.bjetPhi    );
    electronN      = with_suffix(input.electronN  );
    electronPt     = with_suffix(input.electronPt );
    electronE      = with_suffix(input.electronE  );
    electronEta    = with_suffix(input.electronEta);
    electronPhi    = with_suffix(input.electronPhi);
    electronQ      = with_suffix(input.electronQ  );
    muonN          = with_suffix(input.muonN      );
    muonPt         = with_suffix(input.muonPt     );
    muonE          = with_suffix(input.muonE      );
    muonEta        = with_suffix(input.muonEta    );
    muonPhi        = with_suffix(input.muonPhi    );
    muonQ          = with_suffix(input.muonQ      );
    meff           = with_suffix(input.meff       );
    met            = with_suffix(input.met        );
    metPhi         = with_suffix(input.metPhi     );
    numEvents      = with_suffix(input.numEvents  );

    add_histograms_to_output(worker);
}


void TruthReader::generateSrHistograms()
{

    m_sr3b_histos.clone_with_suffix  (m_inclusive_histos, wk(), "_sr3b",   " (sr3b)");
    m_sr1b_histos.clone_with_suffix  (m_inclusive_histos, wk(), "_sr1b",   " (sr1b)");
    m_sr0b5j_histos.clone_with_suffix(m_inclusive_histos, wk(), "_sr0b5j", " (sr0b5j)");
    m_sr0b3j_histos.clone_with_suffix(m_inclusive_histos, wk(), "_sr0b3j", " (sr0b3j)");
}
void TruthReader::SelectionHistograms::add_histograms_to_output(EL::Worker *worker)
{
    for(auto h : histograms())
        worker->addOutput(h);
}

