#ifndef __vtkITKCoG_h
#define __vtkITKCoG_h

#include <vtkImageData.h>
// VTK includes
#include <vtkSimpleImageToImageFilter.h>
#include "vtkSlicerQCLibModuleLogicExport.h"

class VTK_SLICER_QCLIB_MODULE_LOGIC_EXPORT vtkITKCoG: public vtkSimpleImageToImageFilter
{
 public:
  static vtkITKCoG *New();
  vtkTypeMacro(vtkITKCoG,vtkSimpleImageToImageFilter);

  vtkSetVector3Macro(COG,double);
  vtkGetVector3Macro(COG,double);

  vtkSetMacro(labelValue,double);
  vtkGetMacro(labelValue,double);

  vtkSetMacro(slice,int);
  vtkGetMacro(slice,int);

  vtkSetVector3Macro(spacing,double);
  vtkGetVector3Macro(spacing,double);

  void SetInput(vtkDataObject* input);

  void PrintSelf(ostream& os, vtkIndent indent);
 protected:
  vtkITKCoG();
  ~vtkITKCoG();

  double COG[3];
  double labelValue;
  double spacing[3];
  int slice;
  
  void Reset();
  virtual void SimpleExecute(vtkImageData* input,vtkImageData* output);
  virtual void SimpleExecute(vtkImageData* input);
};

#endif
