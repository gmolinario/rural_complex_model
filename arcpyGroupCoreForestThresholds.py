
###############################################################
# Code to group forest into thresholded classes, 
# NOT using small rivers as fragmenting elements, and 
#	then saving a reclassified core forest raster. 
# 	- the core forest raster then needs to be added back into LFT with water and no data (separate script.) 



# Giuseppe Molinario 
# 04/22/2014
# edited 08/10/2016
# 03/2018 - rerun to create v18 that includes 2015

####################################################################

#Import arcpy modules
import arcpy
from arcpy import env
from arcpy.sa import *
import os

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# root 
root= r"C:\Data_Molinario\temp\LFT_local\19th_run\\"

# enviroment folder (root)
env.workspace = root+r"Core_stratification\V5"
coreFolder=env.workspace
# Create the folder if it doesn't exist
if not os.path.exists(coreFolder):
	os.makedirs(coreFolder)

waterAndNoData= root + r"Rural_complex_v5\WaterAndNodata"

groupedCore=root+r"\Core_stratification\V5\Output\With_Water_Nodata\Grouped"

# Name of output folder to be created
outputFolder = "Output"
outputFolderPath = env.workspace+"\\"+outputFolder
# Create the folder if it doesn't exist
if not os.path.exists(outputFolderPath):
	os.makedirs(outputFolderPath)

# LFT mosaic folder
LFTfolder="4_Output_LFT_Mosaic"

pixelsize = 60

# Insert path to raster to snap to 
arcpy.env.snapRaster = r"C:\Data_Molinario\Temp\LFT_local\19th_run\FACET_ROC\myfacet.TIF"

arcpy.env.overwriteOutput=True # careful with this one


#################################################################################
# Reclassify the LFT output into the raster to be used
#################################################################################

# Periods of LFT 
LFTs= ["2000","2005","2010","2015"]
print LFTs

for LFT in LFTs:
	print LFT
	env.workspace=root+str(LFT)+"\\"+LFTfolder # change to lft plus core folder
	print env.workspace
	# Loop through LFT rasters to create a core/non-core mask
	rasters = arcpy.ListRasters()
	print rasters
	for raster in rasters:
		print raster
		reclassField = "Value"
		outTemp=outputFolderPath+'\\'+raster[:-4]+"_temp.tif"
		outputRaster = outputFolderPath+'\\'+ raster[:-4]+"_Core_mask.tif"
		remap= RemapRange([
		[0,3,0], 
		[4,7,1]]) # make sure this is up to date with the number of classes in LFT. 
		print remap
		outReclassify = Reclassify(raster, reclassField, remap)
		print outReclassify
		# Save the reclassify as temp? 
		#outReclassify.save(outTemp)
		# print "Saving temp file " + outTemp
		print "Con isNull of reclassify into " + outputRaster
		# con isnull of the reclassify in RAM
		conditional=Con(IsNull(outReclassify),0,outReclassify)
		# saves temporary cause it will be 32 bit
		conditional.save(outTemp)
		# copies to make an 8 bit
		arcpy.CopyRaster_management(outTemp,outputRaster,"DEFAULTS","","","","","8_BIT_UNSIGNED")
		# deletes temp
		arcpy.Delete_management(outTemp, "")
		print "Deleted ... "+ outTemp + " ...raster."
	print "Done with LFT "+ LFT + "."


################################################################
# Add the water and no data to each year, setting them as NODATA
################################################################

#  Setup environment
env.workspace = outputFolderPath
print env.workspace
# Make a list of the core/non-core masks
rasters = arcpy.ListRasters()
print rasters 
# Make a new output folder
newFolder = "With_Water_Nodata"
newFolderPath = env.workspace+"\\"+newFolder
print newFolderPath
# Create the folder if it doesn't exist
if not os.path.exists(newFolderPath):
	os.makedirs(newFolderPath)


# loop and add rasters
for raster in rasters:
	print raster 
	env.workspace=waterAndNoData+"\\"+"River_shrinking"
	riverShrinkingFolder=env.workspace
	print riverShrinkingFolder
	# only the major rivers
	largeWater=arcpy.ListRasters("*Facet_water_maj_river_expand_1px.tif*")[0]
	print largeWater
	env.workspace=waterAndNoData
	# all water
	allWater=arcpy.ListRasters("*facet_water.tif*")[0]
	print allWater
	nodata=arcpy.ListRasters("*facet_nodata.tif*")[0]
	print nodata
	addedWtrNodata = Raster(outputFolderPath+"\\"+raster)+Raster(allWater)+Raster(riverShrinkingFolder+"\\"+largeWater)+Raster(nodata)
	description="all_wtr_nd"
	outputRaster=raster[:-20]+description+".tif"
	print outputRaster
	addedWtrNodata.save(newFolderPath+"\\"+outputRaster)
	print addedWtrNodata


#####################################################################
# Reclassify the output
# 	make water become forest, nodata become nodata
#	WILL ONLY WORK if LFT output raster mosaics have a VAT
#####################################################################

env.workspace = newFolderPath
print env.workspace
rasters=arcpy.ListRasters()
print rasters
for raster in rasters:
	print raster
	arcpy.BuildRasterAttributeTable_management(raster, "Overwrite")
	reclassField = "Value"
	remap = RemapValue([
		[0,0], # Not forest
		[1,1], # forest stays forest
		[200, "NODATA"], # no data goes to no data
		[100,1], # water becomes forest, so it won't fragment forest (if it were 0, it would fragment forest)
		[101,0], # major rivers go to 0, so they do fragment forest groups. 
		["NODATA",0]]) # not sure why the input no-data needs to go to 0. 
	# out description
	description="_rcl"
	outputRaster=raster[:-4]+description+".tif"
	print outputRaster
	# outReclassify=arcpy.gp.Reclassify_sa(raster, reclassField, remap, newFolderPath+'/'+outputRaster, "DATA")
	outReclassify=Reclassify(raster,reclassField,remap)
	outReclassify.save(newFolderPath+'/'+outputRaster)

#####################################################
# Region group the core
#####################################################

# Setup environment for core/non-core region group
env.workspace = newFolderPath
# Make a list of the core/non-core masks
rasters = arcpy.ListRasters("*all_wtr_nd_rcl*")

# Make a new output folder
outputFolder = "Grouped"
outputFolderPath = env.workspace+"\\"+outputFolder
# Create the folder if it doesn't exist
if not os.path.exists(outputFolderPath):
	os.makedirs(outputFolderPath)

# Loop to RegionGroup, optionally save the raster with group count values
for raster in rasters:
	# # The value to ignore, the non-core should not be grouped
	valToIgnore = 0
	# # Create a raster where the pixel Value is the pixel count of the region
	countValues=Lookup(RegionGroup(raster, "EIGHT", "WITHIN", "NO_LINK", valToIgnore),"COUNT")
	maxValue=arcpy.GetRasterProperties_management(countValues, "MAXIMUM")
	maxValue= int(maxValue.getOutput(0))
	print maxValue
	# countValues=int(countValues.getOutput(0))
	countRaster=SetNull(countValues == maxValue, countValues)
	# # Save the count raster if you want - not necssary for final product 
	outputRaster=raster[:-4]+"_grpd_count.tif"
	countRaster.save(outputFolderPath+'/'+outputRaster)	
	dataType=arcpy.GetRasterProperties_management(countRaster, "VALUETYPE")
	dataType=(dataType.getOutput(0))
	print dataType

######################################################################################
# Create an area raster - Convert the new raster values (count of pixels in the group)
#	to area in hectares (each pixel will have as value the area of its group)
######################################################################################

env.workspace = outputFolderPath
rasters = arcpy.ListRasters("*count*") 

# Make a new output folder
outputFolder = "Hectare"
outputFolderPath = env.workspace+"/"+outputFolder
# Create the folder if it doesn't exist
if not os.path.exists(outputFolderPath):
	os.makedirs(outputFolderPath)

for raster in rasters:
	# commented if you dont need to do the area conversion
	# Need to do the division in float, but a float output is unnecessary and takes up 5gb of space. 
	hectareRaster= ((Raster(raster)*float((pixelsize)**2))/ float(10000))+0.5 # add 0.5 to round up. 
	# Convert the output of the multiplication/division to Integer, round up (Int truncates, doesnt round, so adding 0.5 obtains rounded number.)
	hectareRasterInt=Int(hectareRaster)
	# Save the area raster
	outputRaster=raster[:-4]+"_ha_int.tif"
	hectareRasterInt.save(outputFolderPath+'/'+outputRaster)

###################################################################################
# Reclassify the output raster so that it the core forest is separated into classes
	# uses pixel counts, not area, which is fine. 
	# if you want to reclassify without converting to hectares
###################################################################################


env.workspace = groupedCore
rasters = arcpy.ListRasters("*count*") 
print rasters
for raster in rasters:
	print raster
	reclassField = "Value"
	areaThresholds = [1000,10000,50000] # in hectares
	# also tried threshold 25000 for v4 in version 6lft
	maxCount=arcpy.GetRasterProperties_management(raster, "MAXIMUM")
	pixelCount=[(i * 10000)/(pixelsize**2) for i in areaThresholds] 
	remap = RemapRange([
		[0,0,0],
		[1, pixelCount[0],4], # 1
		[pixelCount[0],pixelCount[1],5], #2
		[pixelCount[1],pixelCount[2],6], #3 
		[pixelCount[2],maxCount,7]]) # 4
	# out path
	outputFolderPath= env.workspace+"\\"+"Hectare"
	# temporary output variable
	outTemp=outputFolderPath+'\\'+raster[:-4]+"_temp.tif"
	# output final
	outputRaster=outputFolderPath+'\\'+raster[:-4]+"_rcl.tif"
	# reclassify the raster
	outReclassify=Reclassify(raster,reclassField,remap)
	# set to zero the null value of the reclassified raster
	print "Con isNull of reclassify into " + outputRaster
	# con isnull of the reclassify in RAM
	conditional=Con(IsNull(outReclassify),0,outReclassify)
	# saves, temporary cause it will be 32 bit
	conditional.save(outTemp)
	# copies to make an 8 bit
	arcpy.CopyRaster_management(outTemp,outputRaster,"DEFAULTS","","","","","8_BIT_UNSIGNED")
	# deletes temp
	arcpy.Delete_management(outTemp, "")
	print "Deleted ... "+ outTemp + " ...raster."


##################################################################


print "...The raster has been reclassified.'"
