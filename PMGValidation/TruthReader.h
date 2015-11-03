#ifndef PMGValidation_TruthReader_H
#define PMGValidation_TruthReader_H

#include <map>
#include <string>
#include <stdlib.h>

#include <TH1.h>

#include <EventLoop/Algorithm.h>

#include "PMGValidation/ProgressPrinter.h"

class TruthReader : public EL::Algorithm
{
  // put your configuration variables here as public variables.
  // that way they can be set directly from CINT and python.

private:
  struct SelectionHistograms {
    TH1 *jetN; // Jet
    TH1 *jetPt;
    TH1 *jetE;
    TH1 *jetEta;
    TH1 *jetPhi;
    TH1 *bjetN; // BJet
    TH1 *bjetPt;
    TH1 *bjetE;
    TH1 *bjetEta;
    TH1 *bjetPhi;
    TH1 *electronN; // Electron
    TH1 *electronPt;
    TH1 *electronE;
    TH1 *electronEta;
    TH1 *electronPhi;
    TH1 *electronQ;
    TH1 *muonN; // Muon
    TH1 *muonPt;
    TH1 *muonE;
    TH1 *muonEta;
    TH1 *muonPhi;
    TH1 *muonQ;
    TH1 *meff; // Global Variable
    TH1 *met;
    TH1 *metPhi;
    TH1 *numEvents;
    std::vector<TH1*> histograms() {
      return {
        jetN, jetPt, jetE, jetEta, jetPhi,
          bjetN, bjetPt, bjetE, bjetEta, bjetPhi,
          electronN, electronPt, electronE, electronEta, electronPhi, electronQ,
          muonN, muonPt, muonE, muonEta, muonPhi, muonQ,
          meff, met, metPhi, numEvents
          };
    }
    void set_to_nullptr() {
      for(auto &h : histograms())
        h = nullptr;
    }
    void sumw2() {
      for(auto &h : histograms())
        h->Sumw2();
    }
    SelectionHistograms() { set_to_nullptr(); }
    void clone_with_suffix(SelectionHistograms &input, EL::Worker *worker, TString name_suffix, TString title_suffix);
    void add_histograms_to_output(EL::Worker *worker);
  };
  /// for each SR, clone the histograms above and store them in the maps below
  void generateSrHistograms();
  SelectionHistograms m_inclusive_histos; //!
  SelectionHistograms m_sr3b_histos; //!
  SelectionHistograms m_sr1b_histos; //!
  SelectionHistograms m_sr0b5j_histos; //!
  SelectionHistograms m_sr0b3j_histos; //!
  SelectionHistograms m_cr2bttV_histos; //!
  ProgressPrinter m_printer; //!

public:
  bool verbose;
  int weightIndex;
  size_t printedEvents;
  // float cutValue;


  // variables that don't get filled at submission time should be
  // protected from being send from the submission node to the worker
  // node (done by the //!)
public:

  // this is a standard constructor
  TruthReader ();

  // these are the functions inherited from Algorithm
  virtual EL::StatusCode setupJob (EL::Job& job);
  virtual EL::StatusCode fileExecute ();
  virtual EL::StatusCode histInitialize ();
  virtual EL::StatusCode changeInput (bool firstFile);
  virtual EL::StatusCode initialize ();
  virtual EL::StatusCode execute ();
  virtual EL::StatusCode postExecute ();
  virtual EL::StatusCode finalize ();
  virtual EL::StatusCode histFinalize ();

  // this is needed to distribute the algorithm to the workers
  ClassDef(TruthReader, 1);
};

#endif
