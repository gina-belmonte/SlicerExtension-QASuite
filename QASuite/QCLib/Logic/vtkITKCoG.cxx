#include <itkImage.h>
#include <vtkObjectFactory.h>
#include <itkImageMomentsCalculator.h>
#include <stdlib.h>

#include "vtkITKCoG.h"

vtkStandardNewMacro(vtkITKCoG);

vtkITKCoG::vtkITKCoG()
{
  this->Reset();
}

vtkITKCoG::~vtkITKCoG()
{}

void vtkITKCoG::Reset()
{
  this->labelValue=0;
  this->slice=-1;
  for(int n=0;n<3;n++)
    {
      this->spacing[n]=1;
    }
  for(int n=0;n<3;n++)
    {
      this->COG[n]=-1;
    }
}

void vtkITKCoG::SetInput(vtkDataObject* input)
{
  this->Reset();
  vtkImageAlgorithm::SetInputData(input);
}

template <class IT>
void vtkITKCoGUpdateCalc(vtkImageData* input, IT *inPtr,vtkITKCoG* self)
{
  int dims[3];
  double spacing[3];

  input->GetDimensions(dims);
  input->GetSpacing(spacing);


  // Wrap scalars into an ITK image
  // - mostly rely on defaults for spacing, origin etc for this filter
  typedef itk::Image<IT, 3> ImageType;
  typedef itk::ImageMomentsCalculator<ImageType> MomentCalcType;
  typename MomentCalcType::Pointer imageCalc = MomentCalcType::New();
  typename ImageType::Pointer inImage = ImageType::New();
  typename ImageType::RegionType region;
  typename ImageType::IndexType index;
  typename ImageType::SizeType size;

  inImage->GetPixelContainer()->SetImportPointer(inPtr, dims[0]*dims[1]*dims[2], false);
  index[0] = index[1] = index[2] = 0;
  region.SetIndex(index);
  size[0] = dims[0]; size[1] = dims[1]; size[2] = dims[2];
  region.SetSize(size);
  inImage->SetLargestPossibleRegion(region);
  inImage->SetBufferedRegion(region);
  inImage->SetSpacing(spacing);

  imageCalc->SetImage(inImage);
  typename MomentCalcType::VectorType CoG;
  imageCalc->Compute();
  CoG = imageCalc->GetCenterOfGravity();

  double COG[3];

  //COG=(double*)malloc(3*sizeof(double));
  for(int i=0;i<3;i++)
    {
      COG[i]=(double)CoG[i];
    }

  self->SetCOG(COG);
}

template <class IT>
void vtkITKCoGUpdate(vtkImageData* input, IT *inPtr,vtkITKCoG* self)
{
  int dims[3];
  double* spacing;
  double CoG[3];

  input->GetDimensions(dims);
  //input->GetSpacing(spacing);

  spacing=self->Getspacing();

  int count=0;
  double sumX=0,sumY=0,sumZ=0;

  for(int x=0;x<dims[0];x++)
    {
      for(int y=0;y<dims[1];y++)
	{
	  for(int z=0;z<dims[2];z++)
	    {
	      double vv=(double)inPtr[x+dims[0]*y+dims[0]*dims[1]*z];
	      if (self->GetlabelValue()==vv)
		{
		  count++;
		  sumX=sumX+x*spacing[0];
		  sumY=sumY+y*spacing[1];
		  sumZ=sumZ+z*spacing[2];
		}
	    }
	}
    }
  if(count>0)
    {
      CoG[0]=sumX/count;
      CoG[1]=sumY/count;
      CoG[2]=sumZ/count;
    }
  self->SetCOG(CoG);
}

// void vtkITKCoG::GetCOG(double CoG[3])
// {
//   for(int n=0;n<3;n++)
//     {
//       CoG[n]=this->COG[n];
//     }
// }

void vtkITKCoG::SimpleExecute(vtkImageData* input,vtkImageData* vtkNotUsed(output))
{
  this->SimpleExecute(input);
}

void vtkITKCoG::SimpleExecute(vtkImageData* input)
{
  void* inPtr = input->GetScalarPointer();

  switch(input->GetScalarType())
    {
      // This is simply a #define for a big case list. It handles all
      // data types VTK supports.
      vtkTemplateMacro(vtkITKCoGUpdate(input, static_cast<VTK_TT *>(inPtr),this));
    default:
      vtkGenericWarningMacro("Execute: Unknown input ScalarType");
      return;
    }
}

void vtkITKCoG::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);
 
  os<<indent<<"COG: "<<this->COG[0]<<" "<<this->COG[1]<<" "<<this->COG[2]<<"\n";
}
