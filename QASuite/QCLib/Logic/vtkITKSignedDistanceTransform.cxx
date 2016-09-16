#include <itkImage.h>
#include <vtkImageData.h>
#include <vtkObjectFactory.h>
#include <stdlib.h>

#include <itkSignedMaurerDistanceMapImageFilter.h>
#include <itkApproximateSignedDistanceMapImageFilter.h>
#include <itkSignedDanielssonDistanceMapImageFilter.h>

#include <itkVectorImageToImageAdaptor.h>
#include <itkImageToVTKImageFilter.h>
#include <itkVTKImageToImageFilter.h>

#include "vtkITKSignedDistanceTransform.h"

vtkStandardNewMacro(vtkITKSignedDistanceTransform);

vtkITKSignedDistanceTransform::vtkITKSignedDistanceTransform()
{
  this->InsideIsPositive=false;
  this->SquaredDistance=false;
  this->UseImageSpacing=true;

  this->SetAlgorithm(SignedMaurer);

  this->BackgroundValue=0;
  this->ObjectValue=1;

  this->VoronoiMap=NULL;
}

vtkITKSignedDistanceTransform::~vtkITKSignedDistanceTransform()
{}

template <class IT>
void vtkVoronoiExecute(IT* vtkNotUsed(inPtr),vtkITKSignedDistanceTransform* self)
{
  typedef itk::Image<IT, 3>  ImageType;
  typedef itk::SignedDanielssonDistanceMapImageFilter<ImageType, ImageType, ImageType> SignedDanielssonDistanceMapImageFilterType;

  typedef itk::ImageToVTKImageFilter<ImageType>  ConnectorType;
  typedef itk::VTKImageToImageFilter<ImageType>  VTKConnectorType;

  typename SignedDanielssonDistanceMapImageFilterType::Pointer danielssonFilter = SignedDanielssonDistanceMapImageFilterType::New();

  typename ConnectorType::Pointer connector = ConnectorType::New();
  typename VTKConnectorType::Pointer vtkconnector = VTKConnectorType::New();

  danielssonFilter->SetInsideIsPositive(self->GetInsideIsPositive());
  danielssonFilter->SetSquaredDistance(self->GetSquaredDistance());
  danielssonFilter->SetUseImageSpacing(self->GetUseImageSpacing());

  vtkconnector->SetInput((vtkImageData*)self->GetInput());
  vtkconnector->Update();

  danielssonFilter->SetInput(vtkconnector->GetOutput());

  danielssonFilter->Update();

  connector->SetInput(danielssonFilter->GetVoronoiMap());
  connector->Update();

  self->SetVoronoiMap(connector->GetOutput());
}

// template <class IT>
// void vtkVectorExecute(IT* vtkNotUsed(inPtr),vtkITKSignedDistanceTransform* self)
// {
//   typedef itk::Image<IT, 3>  ImageType;
//   typedef itk::SignedDanielssonDistanceMapImageFilter<ImageType, ImageType, ImageType> SignedDanielssonDistanceMapImageFilterType;

//   typedef itk::ImageToVTKImageFilter<ImageType>  ConnectorType;
//   typedef itk::VTKImageToImageFilter<ImageType>  VTKConnectorType;
//   typedef itk::VectorImageToImageAdaptor<IT, 3> ImageAdaptorType;

//   typename SignedDanielssonDistanceMapImageFilterType::Pointer danielssonFilter = SignedDanielssonDistanceMapImageFilterType::New();

//   typename ConnectorType::Pointer connector = ConnectorType::New();
//   typename VTKConnectorType::Pointer vtkconnector = VTKConnectorType::New();

//   typename ImageAdaptorType::Pointer adaptor = ImageAdaptorType::New();

//   vtkImageData* vector[3];

//   danielssonFilter->SetInsideIsPositive(self->GetInsideIsPositive());
//   danielssonFilter->SetSquaredDistance(self->GetSquaredDistance());
//   danielssonFilter->SetUseImageSpacing(self->GetUseImageSpacing());

//   vtkconnector->SetInput((vtkImageData*)self->GetInput());
//   vtkconnector->Update();

//   danielssonFilter->SetInput(vtkconnector->GetOutput());

//   danielssonFilter->Update();

//   adaptor->SetImage(danielssonFilter->GetVectorDistanceMap());
  
//   for (int n=0;n<3;n++)
//     {
//       adaptor->SetExtractComponentIndex(n);
//       adaptor->Update();
//       connector->SetInput(adaptor->GetOutput());
//       connector->Update();
//       vector[n]=connector->GetOutput();
//     }

//   self->SetVectorMap(vector);
// }


template <class IT>
void vtkSignedMaurerExecute(vtkITKSignedDistanceTransform* self)
{
  typedef itk::Image<IT, 3>  ImageType;
  typedef itk::SignedMaurerDistanceMapImageFilter<ImageType, ImageType> SignedMaurerDistanceMapImageFilterType;

  typedef itk::ImageToVTKImageFilter<ImageType>  ConnectorType;
  typedef itk::VTKImageToImageFilter<ImageType>  VTKConnectorType;

  typename SignedMaurerDistanceMapImageFilterType::Pointer maurerFilter = SignedMaurerDistanceMapImageFilterType::New();

  typename ConnectorType::Pointer connector = ConnectorType::New();
  typename VTKConnectorType::Pointer vtkconnector = VTKConnectorType::New();

  maurerFilter->SetInsideIsPositive(self->GetInsideIsPositive());
  maurerFilter->SetSquaredDistance(self->GetSquaredDistance());
  maurerFilter->SetUseImageSpacing(self->GetUseImageSpacing());
  maurerFilter->SetBackgroundValue((IT)self->GetBackgroundValue());

  vtkconnector->SetInput((vtkImageData*)self->GetInput());
  vtkconnector->Update();

  maurerFilter->SetInput(vtkconnector->GetOutput());

  maurerFilter->Update();

  connector->SetInput(maurerFilter->GetOutput());
  connector->Update();

  self->GetOutput()->DeepCopy(connector->GetOutput());
}

template <class IT>
void vtkSignedDanielssonExecute(vtkITKSignedDistanceTransform* self)
{
  typedef itk::Image<IT, 3>  ImageType;
  typedef itk::SignedDanielssonDistanceMapImageFilter<ImageType, ImageType, ImageType> SignedDanielssonDistanceMapImageFilterType;

  typedef itk::ImageToVTKImageFilter<ImageType>  ConnectorType;
  typedef itk::VTKImageToImageFilter<ImageType>  VTKConnectorType;

  typename SignedDanielssonDistanceMapImageFilterType::Pointer danielssonFilter = SignedDanielssonDistanceMapImageFilterType::New();

  typename ConnectorType::Pointer connector = ConnectorType::New();
  typename VTKConnectorType::Pointer vtkconnector = VTKConnectorType::New();

  danielssonFilter->SetInsideIsPositive(self->GetInsideIsPositive());
  danielssonFilter->SetSquaredDistance(self->GetSquaredDistance());
  danielssonFilter->SetUseImageSpacing(self->GetUseImageSpacing());

  vtkconnector->SetInput((vtkImageData*)self->GetInput());
  vtkconnector->Update();

  danielssonFilter->SetInput(vtkconnector->GetOutput());

  danielssonFilter->Update();

  connector->SetInput(danielssonFilter->GetDistanceMap());
  connector->Update();

  self->GetOutput()->DeepCopy(connector->GetOutput());

  connector->SetInput(danielssonFilter->GetVoronoiMap());
  connector->Update();

  self->SetVoronoiMap(connector->GetOutput());
}

template <class IT>
void vtkApproximateSignedExecute(vtkITKSignedDistanceTransform* self)
{
  typedef itk::Image<IT, 3>  ImageType;
  typedef itk::ApproximateSignedDistanceMapImageFilter<ImageType, ImageType> ApproximateSignedDistanceMapImageFilterType;

  typedef itk::ImageToVTKImageFilter<ImageType>  ConnectorType;
  typedef itk::VTKImageToImageFilter<ImageType>  VTKConnectorType;

  typename ApproximateSignedDistanceMapImageFilterType::Pointer approxFilter = ApproximateSignedDistanceMapImageFilterType::New();

  typename ConnectorType::Pointer connector = ConnectorType::New();
  typename VTKConnectorType::Pointer vtkconnector = VTKConnectorType::New();

  approxFilter->SetOutsideValue((IT)self->GetBackgroundValue());
  approxFilter->SetInsideValue((IT)self->GetObjectValue());

  vtkconnector->SetInput((vtkImageData*)self->GetInput());
  vtkconnector->Update();

  approxFilter->SetInput(vtkconnector->GetOutput());

  approxFilter->Update();

  connector->SetInput(approxFilter->GetOutput());
  connector->Update();

  self->GetOutput()->DeepCopy(connector->GetOutput());
}

template <class IT>
void vtkSignedDistanceMapExecute(vtkImageData* input, vtkImageData* output, IT* inPtr, IT* vtkNotUsed(outPtr), vtkITKSignedDistanceTransform* self)
{  
  if (input->GetScalarType() != output->GetScalarType())
    {
      vtkGenericWarningMacro(<< "Execute: input ScalarType, " << input->GetScalarType()
			     << ", must match out ScalarType " << output->GetScalarType());
      return;
    }

  if (self->GetAlgorithm()==vtkITKSignedDistanceTransform::SignedMaurer)
    {
      cout<<"SignedMaurer\n";
      vtkSignedMaurerExecute<IT>(self);
      vtkVoronoiExecute<IT>(inPtr,self);
    }
  else if (self->GetAlgorithm()==vtkITKSignedDistanceTransform::ApproximateSigned)
    {
      cout<<"ApproximateSigned\n";
      vtkApproximateSignedExecute<IT>(self);
      vtkVoronoiExecute<IT>(inPtr,self);
    }
  else if (self->GetAlgorithm()==vtkITKSignedDistanceTransform::SignedDanielsson)
    {
      cout<<"SignedDanielsson\n";
      vtkSignedDanielssonExecute<IT>(self);
    }
}

void vtkITKSignedDistanceTransform::SimpleExecute(vtkImageData* input, vtkImageData* output)
{

  void* inPtr = input->GetScalarPointer();
  void* outPtr = output->GetScalarPointer();

  switch(input->GetScalarType())
    {
    // This is simply a #define for a big case list. It handles all
    // data types VTK supports.
      vtkTemplateMacro(vtkSignedDistanceMapExecute(input, output,static_cast<VTK_TT *>(inPtr), static_cast<VTK_TT *>(outPtr),this));
    default:
      vtkGenericWarningMacro("Execute: Unknown input ScalarType");
      return;
    }
}

void vtkITKSignedDistanceTransform::GetVoronoiMap(vtkImageData* voronoi)
{
  voronoi->DeepCopy(this->VoronoiMap);
}

void vtkITKSignedDistanceTransform::SetVoronoiMap(vtkImageData* voronoi)
{
  if (this->VoronoiMap==NULL)
    {
      this->VoronoiMap=vtkImageData::New();
    }
  this->VoronoiMap->DeepCopy(voronoi);
}

// void vtkITKSignedDistanceTransform::GetVectorMap()
// {
//   void* inPtr = ((vtkImageData*)this->GetInput())->GetScalarPointer();
//   switch(((vtkImageData*)this->GetInput())->GetScalarType())
//     {
//     // This is simply a #define for a big case list. It handles all
//     // data types VTK supports.
//       vtkTemplateMacro(vtkVectorExecute(static_cast<VTK_TT *>(inPtr),this));
//     default:
//       vtkGenericWarningMacro("Execute: Unknown input ScalarType");
//       return;
//     }
// }

void vtkITKSignedDistanceTransform::SetVectorMap(vtkImageData** vector)
{
  if (this->VectorMap==NULL)
    {
      vtkImageData* compX=vtkImageData::New();
      vtkImageData* compY=vtkImageData::New();
      vtkImageData* compZ=vtkImageData::New();

      this->VectorMap[0]=compX;
      this->VectorMap[1]=compY;
      this->VectorMap[2]=compZ;
    }
  for(int n=0;n<3;n++)
    {
      this->VectorMap[n]->DeepCopy(vector[n]);
    }
}

void vtkITKSignedDistanceTransform::SetAlgorithm(ITKAlgorithm alg)
{
  this->ITKalgorithm=alg;
  this->Modified();
}

void vtkITKSignedDistanceTransform::SetAlgorithmInt(int alg)
{
  this->SetAlgorithm((ITKAlgorithm) alg);
}

void vtkITKSignedDistanceTransform::SetAlgorithmToSignedMaurer()
{
  this->SetAlgorithm(SignedMaurer);
}

void vtkITKSignedDistanceTransform::SetAlgorithmToApproximateSigned()
{
  this->SetAlgorithm(ApproximateSigned);
}

void vtkITKSignedDistanceTransform::SetAlgorithmToSignedDanielsson()
{
  this->SetAlgorithm(SignedDanielsson);
}
 

vtkITKSignedDistanceTransform::ITKAlgorithm vtkITKSignedDistanceTransform::GetAlgorithm()
{
  return this->ITKalgorithm;
}

int vtkITKSignedDistanceTransform::GetAlgorithmInt()
{
  return ((int) this->ITKalgorithm);
}

void vtkITKSignedDistanceTransform::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);

  os << indent << "InsideIsPositive: " << this->InsideIsPositive <<"\n";
  os << indent << "SquaredDistance: " << this->SquaredDistance <<"\n";
  os << indent << "UseImageSpacing: "<<this->UseImageSpacing<<"\n";
  os << indent << "BackgroundValue: "<<this->BackgroundValue<<"\n";
  os << indent << "ITKalgorithm: "<<this->ITKalgorithm<<"\n";
}
