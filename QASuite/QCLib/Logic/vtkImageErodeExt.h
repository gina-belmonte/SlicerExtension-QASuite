/*=auto=========================================================================

  Portions (c) Copyright 2005 Brigham and Women's Hospital (BWH) All Rights Reserved.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

=========================================================================auto=*/
///  vtkImageErodeExt -  Performs erosion
///
/// Erodes pixels of specified Foreground value by setting them
/// to the Background value. Variable 3D connectivity (4- or 8-neighbor).

#ifndef __vtkImageErodeExt_h
#define __vtkImageErodeExt_h

#include "vtkSlicerQCLibModuleLogicExport.h"

// VTK includes
#include <vtkImageData.h>
#include <vtkImageNeighborhoodFilter.h>

class VTK_SLICER_QCLIB_MODULE_LOGIC_EXPORT vtkImageErodeExt : public vtkImageNeighborhoodFilter
{
 public:
  static vtkImageErodeExt *New();
  //vtkTypeRevisionMacro(vtkImageErodeExt,vtkImageNeighborhoodFilter);
  vtkTypeMacro(vtkImageErodeExt,vtkImageNeighborhoodFilter);

  ///
  /// Background and foreground pixel values in the image.
  /// Usually 0 and some label value, respectively.
  vtkSetMacro(Background, float);
  vtkGetMacro(Background, float);
  vtkSetMacro(Foreground, float);
  vtkGetMacro(Foreground, float);

  //if set butForeground, every voxel value different than foreground
  //are considered in background
  vtkSetMacro(butForeground, bool);
  vtkGetMacro(butForeground, bool);

  void setConnectivity2D();
  void setRadius(int*);
  void setRadius(int,int,int);
  //void setButForeground(bool);

protected:
  vtkImageErodeExt();
  vtkImageErodeExt(float,float,int*,bool,bool);
  vtkImageErodeExt(float,float,int,int,int,bool,bool);
  ~vtkImageErodeExt();

  float Background;
  float Foreground;

  int radii[3];
  bool connectivity2D;
  bool butForeground;

  void ThreadedExecute(vtkImageData *inData, vtkImageData *outData,
    int extent[6], int id);
};

#endif

