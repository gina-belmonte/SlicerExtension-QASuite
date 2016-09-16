#ifndef __vtkITKEdgeDetection_h
#define __vtkITKEdgeDetection_h

#include "vtkSlicerQCLibModuleLogicExport.h"

#include <vtkSimpleImageToImageFilter.h>

class VTK_SLICER_QCLIB_MODULE_LOGIC_EXPORT vtkITKEdgeDetection : public vtkSimpleImageToImageFilter
{
 public:
  static vtkITKEdgeDetection *New();
  vtkTypeMacro(vtkITKEdgeDetection,vtkSimpleImageToImageFilter);

  vtkSetVectorMacro(threshold,double,2);
  vtkGetVectorMacro(threshold,double,2);
  vtkSetMacro(variance, double);
  vtkGetMacro(variance, double);

  enum EdgeDetectAlgorithm
  {
    Canny,
    Sobel,
    ZeroCrossing
  };

  void SetAlgorithm(EdgeDetectAlgorithm);
  EdgeDetectAlgorithm GetAlgorithm();

  //Python wrapper functions
  void SetAlgorithmToCanny();
  void SetAlgorithmToSobel();
  void SetAlgorithmToZeroCrossing();
  int GetAlgorithmInt();
  void SetAlgorithmInt(int);


  void PrintSelf(ostream& os, vtkIndent indent);

 protected:
  vtkITKEdgeDetection();
  ~vtkITKEdgeDetection();

  double variance;
  double threshold[2];

  EdgeDetectAlgorithm algorithm;

  virtual void SimpleExecute(vtkImageData* input,vtkImageData* output);
};

#endif
