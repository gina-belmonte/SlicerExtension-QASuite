#include <vtkImageData.h>
#include <vtkObjectFactory.h>
#include <stdlib.h>

#include "vtkFillVOIImageFilter.h"

vtkStandardNewMacro(vtkFillVOIImageFilter);

//----------------------------------------------------------------------------
// Description:
// Constructor sets default values
//template <class IT>
//vtkFillVOIImageFilter<IT>::vtkFillVOIImageFilter()
vtkFillVOIImageFilter::vtkFillVOIImageFilter()
{
  this->fillValue=1.0;
  this->numVOIs=0;

  //this->VOI[0] = this->VOI[2] = this->VOI[4] = 0;
  //this->VOI[1] = this->VOI[3] = this->VOI[5] = VTK_LARGE_INTEGER;

  this->VOIList=NULL;
}

//template <class IT>
//vtkFillVOIImageFilter<IT>::vtkFillVOIImageFilter(IT fv)
vtkFillVOIImageFilter::vtkFillVOIImageFilter(double fv)
{
  this->fillValue=fv;
  this->numVOIs=0;

  //this->VOI[0] = this->VOI[2] = this->VOI[4] = 0;
  //this->VOI[1] = this->VOI[3] = this->VOI[5] = VTK_LARGE_INTEGER;

  this->VOIList=NULL;
}

vtkFillVOIImageFilter::~vtkFillVOIImageFilter()
{
  this->ClearVOIs();
}

template <class IT>
void vtkFillVOIExecute(vtkImageData* input, vtkImageData* output, IT* inPtr, IT* outPtr, vtkFillVOIImageFilter* vf)
//void vtkFillVOIExecute(vtkImageData* input, vtkImageData* output, void* inPtr, void* outPtr)
{
  int dims[3];
  input->GetDimensions(dims);

  if (input->GetScalarType() != output->GetScalarType())
    {
      vtkGenericWarningMacro(<< "Execute: input ScalarType, " << input->GetScalarType()
			     << ", must match out ScalarType " << output->GetScalarType());
      return;
    }

  for(int x=0;x<dims[0];x++)
    {
      for(int y=0;y<dims[1];y++)
        {	
	  for(int z=0;z<dims[2];z++)
	    {
	      if (vf->IsInVOIs(x,y,z))
		{
		  outPtr[x+dims[0]*y+dims[0]*dims[1]*z]=(IT)vf->GetfillValue();
		}
	      else
		{
		  outPtr[x+dims[0]*y+dims[0]*dims[1]*z]=inPtr[x+dims[0]*y+dims[0]*dims[1]*z];
		}
	    }
	}
    }
}

template <class IT>
void vtkFillVOIExecuteINPLACE(vtkImageData* input, IT* inPtr,vtkFillVOIImageFilter* vf)
{
  for (int nv=0;nv<vf->GetnumVOIs();nv++)
    {
      int dims[3];
      input->GetDimensions(dims);

      int VOI[6];
      vf->GetNthVOI(nv,VOI);

      for(int x=VOI[0];x<=VOI[1];x++)
	{
	  for(int y=VOI[2];y<=VOI[3];y++)
	    {
	      for(int z=VOI[4];z<=VOI[5];z++)
		{
		  inPtr[x+dims[0]*y+dims[0]*dims[1]*z]=vf->GetfillValue();
		}
	    }
	}
    }
}

//Update input image in place for efficiency reasons
void vtkFillVOIImageFilter::UpdateInputImageINPLACE(vtkImageData* input)
{
  void* inPtr = input->GetScalarPointer();

  switch(input->GetScalarType())
    {
    // This is simply a #define for a big case list. It handles all
    // data types VTK supports.
      vtkTemplateMacro(vtkFillVOIExecuteINPLACE(input, static_cast<VTK_TT *>(inPtr),this));
    default:
      vtkGenericWarningMacro("Execute: Unknown input ScalarType");
      return;
    }
}

bool vtkFillVOIImageFilter::IsInVOIs(int x,int y,int z)
{
  if (this->numVOIs>0)
    {
      bool isIN=false;
      for(uint idx=0;idx<this->numVOIs;idx++)
	{
	  int VOI[6];
	  this->GetNthVOI(idx,VOI);
	  if (x>=VOI[0] and x<=VOI[1] and y>=VOI[2] and y<=VOI[3] and z>=VOI[4] and z<=VOI[5])
	    {
	      isIN=true;
	      break;
	    }
	}
      return isIN;
    }
  else
    {
      return true;
    }
}

//template <class IT>
//void vtkFillVOIImageFilter<IT>::SimpleExecute(vtkImageData* input, vtkImageData* output)
void vtkFillVOIImageFilter::SimpleExecute(vtkImageData* input, vtkImageData* output)
{

  void* inPtr = input->GetScalarPointer();
  void* outPtr = output->GetScalarPointer();

  switch(output->GetScalarType())
    {
    // This is simply a #define for a big case list. It handles all
    // data types VTK supports.
      vtkTemplateMacro(vtkFillVOIExecute(input, output,static_cast<VTK_TT *>(inPtr), static_cast<VTK_TT *>(outPtr),this));
    default:
      vtkGenericWarningMacro("Execute: Unknown input ScalarType");
      return;
    }
}

void vtkFillVOIImageFilter::GetNthVOI(int index,int VOI[6])
{
  if ((index>=0) and ((uint)index<this->numVOIs))
    {
      for(int i=0;i<6;i++)
	{
	  VOI[i]=this->VOIList[index*6+i];
	}
    }
  else
    {
      VOI=NULL;
    }
}

// int* vtkFillVOIImageFilter::GetVOI(int index)
// {
//   int* VOI=(int*)malloc(6*sizeof(int));
//   this->GetNthVOI(index,VOI);

//   return VOI;
// }

int vtkFillVOIImageFilter::SetNthVOI(int index,int VOI[6])
{
  if ((index>=0) and ((uint)index<this->numVOIs))
    {
      for(int i=0;i<6;i++)
	{
	  VOIList[index*6+i]=VOI[i];
	}
      return 0;
    }
  else
    {
      return -1;
    }
}

void vtkFillVOIImageFilter::AddVOI(int VOI[6])
{
  uint index=this->numVOIs++;

  this->VOIList=(int*)realloc(this->VOIList,this->numVOIs*6*(sizeof(int)));

  for(int i=0;i<6;i++)
    {
      VOIList[index*6+i]=VOI[i];
    }
}

void vtkFillVOIImageFilter::ClearVOIs()
{
  if (this->VOIList != NULL)
    {
      free(this->VOIList);
      this->VOIList=NULL;
    }
  this->numVOIs=0;
}

void vtkFillVOIImageFilter::PrintSelf(ostream& os, vtkIndent indent)
{
  this->Superclass::PrintSelf(os,indent);

  os << indent << "Number of VOIs: " << this->numVOIs <<"\n";
  for (uint i=0;i<this->numVOIs;i++)
    {
      int VOI[6];
      this->GetNthVOI(i,VOI);
      os << indent << indent << "VOI "<< i << ": \n";
      os << indent << indent << "  Imin,Imax: (" << VOI[0] << ", " 
	 << VOI[1] << ")\n";
      os << indent << indent << "  Jmin,Jmax: (" << VOI[2] << ", " 
	 << VOI[3] << ")\n";
      os << indent << indent << "  Kmin,Kmax: (" << VOI[4] << ", " 
	 << VOI[5] << ")\n";
    }

}
