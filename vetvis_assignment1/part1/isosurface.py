"""Isosurface extraction.

This script should extract and display isosurfaces of the probability
density of a hydrogen atom in a volume dataset.

You can run the script from the command line by typing
python isosurface.py

"""

import vtk


# Define a class for the keyboard interface
class KeyboardInterface(object):
    """Keyboard interface.

    Provides a simple keyboard interface for interaction. You should
    extend this interface with keyboard shortcuts for changing the
    isovalue interactively.

    """

    def __init__(self):
        self.screenshot_counter = 0
        self.render_window = None
        self.window2image_filter = None
        self.png_writer = None
        # Add the extra attributes you need here...

    def keypress(self, obj, event):
        """This function captures keypress events and defines actions for
        keyboard shortcuts."""
        key = obj.GetKeySym()
        if key == "9":
            self.render_window.Render()
            self.window2image_filter.Modified()
            screenshot_filename = ("screenshot%02d.png" %
                                   (self.screenshot_counter))
            self.png_writer.SetFileName(screenshot_filename)
            self.png_writer.Write()
            print("Saved %s" % (screenshot_filename))
            self.screenshot_counter += 1
        # Add your keyboard shortcuts here. You can use, e.g., the
        # "Up" key to increase the isovalue and the "Down" key to
        # decrease it. Don't forget to call the render window's
        # Render() function to update the rendering after you have
        # changed the isovalue.
        # elif key == ...


# Read the volume dataset
filename = "hydrogen.vtk"
reader = vtk.vtkStructuredPointsReader()
reader.SetFileName(filename)
print("Reading volume dataset from " + filename + " ...")
reader.Update()  # executes the reader
print("Done!")

# Just for illustration, extract and print the dimensions of the
# volume. The string formatting used here is similar to the sprintf
# style in C.
width, height, depth = reader.GetOutput().GetDimensions()
print("Dimensions: %i %i %i" % (width, height, depth))

# Create an outline of the volume
outline = vtk.vtkOutlineFilter()
outline.SetInput(reader.GetOutput())
outline_mapper = vtk.vtkPolyDataMapper()
outline_mapper.SetInput(outline.GetOutput())
outline_actor = vtk.vtkActor()
outline_actor.SetMapper(outline_mapper)

# Define actor properties (color, shading, line width, etc)
outline_actor.GetProperty().SetColor(0.8, 0.8, 0.8)
outline_actor.GetProperty().SetLineWidth(2.0)

#
#
# Add your isosurface extraction and colormapping code here...
#
##################################################################################
lut = vtk.vtkLookupTable()

ctf = vtk.vtkColorTransferFunction()
ctf.SetColorSpaceToDiverging()
ctf.AddRGBPoint(0.0, 0.230, 0.299, 0.754)
ctf.AddRGBPoint(1.0, 0.706, 0.016, 0.150)

cc = list()
for i in range(256):
    cc.append(ctf.GetColor(float(i) / 255.0))

lut.SetNumberOfColors(256)
for i,item in enumerate(cc):
    lut.SetTableValue(i, item[0], item[1], item[2], 1.0)
    lut.SetRange(0,10)
lut.Build()

output = reader.GetOutput()
scalar_range = output.GetScalarRange()

mapper = vtk.vtkDataSetMapper()
if vtk.VTK_MAJOR_VERSION <= 5:
    mapper.SetInput(output)
else:
    mapper.SetInputData(output)
mapper.SetScalarRange(scalar_range)
mapper.SetLookupTable(lut)

actor = vtk.vtkActor()
actor.SetMapper(mapper)
 
##################################################################################

# Create a renderer and add the actors to it
renderer = vtk.vtkRenderer()
renderer.SetBackground(0.2, 0.2, 0.2)
renderer.AddActor(outline_actor)
# renderer.AddActor(...) Tambahkan actor baru yaitu skala
renderer.AddActor(actor)

# Create a render window
render_window = vtk.vtkRenderWindow()
render_window.SetWindowName("Isosurface extraction")
render_window.SetSize(800, 800)
render_window.AddRenderer(renderer)

# Create an interactor
interactor = vtk.vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Create a window-to-image filter and a PNG writer that can be used
# for taking screenshots
window2image_filter = vtk.vtkWindowToImageFilter()
window2image_filter.SetInput(render_window)
png_writer = vtk.vtkPNGWriter()
png_writer.SetInput(window2image_filter.GetOutput())

# Set up the keyboard interface
keyboard_interface = KeyboardInterface()
keyboard_interface.render_window = render_window
keyboard_interface.window2image_filter = window2image_filter
keyboard_interface.png_writer = png_writer

# create the scalar_bar
scalar_bar = vtk.vtkScalarBarActor()
scalar_bar.SetOrientationToHorizontal()
scalar_bar.SetLookupTable(lut)

# create the scalar_bar_widget
scalar_bar_widget = vtk.vtkScalarBarWidget()
scalar_bar_widget.SetInteractor(interactor)
scalar_bar_widget.SetScalarBarActor(scalar_bar)
scalar_bar_widget.On()

# Connect the keyboard interface to the interactor
interactor.AddObserver("KeyPressEvent", keyboard_interface.keypress)

# Initialize the interactor and start the rendering loop
interactor.Initialize()
render_window.Render()
interactor.Start()
