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

import array
from ctypes import *
import os
from os.path import join
from subprocess import check_output

import struct
import sqlite3

ida_32 = r'"C:\Program Files (x86)\IDA 6.95\idaq.exe"'
ida_64 = r'"C:\Program Files (x86)\IDA 6.95\idaq64.exe"'
differ_32 = r'"C:\Program Files (x86)\zynamics\BinDiff 4.2\bin\differ.exe"'
differ_64 = r'"C:\Program Files (x86)\zynamics\BinDiff 4.2\bin\differ64.exe"'
def ParseBinDiff(db_file):
	#print '[+] Parsing Bindiff file ',db_file
	conn = sqlite3.connect(db_file)
	c = conn.cursor()
	result = c.execute("SELECT address1, address2, similarity FROM function WHERE  similarity != '1'")
	buff = ''
	for row in result:
		if row[0] == row[1]:
			buff += hex(row[0]) + '|'
		else:
			buff += hex(row[0])+ '>' +hex(row[1]) + '|'
	return buff
def CheckARC(filepath):
	IMAGE_FILE_MACHINE_I386=332
	IMAGE_FILE_MACHINE_IA64=512
	IMAGE_FILE_MACHINE_AMD64=34404
	f=open(filepath, "rb")
	s=f.read(2)
	if s!="MZ":
		print "Not an EXE file"
	else:
		f.seek(60)
		s=f.read(4)
		header_offset=struct.unpack("<L", s)[0]
		f.seek(header_offset+4)
		s=f.read(2)
		machine=struct.unpack("<H", s)[0]
		if machine==IMAGE_FILE_MACHINE_I386:
			return "32"
		else:
			return "64"
	f.close()
def GenerateBINDIFF(primary_BinExport,secondary_BinExport):
	#print '[+] Generating BINDIFF file for ',primary_BinExport,secondary_BinExport
	op_bindiff_file_name = '.'.join(primary_BinExport.split('\\')[-1].split('.')[:-1]) + '_vs_' + '.'.join(secondary_BinExport.split('\\')[-1].split('.')[:-1]) + '.BinDiff'
	try:
		cmd = differ_32+' --primary="' + primary_BinExport +'" --secondary="' +secondary_BinExport +'" --output_dir="'+ os.getcwd() +'\\BinExpoTemp"'
		check_output(cmd,shell=True)
	except Exception as e:
		cmd = differ_64+' --primary="' + primary_BinExport +'" --secondary="' +secondary_BinExport +'" --output_dir="'+ os.getcwd() +'\\BinExpoTemp"'
		check_output(cmd,shell=True)
	
	bindiff_file = 'BinExpoTemp\\'+op_bindiff_file_name
	return bindiff_file
def GenerateBinExport(bin):
	#Accepts binary path
	if CheckARC(bin) == "32":
		my_ida_path = ida_32
	if CheckARC(bin) == "64":
		my_ida_path = ida_64

	unpack_path = '\\'.join(bin.split('\\')[:-1])
	file_name = bin.split('\\')[-1]+'.BinExport'	
	cwd = os.getcwd()
	
	if CheckARC(bin) == "32":
		my_ida_path = ida_32
		op_idb_path = unpack_path+'\\'+'.'.join(file_name.split('.')[:-2])+'.idb'
		new_idb_path = unpack_path+'\\'+bin.split('\\')[-1]+'.idb'
	if CheckARC(bin) == "64":
		my_ida_path = ida_64
		op_idb_path = unpack_path+'\\'+'.'.join(file_name.split('.')[:-2])+'.i64'
		new_idb_path = unpack_path+'\\'+bin.split('\\')[-1]+'.i64'
	
	bin_Expo_path = unpack_path + '\\' + file_name
	asm_path = unpack_path+'\\'+'.'.join(file_name.split('.')[:-2])+'.asm'
	# Generate IDB
	if not os.path.exists(new_idb_path):
		#print '[+] Generating idb file for ',bin
		cmd_old = my_ida_path + ' -c -B "'+  bin + "\""
		check_output(cmd_old,shell=True)
		try:
			os.rename(op_idb_path,new_idb_path)
			os.remove(asm_path)
		except:
			print '[+] Probably idb file was not generated.'
	
	# Generate BinExport
	if not os.path.exists(bin_Expo_path):
		#print '[+] Generating binexpo file for ',bin
		binexport_cmd = my_ida_path + ' -A "-OExporterModule:'+ cwd + '\\' +unpack_path+'\\' +file_name+'" "-S'+cwd+'\\bin_export.idc" "' + cwd + '\\' +new_idb_path +'"'	
		#print binexport_cmd
		check_output(binexport_cmd, shell=True)
	
	bin_exp_file = cwd + '\\' +unpack_path+'\\' +file_name
	return bin_exp_file		
if __name__ == "__main__":
	f = open(binlist)
	bins = f.readlines()
	f.close()
	prim = 'prim\\vmware-tray.exe'
	seco = 'seco\\vmware-tray.exe'
	#primary_BinExport = GenerateBinExport(prim)
	#secondary_BinExport = GenerateBinExport(seco)
	#print GenerateBINDIFF('prim\\vmware-tray.exe.BinExport','seco\\vmware-tray.exe.BinExport')
	#print ParseBinDiff('BinExpoTemp\\VMware-player-12.5.1.exe-vmware-vmx_vs_VMware-player-12.5.2.exe-vmware-vmx.BinDiff')