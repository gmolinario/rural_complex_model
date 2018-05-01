#####################################################################################
# Script to run all processing and analysis for PhD paper 1 - spatial patterns of SC
#   Giuseppe Molinario
#   09/17/2014
#   07/05/2014 update to extend to 2014
#   04/2018 - rerunning to include 2015. 
#
#   This script runs the following scripts:
#   - Create directory structure
#   1. Build input mask
#   2. Delete Non-Forest (NF) and Woodland (WD) outside of AOI 
#   3. Build mask  (- again - but hybrid with GFC. Is this redundant and was developed for v17 but never fixed? If so, DONT RUN!)
#   4. Run the LFT code
#   5. Core forest re-grouping code
#   6. Re-add core forest to LFT, make final Forest Fragmentation Maps.
#   7. Rural Complex Footprint map build
#   8. Intersect GFC and FACET loss with FF and RCF
#   9. Generate report tables by units of area (admin, pa, landscapes)
#   10. Generate maps and animated gifs for illustrations
#   11. **To do** Load tables in R, generate final tables and graphs (modify R scripts from PFL/SFL ratio analysis)
#
######################################################################################

# Import
import arcpy
import os
from arcpy.sa import *
import shutil


version="19"
# version 19 = DRC through 2015
# version 20 = ROC through 2015 



##################################################
# 1. Create and prepare root folder for run
##################################################

# Create root folder
rootFolder=version+"th_run"
# path
root=r"C:\Data_Molinario\temp\LFT_local"
# path with folder
rootFolderPath = root+"/"+rootFolder
# Create the folder if it doesn't exist
if not os.path.exists(rootFolderPath):
    os.makedirs(rootFolderPath)
    print "Created "+rootFolderPath+" folder."

# Copy over water and nodata folder from previous version, which does not change. 

# Source folder for Water and Nodata
# Change if you are running on a brand new map (aka ROC)
src=root+"/"+str(int(version)-1)+"th_run"+"/"+r"Rural_complex_v5\WaterAndNodata"
# Destination folder
dst=rootFolderPath+"/"+r"Rural_complex_v5\WaterAndNodata"
if not os.path.exists(dst):
    shutil.copytree(src, dst)
    print "Copied over the water and noData folder."
else:
    print "Water and noData folder already exists in: "+dst



##################################################
# 1. Run the LFT master mask creation
#
#   - Run it for 2000 only, if working with GFC loss hybrid masks (2018)
##################################################

# Location of build mask script 
buildMaster = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\arcpyBuildInputMaskForLFT_v2.py")
print "python "+buildMaster
handle = os.system("python "+buildMaster)

print "Version: "+version+". Master mask input for LFT has been created."


################################################################
# 2. Run the script to delete the NF and WD from outside the AOI
################################################################

# Location of the script
cleanMaster = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\arcpyCleanMasterForLFTpostAOI.py")
print "python "+buildMaster
handle = os.system("python "+cleanMaster)

print "Version: "+version+". The master mask input for LFT has been cleaned so there is only SF/SFL/WDL outside AOI."



################################################################################
# 3. Create the hybrid FACET/GFC masks
# 4/2018 - question - is this necessary or redundant? Does this only create v17? 
# v16 07/2016
# same as v18,19,20 (v17 used hybrid gfc/facet input masks at 30m and had too much noise)
# 
#################################################################################


# Location of the script to create the v16 folder structure and Master masks for LFT 
hybridMasters = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\LFT\\arcpyBuildHybridFacetGFCInputMasksForLFT_v1.py")


print "python "+hybridMasters
handle = os.system("python "+hybridMasters)

print "Version: "+version+". New hybrid Master masks have been created and put into folder structure."




##################################################
# 4. Run the batch LFT 
##################################################

#   also runs LFT_SA_gm_test_more_core_clss.py

# Location of the batch LFT script 
lftBatch = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\LFT\\batchTiledLFT_v5.py")


print "python "+lftBatch
handle = os.system("python "+lftBatch)

print "Version: "+version+". LFT script has been run."



###############################################################
# 5. Run the core forest grouping - this reruns core forest grouping so that
#         small rivers, or small fragmenting elements, do not result in fragmented forest. 
###############################################################

# Location of script 
coreScript = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\arcpyGroupCoreForestThresholds.py")

print "python "+ coreScript
handle = os.system("python "+coreScript)

print "Version: "+version+". Core classification has been run."



##################################################################
# 6. Run the script to add core forest back into the LFT results, 
#       making the final forest fragmentation maps
################################################################

# Location of script 
addCoreToLftScript = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\arcpyAddCorrectCoreToLFT.py")

print "python "+ addCoreToLftScript
handle = os.system("python "+addCoreToLftScript)

print "Version: "+version+". Core classification has been added to LFT "



################################################
# 7. Run rural complex script
################################################

# Location of script 
ruralComplexScript = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\arcpyCreateRuralComplex_v2.py")

print "python "+ ruralComplexScript
handle = os.system("python "+ruralComplexScript)

print "Version: "+version+". Rural complex classification has been created."


#####################################################################
# 8. Run the intersection of FACET and GFC loss with LFT and RC maps.
#####################################################################

# Location of script 
lossIntersectionScript = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\arcpyIntersectLFTandGFC_v3.py")

print "python "+ lossIntersectionScript
handle = os.system("python "+lossIntersectionScript)

print "Version: "+version+". Loss intersection with FF and RCF classification has been created."


###################################################################
##### Check maps before running tabulation and reporting of results 
###################################################################

# Set code to run or not
#tabulation = "yes"
tabulation= "yes"

#maps="yes"
maps="no"

#########################################################################
# 9. Run the reporting GFC loss and PFL loss by LFT and RC on admin units
################################################################# #######

# Location of script 
reportScript = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\arcpyReportRasters.py")
if "yes" in tabulation:
    print "python "+ reportScript
    handle = os.system("python "+reportScript)
    print "Version: "+version+". All report tables by units of area have been created."
else:
    print "Skipping run tabulation of results."

#################################################################
# 10. Run automatic generation of maps and animated gifs
#################################################################

# Location of script 
createMapsGifsScript = ("C:\\Data_Molinario\\Dropbox\\PhD\\Scripts\\arcpyMappingLayerSwitch.py")

if "yes" in maps:
    print "python "+ createMapsGifsScript
    handle = os.system("python "+createMapsGifsScript)
    print "Version: "+version+". All map illustrations and animated gifs have been created."
else:
    print "Skipping run creation of maps and gifs."


#################################################################
# 11. Run R to load tables, manipulate them, make figures
#################################################################

'''


# To do 


# End script 

