#include "PMGValidation/TruthReader.h"

#include "xAODRootAccess/Init.h"
#include "SampleHandler/SampleHandler.h"
#include "SampleHandler/ToolsDiscovery.h"
#include "SampleHandler/ScanDir.h"
#include "EventLoop/Job.h"
#include "EventLoop/DirectDriver.h"
#include "SampleHandler/DiskListLocal.h"

#include <TSystem.h>

#include <string>
using namespace std;

int main( int argc, char* argv[] ) {

  // Take the submit directory from the input if provided:
  string submitDir = "submitDir";
  string inputFilePath = gSystem->ExpandPathName ("/data1/atlas/berlendis/Data/4top/");
  string filename = "DAOD_TRUTH1.mc15_4top.pool.root";

  if( argc > 1 ) inputFilePath = argv[ 1 ];
  if( argc > 2 ) filename = argv[ 2 ];
  if( argc > 3 ) submitDir = argv[ 3 ];

  // Set up the job for xAOD access:
  xAOD::Init().ignore();

  // Construct the samples to run on:
  SH::SampleHandler sh;

  // use SampleHandler to scan all of the subdirectories of a directory for particular MC single file:
  SH::ScanDir().sampleDepth(0).samplePattern( filename ).scan(sh, inputFilePath);

  // Set the name of the input TTree. It's always "CollectionTree"
  // for xAOD files.
  sh.setMetaString( "nc_tree", "CollectionTree" );

  // Print what we found:
  sh.print();

  // Create an EventLoop job:
  EL::Job job;
  job.sampleHandler( sh );
  job.options()->setDouble (EL::Job::optMaxEvents, 5000);

  // Add our analysis to the job:
  TruthReader* aTruth = new TruthReader();
  job.algsAdd( aTruth );

  // Run the job using the local/direct driver:
  EL::DirectDriver driver;
  driver.submit( job, submitDir );

  return 0;
}
