#ifndef __vtkITKSignedDistanceTransform_h
#define __vtkITKSignedDistanceTransform_h

#include "vtkSlicerQCLibModuleLogicExport.h"

#include <vtkSimpleImageToImageFilter.h>

class VTK_SLICER_QCLIB_MODULE_LOGIC_EXPORT vtkITKSignedDistanceTransform : public vtkSimpleImageToImageFilter
{
 public:
  static vtkITKSignedDistanceTransform *New();
  vtkTypeMacro(vtkITKSignedDistanceTransform,vtkSimpleImageToImageFilter);

  vtkSetMacro(InsideIsPositive,bool);
  vtkGetMacro(InsideIsPositive,bool);
  vtkSetMacro(SquaredDistance,bool);
  vtkGetMacro(SquaredDistance,bool);
  vtkSetMacro(UseImageSpacing,bool);
  vtkGetMacro(UseImageSpacing,bool);
  vtkSetMacro(BackgroundValue,double);
  vtkGetMacro(BackgroundValue,double);
  vtkSetMacro(ObjectValue,double);
  vtkGetMacro(ObjectValue,double);

  enum ITKAlgorithm
  {
    SignedMaurer,
    ApproximateSigned,
    SignedDanielsson
  };

  void SetAlgorithm(ITKAlgorithm);
  ITKAlgorithm GetAlgorithm();

  //Python wrapper functions
  void SetAlgorithmToSignedMaurer();
  void SetAlgorithmToApproximateSigned();
  void SetAlgorithmToSignedDanielsson();
  int GetAlgorithmInt();
  void SetAlgorithmInt(int);

  void GetVoronoiMap(vtkImageData*);
  //void GetVectorMap();

  void SetVoronoiMap(vtkImageData*);
  void SetVectorMap(vtkImageData**);

  void PrintSelf(ostream& os, vtkIndent indent);

 protected:
  vtkITKSignedDistanceTransform();
  ~vtkITKSignedDistanceTransform();

  bool InsideIsPositive;
  bool SquaredDistance;
  bool UseImageSpacing;

  ITKAlgorithm ITKalgorithm;
  
  double BackgroundValue;
  double ObjectValue;

  vtkImageData* VoronoiMap;
  vtkImageData* VectorMap[3];

  virtual void SimpleExecute(vtkImageData* input,vtkImageData* output);
};

#endif
