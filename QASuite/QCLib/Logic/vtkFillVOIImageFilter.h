#ifndef __vtkFillVOIImageFilter_h
#define __vtkFillVOIImageFilter_h

#include "vtkSlicerQCLibModuleLogicExport.h"

// VTK includes
#include <vtkSimpleImageToImageFilter.h>

//template <class IT>
class VTK_SLICER_QCLIB_MODULE_LOGIC_EXPORT vtkFillVOIImageFilter : public vtkSimpleImageToImageFilter
{
 public:
  static vtkFillVOIImageFilter *New();
  vtkTypeMacro(vtkFillVOIImageFilter,vtkSimpleImageToImageFilter);

  //vtkSetVector6Macro(VOI,int);
  //vtkGetVectorMacro(VOI,int,6);

  //vtkSetMacro(fillValue, IT);
  //vtkGetMacro(fillValue, IT);

  vtkSetMacro(fillValue,double);
  vtkGetMacro(fillValue,double);

  vtkGetMacro(numVOIs,int);

  void GetNthVOI(int index,int VOI[6]);
  //int* GetVOI(int index);
  int SetNthVOI(int index,int VOI[6]);
  void AddVOI(int VOI[6]);
  void ClearVOIs();

  bool IsInVOIs(int,int,int);

  void UpdateInputImageINPLACE(vtkImageData*);

  void PrintSelf(ostream& os, vtkIndent indent);

 protected:
  vtkFillVOIImageFilter();
  //vtkFillVOIImageFilter(IT);
  vtkFillVOIImageFilter(double);
  ~vtkFillVOIImageFilter();

  //IT fillValue;
  double fillValue;
  //int VOI[6];
  int* VOIList;
  uint numVOIs;

  virtual void SimpleExecute(vtkImageData* input,vtkImageData* output);
};

#endif
