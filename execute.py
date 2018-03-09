'''
This software is licensed under a Beerware license. 
/*
 * ----------------------------------------------------------------------------
 * "THE BEER-WARE LICENSE" (Revision 42):
 * <debasishm89@gmail.com> wrote this file. As long as you retain this notice you
 * can do whatever you want with this stuff. If we meet some day, and you think
 * this stuff is worth it, you can buy me a beer in return Debasish Mandal.
 * ----------------------------------------------------------------------------
 */
'''



import os
import array
from os.path import join
from ctypes import *
from win32com.client import Dispatch
from win32api import GetFileVersionInfo
import csv
from MassDiffer import *
import thread
from time import sleep

all_packages  = ['VMware-workstation-full-12.1.1.exe',
					'VMware-workstation-full-12.5.0.exe',
					'VMware-workstation-full-12.5.1.exe',
					'VMware-workstation-full-12.5.2.exe',
					'VMware-workstation-full-12.5.3.exe',
					'VMware-workstation-full-12.5.4.exe',
					'VMware-workstation-full-12.5.5.exe',
					'VMware-workstation-full-12.5.6.exe']
					
def getFileDescription(windows_exe):
	try:
		language, codepage = GetFileVersionInfo(windows_exe, '\\VarFileInfo\\Translation')[0]
		stringFileInfo = u'\\StringFileInfo\\%04X%04X\\%s' % (language, codepage, "FileDescription")
		description = GetFileVersionInfo(windows_exe, stringFileInfo)
	except:
		description = "unknown"
	return description
def get_file_info(path):
	ver_parser = Dispatch('Scripting.FileSystemObject')
	info = ver_parser.GetFileVersion(path)
	#print ver_parser.GetProduct(path)
	if info == 'No Version Information Available':
		info = None
	return info
def isPE(file):
	hnd = open(file,"rb")
	if hnd.read(2) == "MZ":
		return True
	else:
		return False
def FindAllFilesBINFileInPackage(pack_name):
	print '[+] Finding Package Content for ',pack_name
	basefilelist = {}
	bases = list()
	for (dirpath, dirname, filenames) in os.walk(pack_name):
		for name in filenames:
			a, b = os.path.splitext(join(dirpath,name))
			bases.append((a, b))
	for i in bases:
		if isPE(i[0]+i[1]):
			full = i[0]+i[1]
			basefilelist[full.replace(pack_name+'\\','')] = get_file_info(i[0]+i[1])
		else:
			pass
	return basefilelist
def ErrorLog(string):
	f = open('error.log','a')
	f.write(string+'\n\n')
	f.close()
def openLog(fname):
	f = open(fname, "wb")
	c = csv.writer(f)
	c.writerow(["Diff_MAP","OldBinName","NewBinName","Old File Version","New File Version","Modified","Company", "ChangedFunctionAddress"])
	f.close()
def addToLog(f_name,data):
	f = open(f_name, "ab")
	c = csv.writer(f)
	c.writerow(data)
	f.close()
def IDBJobThread(old_pack,new_pack,new,old,file,log_name):
	#print '[+] Operating on',file	
	fresh_list = []		
    
	diff_name  =  old_pack+'=>'+new_pack	
	vm_ver_old = old_pack
	vm_ver_new = new_pack
	new_abs_path = new_pack+'\\'+file
	old_abs_path = old_pack+'\\'+file
	new_file_ver = new[file]
	old_file_ver = old[file]
	description = repr(getFileDescription(new_abs_path)).lower()				
					
	if new[file] != old[file]:
		modified = 'Yes'	
	else:				
		modified = 'No'		
	if modified == 'Yes' and new_file_ver != old_file_ver and 'vmware' in description and 'VMware Workstation\\' in new_abs_path and 'vmware-vmx-debug.exe' not in new_abs_path and 'vmware-vmx-stats.exe' not in new_abs_path:	
		print '[+] Operating on',file
		fresh_list.append(diff_name)
		fresh_list.append(old_abs_path)
		fresh_list.append(new_abs_path)
		fresh_list.append(new_file_ver)
		fresh_list.append(old_file_ver)
		fresh_list.append(modified)
		fresh_list.append(description)
		# Try to get the diffing info.
		try:
			primary_BinExport = GenerateBinExport(old_abs_path)	
			secondary_BinExport = GenerateBinExport(new_abs_path)	
						
			Bindiff_file = GenerateBINDIFF(primary_BinExport,secondary_BinExport)	
			changed_funk = ParseBinDiff(Bindiff_file)	
		
			os.remove(primary_BinExport)		# We only remove the old binexport file since it will not be required later 	
			#os.remove(secondary_BinExport)		# We keep the secondary binary ; since it will be requried as primary later.	
			os.remove(Bindiff_file)
			fresh_list.append(changed_funk)		# No Error Hence we are writing all changed function addresses..
		except Exception as e:
			fresh_list.append(str(e))			# Write the error in CSV file.
		addToLog(log_name,fresh_list)	
	else:	
		pass
	return True
if __name__ == "__main__":
	for i in range(0,len(all_packages)):
		old_pack = all_packages[i]
		new_pack = all_packages[i+1]
		fname = old_pack+'-'+new_pack+'.csv'
		openLog(fname)
		print '*'*50
		print '[+] Old Workstation Version :',old_pack	
		print '[+] New Workstation Version :',new_pack
		print '*'*50
		new = FindAllFilesBINFileInPackage(new_pack)	
		old = FindAllFilesBINFileInPackage(old_pack)			
		for file in new:
			if file in old:
				IDBJobThread(old_pack,new_pack,new,old,file,fname)
				#thread.start_new_thread(IDBJobThread, (old_pack,new_pack,new,old,file,fname,))
				#sleep(1)
			else:
				pass