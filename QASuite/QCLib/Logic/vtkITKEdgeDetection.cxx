#include <itkImage.h>
#include <itkCannyEdgeDetectionImageFilter.h>
#include <itkSobelEdgeDetectionImageFilter.h>
#include <itkZeroCrossingBasedEdgeDetectionImageFilter.h>
#include <itkImageToVTKImageFilter.h>
#include <itkVTKImageToImageFilter.h>
#include <vtkImageData.h>
#include <vtkObjectFactory.h>
#include <stdlib.h>
#include <vtkImageCast.h>

#include "vtkITKEdgeDetection.h"

vtkStandardNewMacro(vtkITKEdgeDetection);

vtkITKEdgeDetection::vtkITKEdgeDetection()
{
  this->variance=2.0;
  for(int n=0;n<2;n++)
  {
    this->threshold[n]=0.0;
  }
  this->SetAlgorithm(Canny);
}

vtkITKEdgeDetection::~vtkITKEdgeDetection()
{}

void vtkZeroCrossEdgeDetectionExecute(vtkITKEdgeDetection* self)
{
  typedef itk::Image<double, 3>  ImageType;
  typedef itk::ZeroCrossingBasedEdgeDetectionImageFilter <ImageType, ImageType> ZeroCrossingBasedEdgeDetectionImageFilterType;

  typedef itk::ImageToVTKImageFilter<ImageType>  ConnectorType;
  typedef itk::VTKImageToImageFilter<ImageType>  VTKConnectorType;

  typename ZeroCrossingBasedEdgeDetectionImageFilterType::Pointer zerocFilter = ZeroCrossingBasedEdgeDetectionImageFilterType::New();
  typename ConnectorType::Pointer connector = ConnectorType::New();
  typename VTKConnectorType::Pointer vtkconnector = VTKConnectorType::New();

  typedef itk::FixedArray< double, 3 > ArrayType;
  ArrayType m_Variance;
  m_Variance.Fill(self->Getvariance());

  vtkImageCast *cast=vtkImageCast::New();

  cast->SetInputData((vtkImageData*)self->GetInput());
  cast->SetOutputScalarTypeToDouble();
  cast->Update();

  vtkconnector->SetInput(cast->GetOutput());
  vtkconnector->Update();

  zerocFilter->SetInput(vtkconnector->GetOutput());
  zerocFilter->SetVariance(m_Variance);

  zerocFilter->Update();

  connector->SetInput(zerocFilter->GetOutput());
  connector->Update();

  cast->SetInputData(connector->GetOutput());
  cast->SetOutputScalarType(((vtkImageData*)self->GetInput())->GetScalarType());
  cast->Update();

  self->SetOutput(cast->GetOutput());
}

void vtkSobelEdgeDetectionExecute(vtkITKEdgeDetection* self)
{
  typedef itk::Image<double, 3>  ImageType;
  typedef itk::SobelEdgeDetectionImageFilter <ImageType, ImageType> SobelEdgeDetectionImageFilterType;

  typedef itk::ImageToVTKImageFilter<ImageType>  ConnectorType;
  typedef itk::VTKImageToImageFilter<ImageType>  VTKConnectorType;

  typename SobelEdgeDetectionImageFilterType::Pointer sobelFilter = SobelEdgeDetectionImageFilterType::New();
  typename ConnectorType::Pointer connector = ConnectorType::New();
  typename VTKConnectorType::Pointer vtkconnector = VTKConnectorType::New();

  vtkImageCast *cast=vtkImageCast::New();

  cast->SetInputData((vtkImageData*)self->GetInput());
  cast->SetOutputScalarTypeToDouble();
  cast->Update();

  vtkconnector->SetInput(cast->GetOutput());
  vtkconnector->Update();

  sobelFilter->SetInput(vtkconnector->GetOutput());
  sobelFilter->Update();

  connector->SetInput(sobelFilter->GetOutput());
  connector->Update();

  cast->SetInputData(connector->GetOutput());
  cast->SetOutputScalarType(((vtkImageData*)self->GetInput())->GetScalarType());
  cast->Update();

  self->SetOutput(cast->GetOutput());
}

void vtkCannyEdgeDetectionExecute(vtkITKEdgeDetection* self)
{
  typedef itk::Image<double, 3>  ImageType;
  typedef itk::CannyEdgeDetectionImageFilter <ImageType, ImageType> CannyEdgeDetectionImageFilterType;

  typedef itk::ImageToVTKImageFilter<ImageType>  ConnectorType;
  typedef itk::VTKImageToImageFilter<ImageType>  VTKConnectorType;

  typename CannyEdgeDetectionImageFilterType::Pointer cannyFilter = CannyEdgeDetectionImageFilterType::New();
  typename ConnectorType::Pointer connector = ConnectorType::New();
  typename VTKConnectorType::Pointer vtkconnector = VTKConnectorType::New();

  vtkImageCast *cast=vtkImageCast::New();

  cast->SetInputData((vtkImageData*)self->GetInput());
  cast->SetOutputScalarTypeToDouble();
  cast->Update();

  vtkconnector->SetInput(cast->GetOutput());
  vtkconnector->Update();

  cannyFilter->SetInput(vtkconnector->GetOutput());
  cannyFilter->SetVariance(self->Getvariance());
  cannyFilter->SetLowerThreshold(self->Getthreshold()[0]);
  cannyFilter->SetUpperThreshold(self->Getthreshold()[1]);

  cannyFilter->Update();

  connector->SetInput(cannyFilter->GetOutput());
  connector->Update();

  cast->SetInputData(connector->GetOutput());
  cast->SetOutputScalarType(((vtkImageData*)self->GetInput())->GetScalarType());
  cast->Update();

  self->SetOutput(cast->GetOutput());
}


template <class IT>
void vtkEdgeDetectionExecute(vtkImageData* input,vtkImageData* output,IT* vtkNotUsed(inPtr), IT* vtkNotUsed(outPtr),vtkITKEdgeDetection* self)
{
  if (input->GetScalarType() != output->GetScalarType())
    {
      vtkGenericWarningMacro(<< "Execute: input ScalarType, " << input->GetScalarType()
			     << ", must match out ScalarType " << output->GetScalarType());
      return;
    }

  cout<<"exec deep "<<self->GetAlgorithm()<<"\n";

  if (self->GetAlgorithm()==vtkITKEdgeDetection::Canny)
    {
      cout<<"canny\n";
      vtkCannyEdgeDetectionExecute(self);
    }
  else if (self->GetAlgorithm()==vtkITKEdgeDetection::Sobel)
    {
      cout<<"sobel\n";
      vtkSobelEdgeDetectionExecute(self);
    }
  else if (self->GetAlgorithm()==vtkITKEdgeDetection::ZeroCrossing)
    {
      cout<<"zero crossing\n";
      vtkZeroCrossEdgeDetectionExecute(self);
    }
}

void vtkITKEdgeDetection::SimpleExecute(vtkImageData* input, vtkImageData* output)
{

  void* inPtr = input->GetScalarPointer();
  void* outPtr = output->GetScalarPointer();

  cout<<"exec "<<this->GetAlgorithm()<<"\n";

  switch(output->GetScalarType())
    {
    // This is simply a #define for a big case list. It handles all
    // data types VTK supports.
      vtkTemplateMacro(vtkEdgeDetectionExecute(input, output,static_cast<VTK_TT *>(inPtr), static_cast<VTK_TT *>(outPtr),this));
    default:
      vtkGenericWarningMacro("Execute: Unknown input ScalarType");
      return;
    }
}


void vtkITKEdgeDetection::SetAlgorithm(EdgeDetectAlgorithm alg)
{
  this->algorithm=alg;
  this->Modified();
}

void vtkITKEdgeDetection::SetAlgorithmInt(int alg)
{
  this->SetAlgorithm((EdgeDetectAlgorithm) alg);
}

void vtkITKEdgeDetection::SetAlgorithmToCanny()
{
  this->SetAlgorithm(Canny);
}

void vtkITKEdgeDetection::SetAlgorithmToSobel()
{
  this->SetAlgorithm(Sobel);
}

void vtkITKEdgeDetection::SetAlgorithmToZeroCrossing()
{
  this->SetAlgorithm(ZeroCrossing);
}
 

vtkITKEdgeDetection::EdgeDetectAlgorithm vtkITKEdgeDetection::GetAlgorithm()
{
  return this->algorithm;
}

int vtkITKEdgeDetection::GetAlgorithmInt()
{
  return ((int) this->algorithm);
}

void vtkITKEdgeDetection::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);

  os << indent << "Variance: " << this->variance <<"\n";
  os << indent << "Threashold Range: " << this->threshold[0] << " "<<  this->threshold[1] <<"\n";
  os << indent << "Algorithm: "<<this->algorithm<<"\n";
}
