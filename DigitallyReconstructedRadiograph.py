#!/usr/bin/env python
# coding: utf-8
import itk
import math

input_name = "D:\\rawdata\\T15\\T15"
output_name = "1.gipl"
ok = False
verbose = True
rx = -90.0
ry = 0.0
rz = 0

tx = 0.
ty = 0.
tz = 0.

cx = 0.
cy = 0.
cz = 0.

sid = 400.
sx = 1.
sy = 1.

dx = 501.
dy = 501.

o2Dx = 0
o2Dy = 0
threshold = 0

# parse arg
# TODO

Dimension = 3

PixelType = itk.UC
InputPixelType = itk.SS
OutputPixelType = itk.UC
InputImageType = itk.Image[InputPixelType, Dimension]
OutputImageType = itk.Image[OutputPixelType, Dimension]
image = InputImageType.New()
if input_name:
    ImageType = itk.Image[PixelType, Dimension]
    ReaderType = itk.ImageSeriesReader[InputImageType]
    gdcmIO = itk.GDCMImageIO.New()
    nameGenerator = itk.GDCMSeriesFileNames.New()
    nameGenerator.SetInputDirectory(input_name)

    files = nameGenerator.GetInputFileNames()
    reader = ReaderType.New()
    reader.SetImageIO(gdcmIO)
    reader.SetFileNames(files)
    reader.Update()
    image = reader.GetOutput()
    WriterType = itk.ImageFileWriter[InputImageType]
    writer = WriterType.New()
    itk.GiplImageIOFactory.RegisterOneFactory()
    writer.SetFileName("./body.gipl")
    writer.SetInput(image)
    writer.Update()
else:
    image = InputImageType.New()
    spacing = [3, 3, 3]
    image.SetSpacing(spacing)

    origin = [0, 0, 0]
    image.SetOrigin(origin)

    start = [0, 0, 0]
    size = [61, 61, 61]
    region = itk.itkImageRegionPython.itkImageRegion3()
    region.SetSize(size)
    region.SetIndex(start)

    image.SetRegions(region)
    image.Allocate(True)
    image.Update()
    array = itk.GetArrayFromImage(image)
    for i in range(array.shape[0]):
        for j in range(array.shape[1]):
            for k in range(array.shape[2]):
                if ((i >= 6) and (i <= 54) and (j >= 6) and (j <= 54)
                        and (k >= 6) and (k <= 54) and
                    ((((i <= 11) or (i >= 49)) and ((j <= 11) or (j >= 49))) or
                     (((i <= 11) or (i >= 49)) and ((k <= 11) or (k >= 49))) or
                     (((j <= 11) or (j >= 49)) and ((k <= 11) or (k >= 49))))):
                    array[i][j][k] = 10
                elif (
                    (i >= 18) and (i <= 42) and (j >= 18) and (j <= 42)
                        and (k >= 18) and (k <= 42) and
                    ((((i <= 23) or (i >= 37)) and ((j <= 23) or (j >= 37))) or
                     (((i <= 23) or (i >= 37)) and ((k <= 23) or (k >= 37))) or
                     (((j <= 23) or (j >= 37)) and ((k <= 23) or (k >= 37))))):
                    array[i][j][k] = 60
                elif ((i == 30) and (j == 30) and (k == 30)):
                    array[i][j][k] = 100
    image = itk.GetImageFromArray(array)
    filename = "body.gipl"
    WriterType = itk.ImageFileWriter[ImageType]
    writer = WriterType.New()
    itk.GiplImageIOFactory.RegisterOneFactory()
    writer.SetFileName(filename)
    writer.SetInput(image)
    writer.Update()

if verbose:
    print("Input: ")
    print(f"{image.GetBufferedRegion()}")
    print(f" Resolution: {image.GetSpacing()}")
    print(f"Origin: {image.GetOrigin()}")

FilterType = itk.ResampleImageFilter[InputImageType, InputImageType]
filter = FilterType.New()
print(type(image))
filter.SetInput(image)
filter.SetDefaultPixelValue(0)
TransforType = itk.CenteredEuler3DTransform[itk.D]
transform = TransforType.New()
transform.SetComputeZYX(True)
translation = [tx, ty, tz]

dtr = (math.atan(1.0) * 4.0) / 180.0
transform.SetTranslation(translation)
transform.SetRotation(dtr * rx, dtr * ry, dtr * rz)
imOrigin = image.GetOrigin()
imRes = image.GetSpacing()

imRegion = image.GetBufferedRegion()
imSize = imRegion.GetSize()
imOrigin[0] += imRes[0] * imSize[0] / 2.0
imOrigin[1] += imRes[1] * imSize[1] / 2.0
imOrigin[2] += imRes[2] * imSize[2] / 2.0

center = [cx + imOrigin[0], cy + imOrigin[1], cz + imOrigin[2]]
transform.SetCenter(center)

if verbose:
    print(f"Image Size: {imSize}")
    print(f"Resolution: {imRes}")
    print(f"origin: {imOrigin}")
    print(f"center: {center}")
    print(f"Transform: {transform}")

InterpolatorType = itk.itkRayCastInterpolateImageFunctionPython.itkRayCastInterpolateImageFunctionISS3D
interpolator = InterpolatorType.New()
interpolator.SetTransform(transform)
interpolator.SetThreshold(threshold)
focalpoint = [imOrigin[0], imOrigin[1], imOrigin[2] - sid / 2.]
interpolator.SetFocalPoint(focalpoint)
if verbose:
    print(f"Focal Point: {focalpoint[0]}, {focalpoint[1]}, {focalpoint[2]}")
print(interpolator)
filter.SetInterpolator(interpolator)
filter.SetTransform(transform)
size = itk.Size[Dimension]()
size[0] = int(dx)
size[1] = int(dy)
size[2] = 1
filter.SetSize(size)
spacing = [sx, sy, 1.0]
filter.SetOutputSpacing(spacing)

if verbose:
    print(f"Output Image Size: {size[0]}, {size[1]}, {size[2]}")
    print(f"Output Image Spacing: {spacing[0]}, {spacing[1]}, {spacing[2]}")

origin = []
origin.append(imOrigin[0] + o2Dx - sx * ((dx - 1.0) / 2.0))
origin.append(imOrigin[1] + o2Dy - sy * ((dy - 1.0) / 2.0))
origin.append(imOrigin[2] + sid / 2.0)
if verbose:
    print(f"Output Image Origin: {origin}")

RescaleFilterType = itk.itkRescaleIntensityImageFilterPython.itkRescaleIntensityImageFilterISS3ISS3
rescaler = RescaleFilterType.New()
rescaler.SetOutputMinimum(0)
rescaler.SetOutputMaximum(255)
rescaler.SetInput(filter.GetOutput())
WriterType = itk.ImageFileWriter[OutputImageType]
writer = WriterType.New()
itk.GiplImageIOFactory.RegisterOneFactory()
writer.SetFileName(output_name)
writer.SetInput(reader.GetOutput())
writer.Update()
