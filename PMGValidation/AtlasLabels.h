//
//   @file    AtlasLabels.h         
//   
//   @author M.Sutton
// 
//   Copyright (C) 2010 Atlas Collaboration
//
//   $Id: AtlasLabels.h, v0.0   Thu 25 Mar 2010 10:34:20 CET $


#ifndef __ATLASLABELS_H
#define __ATLASLABELS_H

#include "TColor.h"
#include "TPad.h"

void ATLASLabelAutoScale(double x,double y,bool Preliminary=false,Color_t color=1); 

void ATLASLabelOld(double x,double y,bool Preliminary=false,Color_t color=1); 

void ATLASVersion(char* version=NULL,double x=0.88,double y=0.975,Color_t color=1); 

void myText(double x,double y,Color_t color,char *text); 

void BoxText(double x, double y,double boxsize,int mcolor,char *text); 

void myMarkerText(double x,double y,int color,int mstyle,char *text); 

#endif // __ATLASLABELS_H
