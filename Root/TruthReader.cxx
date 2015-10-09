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


TruthReader :: TruthReader ()
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

  // Jet
  h_jetN   = new TH1F("h_jetN", "h_jetN", 25, 0, 25);
  h_jetPt  = new TH1F("h_jetPt", "h_jetPt", 50, 0, 1000);
  h_jetE   = new TH1F("h_jetE", "h_jetE", 50, 0, 1200);
  h_jetEta = new TH1F("h_jetEta", "h_jetEta", 50, -5, 5);
  h_jetPhi = new TH1F("h_jetPhi", "h_jetPhi", 20, 0, 3.14);
  wk()->addOutput (h_jetN);
  wk()->addOutput (h_jetPt);
  wk()->addOutput (h_jetE);
  wk()->addOutput (h_jetEta);
  wk()->addOutput (h_jetPhi);

  // BJet
  h_bjetN   = new TH1F("h_bjetN", "h_bjetN", 8, 0, 8);
  h_bjetPt  = new TH1F("h_bjetPt", "h_bjetPt", 50, 0, 800);
  h_bjetE   = new TH1F("h_bjetE", "h_bjetE", 50, 0, 1000);
  h_bjetEta = new TH1F("h_bjetEta", "h_bjetEta", 50, -5, 5);
  h_bjetPhi = new TH1F("h_bjetPhi", "h_bjetPhi", 20, 0, 3.14);
  wk()->addOutput (h_bjetN);
  wk()->addOutput (h_bjetPt);
  wk()->addOutput (h_bjetE);
  wk()->addOutput (h_bjetEta);
  wk()->addOutput (h_bjetPhi);

  // Electron
  h_electronN   = new TH1F("h_electronN", "h_electronN", 7, 0, 7);
  h_electronPt  = new TH1F("h_electronPt", "h_electronPt", 50, 0, 300);
  h_electronE   = new TH1F("h_electronE", "h_electronE", 50, 0, 300);
  h_electronEta = new TH1F("h_electronEta", "h_electronEta", 50, -3, 3);
  h_electronPhi = new TH1F("h_electronPhi", "h_electronPhi", 20, 0, 3.14);
  h_electronQ   = new TH1F("h_electronQ", "h_electronQ", 2, -1, 1);
  wk()->addOutput (h_electronN);
  wk()->addOutput (h_electronPt);
  wk()->addOutput (h_electronE);
  wk()->addOutput (h_electronEta);
  wk()->addOutput (h_electronPhi);
  wk()->addOutput (h_electronQ);

  // Muon
  h_muonN   = new TH1F("h_muonN", "h_muonN", 7, 0, 7);
  h_muonPt  = new TH1F("h_muonPt", "h_muonPt", 50, 0, 300);
  h_muonE   = new TH1F("h_muonE", "h_muonE", 50, 0, 300);
  h_muonEta = new TH1F("h_muonEta", "h_muonEta", 50, -3, 3);
  h_muonPhi = new TH1F("h_muonPhi", "h_muonPhi", 20, 0, 3.14);
  h_muonQ   = new TH1F("h_muonQ", "h_muonQ", 2, -1, 1);
  wk()->addOutput (h_muonN);
  wk()->addOutput (h_muonPt);
  wk()->addOutput (h_muonE);
  wk()->addOutput (h_muonEta);
  wk()->addOutput (h_muonPhi);
  wk()->addOutput (h_muonQ);

  // Global Variable
  h_meff   = new TH1F("h_meff", "h_meff", 50, 0, 3000);
  h_met    = new TH1F("h_met", "h_met", 50, 0, 500);
  h_metPhi = new TH1F("h_metPhi", "h_metPhi", 20, 0, 3.14);
  wk()->addOutput (h_meff);
  wk()->addOutput (h_met);
  wk()->addOutput (h_metPhi);

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



EL::StatusCode TruthReader :: execute ()
{
  // Here you do everything that needs to be done on every single
  // events, e.g. read input variables, apply cuts, and fill
  // histograms and trees.  This is where most of your actual analysis
  // code will go.

  xAOD::TEvent* event = wk()->xaodEvent();

  //----------------------------
  // Event information
  //---------------------------
  const xAOD::EventInfo* eventInfo = 0;
  EL_RETURN_CHECK("execute",event->retrieve( eventInfo, "EventInfo"));
  //  std::cout << eventInfo->eventNumber() << std::endl;

  const xAOD::TruthEventContainer* truthEvents = 0;
  EL_RETURN_CHECK("execute()", event->retrieve(truthEvents, "TruthEvents"));
  if(truthEvents){
      xAOD::TruthEventContainer::const_iterator te_itr = truthEvents->begin();
      xAOD::TruthEventContainer::const_iterator te_end = truthEvents->end();
      cout<<"TruthEvents : ";
      for(; te_itr!=te_end; ++te_itr) {
          cout<<"TruthEvent::weights() : ";
          for(auto w : (*te_itr)->weights())
              cout<<" "<<w;
          cout<<endl;
      }
      cout<<endl;
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

  h_met->Fill( (*met_it)->met() * 0.001 );
  h_metPhi->Fill( (*met_it)->phi() );

  double meff = (*met_it)->met() * 0.001 ;

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

  //----------------------------
  // Fill Histograms
  //---------------------------

  h_jetN->Fill( v_jet.size() );
  const double mev2gev = 1.0e-3;
  int N_bjet =0;
  for( int i_jet = 0 ; i_jet < (int)v_jet.size() ; i_jet++ ) {

    h_jetPt->Fill( ( v_jet.at(i_jet)->pt()) * mev2gev);
    h_jetE->Fill( ( v_jet.at(i_jet)->e()) * mev2gev);
    h_jetEta->Fill( v_jet.at(i_jet)->eta() );
    h_jetPhi->Fill( v_jet.at(i_jet)->phi() );

    meff += ( v_jet.at(i_jet)->pt() ) * mev2gev ;

    if( abs( v_jet.at(i_jet)->auxdata<int>("PartonTruthLabelID") ) != 5 ) continue;

    h_bjetPt->Fill( ( v_jet.at(i_jet)->pt()) * mev2gev);
    h_bjetE->Fill( ( v_jet.at(i_jet)->e()) * mev2gev);
    h_bjetEta->Fill( v_jet.at(i_jet)->eta() );
    h_bjetPhi->Fill( v_jet.at(i_jet)->phi() );

    N_bjet++;
  }

  h_bjetN->Fill( N_bjet );
  h_electronN->Fill( v_electron.size() );

  for( int i_electron = 0 ; i_electron < (int)v_electron.size() ; i_electron++ ) {

    h_electronPt->Fill( ( v_electron.at(i_electron)->pt()) * mev2gev);
    h_electronE->Fill( ( v_electron.at(i_electron)->e()) * mev2gev);
    h_electronEta->Fill( v_electron.at(i_electron)->eta() );
    h_electronPhi->Fill( v_electron.at(i_electron)->phi() );
    h_electronQ->Fill( v_electron.at(i_electron)->charge()/2 );

    meff += ( v_electron.at(i_electron)->pt() ) * mev2gev ;
  }

  h_muonN->Fill( v_muon.size() );

  for( int i_muon = 0 ; i_muon < (int)v_muon.size() ; i_muon++ ) {

    h_muonPt->Fill( ( v_muon.at(i_muon)->pt()) * mev2gev);
    h_muonE->Fill( ( v_muon.at(i_muon)->e()) * mev2gev);
    h_muonEta->Fill( v_muon.at(i_muon)->eta() );
    h_muonPhi->Fill( v_muon.at(i_muon)->phi() );
    h_muonQ->Fill( v_muon.at(i_muon)->charge()/2 );

    meff += ( v_muon.at(i_muon)->pt() ) * mev2gev ;
  }

  h_meff->Fill( meff );

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

  // Jet
  h_jetN->GetYaxis()->SetTitle(" # of events ");
  h_jetN->GetXaxis()->SetTitle(" Number of Jets ");
  h_jetN->SetLineColor( kBlue + 2);

  h_jetPt->GetYaxis()->SetTitle(" # of events ");
  h_jetPt->GetXaxis()->SetTitle(" Pt_{jet} [GeV] ");
  h_jetPt->SetLineColor( kBlue + 2);

  h_jetE->GetYaxis()->SetTitle(" # of events ");
  h_jetE->GetXaxis()->SetTitle(" E_{jet} [GeV] ");
  h_jetE->SetLineColor( kBlue + 2);

  h_jetEta->GetYaxis()->SetTitle(" # of events ");
  h_jetEta->GetXaxis()->SetTitle(" #eta_{jet} ");
  h_jetEta->SetLineColor( kBlue + 2);

  h_jetPhi->GetYaxis()->SetTitle(" # of events ");
  h_jetPhi->GetXaxis()->SetTitle(" #phi_{jet} ");
  h_jetPhi->SetMinimum(0.1);
  h_jetPhi->SetLineColor( kBlue + 2);

  // BJet
  h_bjetN->GetYaxis()->SetTitle(" # of events ");
  h_bjetN->GetXaxis()->SetTitle(" Number of b-jets");
  h_bjetN->SetLineColor( kBlue + 2);

  h_bjetPt->GetYaxis()->SetTitle(" # of events ");
  h_bjetPt->GetXaxis()->SetTitle(" Pt_{b-jet} [GeV] ");
  h_bjetPt->SetLineColor( kBlue + 2);

  h_bjetE->GetYaxis()->SetTitle(" # of events ");
  h_bjetE->GetXaxis()->SetTitle(" E_{b-jet} [GeV] ");
  h_bjetE->SetLineColor( kBlue + 2);

  h_bjetEta->GetYaxis()->SetTitle(" # of events ");
  h_bjetEta->GetXaxis()->SetTitle(" #eta_{b-jet} ");
  h_bjetEta->SetLineColor( kBlue + 2);

  h_bjetPhi->GetYaxis()->SetTitle(" # of events ");
  h_bjetPhi->GetXaxis()->SetTitle(" #phi_{b-jet} ");
  h_bjetPhi->SetMinimum(0.1);
  h_bjetPhi->SetLineColor( kBlue + 2);

  // Electron
  h_electronN->GetYaxis()->SetTitle(" # of events ");
  h_electronN->GetXaxis()->SetTitle(" Number of Electrons");
  h_electronN->SetLineColor( kBlue + 2);

  h_electronPt->GetYaxis()->SetTitle(" # of events ");
  h_electronPt->GetXaxis()->SetTitle(" Pt_{electron} [GeV] ");
  h_electronPt->SetLineColor( kBlue + 2);

  h_electronE->GetYaxis()->SetTitle(" # of events ");
  h_electronE->GetXaxis()->SetTitle(" E_{electron} [GeV] ");
  h_electronE->SetLineColor( kBlue + 2);

  h_electronEta->GetYaxis()->SetTitle(" # of events ");
  h_electronEta->GetXaxis()->SetTitle(" #eta_{electron} ");
  h_electronEta->SetLineColor( kBlue + 2);

  h_electronPhi->GetYaxis()->SetTitle(" # of events ");
  h_electronPhi->GetXaxis()->SetTitle(" #phi_{electron} ");
  h_electronPhi->SetMinimum(0.1);
  h_electronPhi->SetLineColor( kBlue + 2);

  h_electronQ->GetYaxis()->SetTitle(" # of events ");
  h_electronQ->GetXaxis()->SetTitle(" Charge_{electron} ");
  h_electronQ->SetMinimum(0.1);
  h_electronQ->SetLineColor( kBlue + 2);

  // Muon
  h_muonN->GetYaxis()->SetTitle(" # of events ");
  h_muonN->GetXaxis()->SetTitle(" Number of Muons");
  h_muonN->SetLineColor( kBlue + 2);

  h_muonPt->GetYaxis()->SetTitle(" # of events ");
  h_muonPt->GetXaxis()->SetTitle(" Pt_{muon} [GeV] ");
  h_muonPt->SetLineColor( kBlue + 2);

  h_muonE->GetYaxis()->SetTitle(" # of events ");
  h_muonE->GetXaxis()->SetTitle(" E_{muon} [GeV] ");
  h_muonE->SetLineColor( kBlue + 2);

  h_muonEta->GetYaxis()->SetTitle(" # of events ");
  h_muonEta->GetXaxis()->SetTitle(" #eta_{muon} ");
  h_muonEta->SetLineColor( kBlue + 2);

  h_muonPhi->GetYaxis()->SetTitle(" # of events ");
  h_muonPhi->GetXaxis()->SetTitle(" #phi_{muon} ");
  h_muonPhi->SetMinimum(0.1);
  h_muonPhi->SetLineColor( kBlue + 2);

  h_muonQ->GetYaxis()->SetTitle(" # of events ");
  h_muonQ->GetXaxis()->SetTitle(" Charge_{muon} ");
  h_muonQ->SetMinimum(0.1);
  h_muonQ->SetLineColor( kBlue + 2);

  //Global Variable
  h_met->GetYaxis()->SetTitle(" # of events ");
  h_met->GetXaxis()->SetTitle(" MET [GeV] ");
  h_met->SetLineColor( kBlue + 2);

  h_metPhi->GetYaxis()->SetTitle(" # of events ");
  h_metPhi->GetXaxis()->SetTitle(" PHI_{MET} ");
  h_metPhi->SetMinimum(0.1);
  h_metPhi->SetLineColor( kBlue + 2);

  h_meff->GetYaxis()->SetTitle(" # of events ");
  h_meff->GetXaxis()->SetTitle(" M_{eff} [GeV] ");
  h_meff->SetLineColor( kBlue + 2);

  return EL::StatusCode::SUCCESS;
}
