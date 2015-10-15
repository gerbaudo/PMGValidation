#include "PMGValidation/TruthReader.h"
#include "PMGValidation/utils.h"

#include "xAODRootAccess/Init.h"
#include "SampleHandler/SampleHandler.h"
#include "SampleHandler/ToolsDiscovery.h"
#include "SampleHandler/ScanDir.h"
#include "EventLoop/Job.h"
#include "EventLoop/DirectDriver.h"
#include "EventLoop/LSFDriver.h"
#include "SampleHandler/DiskListLocal.h"

#include <TSystem.h>

#include <iostream>
#include <string>

using namespace std;

void help() {
    cout<<"Usage:"
        <<"TruthPlot [options]"<<endl
        <<"-o --output"      <<"\t"<<" output directory"<<endl
        <<"-f --filelist"    <<"\t"<<" input filelist"<<endl
        <<"-i --input-dir"   <<"\t"<<" input directory"<<endl
        <<"  to be scanned if you do not provide a filelist"<<endl
        <<"-p --file-pattern"<<"\t"<<" pattern used to scan directory"<<endl
        <<"-s --sample-name" <<"\t"<<" sample name (used for output)"<<endl
        <<"-n --num-events"  <<"\t"<<" number of events to process"<<endl
        <<"-v --verbose"     <<"\t"<<" print more"<<endl
        <<"-w --weight-index"<<"\t"<<" weight index from 'TruthEvents'"<<endl
        <<"  default =-1, i.e. no event weight"<<endl
        <<"--lxbatch"        <<"\t"<<" submit job to lxbatch (currently broken)"<<endl
        <<endl;
}

int main( int argc, char* argv[] ) {

    string sampleName;
    string outputDir;
    string inputFilelist;
    string inputDirectory;
    string inputFilePattern; // used when scanning input directory
    int numEvents=-1;
    bool verbose = false;
    int weightIndex=-1;
    bool lxbatch = false;

    for(int i = 1; i < argc; i++) {
        string opt = argv[i];
        if     (opt=="-s"||opt=="--sample-name") sampleName = argv[++i];
        else if(opt=="-o"||opt=="--output") outputDir = argv[++i];
        else if(opt=="-f"||opt=="--filelist") inputFilelist = argv[++i];
        else if(opt=="-i"||opt=="--input-dir") inputDirectory = argv[++i];
        else if(opt=="-p"||opt=="--file-pattern") inputFilePattern = argv[++i];
        else if(opt=="-n"||opt=="--num-events") numEvents = atoi(argv[++i]);
        else if(opt=="-v"||opt=="--verbose") verbose=true;
        else if(opt=="-w"||opt=="--weight-index") weightIndex = atoi(argv[++i]);
        else if(opt=="--lxbatch") lxbatch=true;
        else {
            cout<<"unknwown option '"<<opt<<"'"<<endl;
            help();
            return 1;
        }
    }

    if(verbose) {
        cout<<"being called as "<<commandLineArguments(argc, argv)<<endl;
        cout<<"Options:"<<endl
            <<" sample-name '"<<sampleName<<"'"<<endl
            <<" output '"<<outputDir<<"'"<<endl
            <<" filelist '"<<inputFilelist<<"'"<<endl
            <<" input-dir '"<<inputDirectory<<"'"<<endl
            <<" file-pattern '"<<inputFilePattern<<"'"<<endl
            <<" num-events '"<<numEvents<<"'"<<endl
            <<" verbose '"<<verbose<<"'"<<endl
            <<" weightIndex '"<<weightIndex<<"'"<<endl
            <<" lxbatch '"<<lxbatch<<"'"<<endl;
    }
    xAOD::Init().ignore(); // Set up the job for xAOD access:

    SH::SampleHandler sh;

    if(not sampleName.size()) {
        cout<<"required sample name"<<endl;
        return 1;
    }

    if(not outputDir.size()) {
        cout<<"required output directory"<<endl;
        return 1;
    }
    mkdirIfNeeded(basedir(outputDir));


    if(inputFilelist.size())
        SH::readFileList(sh, sampleName, inputFilelist);
    else if(inputDirectory.size() && inputFilePattern.size())
        SH::ScanDir().sampleDepth(0).samplePattern(inputFilePattern).scan(sh, inputDirectory);
    else {
        cout<<"required input (filelist or directory)"<<endl;
        return 1;
    }

    sh.setMetaString( "nc_tree", "CollectionTree" );
    if(verbose)
        sh.print();

    EL::Job job;
    job.sampleHandler( sh );
    if(numEvents>0)
        job.options()->setDouble (EL::Job::optMaxEvents, numEvents);

    TruthReader* aTruth = new TruthReader();
    aTruth->verbose = verbose;
    aTruth->weightIndex = weightIndex;
    job.algsAdd( aTruth );

    cout<<"outputDir "<<outputDir<<endl;
    if(lxbatch) {
        EL::LSFDriver driver;
        driver.submitOnly( job, outputDir );
        EL::LSFDriver::wait(outputDir);
    } else {
        EL::DirectDriver driver;
        driver.submit( job, outputDir );
    }

    return 0;
}
