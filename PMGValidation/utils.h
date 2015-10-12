// emacs -*- C++ -*-
#ifndef SUSYNTHLFV_UTILS_H
#define SUSYNTHLFV_UTILS_H

/*
  Generic utility functions
  davide.gerbaudo@gmail.com
  Aug 2013
*/

#include <string>

std::string basedir(const std::string &path);
bool dirExists(const std::string &dirname);
/// mkdir if it is not already there. Return dir path; return empty string if there was a problem
std::string mkdirIfNeeded(const std::string &dirname);
/// return a string reproducting the command being executed
std::string commandLineArguments(int argc, char **argv);

#endif
