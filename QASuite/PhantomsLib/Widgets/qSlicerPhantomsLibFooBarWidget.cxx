/*==============================================================================

  Program: 3D Slicer

  Copyright (c) Kitware Inc.

  See COPYRIGHT.txt
  or http://www.slicer.org/copyright/copyright.txt for details.

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.

  This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
  and was partially funded by NIH grant 3P41RR013218-12S1

==============================================================================*/

// FooBar Widgets includes
#include "qSlicerPhantomsLibFooBarWidget.h"
#include "ui_qSlicerPhantomsLibFooBarWidget.h"

//-----------------------------------------------------------------------------
/// \ingroup Slicer_QtModules_PhantomsLib
class qSlicerPhantomsLibFooBarWidgetPrivate
  : public Ui_qSlicerPhantomsLibFooBarWidget
{
  Q_DECLARE_PUBLIC(qSlicerPhantomsLibFooBarWidget);
protected:
  qSlicerPhantomsLibFooBarWidget* const q_ptr;

public:
  qSlicerPhantomsLibFooBarWidgetPrivate(
    qSlicerPhantomsLibFooBarWidget& object);
  virtual void setupUi(qSlicerPhantomsLibFooBarWidget*);
};

// --------------------------------------------------------------------------
qSlicerPhantomsLibFooBarWidgetPrivate
::qSlicerPhantomsLibFooBarWidgetPrivate(
  qSlicerPhantomsLibFooBarWidget& object)
  : q_ptr(&object)
{
}

// --------------------------------------------------------------------------
void qSlicerPhantomsLibFooBarWidgetPrivate
::setupUi(qSlicerPhantomsLibFooBarWidget* widget)
{
  this->Ui_qSlicerPhantomsLibFooBarWidget::setupUi(widget);
}

//-----------------------------------------------------------------------------
// qSlicerPhantomsLibFooBarWidget methods

//-----------------------------------------------------------------------------
qSlicerPhantomsLibFooBarWidget
::qSlicerPhantomsLibFooBarWidget(QWidget* parentWidget)
  : Superclass( parentWidget )
  , d_ptr( new qSlicerPhantomsLibFooBarWidgetPrivate(*this) )
{
  Q_D(qSlicerPhantomsLibFooBarWidget);
  d->setupUi(this);
}

//-----------------------------------------------------------------------------
qSlicerPhantomsLibFooBarWidget
::~qSlicerPhantomsLibFooBarWidget()
{
}
