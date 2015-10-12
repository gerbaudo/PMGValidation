#include "PMGValidation/utils.h"

#include <sys/stat.h>
#include <sys/types.h>

#include <sstream>

using std::string;

//----------------------------------------------------------
std::string basedir(const std::string &path)
{
    size_t found = path.find_last_of('/');
    return path.substr(0, found+1);
}
//----------------------------------------------------------
bool dirExists(const std::string &dirname)
{
    bool doesExist(false);
    if(dirname.length()<1) return doesExist;
    typedef struct stat Stat; Stat st;
    doesExist = (0==stat(dirname.c_str(), &st));
    bool isDir(S_ISDIR(st.st_mode));
    return doesExist && isDir;
}
//----------------------------------------------------------
// from : http://stackoverflow.com/questions/675039/how-can-i-create-directory-tree-in-c-linux
std::string mkdirIfNeeded(const std::string &dirname)
{
    std::string result;
    if(dirname.length()<1)      result = "";
    else if(dirExists(dirname)) result = dirname;
    else {
        int status(mkdir(dirname.c_str(), S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH));
        bool success(status==0);
        result = (success ? dirname : "");
    }
    return result;
}
//----------------------------------------------------------
std::string commandLineArguments(int argc, char **argv)
{
    int iarg=0;
    std::ostringstream oss;
    while(iarg<argc){
        oss<<" "<<argv[iarg];
        iarg++;
    }
    return oss.str();
}
//----------------------------------------------------------
