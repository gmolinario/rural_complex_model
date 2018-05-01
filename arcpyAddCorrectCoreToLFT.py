#####################################################

# This script adds the classified core forest raster (including avoiding the minor rivers) back into the LFT
#	also adds NoData and Water (all) back into final LFT classification. 

# Giuseppe Molinario 
# 03/18/2014 
# edited 08/11/2016
# updated to 2015  03/30/2018

######################################################


######################################################
# Import and variables 
import arcpy
from arcpy import env
from arcpy.sa import *
from datetime import datetime
import os

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Set overwrite to false - change only if really needed and in the appropriate snippet only.  
arcpy.env.overwriteOutput = True

# Enviroment folder is the root directory
env.workspace = r"C:\Data_Molinario\temp\LFT_local\19th_run"
root=env.workspace

# Insert path to raster to snap to 
tempEnvironment0 = arcpy.env.snapRaster
arcpy.env.snapRaster = r"C:\Data_Molinario\Temp\LFT_local\19th_run\FACET_ROC\myfacet.TIF"
arcpy.env.cellSize = 60

# Name of rural complex folder
ruralComplexFolder= "Rural_complex_v5"

# Name of folder with water and nodata masks made from FACET
WaterAndNodata="WaterAndNodata"
# Path  of it 
waterAndNodata=env.workspace+"\\"+ruralComplexFolder+"\\"+WaterAndNodata+"\\"

# LFT mosaic folder
LFTfolder="4_Output_LFT_Mosaic"

# Name of water mask
water = "Facet_water.tif"

# Name of nodata mask
nodata = "Facet_nodata.tif"

# Name of output folder
outputFolder = "Output"
# Path of output rural complex classifications folder
outputFolderPath = env.workspace+"\\"+ruralComplexFolder+"\\"+outputFolder
# Create the folder if it doesn't exist
if not os.path.exists(outputFolderPath):
	os.makedirs(outputFolderPath)

# LFTs with water and nodata in output folder
newLFTname="LFTplusWaterNodata"
# Path of it 
newLFTs=root+"\\"+ruralComplexFolder+"\\"+outputFolder+"\\"+newLFTname
# Create if it doesnt exist
if not os.path.exists(newLFTs):
	os.makedirs(newLFTs)

# Core forest folder
coreForestPath = env.workspace+r"\Core_stratification\v5\Output\With_Water_Nodata\Grouped\Hectare"

# Periods of LFT 
LFTs= ["2000","2005","2010","2015"]

##################################################################################
# Megaloop to go through all the LFT folders
##################################################################################

print "...Starting the megaloop to go through all the LFT folders ..."
print "......The LFT folders are: "
print LFTs
for LFT in LFTs:
	print "The LFT being processed is: "+ LFT
	env.workspace=root+"\\"+str(LFT)+"\\"+LFTfolder # change to lft plus core folder
	rootLFT=root+"\\"+str(LFT)
	rasters=arcpy.ListRasters()
	
	########################################################
	# Add water and no-data classes to LFT
	########################################################
	print "The list of rasters in the folder is: "
	print rasters
	for raster in rasters:
		print "Base raster is: " + raster

		# Folder with the LFT with the fixed core 
		LFTFixFolder = "5_LFT_Reclassifications"
		lftFixFolderPath=rootLFT+"\\"+LFTFixFolder
		if not os.path.exists(lftFixFolderPath):
			os.makedirs(lftFixFolderPath)
			print " Creating the folder: " + lftFixFolderPath

		# Folder for LFTs with correct core
		newFolder="With_Correct_Core"
		newFolderPath=lftFixFolderPath+"\\"+newFolder
		if not os.path.exists(newFolderPath):
			os.makedirs(newFolderPath)
			print " Creating the folder: " + newFolderPath
		

		

		print "...Adding water and nodata to the LFT output mosaic..."
		lftRaster = Raster(raster)
		env.workspace=waterAndNodata
		water=arcpy.ListRasters("*water.tif*")[0]
		nodata=arcpy.ListRasters("*nodata.tif*")[0]
		LFTplusWaterNodata= Raster(nodata)+Raster(water)+lftRaster
		rasterName = raster[:-11]
		print rasterName
		outTemp1="_temp1"
		# Descriptor for output file
		outDescription="LFT_w_WtrNodata"
		# Save the reclassified raster
		# uncomment below to save output , comment to have loop define variables
		tempRasterPath=lftFixFolderPath+"\\"+rasterName+"_"+outTemp1+".tif"
		# Save temp (will be 32 bit unsigned)
		LFTplusWaterNodata.save(tempRasterPath) 
		# Final raster description
		outRaster=lftFixFolderPath+"\\"+rasterName+"_"+outDescription+".tif"
		# Copy to final raster (so it can be made into an 8bit raster)
		arcpy.CopyRaster_management(LFTplusWaterNodata,outRaster,"DEFAULTS","","","","","8_BIT_UNSIGNED")
		# delete temp raster
		arcpy.Delete_management(tempRasterPath, "")
		print " ...finished raster " + raster
	print " ...finished LFT " + LFT
		
	######################################################################################
	# Set to zero the core classes in the original LFT so that the core can be added again
	######################################################################################
	
	print "...Setting to zero the core of the LFT outputs ..."
	arcpy.env.overwriteOutput = True
	env.workspace=lftFixFolderPath
	print env.workspace
	rasters=arcpy.ListRasters("*WtrNodata.tif*")
	print rasters
	for raster in rasters:
		print raster
		reclassField="Value"
		# remap
		remap=RemapValue([
			[0,0],
			[1,1],
			[2,2],
			[3,3],
			[4,0],
			[5,0],
			[6,0],
			[7,0],
			[100,100],
			[200,200]])
		# base raster name 
		rasterName=raster[:-4]
		outRclCoreTemp="_tempRclCore"
		outCoreTemp="_tempCore"
		outRclCoreRaster=lftFixFolderPath+"\\"+rasterName+outRclCoreTemp+".tif"
		# reclassify
		# lftCoreSetZero=Reclassify(raster, reclassField, remap)
		arcpy.gp.Reclassify_sa(arcpy.ListRasters("*WtrNodata.tif*")[0], "Value", "0 0;1 1;2 2;3 3;4 0;5 0;6 0;7 0;100 100;200 200", ""+outRclCoreRaster+"", "DATA")
		# temp raster full name
		outTempRaster=lftFixFolderPath+"\\"+rasterName+outCoreTemp+".tif"
		# final raster full name
		outputRaster=lftFixFolderPath+"\\"+rasterName[:-4]+"_core_zero.tif"
		# Now Conditional is null to make sure resulting raster has zero and not nodata
		print "Now Con isNull of reclassify into " + outTempRaster
		# con isnull of the reclassify in RAM
		conditional=Con(IsNull(outRclCoreRaster),0,outRclCoreRaster)
		# saves temporary cause it will be 32 bit
		conditional.save(outTempRaster)
		# copies to make an 8 bit
		arcpy.CopyRaster_management(outTempRaster,outputRaster,"DEFAULTS","","","","","8_BIT_UNSIGNED")
		# deletes temp
		arcpy.Delete_management(outTempRaster, "")
		# deletes temp
		arcpy.Delete_management(outRclCoreRaster, "")
	
	

	######################################################################################
	# Reclass the LFT input mask so that it has only nodata as 300
	######################################################################################
	
	print "...Reclassing the LFT input mask so NoData is 300..."
	env.workspace=root+"\\"+str(LFT)+"\\"+"Master"
	print env.workspace
	rasters=arcpy.ListRasters("*final*")
	for raster in rasters:
		print raster 
		rasterPath=env.workspace+"\\"+raster+".tif"
		print rasterPath
		reclassField="Value"
		remap=RemapValue([
		[0,300],
		[1,0],
		[2,0]]) # doesn't work, hardcoded into the reclassify
		print remap 
		outReclassTemp="_tempRcl"
		outConTemp="_tempCon"
		rasterName=raster[:-4]
		print rasterName
		# temp raster full name
		outRclTempRaster=lftFixFolderPath+"\\"+rasterName+outReclassTemp+".tif"
		print outRclTempRaster
		# final raster full name
		outputRaster=lftFixFolderPath+"\\"+rasterName[:-4]+"_rcl_nodata.tif"
		print outputRaster
		# reclassify the input 
		# reclassNoData=Reclassify(""+raster+"", reclassField, remap)
		# SNIPPET FROM ARCMAP SEEMS TO BE THE ONLY THING THAT WORKS. 
		# arcpy.gp.Reclassify_sa(""+raster+".tif", "Value", "0 300;1 0;2 0", ""+outTempRaster+"", "DATA")
		# original 
		arcpy.gp.Reclassify_sa(arcpy.ListRasters("*final*")[0], "Value", "0 300;1 0;2 0", ""+outRclTempRaster+"", "DATA")
		#  "0 300; 1 0; 2 0"
		# Now Conditional is null to make sure resulting raster has zero and not nodata
		print "Now Con isNull of reclassify into " + outConTemp
		# con isnull of the reclassify in RAM
		conditional=Con(IsNull(outRclTempRaster),0,outRclTempRaster)
		# saves temporary cause it will be 32 bit
		conditional.save(outConTemp)
		# copies to make an 8 bit
		arcpy.CopyRaster_management(outConTemp,outputRaster,"DEFAULTS","","","","","16_BIT_UNSIGNED")
		# deletes temp con
		arcpy.Delete_management(outConTemp, "")
		# deletes temp rcl
		arcpy.Delete_management(outRclTempRaster, "")
	
	#############################################################################################################
	# Now loop again for the temp LFT files (core set to zero, and add the core and the nodata from mask back in)
	#############################################################################################################
	LFTFixFolder = "5_LFT_Reclassifications"
	rootLFT=root+"\\"+str(LFT)
	lftFixFolderPath=rootLFT+"\\"+LFTFixFolder
	newFolder="With_Correct_Core"
	newFolderPath=lftFixFolderPath+"\\"+newFolder
	# delete above after running on 3/30/2018

	print "...Looping the LFT temp files to add to them the core and nodata ..."
	env.workspace=lftFixFolderPath
	rasters=arcpy.ListRasters("*core_zero*") # the LFT with cores set to 0
	print rasters
	for raster in rasters:
		print "Processing raster "+ raster

		if "2000" in raster:# 2000
			env.workspace=coreForestPath
			print env.workspace
			coreRaster=str(arcpy.ListRasters("*"+"2000"+"*rcl.tif*")[0]) # the core raster
			coreRasterPath=coreForestPath+"\\"+coreRaster
			print coreRaster
			env.workspace=lftFixFolderPath
			inputLftNodata=arcpy.ListRasters("*rcl_nodata*")[0] # the raster with the input LFT nodata (includes NF and WD)
			print coreRasterPath
			print raster
			print inputLftNodata
			newCoreLFT=Raster(coreRasterPath)+Raster(raster)+Raster(inputLftNodata) # add the rasters together
			outDescription="CrctCore"
			rasterName=raster[:-8]
			newCoreLFT.save(newFolderPath+"\\"+rasterName+outDescription+".tif")
		elif "2005" in raster:# 2005
			env.workspace=coreForestPath
			coreRaster=str(arcpy.ListRasters("*"+"2005"+"*rcl.tif*")[0])
			coreRasterPath=coreForestPath+"\\"+coreRaster
			print coreRaster
			env.workspace=lftFixFolderPath
			inputLftNodata=arcpy.ListRasters("*rcl_nodata*")[0] # the raster with the input LFT nodata (includes NF and WD)
			newCoreLFT=Raster(coreRasterPath)+Raster(raster)+Raster(inputLftNodata)
			outDescription="CrctCore"
			rasterName=raster[:-8]
			newCoreLFT.save(newFolderPath+"\\"+rasterName+outDescription+".tif")

		elif "2010" in raster: # 2010
			env.workspace=coreForestPath
			coreRaster=str(arcpy.ListRasters("*"+"2010"+"*rcl.tif*")[0])
			coreRasterPath=coreForestPath+"\\"+coreRaster
			print coreRaster
			env.workspace=lftFixFolderPath
			inputLftNodata=arcpy.ListRasters("*rcl_nodata*")[0] # the raster with the input LFT nodata (includes NF and WD)
			newCoreLFT=Raster(coreRasterPath)+Raster(raster)+Raster(inputLftNodata)
			outDescription="CrctCore"
			rasterName=raster[:-8]
			newCoreLFT.save(newFolderPath+"\\"+rasterName+outDescription+".tif")
		
		elif "2015" in raster: # 2015
			env.workspace=coreForestPath
			coreRaster=str(arcpy.ListRasters("*"+"2015"+"*rcl.tif")[0])
			coreRasterPath=coreForestPath+"\\"+coreRaster
			print coreRaster
			env.workspace=lftFixFolderPath
			inputLftNodata=arcpy.ListRasters("*rcl_nodata*")[0] # the raster with the input LFT nodata (includes NF and WD)
			newCoreLFT=Raster(coreRasterPath)+Raster(raster)+Raster(inputLftNodata)
			outDescription="CrctCore"
			rasterName=raster[:-8]
			newCoreLFT.save(newFolderPath+"\\"+rasterName+outDescription+".tif")
		
	print "...Finished adding core and nodata to temp LFTs..."
	
	

	######################################################################
	# Reclassify these final LFTs and overwrite the old ones in the folder
	######################################################################

	env.workspace=newFolderPath
	print "...Reclassifying the final LFT output. "
	rasters=arcpy.ListRasters("*CrctCore*")
	for raster in rasters:
		print "Processing raster "+ raster
		reclassField="Value"
		remap=RemapValue([
			[200,0], # from nodata raster (might actually not exist anymore in this raster) (only 500)
			[500,0], # matching nodata from input LFT and standalone nodata raster mask
			[100,1], # water - might actually not exist anymore in this raster (only 400)
			[400,1],	# matching water and nodatafrom input LFT
			[300,2], # 300 is ND and WL from the LFT input mask - this class is "Natural NF and WD"
			[0,3], # Rural complex
			[1,4], 
			[2,5],
			[3,6],
			[4,7],
			[5,8],
			[6,9],
			[7,10],
			[104,1],# water classified as water because of the forest core classification with shrunk rivers
			[105,1],
			[106,1],
			[107,1],
			[404,1],
			[405,1],
			[406,1],
			[407,1]])

		outTempRaster=newFolderPath+"\\"+"temp.tif"
		rasterName=raster[:-4]+"_rcl"
		outRaster=newFolderPath+"\\"+rasterName+".tif"
		arcpy.gp.Reclassify_sa(arcpy.ListRasters("*CrctCore*")[0], "Value", "0 3;1 4;2 5;3 6;4 7;5 8;6 9;7 10;100 1;200 0;300 2;400 1;500 0;104 1;105 1;106 1;107 1;404 1;405 1;406 1;407 1", ""+outRaster+"", "DATA")
		#arcpy.CopyRaster_management(arcpy.ListRasters("*CrctCore*")[0],outTempRaster,"DEFAULTS","","","","","16_BIT_UNSIGNED")
		#reclassRaster=Reclassify(outTempRaster, reclassField, remap)
		# deletes temp con
		#arcpy.Delete_management(outTempRaster, "")


		#reclassRaster=Reclassify(raster, reclassField, remap)
		#outDescription="_temp"
		#rasterName=raster[:-4]+"_rcl"
		# outRaster=newFolderPath+"\\"+rasterName+".tif"
		# arcpy.gp.Reclassify_sa(arcpy.ListRasters("*CrctCore*")[0], "Value", ""+remap+"", ""+outRaster+"", "DATA")
		# arcpy.env.overwriteOutput = True
		#reclassRaster.save(newFolderPath+"\\"+rasterName+".tif")
		
	print "...Finished creating the final LFTs for *"+LFT+"* with water, nodata and correct core."




########################################################### 		