#####################################################
# This script creates the rural complex/perforated forest reclassification based on the FACET LFT outputs. 
#
# Giuseppe Molinario 
# 03/18/2014 
# version update 07/05/2016
# updated to 2015 on 3/30/2018
#
######################################################


######################################################
# Import modules
######################################################
import os
import arcpy
from arcpy import env
from arcpy.sa import *
from datetime import datetime
arcpy.CheckOutExtension("Spatial")

# Arcpy settings
######################################################

# Check out any necessary licenses
arcpy.CheckOutExtension("spatial")

# Set environment 
# Enviroment folder is the root directory
env.workspace = r"C:\Data_Molinario\temp\LFT_local\19th_run"
root=env.workspace

# Insert path to raster to snap to 
tempEnvironment0 = arcpy.env.snapRaster
arcpy.env.snapRaster = r"C:\Data_Molinario\Temp\LFT_local\19th_run\FACET_ROC\myfacet.TIF"

# Set overwrite to false - change only if really needed and in the appropriate snippet only.  
arcpy.env.overwriteOutput = True

#####################################################
# Build folder structure
#####################################################

# Name of rural complex folder
ruralComplexFolder= "Rural_complex_v5"
# Name of folder with water and nodata masks made from FACET
WaterAndNodata="WaterAndNodata"
# Path for water and no-data
waterAndNodata=env.workspace+"/"+ruralComplexFolder+"/"+WaterAndNodata+"/"
#path for core forest
coreForestPath=root+'/'+"Core_stratification\V5\Output\With_Water_Nodata\Grouped\Hectare"
# Folder with the LFT with the fixed core 
LFTFixFolder = "5_LFT_Reclassifications"
if not os.path.exists(LFTFixFolder):
	os.makedirs(LFTFixFolder)
# Name of water mask
water = "Facet_water.tif"
# Name of nodata mask
nodata = "Facet_nodata.tif"
# Name of RC output folder
outputFolder = "Output"
# Path of output rural complex classifications folder
outputFolderPath = env.workspace+"/"+ruralComplexFolder+"/"+outputFolder
# Create the folder if it doesn't exist
if not os.path.exists(outputFolderPath):
	os.makedirs(outputFolderPath)

# not sure what this is. delete? 
# # LFTs with water and nodata in output folder
# newLFTs=root+"/"+ruralComplexFolder+"/"+outputFolder+"/"+"LFTplusWaterNodata"
# if not os.path.exists(newLFTs):
# 	os.makedirs(newLFTs)

# Folder for LFTs with correct core
# newFolder="With_Correct_Core"
# newFolderPath=newLFTs+"/"+newFolder
# if not os.path.exists(newFolderPath):
# 	os.makedirs(newFolderPath)


# Periods of LFT  
LFTs= ["2000","2005","2010","2015"] # 2015 added after  , or if one period only. 
# LFTs= ["2010","2014"] # 

# Area thresholds for grouping and classifying RC vs perforations. 
# 	400px area means 20px x 20px =  1200m x 1200m and so forth
# 	400, 625, 900, 1110, 2500]
# 	chosen threshold is 625 (03/2015)
# grpThresholds=[279,400, 625, 900] # for running with multiple thresholds
grpThresholds=[625]






###################################################################
# Process the LFT to separate RC and isolated forest perforation with region group
###################################################################

################################################################################################
# Reclassify the FF maps to a core forest/everthing else bin mask for each LFT output period
################################################################################################

for LFT in LFTs:
	rootLFT=root+"/"+str(LFT)
	LFTFixFolder = "5_LFT_Reclassifications"
	lftFixFolderPath=rootLFT+"/"+LFTFixFolder
	newFolder="With_Correct_Core"
	newFolderPath=lftFixFolderPath+"/"+newFolder
	env.workspace=newFolderPath
	# make a list of rasters rcl.tif made in previous script.
	rasters=arcpy.ListRasters("*rcl.tif*")
	for raster in rasters:
		start = datetime.now()
		print " "
		print start
		print raster
		print " "
		reclassField = "Value"
		# Reclassify the LFT output into a core forest and everything else mask
		remap= RemapRange([
			[0,2,"NODATA"],
			[3,6,1],
			[7,10,"NODATA"]])
		# Reclassify the raster 
		outReclassify = Reclassify(raster, reclassField, remap)
		print " "
		print outReclassify
		print " "
		# Get the LFT output raster name
		rasterName = raster[:-8]
		print " "
		print rasterName
		print " "
		# Descriptor for output file
		outDescription="rcl_for_RC_rgngrp"
		print " "
		print "Writng output files to: " + outputFolderPath
		print " "
		# Save the reclassified raster
		outReclassify.save(outputFolderPath+"/"+rasterName+"_"+outDescription+".tif")
		end = datetime.now()
		print " "
		print start - end 
		print "LFT raster "+ str(raster)+" has been reclassified."
		print " "
print " "
print "...Next step: set null to lookup of regiongroup."
print " "


##################################################################
# Region group the class of everything that is not core forest 
##################################################################


env.workspace = outputFolderPath
# List rasters again 
reclassRasters = arcpy.ListRasters()
# Loop through each threshold
# 1 raster per threshold per LFT mask will be created
for threshold in grpThresholds:
	# Loop through the reclassified LFT rasters and region group
	for raster in reclassRasters:
		print " "
		print reclassRasters
		print " "
		print raster
		print " "
		thresholdFolder=env.workspace+"/"+str(threshold)
		if not os.path.exists(thresholdFolder):
			os.makedirs(thresholdFolder)
		# Core forest value, to ignore in region group
		# valToIgnore = NoData

		# Get the name of the raster
		rasterName = raster[:-13]

		
		# Description
		description="smaller"
		# Get raster of perforating non-forest using given threshold 
		# 	(set null to the looked up count values of the region group where a group is smaller then pixels of threshold)
		RegionGrpRaster = SetNull(Lookup(RegionGroup(raster, "EIGHT", "WITHIN", "NO_LINK", ""),"COUNT") > threshold, raster)
		arcpy.env.overwriteOutput = True
		# Save the raster output
		outputRaster= rasterName+"_RgnGrp_"+description+"_"+str(threshold)+".tif"
		print " "
		print "Writing output files to: " + thresholdFolder
		print " "
		RegionGrpRaster.save(thresholdFolder+"/"+outputRaster)
		print " "
		print "Completed: "+ outputRaster
		print " "
		

		# Get raster of the rural complex using the same given threshold 
		#	(set null to the looked up count values of the region group where a group is larger then pixels of threshold)
		# Change descriptor
		description="larger"
		# Rerun regiongroup
		RegionGrpRaster = SetNull(Lookup(RegionGroup(raster, "EIGHT", "WITHIN", "NO_LINK", ""),"COUNT") < threshold, raster)
		# Save new raster
		arcpy.env.overwriteOutput = True
		outputRaster= rasterName+"_RgnGrp_"+description+"_"+str(threshold)+".tif"
		RegionGrpRaster.save(thresholdFolder+"/"+outputRaster)
		print " "
		print "Completed: "+ outputRaster
		print " "
	print " "
	print "...Completed: Set Null to Lookup of count of region group has been run on all files."
	print " "
print " "	
print "...Next step: reclassify the 'small' and 'large' perforating land cover masks."
print " "


#######################################################################
# Reclassify the outputs of the region group to prepare for merging 
#######################################################################

env.workspace = outputFolderPath 
# Reclassify the fragmenting NF
for threshold in grpThresholds:
	start = datetime.now()
	print " "
 	print start
 	print " "
	env.workspace=outputFolderPath+"/"+str(threshold)
	reclassPath=env.workspace+"/"+"Reclassified"
	if not os.path.exists(reclassPath):
		os.makedirs(reclassPath)
	RgnGrpRasters = arcpy.ListRasters()
	for raster in RgnGrpRasters:	
		tag=["larger","smaller"]

		if "smaller" in raster:
			print tag
			print raster
			print " "
			if "2000" in raster: #2000 
				conditional=Con(IsNull(raster),0,20)
				rasterName = raster[:-4]
				outDescription="reclass"
				outputRaster=rasterName+"_"+outDescription+".tif"
				arcpy.CopyRaster_management(conditional,reclassPath+"/"+outputRaster, "", "", "", "","", "16_BIT_UNSIGNED")
				print outputRaster
				print " "
			
			if "2005" in raster: #2005
				conditional=Con(IsNull(raster),0,50)
				rasterName = raster[:-4]
				outDescription="reclass"
				outputRaster=rasterName+"_"+outDescription+".tif"
				arcpy.CopyRaster_management(conditional,reclassPath+"/"+outputRaster, "", "", "", "","", "16_BIT_UNSIGNED")
				print outputRaster
				print " "	

			if "2010" in raster: #2010
				conditional=Con(IsNull(raster),0,10)
				rasterName = raster[:-4]
				outDescription="reclass"
				outputRaster=rasterName+"_"+outDescription+".tif"
				arcpy.CopyRaster_management(conditional,reclassPath+"/"+outputRaster, "", "", "", "","", "16_BIT_UNSIGNED")
				print outputRaster
				print " "

			if "2015" in raster: #2015
				conditional=Con(IsNull(raster),0,40)
				rasterName = raster[:-4]
				outDescription="reclass"
				outputRaster=rasterName+"_"+outDescription+".tif"
				arcpy.CopyRaster_management(conditional,reclassPath+"/"+outputRaster, "", "", "", "","", "16_BIT_UNSIGNED")
				print outputRaster
				print " "


		if "larger" in raster:
			if "2000" in raster:
				print tag
				conditional=Con(IsNull(raster),0,2000)
				rasterName = raster[:-4]
				outDescription="reclass"
				outputRaster=rasterName+"_"+outDescription+".tif"
				print outputRaster
				arcpy.CopyRaster_management(conditional,reclassPath+"/"+outputRaster, "", "", "", "","", "16_BIT_UNSIGNED")
			
			if "2005" in raster:
				print tag
				conditional=Con(IsNull(raster),0,2500)
				rasterName = raster[:-4]
				outDescription="reclass"
				outputRaster=rasterName+"_"+outDescription+".tif"
				print outputRaster
				arcpy.CopyRaster_management(conditional,reclassPath+"/"+outputRaster, "", "", "", "","", "16_BIT_UNSIGNED")

			if "2010" in raster:
				print tag
				conditional=Con(IsNull(raster),0,2100)
				rasterName = raster[:-4]
				outDescription="reclass"
				outputRaster=rasterName+"_"+outDescription+".tif"
				print outputRaster
				arcpy.CopyRaster_management(conditional,reclassPath+"/"+outputRaster, "", "", "", "","", "16_BIT_UNSIGNED")

			if "2015" in raster: #2015
				print tag
				conditional=Con(IsNull(raster),0,2400)
				rasterName = raster[:-4]
				outDescription="reclass"
				outputRaster=rasterName+"_"+outDescription+".tif"
				print outputRaster
				arcpy.CopyRaster_management(conditional,reclassPath+"/"+outputRaster, "", "", "", "","", "16_BIT_UNSIGNED")

		else:
			pass
	end = datetime.now()
	print " "
 	print end-start
	print " "


	

####################################################################################
# Reclassify the core raster so that the class codes will stay unique after merging
# 		-- Not necessary if already done. 
####################################################################################

# period=["2000","2005","2010","2015"]
# period=["2015"] # 2015 only of all LFTs

coreForestPath=root+'/'+"Core_stratification\V5\Output\With_Water_Nodata\Grouped\Hectare"
for period in LFTs:
	print " "
	env.workspace=coreForestPath
	raster=arcpy.ListRasters("*"+period+"*rcl.tif*")[0]
	# reclassField = "Value"
	# remap= RemapRange([
	# [4,4,100],
	# [5,5,200],
	# [6,6,300],
	# [7,7,400]])
	# coreReclass=Reclassify(raster,reclassField, remap)
	outDescription="_for_RCmap"
	rasterName = raster.replace(".tif",outDescription+".tif")
	# use of gp method below is probably because the reclassify method above didn't work? 
	arcpy.gp.Reclassify_sa(arcpy.ListRasters("*"+period+"*rcl.tif*")[0], "Value", "4 100;5 200;6 300;7 400", ""+rasterName+"", "DATA")
	print " "
	print coreForestPath
	print " "
	print rasterName
	print " "


##################################################################################
# 		Add core classes, water and nodata to each period/threshold "comb" raster
# 		-- Not necessary if it's already done.
# 		-----it's already done in core classification.-----
##################################################################################

# env.workspace=waterAndNodata
# water=arcpy.ListRasters("*water*")[0]
# nodata=arcpy.ListRasters("*nodata*")[0]
# print water
# print nodata
# # Reclassify on the fly
# reclassField = "Value"
# remapNodata= RemapValue([
# [200,2],
# ["NODATA",0]])
# remapWater = RemapValue([
# [100,1],
# ["NODATA",0]])
# nodataReclass=Reclassify(nodata,reclassField, remapNodata)
# waterReclass=Reclassify(water,reclassField, remapWater)
# waterName = water.replace(".tif","_reclass.tif")
# nodataName = nodata.replace(".tif","_reclass.tif")
# print waterName
# print nodataName
# # arcpy.env.overwriteOutput = True
# waterReclass.save(waterAndNodata+"/"+waterName)
# nodataReclass.save(waterAndNodata+"/"+nodataName)
# print "Done reclassifying the water and nodata masks..."



#########################################################################
# For each period, and threshold, Add natural NF, water, nodata, 
#		core and larger and smaller core NF groups back into one raster. 
#########################################################################
arcpy.env.overwriteOutput = True


for folder in grpThresholds:
	reclassPath=outputFolderPath+"/"+str(folder)+"/"+"Reclassified"
	env.workspace=reclassPath
	for period in LFTs:
		# Get only the "natural and older development NF, SF and wd" class from LFT
		env.workspace=root+"/"+period+"/"+LFTFixFolder+"/With_Correct_Core"
		print " "
		print env.workspace
		print " "
		naturalNF=arcpy.ListRasters("*rcl.tif*")[0]
		print naturalNF
		raster=naturalNF
		# make a reclassification on the fly
		print " "
		print naturalNF
		print " "
		# reclassField = "Value"
		#remap = RemapRange([
		# [0,1,0],
		# [2,2,500], # make it go to 500 so it stays separate
		# [3,10,0]])
		# rclNaturalNF=Reclassify(naturalNF,reclassField, remap)

		outDescription="natNfMsk"		
		rasterName = raster.replace("rcl.tif",outDescription+".tif")
		arcpy.gp.Reclassify_sa(arcpy.ListRasters("*rcl.tif*")[0], "Value", "0 0; 1 0; 2 500; 3 0; 4 0; 5 0; 6 0; 7 0; 8 0; 9 0; 10 0", ""+rasterName+"", "DATA")
		print " "
		print env.workspace
		print rasterName
		print " "

		naturalNFPath=env.workspace+"/"+rasterName
		# done with natural NF mask

		env.workspace=reclassPath
		# Get the names and paths of the larger and smaller rasters
		largerRaster=arcpy.ListRasters("*"+period+"*larger*")[0]
		print largerRaster
		largerRasterWithPath = reclassPath+"/"+largerRaster
		print largerRasterWithPath
		print " "

		smallerRaster=arcpy.ListRasters("*"+period+"*smaller*")[0]
		smallerRasterWithPath = reclassPath+"/"+smallerRaster
		print smallerRaster
		print smallerRasterWithPath
		print " "

		# Get the name and path of the core raster
		env.workspace=coreForestPath
		coreRaster=arcpy.ListRasters("*"+period+"*_for_RCmap.tif*")[0]
		print coreRaster
		coreRasterPath=coreForestPath+"/"+coreRaster
		print coreRasterPath
		print " "

		# Get the names of the water and nodata layers
		env.workspace=waterAndNodata
		water=arcpy.ListRasters("*water*reclass*")[0]
		print water
		print " "

		nodata=arcpy.ListRasters("*nodata*reclass*")[0]
		print nodata
		print " "

		# Add all rasters together 
		print "Adding the following together:"
		print naturalNFPath
		print largerRasterWithPath
		print smallerRasterWithPath
		print coreRasterPath
		print nodata
		print water
		print " "
		mergeRaster=Raster(naturalNFPath)+Raster(largerRasterWithPath)+Raster(smallerRasterWithPath)+Raster(coreRasterPath)+Raster(nodata)+Raster(water)
		# print mergeRaster
		outDescription="combWithCore"
		# arcpy.env.overwriteOutput = True
		rasterName = largerRaster[:-22]+"_"+str(folder)+"_"+outDescription+".tif"
		print rasterName
		print " "

		# Save the raster
		mergeRaster.save(reclassPath+"/"+rasterName)

		print " "
		print "...Done combining rasters in: "+rasterName+ " for period: " + period + "."
		print " "

	print " "
	print "...Done with threshold " + str(folder) + "."
	print " "

'''
###########################################################
# LEgend for reference: Reclassification for the single period RC rasters
###########################################################
			# Class legend 
			# 2000 classes are:
				# Water 1
				# nodata 2
				# Perf 20
				# RC 2000
				# Core 1-4: 100,200,300,400 

			# 2005 classes are:
				# Water 1
				# nodata 2
				# Perf 50
				# RC 2500
				# Core 1-4: 100,200,300,400 

			# 2010 classes are:
				# Water 1
				# nodata 2
				# Perf 10
				# RC 2100
				# Core 1-4: 100,200,300,400 

			# 2015 classes are:
				# Water 1
				# nodata 2
				# Perf 40
				# RC 2400
				# Core 1-4: 100,200,300,400 

			# Summary 2000,2005,2010,2015
			# 	Water 1 - also water 101,201,301,401 are new core forest overlapping water
			# 	nodata 2
			# 	Perf 2000 - 20
			# 	Perf 2005 - 50
			# 	Perf 2010	- 10
			# 	Perf 2015 - 40
			# 	RC 2000 - 2000
			# 	RC 2005 - 2500
			# 	RC 2010 - 2100
			# 	RC 2015 - 2400
			# 	Core 1-4: 100,200,300,400 

'''

######################################################################
# Reclass the FINAL RC map for each of the 3 period/threshold
#######################################################################

# do this when i have all the rasters of the time periods in the same place. 

for folder in grpThresholds:
	env.workspace=outputFolderPath+"/"+str(folder)
	reclassPath=env.workspace+"/"+"Reclassified"
	env.workspace=reclassPath
	outDescription="_final"
	# make a list of Comb rasters
	start = datetime.now()
	print " "
	print start
	print " "
	years=arcpy.ListRasters("*combWithCore*")
	for raster in years:
		if "2000" in raster:
			reclassField = "Value"
			remap= RemapRange([
			[2,2,0], # nodata
			[1,1,1], # water
			[500,500,2], # natural NF
			[2000,2020,3], # RC
			[20,20,4], # perforated
			[100,100,5],# frag forest
			[200,200,6], # frag forest
			[300,300,7], # frag forest 
			[400,400,8],# core forest
			[101,101,1],# MORE WATER? not sure why but its like that. 
			[201,201,1],# MORE WATER? not sure why but its like that. 
			[301,301,1], # MORE WATER? not sure why but its like that. 
			[401,401,1]]) # MORE WATER? not sure why but its like that.
			finalReclass=Reclassify(raster,reclassField, remap)
			# arcpy.env.overwriteOutput = True
			rasterName = raster.replace("_combWithCore.tif",outDescription+".tif")
			print " "
			print rasterName
			print " "
			# Save the raster
			arcpy.env.overwriteOutput = True
			finalReclass.save(reclassPath+"/"+rasterName)
		elif "2005" in raster:
			reclassField = "Value"
			remap= RemapRange([
			[2,2,0], # nodata
			[1,1,1], # water
			[500,500,2],# natural NF
			[2500,2550,3], # RC
			[50,50, 4], # perforated
			[100,100, 5], # frag forest
			[200,200, 6], # frag forest 
			[300,300, 7], # frag forest 
			[400,400, 8], # core forest
			[101,101, 1], # check, more water? 
			[201,201, 1], # check, more water? 
			[301,301, 1], # check, more water? 
			[401,401, 1]]) # check, more water? 
			finalReclass=Reclassify(raster,reclassField, remap)
			# arcpy.env.overwriteOutput = True
			rasterName = raster.replace("_combWithCore.tif",outDescription+".tif")
			print " "
			print rasterName
			print " "
			# Save the raster
			arcpy.env.overwriteOutput = True
			finalReclass.save(reclassPath+"/"+rasterName)
		
		if "2010" in raster:
			reclassField = "Value"
			remap= RemapValue([
			[2,2,0], # nodata
			[1,1,1], # water
			[500,500,2],# natural nf
			[2100,2110,3], # RC
			[10,10,4], # perforated
			[100,100,5], # frag forest
			[200,200,6], # frag forest
			[300,300,7], # frag forest
			[400,400,8], # core forest
			[101,101,1],# check, more water? 
			[201,201,1], # check, more water? 
			[301,301,1], # check, more water? 
			[401,401,1]]) # check, more water? 
			finalReclass=Reclassify(raster,reclassField, remap)
			rasterName = raster.replace("_combWithCore.tif",outDescription+".tif")
			print " "
			print rasterName
			print " "
			outRaster=reclassPath+"/"+rasterName
			# arcpy.gp.Reclassify_sa(raster, "Value", "2 0;1 1;500 2;2100 3;2110 3;10 4;100 5;200 6;300 7;400 8;101 1;201 1;301 1;401 1", ""+outRaster+"", "DATA")
			# Save the raster
			arcpy.env.overwriteOutput = True
			finalReclass.save(reclassPath+"/"+rasterName)

		if "2015" in raster:
			reclassField = "Value"
			remap= RemapValue([
			[2,2,0], # nodata
			[1,1,1], # water
			[500,500,2],# natural nf
			[2400,2440,3], # RC
			[40,40,4], # perforated
			[100,100,5], # frag forest
			[200,200,6], # frag forest
			[300,300,7], # frag forest
			[400,400,8], # core forest
			[101,101,1],# check, more water? 
			[201,201,1], # check, more water?
			[301,301,1], # check, more water?
			[401,401,1]]) # check, more water?
			finalReclass=Reclassify(raster,reclassField, remap)
			rasterName = raster.replace("_combWithCore.tif",outDescription+".tif")
			print " "
			print rasterName
			print " "
			outRaster=reclassPath+"/"+rasterName
			#arcpy.gp.Reclassify_sa(raster, "Value", "2 0;1 1;500 2;2400 3;2440 3;40 4;100 5;200 6;300 7;400 8;101 1;201 1;301 1;401 1", ""+outRaster+"", "DATA")
			arcpy.env.overwriteOutput = True
			finalReclass.save(reclassPath+"/"+rasterName)
		else:
			pass
		end = datetime.now()
		print " "
		print end-start
		print " "

'''







############################################################
# Create a summary raster that has every class - made from adding the above rasters together
#		The output has all the class combinations, i.e. also the core forest going to fragmented etc. 
#		This output is more adequeate for analysis and less for display. 
# 		~ 180 classes....
############################################################


for folder in grpThresholds:
	reclassPath=outputFolderPath+"/"+str(folder)+"/"+"Reclassified"
	env.workspace=reclassPath
	print reclassPath
	#2000
	raster2000select=arcpy.ListRasters("*2000*combWithCore*")[0]
	raster2000=reclassPath+"/"+raster2000select
	#2005
	raster2005select=arcpy.ListRasters("*2005*combWithCore*")[0] 
	raster2005=reclassPath+"/"+raster2005select
	#2010
	raster2010select=arcpy.ListRasters("*2010*combWithCore*")[0]
	raster2010=reclassPath+"/"+raster2010select
	#2015
	raster2015select=arcpy.ListRasters("*2015*combWithCore*")[0]
	raster2015=reclassPath+"/"+raster2015select
	#conditional statement to put these together 
	outCon1= Con((raster2000==0) or (raster2005==0) or (raster2010==0) or (raster2015==0), 100, raster2000)
	outCon2= Con((outCon1==1) & (raster2005==0) & (raster2010==0) & (raster2015==0), 100, 0)
	#final saving of a 


'''

# original summary raster script that gives 32 classes 
for folder in grpThresholds:
	reclassPath=outputFolderPath+"/"+str(folder)+"/"+"Reclassified"
	env.workspace=reclassPath
	print reclassPath
	raster2000select=arcpy.ListRasters("*2000*combWithCore*")[0]
	print raster2000select
	raster2000=reclassPath+"/"+raster2000select
	raster2005select=arcpy.ListRasters("*2005*combWithCore*")[0] 
	raster2005=reclassPath+"/"+raster2005select
	raster2010select=arcpy.ListRasters("*2010*combWithCore*")[0]
	raster2010=reclassPath+"/"+raster2010select
	raster2015select=arcpy.ListRasters("*2015*combWithCore*")[0]
	raster2015=reclassPath+"/"+raster2015select
	summaryRaster=Raster(raster2000)+Raster(raster2005)+Raster(raster2010)+Raster(raster2015)
	summaryRasterName = raster2015.replace(".tif","_summary_v2.tif")
	# Save the raster
	summaryRaster.save(summaryRasterName)
	print "Done with summary raster for the folder " + str(folder) + "..."



#######################################################################
# Create a summary raster of all the periods together
#		More adequate for display than analysis - contains frag and core forest, 
#			water, nodata, natural NF/WD all from one year only. 
# 			edited 03/2018
#			~ 67 classes
#######################################################################


	##########################################################################
	# Make combined smaller and larger rasters for each period/threshold (WITHOUT CORE)
	#
	# 	The reason to go back and remake a summary raster using the combined rasters, 
	# 	and then later adding the forest, water and no data from a single period (2015),
	# 	is that the output final raster will have less classes 
	# 	(not all combinations of core/fragmented forest becoming more fragmented.)
	###########################################################################

# Create interim "combined" rasters for each period, merging small and large groups. 
for folder in grpThresholds:
	arcpy.env.overwriteOutput = True
	reclassPath=outputFolderPath+"/"+str(folder)+"/"+"Reclassified"
	env.workspace=reclassPath
	for period in LFTs:
		env.workspace=reclassPath
		# Get the names and paths of the larger raster 
		largerRaster=arcpy.ListRasters("*"+period+"*larger*")[0]
		print " "
		print largerRaster
		print " "
		largerRasterWithPath = reclassPath+"/"+largerRaster
		print " "
		print largerRasterWithPath
		print " "

		# Get the names and paths of the smaller raster 
		smallerRaster=arcpy.ListRasters("*"+period+"*smaller*")[0]
		smallerRasterWithPath = reclassPath+"/"+smallerRaster
		print " "
		print smallerRaster
		print " "
		print smallerRasterWithPath
		print " "
		
		# Put the two rasters together
		combRasters=Raster(largerRaster)+Raster(smallerRaster)
		# Name the raster
		outDescription="_combined"
		rasterName = largerRaster[:-59]+str(folder)+outDescription+".tif"
		print " "
		print rasterName
		print " "
		# Save the raster
		combRasters.save(reclassPath+"/"+rasterName)
		print " "
		print "...Done with folder " + str(folder) + ","
		print " "
		print "...Done with period " + period + "."
		print " "


	######################################################
	# Make summary raster adding all combined raster years above	
	######################################################


for folder in grpThresholds:
	reclassPath=outputFolderPath+"/"+str(folder)+"/"+"Reclassified"
	env.workspace=reclassPath

	
	outDescription="AllYears"
	combinedRaster2000=arcpy.ListRasters("*"+"2000"+"*combined*")[0]
	combinedRaster2005=arcpy.ListRasters("*"+"2005"+"*combined*")[0]
	combinedRaster2010=arcpy.ListRasters("*"+"2010"+"*combined*")[0]
	combinedRaster2015=arcpy.ListRasters("*"+"2015"+"*combined*")[0]
	allYears=Raster(combinedRaster2000)+Raster(combinedRaster2005)+Raster(combinedRaster2010)+Raster(combinedRaster2015)
	rasterName = combinedRaster2000.replace("_combined.tif",outDescription+".tif")
	print rasterName
	# Save the raster
	arcpy.env.overwriteOutput = True
	allYears.save(reclassPath+"/"+rasterName)
	

	#############################################################
	# Add forest (fragmented and core) and water and nodata to the final combined raster
	#############################################################
for folder in grpThresholds:
	reclassPath=outputFolderPath+"/"+str(folder)+"/"+"Reclassified"
	env.workspace=reclassPath

	# Make a variable with 'all years' raster paths
	allYears=arcpy.ListRasters("*AllYears*")[0]
	allYearsPath=reclassPath+"/"+allYears

	# Make variable with core raster path to the core raster from 2010 (the final core classes)
	env.workspace=coreForestPath
	coreRaster=arcpy.ListRasters("*2015*rcl_for_RCmap*")[0]
	print coreRaster
	coreRasterPath=coreForestPath+"/"+coreRaster
	print coreRasterPath

	# Get the names of the water and nodata layers
	env.workspace=waterAndNodata
	water=arcpy.ListRasters("*water*reclass*")[0]
	print water
	nodata=arcpy.ListRasters("*nodata*reclass*")[0]
	print nodata

	# Add all rasters together 
	allYearsFull=Raster(allYearsPath)+Raster(coreRasterPath)+Raster(nodata)+Raster(water)
	# print mergeRaster
	# outDescription="AllYearsFull"
	rasterName = allYears.replace(".tif","_full.tif")
	print rasterName
	# Save the raster
	allYearsFull.save(reclassPath+"/"+rasterName)
	print "Done with folder " + str(folder) + "..."






############################################################
# Make a final reclassification of the summary final raster "AllYears_full"
############################################################
# continue remapping the reclassification of the final map. LAst step to be able to deliver DRC >


env.workspace=reclassPath
outDescription="_AY_final"
# make a list of Comb rasters
allYears=arcpy.ListRasters("*AllYears_full*")
for raster in allYears:
	print raster
	reclassField = "Value"
	remap= RemapRange([
	[1,1,1], # Water
	[0,0,2], # Not forest or rural complex
	[2,2,0], # Nodata
	[10,10, 8], # Perforated forest 2010
	[20,20, 6], # Perforated forest 2000
	[30,30,6], # Perforated forest 2000
	[60,60,7], # Perforated forest 2005
	[80,80,6], # Perforated forest 2000
	[100,100, 9],
	[200, 200, 10],
	[300,300, 11],
	[400,400,12],
	[101,101,1], # water 
	[201,201,1], # water 
	[301,301,1], # water
	[401,401,1], # water 
	[2000,2000,3], # only one pixel of this also, made it go to RC 2000
	[2100, 2180, 5],
	[4600, 4680, 4],
	[6600,6680,3],
	[7000,7070,],
	[],
	])

	finalReclass=Reclassify(raster,reclassField, remap)
	rasterName = raster.replace("AllYears_full.tif", outDescription+".tif")
	print rasterName

	# Save the raster
	finalReclass.save(reclassPath+"/"+rasterName)
	print "Done with folder " + str(folder) + "..."


# End
arcpy.env.snapRaster = tempEnvironment0
print "....................................."
print "..........End of the script.........."
print "....................................."