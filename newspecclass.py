import numpy as np
import get_param_idx 
import struct
import matplotlib.pyplot as plt
import os
import shutil
import sys
import fileinput
import platform
from datetime import datetime, date, time, timedelta
import time
import urllib2
import pickle
import copy
import pyximport; pyximport.install()
import ifgtoolsc


from sys import platform as _platform
global operatingsystem
operatingsystem=_platform

class spec:

	def __init__(self, fname):
		self.filename = fname
		self.name = os.path.basename(fname)
		   
		f=open(self.filename,'rb')
		f.seek(0)
		field1=np.fromfile(f,dtype='int32',count=1)
		field2=np.fromfile(f,dtype='float64',count=1)
		self.opusversion=field2[0]
		field3=np.fromfile(f,dtype='int32',count=1)
		ipdir=field3[0]
		self.ipdir=ipdir
		field4=np.fromfile(f,dtype='int32',count=1)
		mnbl=field4[0]
		self.mnbl=mnbl
		field5=np.fromfile(f,dtype='int32',count=1)
		nbl=field5[0]
		self.nbl=nbl
		
		blocktyparr=[]
		blocklenarr=[]
		blockpntarr=[]
		for i in range(nbl):
		    field6=np.fromfile(f,dtype='int32',count=1)
		    blocktyparr.append(field6[0])
		    field7=np.fromfile(f,dtype='int32',count=1)
		    blocklenarr.append(field7[0])
		    field8=np.fromfile(f,dtype='uint32',count=1)
		    blockpntarr.append(field8[0])
		f.close()
		self.blocktyparr=blocktyparr
		self.blocklenarr=blocklenarr
		self.blockpntarr=blockpntarr
		
		self.readdir()

	def readdir(self):
		blockidarr=[]
		f=open(self.filename,'rb')

		for idx in range(self.nbl):
		    flag='DBL'
		    ipoint=self.blockpntarr[idx]
		    nbits=self.blocklenarr[idx]*4
		    f.seek(ipoint)
		    data=f.read(nbits)
		    if idx==0: flag='DIR'
		    if data[0:3] == 'APT': flag= 'OPT'
		    if data[0:3] == 'APF': flag= 'FFT'
		    if data[0:3] == 'AQM': flag= 'ACQ'
		    if data[0:3] == 'BLD': flag= 'OPU'
		    if data[0:3] == 'DPF': flag= 'DBS'
		    if data[0:3] == 'HFL': flag= 'INS'
		    blockidarr.append(flag)

		index1=blockidarr.index('DBS')
		xunit= get_param_idx.get_param_idx(f,index1,'DXU')
		if xunit == 'PN':     
		    blockidarr[index1]= blockidarr[index1]+'_ifg'
		    index1=blockidarr.index('DBL')
		    blockidarr[index1]= blockidarr[index1]+'_ifg'
		
		try:
		    index1=blockidarr.index('DBS')
		except ValueError:
		    print 'EXCEPTION #1 readdir()'
		    
		xunit= get_param_idx.get_param_idx(f,index1,'DXU')
		if xunit == 'PN':
		    self.doublesided='true'
		    blockidarr[index1]= blockidarr[index1]+'_ifg2'
		           
		try:
		    index1=blockidarr.index('DBS')
		except ValueError:
		    print 'EXCEPTION #2 readdir()'
		    
		xunit= get_param_idx.get_param_idx(f,index1,'DXU')
		if xunit == 'PN':
		    self.doublesided='true'
		    blockidarr[index1]= blockidarr[index1]+'_ifg2'
                          
		try:
		    index1=blockidarr.index('DBS')
		    xunit= get_param_idx.get_param_idx(f,index1,'DXU')
		    if xunit == 'WN':
		        blockidarr[index1]= blockidarr[index1]+'_spc2'
		    else:
		        blockidarr[index1]= blockidarr[index1]+'_dbs'
		except ValueError:
		    print 'EXCEPTION #3 readdir()'

		try:
		    index1=blockidarr.index('DBS')
		    xunit= get_param_idx.get_param_idx(f,index1,'DXU')
		    if xunit == 'WN':
		        blockidarr[index1]= blockidarr[index1]+'_spc'
		    else:
		        if xunit == 'PN':
		            print xunit
		        else:
		            blockidarr[index1]= blockidarr[index1]+'_dbs'
		except ValueError:
		    print 'EXCEPTION #4 readdir()'

		try:
		    index1=blockidarr.index('DBS_spc2')
		    blockidarr[index1]= 'DBS_spc'
		except ValueError:
		    print 'EXCEPTION #5 readdir()'

		f.close 
		self.blockidarr=blockidarr

	def readOPT(self):
		idx=self.blockidarr.index('OPT')
		ipoint=self.blockpntarr[idx]
		f=open(self.filename,'rb')
		
		self.APT = get_param_idx.get_param_idx(f,idx,'APT')
		self.BMS = get_param_idx.get_param_idx(f,idx,'BMS')
		self.CHN = get_param_idx.get_param_idx(f,idx,'CHN')
		self.DTC = get_param_idx.get_param_idx(f,idx,'DTC')
		self.HPF = get_param_idx.get_param_idx(f,idx,'HPF')
		self.LPF = get_param_idx.get_param_idx(f,idx,'LPF')
		self.OPF = get_param_idx.get_param_idx(f,idx,'OPF')
		self.PGN = get_param_idx.get_param_idx(f,idx,'PGN')
		self.RCH = get_param_idx.get_param_idx(f,idx,'RCH')
		self.RDX = get_param_idx.get_param_idx(f,idx,'RDX')
		self.SRC = get_param_idx.get_param_idx(f,idx,'SRC')
		self.VEL = get_param_idx.get_param_idx(f,idx,'VEL')
		self.SON = get_param_idx.get_param_idx(f,idx,'SON')
	
		if self.station == 'ALTZ':
			try:
				nfilter=int(self.OPF.split()[1])
			except:
				nfilter=8
		if self.station == 'CCA':
			try:
				nfilter=int(self.OPF.split()[1])
			except:
				try:
					if self.OPF.split()[1] == 'NG11':
						nfilter = 3
				except:
					if self.DTC[0:9] == 'TE-InGaAs':
						nfilter = 8
					else:
						nfilter = 9
		filternamearr=['---','A','B','C','D','E','F','G','N','O']
		self.filter=filternamearr[nfilter]
		self.readACQ()

		f.close()
        
	def readFFT(self):
		idx=self.blockidarr.index('FFT')
		ipoint=self.blockpntarr[idx]
		f=open(self.filename,'rb')

		self.APF = get_param_idx.get_param_idx(f,idx,'APF')
		self.HFQ = get_param_idx.get_param_idx(f,idx,'HFQ')
		self.LFQ = get_param_idx.get_param_idx(f,idx,'LFQ')
		self.NLI = get_param_idx.get_param_idx(f,idx,'NLI')
		self.PHR = get_param_idx.get_param_idx(f,idx,'PHR')
		self.PHZ = get_param_idx.get_param_idx(f,idx,'PHZ')
		self.SPZ = get_param_idx.get_param_idx(f,idx,'SPZ')
		self.ZFF = get_param_idx.get_param_idx(f,idx,'ZFF')
		f.close()
        
	def readACQ(self):
		idx=self.blockidarr.index('ACQ')
		ipoint=self.blockpntarr[idx]
		f=open(self.filename,'rb')

		self.AQM = get_param_idx.get_param_idx(f,idx,'AQM')
		self.COR = get_param_idx.get_param_idx(f,idx,'COR')
		self.DEL = get_param_idx.get_param_idx(f,idx,'DEL')
		self.DLY = get_param_idx.get_param_idx(f,idx,'DLY')
		self.HFW = get_param_idx.get_param_idx(f,idx,'HFW')
		self.LFW = get_param_idx.get_param_idx(f,idx,'LFW')
		self.NSS = get_param_idx.get_param_idx(f,idx,'NSS')
		self.PLF = get_param_idx.get_param_idx(f,idx,'PLF')
		self.RES = get_param_idx.get_param_idx(f,idx,'RES')
		self.OPD= 0.9/float(self.RES)   
		self.RGN = get_param_idx.get_param_idx(f,idx,'RGN')
		self.TDL = get_param_idx.get_param_idx(f,idx,'TDL')
		self.SGN = get_param_idx.get_param_idx(f,idx,'SGN')
		self.SG2 = get_param_idx.get_param_idx(f,idx,'SG2')
		self.RG2 = get_param_idx.get_param_idx(f,idx,'RG2')
		if (self.station == 'ALTZ') & (self.OPF != 'Open'):
			if self.OPD == 9.0:
				self.spc_type = 'V'
			else:
				self.spc_type = 'S'
		if (self.station == 'CCA'):
			self.spc_type = 'S'

	        f.close()

	def readOPU(self):
		idx=self.blockidarr.index('OPU')
		ipoint=self.blockpntarr[idx]
		f=open(self.filename,'rb')

		self.BLD = get_param_idx.get_param_idx(f,idx,'BLD')
		self.CPY = get_param_idx.get_param_idx(f,idx,'CPY')
		self.DPM = get_param_idx.get_param_idx(f,idx,'DPM')
		self.EXP = get_param_idx.get_param_idx(f,idx,'EXP')
		self.LCT = get_param_idx.get_param_idx(f,idx,'LCT')
		self.SFM = get_param_idx.get_param_idx(f,idx,'SFM')
		self.SNM = get_param_idx.get_param_idx(f,idx,'SNM')
		self.XPP = get_param_idx.get_param_idx(f,idx,'XPP')
		self.IST = get_param_idx.get_param_idx(f,idx,'IST')
        
	        f.close()
        
	def readINS(self):
		self.readOPT()
		idx=self.blockidarr.index('INS')
		ipoint=self.blockpntarr[idx]
		f=open(self.filename,'rb')
		f.seek(ipoint)

		self.HFL = get_param_idx.get_param_idx(f,idx,'HFL')
		self.LFL = get_param_idx.get_param_idx(f,idx,'LFL')
		self.LWN = get_param_idx.get_param_idx(f,idx,'LWN')
		self.ABP = get_param_idx.get_param_idx(f,idx,'ABP')
		self.SSP = get_param_idx.get_param_idx(f,idx,'SSP')
		self.ASG = get_param_idx.get_param_idx(f,idx,'ASG')
		self.ARG = get_param_idx.get_param_idx(f,idx,'ARG')
		self.ASS = get_param_idx.get_param_idx(f,idx,'ASS')
		self.GFW = get_param_idx.get_param_idx(f,idx,'GFW')
		self.GBW = get_param_idx.get_param_idx(f,idx,'GBW')
		self.BFW = get_param_idx.get_param_idx(f,idx,'BFW')
		self.BBW = get_param_idx.get_param_idx(f,idx,'BBW')
		self.PKA = get_param_idx.get_param_idx(f,idx,'PKA')
		self.PKL = get_param_idx.get_param_idx(f,idx,'PKL')
		self.PRA = get_param_idx.get_param_idx(f,idx,'PRA')
		self.PRL = get_param_idx.get_param_idx(f,idx,'PRL')
		self.P2A = get_param_idx.get_param_idx(f,idx,'P2A')
		self.P2L = get_param_idx.get_param_idx(f,idx,'P2L')
		self.P2R = get_param_idx.get_param_idx(f,idx,'P2R')
		self.P2K = get_param_idx.get_param_idx(f,idx,'P2K')
		self.DAQ = get_param_idx.get_param_idx(f,idx,'DAQ')
		self.AG2 = get_param_idx.get_param_idx(f,idx,'AG2')
		self.HUM = get_param_idx.get_param_idx(f,idx,'HUM')
		self.SSM = get_param_idx.get_param_idx(f,idx,'SSM')
		self.RSN = get_param_idx.get_param_idx(f,idx,'RSN')
		self.SRT = get_param_idx.get_param_idx(f,idx,'SRT')
		self.DUR = get_param_idx.get_param_idx(f,idx,'DUR')
		self.TSC = get_param_idx.get_param_idx(f,idx,'TSC')
		self.MVD = get_param_idx.get_param_idx(f,idx,'MVD')
		self.AN1 = get_param_idx.get_param_idx(f,idx,'AN1')
		self.AN2 = get_param_idx.get_param_idx(f,idx,'AN2')
		#self.VSN = get_param_idx.get_param_idx(f,idx,'VSN')
		self.SRN = get_param_idx.get_param_idx(f,idx,'SRN')
		self.INS = get_param_idx.get_param_idx(f,idx,'INS')
		self.FOC = get_param_idx.get_param_idx(f,idx,'FOC')
		self.FOV=float(self.APT.split()[0])/float(self.FOC)
		self.SEMIFOV=self.FOV/2.0
		self.RDY = get_param_idx.get_param_idx(f,idx,'RDY')
		self.ARS = get_param_idx.get_param_idx(f,idx,'ARS')

	        f.close()

	def readspec(self):
		idx=self.blockidarr.index('DBS_spc')
		ipoint=self.blockpntarr[idx]
		f=open(self.filename,'rb')

		self.spc_DPF = get_param_idx.get_param_idx(f,idx,'DPF')
		self.spc_NPT = get_param_idx.get_param_idx(f,idx,'NPT')
		self.spc_NSN = get_param_idx.get_param_idx(f,idx,'NSN')
		self.spc_TPX = get_param_idx.get_param_idx(f,idx,'TPX')
		self.spc_FXV = get_param_idx.get_param_idx(f,idx,'FXV')		### FIRST
		self.spc_LXV = get_param_idx.get_param_idx(f,idx,'LXV')		### LAST
		self.spc_CSF = get_param_idx.get_param_idx(f,idx,'CSF')
		self.spc_MXY = get_param_idx.get_param_idx(f,idx,'MXY')
		self.spc_MNY = get_param_idx.get_param_idx(f,idx,'MNY')
		self.spc_DXU = get_param_idx.get_param_idx(f,idx,'DXU')
		self.spc_DAT = get_param_idx.get_param_idx(f,idx,'DAT')
		self.spc_TIM = get_param_idx.get_param_idx(f,idx,'TIM')
		print 'FIRST AND LAST: %.1f-%.1f' % (self.spc_FXV,self.spc_LXV)
		dummy_v = self.spc_FXV
		self.ud_flag = 0
		if self.spc_FXV > self.spc_LXV:
			self.spc_FXV = self.spc_LXV
			self.spc_LXV = dummy_v
			self.ud_flag = 1
		print 'FIRST AND LAST: %.1f-%.1f' % (self.spc_FXV,self.spc_LXV)
	        f.close()
        
	def readspec2(self):
		idx=self.blockidarr.index('DBS_spc2')
		ipoint=self.blockpntarr[idx]
		f=open(self.filename,'rb')

		self.spc2_DPF = get_param_idx.get_param_idx(f,idx,'DPF')
		self.spc2_NPT = get_param_idx.get_param_idx(f,idx,'NPT')
		self.spc2_NSN = get_param_idx.get_param_idx(f,idx,'NSN')
		self.spc2_TPX = get_param_idx.get_param_idx(f,idx,'TPX')
		self.spc2_FXV = get_param_idx.get_param_idx(f,idx,'FXV')
		self.spc2_LXV = get_param_idx.get_param_idx(f,idx,'LXV')
		self.spc2_CSF = get_param_idx.get_param_idx(f,idx,'CSF')
		self.spc2_MXY = get_param_idx.get_param_idx(f,idx,'MXY')
		self.spc2_MNY = get_param_idx.get_param_idx(f,idx,'MNY')
		self.spc2_DXU = get_param_idx.get_param_idx(f,idx,'DXU')
		self.spc2_DAT = get_param_idx.get_param_idx(f,idx,'DAT')
		self.spc2_TIM = get_param_idx.get_param_idx(f,idx,'TIM')
	
	        f.close()
       
	def readdbs(self):
		idx=self.blockidarr.index('DBS_dbs')
		ipoint=self.blockpntarr[idx]
		f=open(self.filename,'rb')

		self.dbs_DPF = get_param_idx.get_param_idx(f,idx,'DPF')
		self.dbs_NPT = get_param_idx.get_param_idx(f,idx,'NPT')
		self.dbs_NSN = get_param_idx.get_param_idx(f,idx,'NSN')
		self.dbs_TPX = get_param_idx.get_param_idx(f,idx,'TPX')
		self.dbs_FXV = get_param_idx.get_param_idx(f,idx,'FXV')
		self.dbs_LXV = get_param_idx.get_param_idx(f,idx,'LXV')
		self.dbs_CSF = get_param_idx.get_param_idx(f,idx,'CSF')
		self.dbs_MXY = get_param_idx.get_param_idx(f,idx,'MXY')
		self.dbs_MNY = get_param_idx.get_param_idx(f,idx,'MNY')
		self.dbs_DXU = get_param_idx.get_param_idx(f,idx,'DXU')
		self.dbs_DAT = get_param_idx.get_param_idx(f,idx,'DAT')
		self.dbs_TIM = get_param_idx.get_param_idx(f,idx,'TIM')

	        f.close()

	def readifg(self):
		idxdbl=self.blockidarr.index('DBL_ifg')
		idx=self.blockidarr.index('DBS_ifg')
	        ipoint=self.blockpntarr[idx]
	        f=open(self.filename,'rb')

		self.ifg_DPF = get_param_idx.get_param_idx(f,idx,'DPF')
		self.ifg_NPT = get_param_idx.get_param_idx(f,idx,'NPT')
		self.ifg_NSN = get_param_idx.get_param_idx(f,idx,'NSN')
		self.ifg_TPX = get_param_idx.get_param_idx(f,idx,'TPX')
		self.ifg_FXV = get_param_idx.get_param_idx(f,idx,'FXV')
		self.ifg_LXV = get_param_idx.get_param_idx(f,idx,'LXV')
		self.ifg_CSF = get_param_idx.get_param_idx(f,idx,'CSF')
		self.ifg_MXY = get_param_idx.get_param_idx(f,idx,'MXY')
		self.ifg_MNY = get_param_idx.get_param_idx(f,idx,'MNY')
		self.ifg_DXU = get_param_idx.get_param_idx(f,idx,'DXU')
		self.ifg_DAT = get_param_idx.get_param_idx(f,idx,'DAT')
		self.ifg_TIM = get_param_idx.get_param_idx(f,idx,'TIM')

	        f.close()

	def readifg2(self):
		idx=self.blockidarr.index('DBS_ifg2')
		ipoint=self.blockpntarr[idx]
		f=open(self.filename,'rb')

		self.ifg2_DPF = get_param_idx.get_param_idx(f,idx,'DPF')
		self.ifg2_NPT = get_param_idx.get_param_idx(f,idx,'NPT')
		self.ifg2_NSN = get_param_idx.get_param_idx(f,idx,'NSN')
		self.ifg2_TPX = get_param_idx.get_param_idx(f,idx,'TPX')
		self.ifg2_FXV = get_param_idx.get_param_idx(f,idx,'FXV')
		self.ifg2_LXV = get_param_idx.get_param_idx(f,idx,'LXV')
		self.ifg2_CSF = get_param_idx.get_param_idx(f,idx,'CSF')
		self.ifg2_MXY = get_param_idx.get_param_idx(f,idx,'MXY')
		self.ifg2_MNY = get_param_idx.get_param_idx(f,idx,'MNY')
		self.ifg2_DXU = get_param_idx.get_param_idx(f,idx,'DXU')
		self.ifg2_DAT = get_param_idx.get_param_idx(f,idx,'DAT')
		self.ifg2_TIM = get_param_idx.get_param_idx(f,idx,'TIM')

	        f.close()

	def getifg(self,station,write_flag=0):
		idx=self.blockidarr.index('DBL_ifg')
		ipoint=self.blockpntarr[idx]
		npts=self.blocklenarr[idx]
		f=open(self.filename,'rb')
		f.seek(ipoint)

	        #offset=np.fromfile(f,dtype='int32',count=10)
	        ifg=np.fromfile(f,dtype='float32',count=npts)
        
		xx=0
	        #for x in ifg[npts-20:npts]:
	        #    if np.abs(x) < 1.0E-30: 
	        #        xx=xx+1
	        ifg=ifg[0:npts-xx]
		ifgOPUS = copy.deepcopy(ifg)
		self.ifgOPUS = ifgOPUS
		ifg = np.multiply(ifg, self.ifg_CSF)
		ifg[np.size(ifg)/2:np.size(ifg)] = np.flipud(ifg[np.size(ifg)/2:np.size(ifg)])		### AGREGADO POR JORGE EL 12/01/2017
		self.ifg = ifg.astype(np.float64)
		if write_flag == 1:
			np.save(self.filename+"_specclass_ifg.npy",self.ifg)
			header = {}
			header['PHR'] = self.PHR
			header['GFW'] = self.GFW
			header['GBW'] = self.GBW
			header['HFL'] = self.HFL
			header['LFL'] = self.LFL
			header['AQM'] = self.AQM
			header['NSS'] = self.NSS
			with open(self.filename+"_specclass_header.pkl", 'wb') as f:
        			pickle.dump(header, f, pickle.HIGHEST_PROTOCOL)
	
	        f.close()
	
	def getspc(self,write_flag=0):
	        idx=self.blockidarr.index('DBL')
                ipoint=self.blockpntarr[idx]
		npts=self.blocklenarr[idx]
		while abs(npts-self.spc_NPT) > 2:
			self.blockidarr[idx] = 'DBL_X'
			idx=self.blockidarr.index('DBL')
			ipoint=self.blockpntarr[idx]
			npts=self.blocklenarr[idx]
		f=open(self.filename,'rb')
		f.seek(ipoint)
		self.spc_org=np.fromfile(f,dtype='float32',count=npts)
		if self.ud_flag == 1:
			self.spc_org = np.flipud(self.spc_org)
		f.close()
		if write_flag == 1:
			dnpt=len(self.spc_org)-self.spc_NPT
			spc_str = np.empty(len(self.spc_org),dtype=[('spc',float),('w',float)])
			spc_str['w'] = np.arange(self.spc_NPT+dnpt)*(self.spc_LXV-self.spc_FXV)/(self.spc_NPT+dnpt)+self.spc_FXV
			spc_str['spc'] = self.spc_org
			np.save(self.filename+"_specclass_spcorg.npy",spc_str)
		
	def w(self):
		w=np.arange(self.spc_NPT+self.dnpt)*(self.spc_LXV-self.spc_FXV)/(self.spc_NPT+self.dnpt)+self.spc_FXV
		self.wavenumber=w
		self.spc_dw=np.abs(w[1]-w[0])
		return w

	def control(self,station):
		self.readdir()
		self.readFFT()
		self.readspec()
		self.getspc()
		self.dnpt=len(self.spc_org)-self.spc_NPT
		self.readifg()
		self.getifg(station)
		w=self.w()
		self.corrigeSF()

		SNR_limit=0.0
		RNL_limit=0.0

		if station == 'ALTZ':
		# filter A
		#########################################
			if self.filter == 'A':
				SNR_limit=50.0
				cloud_limit=0.2
				RNL_limit=0.01  
				rango=[4029,4032]  
				w_line_base_chico=3500
				w_line_base_grande=3600
				w_max_chico=4200
				w_max_grande=4300             
		# filter B
		#########################################
			if self.filter == 'B':
				SNR_limit=50.0
				cloud_limit=0.2
				RNL_limit=0.01    
				rango=[2925,2930]
				w_line_base_chico=2100	#2200
				w_line_base_grande=2400  
				w_max_chico=3100
				w_max_grande=3300
		# filter C
		#########################################
			if self.filter == 'C':
				SNR_limit=50.0
				cloud_limit=0.2
				RNL_limit=0.01
				rango=[2925,2930]
				w_line_base_chico=2100	#2200
				w_line_base_grande=2300
				w_max_chico=2600
				w_max_grande=2700
		# filter D
		#########################################
			if self.filter == 'D':
				SNR_limit=50.0
				cloud_limit=0.2
				RNL_limit=0.01
				rango=[2480,2482] 
				w_line_base_chico=2275
				w_line_base_grande=2375
				w_max_chico=2100
				w_max_grande=2200
		# filter E
		#########################################
			if self.filter == 'E':
				SNR_limit=50.0
				cloud_limit=0.2
				RNL_limit=0.010
				rango=[1898,1902]
				w_line_base_chico=2275
				w_line_base_grande=2375
				w_max_chico=2100
				w_max_grande=2200 
		 # filter F
		#########################################
			if self.filter == 'F':
				SNR_limit=50.0
				cloud_limit=0.2
				RNL_limit=0.01
				rango=[779.5,780.4]
				w_line_base_chico=1400
				w_line_base_grande=1475
				w_max_chico=1125
				w_max_grande=1200  
		 # filter G
		#########################################
			if self.filter == 'G':
				SNR_limit=50.0
				cloud_limit=0.2
				RNL_limit=0.01
				rango=[4830,4850]
				w_line_base_chico=4000
				w_line_base_grande=4125
				w_max_chico=4675
				w_max_grande=4800 
		 # InGaAs
		#########################################
			if self.filter == 'N':
				SNR_limit=50.0
				cloud_limit=0.2
				RNL_limit=0.01  
				rango=[6200,6280]
				w_line_base_chico=3800
				w_line_base_grande=3900	#4000
				w_max_chico=4500
				w_max_grande=4700
				if self.spc_FXV > 3800:
					print 'CASO B'
					w_line_base_chico=5300
					w_line_base_grande=5400	#4000
					w_max_chico=5900
					w_max_grande=6100

		if station == 'CCA':
			cloud_limit = 0.2		### PARA QUE NUNCA SALGA EL QUALITY FLAG "CLOUDY"		
		# filter C
		#########################################
			if self.filter == 'C':
				SNR_limit=50.0
				RNL_limit=0.01
				w_line_base_chico=2200
				w_line_base_grande=2300
				w_max_chico=2600
				w_max_grande=2700
		# filter D
		#########################################
			if self.filter == 'D':
				SNR_limit=50.0
				RNL_limit=0.01
				w_line_base_chico=2275
				w_line_base_grande=2375
				w_max_chico=2100
				w_max_grande=2200
		 # filter F
		#########################################
			if self.filter == 'F':
				SNR_limit=50.0
				RNL_limit=0.02
				w_line_base_chico=525
				w_line_base_grande=600
				w_max_chico=1125
				w_max_grande=1200  
		 # filter E
		#########################################
			if self.filter == 'E':
				SNR_limit=50.0
				RNL_limit=0.01
				w_line_base_chico=4000
				w_line_base_grande=4125
				w_max_chico=4675
				w_max_grande=4800 
		 # InGaAs
		#########################################
			if self.filter == 'N':
				SNR_limit=50.0
				RNL_limit=0.01  
				w_line_base_chico=3600
				w_line_base_grande=3800
				w_max_chico=5800
				w_max_grande=6000
				if self.spc_FXV > 3600:
					print 'CASO B'
					w_line_base_chico=5250
					w_line_base_grande=5450
					w_max_chico=5800
					w_max_grande=6000
					
		 # OPEN
		#########################################
			if self.filter == 'O':
				SNR_limit=50.0
				RNL_limit=0.01  
				w_line_base_chico=3600
				w_line_base_grande=3800
				w_max_chico=5900
				if self.spc_LXV > 6000.0:
					w_max_grande=6100
				else:
					w_max_grande=6000
			SNR_limit=1.0		###	PARA NO FILTRAR EN CCA
			RNL_limit=1.0		###	PARA NO FILTRAR EN CCA

		print '----------------------------'

		def windex(wlow,wup,www):
			iindex=[]
			for i,j in enumerate(www):
				if j >= wlow and j <= wup:
					iindex.append(i)
			return iindex
		
		centerburst=np.int(2*0.9*self.HFL/self.PHR)
		if station == 'ALTZ':
			try:
				cloudindex=(np.max(self.ifgZPD[2*centerburst:self.ifg_NPT-2*centerburst])-np.min(self.ifgZPD[2*centerburst:self.ifg_NPT-2*centerburst]))/np.average(self.ifgZPD[2*centerburst:self.ifg_NPT-2*centerburst])

			except:
				cloudindex=(np.max(self.ifgOPUS[2*centerburst:self.ifg_NPT-2*centerburst])-np.min(self.ifgOPUS[2*centerburst:self.ifg_NPT-2*centerburst]))/np.average(self.ifgOPUS[2*centerburst:self.ifg_NPT-2*centerburst])
		else :
			cloudindex = 0.0

		#print 'LEN_W',len(w),'LEN_SPC',len(self.spc_org),'DNPT',self.spc_NPT
		signalindex=windex(w_max_chico,w_max_grande,w)
		try:
			signalregion=self.spc_corrSF[signalindex]
		except:
			try:
				signalregion=self.spc_DCcorr[signalindex]
			except:
				signalregion=self.spc_org[signalindex]

		baseindex=windex(w_line_base_chico,w_line_base_grande,w)
		try:
			baseregion=self.spc_corrSF[baseindex]
		except:
			try:
				baseregion=self.spc_DCcorr[baseindex]
			except:
				baseregion=self.spc_org[baseindex]
		wsignal=w[signalindex]
		wbase=w[baseindex]
		
		signal=np.average(signalregion)
		noise=np.std(baseregion)
		nonlinealidad=np.average(baseregion)
		SNR=signal/noise
		RNL=np.abs(nonlinealidad)/signal
		
		#print 'CLOUDINDEX',cloudindex,'LIMIT',cloud_limit
		#print 'SIGNAL TO NOISE',SNR,'LIMIT',SNR_limit
		#print 'NO LINEALIDAD',RNL,'LIMIT',RNL_limit 
		

		try:
			self.qflag
		except:			
			self.qflag=1
		
		if SNR < SNR_limit:
			try:
				self.comment=self.comment+', noisy'
			except:				
				self.comment='noisy'
			self.qflag=0
		if RNL > RNL_limit:
			try:
				self.comment=self.comment+', nonlinear'
			except:				
				self.comment='nonlinear'
			self.qflag=0
		if  cloudindex > cloud_limit:
			try:
				self.comment=self.comment+', cloudy'
			except:				
				self.comment='cloudy'
			self.qflag=0  
		
		try:
			self.comment
		except:
			self.comment='good'		


		print 'QUALITY FLAG', self.qflag
		print 'COMMENT', self.comment
		print '----------------------------'

		self.SNR=SNR
		self.RNL=RNL
		self.cloudindex=cloudindex
		self.SNR_limit=SNR_limit
		self.RNL_limit=RNL_limit
		self.cloud_limit=cloud_limit

	def protocolo(self,txtfile):
		self.readOPT()
		SGN=self.SGN[0]
		PGN=self.PGN[0]
                
        #line='echo "'+ os.path.basename(self.filename)+' '+self.ifg_TIM+' '+self.comment+' '+str(self.SNR)+' '+str(self.RNL)+' '
        #line=line+str(np.round(self.cloudindex,decimals=4)+' '+str(self.PGN)+' '+str(self.SGN)+' '
        #line=line+' '+str(self.APT)+' '+str(1/(0.9*self.RES))+' '+str(self.BMS)+' '   +'" >> '+txtfile
		line='echo "'+ os.path.basename(self.filename)+' '+str(self.corr_fechr.time())+' '+'(UTC-6)'+' '+self.comment+' '+str(np.round(self.SNR,decimals=2))+' '+str(np.round(self.RNL,decimals=6))+' '
		line=line+' '+str(PGN)+' '+str(SGN)+' '
		line=line+str(self.APT)+' '+str(np.round((0.9/self.RES),decimals=2))+' '+str(self.BMS)
		line=line+'" >> '+txtfile
		os.system(line)

	def get_ILS(self,station):
		if station=='ALTZ':
			if self.fecha<='131106':        	
				ilsfile='/home/jorge/OPUS/ILS/'+station+'/ilsparms_131106_AP1.dat'
			else:
				ilsfile='/home/jorge/OPUS/ILS/'+station+'/ilsparms_140112_AP1.dat'
		if station=='CCA':
			ilsfile='/home/D2_PROFFIT/OPUS/ILS/'+station+'/ilsparms.dat'
		try:
			self.ILS=np.genfromtxt(ilsfile)
			print 'ILS FILE FOUND'
		except:
		    	print 'NO ILS FILE'

	def time(self,station):
		self.station = station
		self.readINS()
		self.readifg()
		try:
			self.UTCzone = self.ifg_TIM.split(' ')[1].split('UTC')[1][0:2]
		except:
			self.UTCzone = self.ifg_TIM.split(' ')[1].split('GMT')[1][0:2]
		self.fechr = datetime.strptime(self.ifg_DAT+'-'+self.ifg_TIM.split('(')[0].strip(),'%d/%m/%Y-%H:%M:%S.%f')	###   FECHA Y HORA DE COMIENZO DE MEDICION

		self.year=self.fechr.year
		self.month=self.fechr.month
		self.day=self.fechr.day
		self.hour=self.fechr.hour
		self.minute=self.fechr.minute
		self.seconds=self.fechr.second
		self.microseconds=self.fechr.microsecond

		self.ut_fechr = self.fechr + timedelta(hours = -int(self.UTCzone)) + timedelta(seconds = +self.DUR/2.0)	###   SE PASA LA HORA A UT SUMANDO 6 HORAS Y SE CORRIGE SUMANDO LA MITAD DE LA DURACION DE LA MEDICION PARA EL CALCULO DE SZA
		self.ut_year=self.ut_fechr.year
		self.ut_month=self.ut_fechr.month
		self.ut_day=self.ut_fechr.day
		self.ut_hour=self.ut_fechr.hour
		self.ut_minute=self.ut_fechr.minute
		self.ut_seconds=self.ut_fechr.second
		self.ut_microseconds=self.ut_fechr.microsecond

		self.corr_fechr = self.fechr + timedelta(seconds = +self.DUR/2.0,hours = -int(self.UTCzone) - 6)	###   SE CORRIGE SUMANDO LA MITAD DE LA DURACION DE LA MEDICION PARA USARLO EN EL BIN
		self.corr_year=self.corr_fechr.year
		self.corr_month=self.corr_fechr.month
		self.corr_day=self.corr_fechr.day
		self.corr_hour=self.corr_fechr.hour
		self.corr_minute=self.corr_fechr.minute
		self.corr_seconds=self.corr_fechr.second
		self.corr_microseconds=self.corr_fechr.microsecond
		self.fecha='%02i%02i%02i' % (self.corr_year-2000,self.corr_month,self.corr_day)
		
		stime=self.ifg_TIM.split('(')
		szone=stime[1].split(')')
		self.zone=int(szone[0][3:])

		if station == 'ALTZ': 
		    self.site='Altzomoni'
		    self.lat=19.1187
		    self.lon=-98.6552
		    self.alt=3985.0  

		if station == 'CCA':
		    self.site='CCA'
		    self.lat=19.3262
		    self.lon=-99.1761
		    self.alt=2280.0

	def calc_apparent_elevation(self,station):
		finp=open('sun_pos_2.inp','wb')
		finp.writelines( '$1\r\n'   )
		finp.writelines('%i\r\n' % (self.ut_year-2000))
		finp.writelines( '%i\r\n' % (self.ut_month))
		finp.writelines( '%i\r\n' % (self.ut_day))
		finp.writelines( '%i\r\n' % (self.ut_hour))
		finp.writelines( '%i\r\n' % (self.ut_minute))
		finp.writelines( '%f\r\n' % (self.ut_seconds + self.ut_microseconds/1000000.0))
		finp.writelines( '%f\r\n' % (self.lat))
		finp.writelines('%f\r\n' % ( self.lon))
		finp.writelines( '%f\r\n' % (self.alt/1000.0))        
		finp.writelines( '\r\n')
		finp.writelines( '$2\r\n')
		finp.writelines( '1\r\n')
		ptfile= '/home/D2_PROFFIT/pt_profiles/PT_FROM_RADIOSONDEOS/'+station+'/%i%02i%02i_PT.prf' % (self.corr_year,self.corr_month,self.corr_day)
		finp.writelines( 'pt\\'+station+'\r\n')
		finp.writelines( 'sun\r\n')
		finp.close()

		if operatingsystem[:5] =='linux':
			ptfile=ptfile.replace('\\','/')

		if os.path.exists(ptfile) == False:
			self.download_pt_radiosonde(self.corr_fechr,station)

		shutil.copyfile(ptfile,'pt/'+station+'/PT.prf')
		
		comand='sun_pos_2b.exe'
		if operatingsystem[:5] =='linux':
			comand='wine  '+comand
		os.system(comand)

		lines=[]
		for line in fileinput.input('sun_pos_2.out'):
			lines.append(line)
		if int(lines[0].strip()) == 1:
			shutil.move("eopc04.62-now","eopc04.62-now_old")
			sock = urllib2.urlopen('http://hpiers.obspm.fr/iers/eop/eopc04/eopc04.62-now')
			lineas = sock.readlines()
			sock.close()
			filename_sonde = 'eopc04.62-now'
			fsonde = open(filename_sonde,'w')
			for lin in lineas:
				fsonde.write(lin)
			fsonde.close()
			os.system(comand)
			lines=[]
			for line in fileinput.input('sun_pos_2.out'):
				lines.append(line)

		self.unrefracted_elev=float(lines[1])
		self.refracted_elev=float(lines[2])
		self.Azimuth=float(lines[3])
		self.airmassfraction=float(lines[7])

#########################################################################
	def download_pt_radiosonde(self,fec,station):
		url='http://weather.uwyo.edu/cgi-bin/sounding?Fregion=naconf&TYPE=TEXT%%3ALIST&YEAR=%i&MONTH=%i&FROM=%i12&TO=%i12&STNM=76679' % (fec.year,fec.month,fec.day,fec.day)
		sock = urllib2.urlopen(url)
		lineas = sock.readlines()
		sock.close()
		filename_sonde = "sonda.html"
		fsonde = open(filename_sonde,"w")
		for lin in lineas:
			fsonde.write(lin)
		fsonde.close()
		contador = 0
		for lin in lineas[10:]:
			if len(lin.strip().split()) == 11: 
				try:
					float(lin.strip().split()[0])
					contador = contador + 1
				except:
					pass
		if contador < 30:
			self.download_pt_radiosonde(fec+timedelta(days=-1),station)
		else:
			self.htlm2ptprf(filename_sonde,station)
			f2 = open('RADIOSONDEO.TXT','wb')
			f2.write(lineas[4].split()[10][2:4]+'%02i' % datetime.strptime(lineas[4].split()[9],"%b").month+lineas[4].split()[8])
			f2.close()
			os.remove(filename_sonde)
			print 'PT PROFILE DATE',fec

	def htlm2ptprf(self,filename_sonde,station):
		sdate='%i%02i%02i' % (self.corr_year,self.corr_month,self.corr_day)
		#######filename_sonde='pt_sounding/20'+sdate+'.htlm'
		filename_pt='/home/D2_PROFFIT/pt_profiles/PT_FROM_RADIOSONDEOS/'+station+'/'+sdate+'_PT.prf'

		if operatingsystem[0:5] == 'linux':
			filename_pt=filename_pt.replace('\\','/')

		p_sonde=[]
		T_sonde=[]
		z_sonde=[]

		######################################################3
		f=open(filename_sonde,'rb')
		for i in range(11):
			if i == 4:
				date_line = f.readline()[4:].split('<')[0]
			else:
				f.readline()
		dummy=f.readline()
		while len(dummy.split()) < 3:
			dummy=f.readline()
		while dummy.strip() <> '</PRE><H3>Station information and sounding indices</H3><PRE>':
			p_sonde.append(float(dummy.split()[0]))
			z_sonde.append(float(dummy.split()[1])/1000.0)
			T_sonde.append(float(dummy.split()[2])+273.15)
			dummy=f.readline()    
		f.close()   
	
		############## read climatologia para extrapolacion
		def gotonextdollar(f):
			while 1:
				character=f.read(1)
				if character == '$':
					return f.tell()
				if not character: break
			return -1
		##############################
		fT=open('T_'+station+'.prf','rb')
		pos=gotonextdollar(fT)
		fT.seek(pos-1)
		fT.readline()
		Nlevels=int(fT.readline()) 
		pos=gotonextdollar(fT)
		fT.seek(pos-1)
		fT.readline()
		lines=''
		counter=0
		zT_WACCM=[]
		while counter < Nlevels:
			line=fT.readline()
			zz=np.array((line[:-1].split()),dtype=float)
			for zzz in zz:
				zT_WACCM.append(zzz)
				counter=counter+1
		pos=gotonextdollar(fT)
		fT.seek(pos-1)
		fT.readline()
		lines=''
		counter=0
		T_WACCM=[]
		while counter < Nlevels:
			line=fT.readline()
			TT=np.array((line[:-1].split()),dtype=float)
			for TTT in TT:
				T_WACCM.append(TTT)
				counter=counter+1
		fT.close() 
		################################p-Waccom
		fP=open('P_'+station+'.prf','rb')  
		pos=gotonextdollar(fP)
		fP.seek(pos-1)
		fP.readline()
		Nlevels=int(fP.readline()) 
		pos=gotonextdollar(fP)
		fP.seek(pos-1)
		fP.readline()
		lines=''
		counter=0
		zP_WACCM=[]
		while counter < Nlevels:
			line=fP.readline()
			zz=np.array((line[:-1].split()),dtype=float)
			for zzz in zz:
				zP_WACCM.append(zzz)
				counter=counter+1
		pos=gotonextdollar(fP)
		fP.seek(pos-1)
		fP.readline()
		lines=''
		counter=0
		P_WACCM=[]
		while counter < Nlevels:
			line=fP.readline()
			PP=np.array((line[:-1].split()),dtype=float)
			for PPP in PP:
				P_WACCM.append(PPP)
				counter=counter+1
		fP.close() 
        ###########################
		############read z para output
		fz=open('z_'+station+'.prf','rb')  
		pos=gotonextdollar(fz)
		fz.seek(pos-1)
		fz.readline()
		Nlevels=int(fz.readline()) 
		pos=gotonextdollar(fz)
		fz.seek(pos-1)
		fz.readline()
		lines=''
		counter=0
		znew=[]
		while counter < Nlevels:
			line=fz.readline()
			zz=np.array((line[:-1].split()),dtype=float)
			for zzz in zz:
				znew.append(zzz)
				counter=counter+1
		fz.close()
		##################################
		pclim=np.interp(znew,zP_WACCM,P_WACCM,left=-999,right=-999)
		Tclim=np.interp(znew,zT_WACCM,T_WACCM,left=-999,right=-999)
		pnew=np.interp(znew,z_sonde,p_sonde,left=-999,right=-999)
		Tnew=np.interp(znew,z_sonde,T_sonde,left=-999,right=-999)
		for i,ppp in enumerate(pnew):
			if ppp < 0:
				pnew[i]=pclim[i]
				Tnew[i]=Tclim[i]
		##################################
		#####################################################
		fout=open(filename_pt,'wb')
		fout.write('PT prodiles from sonde and WACCM\n')
		fout.write(date_line+'\n')
		fout.write('Nlevels\r\n')
		fout.write('$\r\n')
		fout.write(('%i\r\n')%(Nlevels))
		fout.write('\r\n')
		fout.write('\r\n')
		fout.write('altitude [km]\r\n')
		fout.write('$\r\n')
		fmts=''
		for i in range(Nlevels):
			fmts=fmts+' %7.3f   '
			if np.mod(i,5) == 4:
				fmts=fmts+'\r\n'
		fmts=fmts+'\r\n'
		altitudestring=(fmts) % (tuple(znew))
		fout.write(altitudestring)
		fout.write('\r\n')
		fout.write('\r\n')
		fout.write('pressure [hPa]\r\n')
		fout.write('$\r\n')
		fmts=''
		for i in range(Nlevels):
			fmts=fmts+' %7.3e   '
			if np.mod(i,5) == 4:
				fmts=fmts+'\r\n'
		fmts=fmts+'\r\n'
		pressurestring= (fmts) % (tuple(pnew))
		fout.write(pressurestring)
		fout.write('\r\n')
		fout.write('\r\n')
		fout.write('Temperature [K]\r\n')
		fout.write('$\r\n')
		fmts=''
		for i in range(Nlevels):
			fmts=fmts+' %7.4f   '
			if np.mod(i,5) == 4:
				fmts=fmts+'\r\n'
		fmts=fmts+'\r\n'
		Tstring=(fmts) % (tuple(Tnew))
		fout.write(Tstring)
		fout.write('\r\n')
		fout.write('\r\n')
		fout.close()

	def descargaRUOA(self):
		#os.system('rm index.html')
		url='http://132.248.8.131'	###   DATOS DE ALTZOMONI
		'''
		try:
			sock = urllib2.urlopen(url)
			data = sock.read()
			sock.close()
			dataarray=data.split('</p><p>')
			for idx,line in enumerate(dataarray):
				if line[:len('Presion Barometrica:')]=='Presion Barometrica:':
					self.surfacepress = float(line.split(':')[1].split()[0])
					unitssp = line.split(':')[1].split()[1]
				if line[:len('Temperatura Ambiente:')]=='Temperatura Ambiente:':
					self.surfacetemp = float(line.split(':')[1].split()[0])
					unitsst = line.split(':')[1].split()[1]
				if line[:len('Humedad Relativa:')]=='Humedad Relativa:':
					self.relativehum = float(line.split(':')[1].split()[0])
					unitsrh = line.split(':')[1].split()[1]
				if line[:len('Radiacion Total:')]=='Radiacion Total:':
					self.totalradiation =  float(line.split(':')[1].split()[0])
					unitstr = line.split(':')[1].split()[1]
				if line[:len('Direccion de Viento:')]=='Direccion de Viento:':			
					self.winddir =  float(line.split(':')[1].split()[0])
					unitswd = line.split(':')[1].split()[1]
					for uuu,ele in enumerate(dataarray[idx-1].split('<p>')):
						if ele[:len('Velocidad de Viento:')]=='Velocidad de Viento:':	
							self.windspeed =  float(ele.split(':')[1].split()[0])
							unitsws = ele.split(':')[1].split()[1]
						if ele[:len('Ultima actualizacion:')]=='Ultima actualizacion:':
							self.hractRUOA = "%02i:%02i" % (int(ele.split(':')[1]),int(ele.split(':')[2].split('</p>')[0].split('-')[0]))
							self.fecactRUOA = "%02i-%02i-%04i" %(int(ele.split(':')[2].split('</p>')[0].split('-')[1]),int(ele.split(':')[2].split('</p>')[0].split('-')[2]),int(ele.split(':')[2].split('</p>')[0].split('-')[3]))
		
		FORMATO DE URL DE RUOA NO CORRESPONDE CON EL SCRIPT, NO HAY RENGLON DE 'Ultima actualizacion', SE MOVIO SANGRIA DEL EXCEPT 18/11/2016
		except:
		'''
		
		self.surfacepress = -9999
		self.surfacetemp = -9999
		self.relativehum = -9999
		self.totalradiation = -9999
		self.winddir = -9999
		self.windspeed = -9999
		self.hractRUOA = "00:00"
		self.fecactRUOA = '01-01-1900'
		print "----------------------------"
		print "RUOA DATA NOT AVAILABLE"
		print "----------------------------"
		
		if self.fecactRUOA != "%02i-%02i-%04i" % (self.corr_day,self.corr_month,self.corr_year):
			self.surfacepress = -9999
			self.surfacetemp = -9999
			self.relativehum = -9999
			self.totalradiation = -9999
			self.winddir = -9999
			self.windspeed = -9999
			self.hractRUOA = "00:00"
			self.fecactRUOA = '01-01-1900'


	def writebin(self,pathout):
		fname='%02i%02i%02i' % (self.corr_year-2000,self.corr_month,self.corr_day)+'.'+self.name.split('.')[1]+'_'+'%02i%02i%02i' % (self.corr_hour,self.corr_minute,self.corr_seconds)+self.spc_type+self.filter+'.bin'
		self.binname = fname
		fbinout = open(pathout+fname,'wb')		###   ATENCION: WB SIEMPRE

		#####
		header = 'Location \n Date \n Time eff. UT [h,decimals] \n Apparent elevation [deg] \n Azimuth [deg] \n Duration of measurement [s] \n$\n'
		fbinout.writelines(header)
		self.date='%02i%02i%02i' % (self.corr_year-2000,self.corr_month,self.corr_day)+'\n'
		fbinout.writelines(self.site+'\n')        
		fbinout.writelines(self.date)
		self.timeeff = self.corr_hour+self.corr_minute/60.0+(self.corr_seconds + self.corr_microseconds/1000000.0)/3600.0
		fbinout.writelines(str(self.timeeff)+'\n')
		try: 
			fbinout.writelines(str(self.refracted_elev)+'\n')
		except:
			fbinout.writelines('%ref_elev\n')
		try: 
			fbinout.writelines(str(self.Azimuth)+'\n')
		except:
			fbinout.writelines('%Azimuth\n')
		fbinout.writelines(str(self.DUR)+'\n')
		fbinout.writelines('\n')
		fbinout.writelines('\n')

		#####
		header = 'Filter \n OPDmax [cm] \n semi FOV [rad] \n APpodizacion \n$\n'
		fbinout.writelines(header)
		fbinout.writelines(str(self.OPF)+'\n')
		fbinout.writelines(str(self.OPD)+'\n')
		fbinout.writelines(str(self.SEMIFOV)+'\n')
		self.readFFT()
		fbinout.writelines(str(self.APF)+'\n')
		fbinout.writelines('\n')
		fbinout.writelines('\n')

		#####
		header = 'ILS simple(1) or extended(2) \n$\n'
		fbinout.writelines(header)
		try:
			self.ILS
			fbinout.writelines('2\n')
			for i in range(20):
				fbinout.writelines('%5f  %5f \n' % (self.ILS[i,0],+self.ILS[i,1]))
		except:
			fbinout.writelines('1\n')
			#fbinout.writelines('%ILS\r\n')
			fbinout.writelines('1.0 0.0\n')
		fbinout.writelines('\n')

		#####
		header = 'firstnue \n lastnue \n deltanue \n Ngridpts \n$\n'
		fbinout.writelines(header)

		fbinout.writelines(str(self.spc_FXV)+'\n')
		fbinout.writelines(str(self.spc_LXV)+'\n')
		fbinout.writelines(str(self.spc_dw)+'\n')
		fbinout.writelines(str(self.spc_NPT+self.dnpt)+'\n')

		fbinout.writelines('\n')
		fbinout.writelines('\n')

		#####
		header = 'Comments:  \n nonlinearity corr \n DC corr \n time-zone \n que FFT  \n qflag \n$\n'
		fbinout.writelines(header)
		
		self.bincomment = '%LATITUDE: '+str(self.lat)+' \n'
		self.bincomment = self.bincomment+'%LONGITUDE: '+str(self.lon)+' \n'
		self.bincomment = self.bincomment+'%ALTITUDE: '+str(self.alt)+' \n'
		self.bincomment = self.bincomment+'%COMMENT: '+self.comment+' \n'
		self.bincomment = self.bincomment+'%QUALITY_FLAG: '+str(self.qflag)+' \n'
		self.bincomment = self.bincomment+'%CLOUD_INDEX: '+str(self.cloudindex)+' \n'
		self.bincomment = self.bincomment+'%SIGNAL_TO_NOISE: '+str(self.SNR)+' \n'
		self.bincomment = self.bincomment+'%NONLINEARITY: '+str(self.RNL)+' \n'
		self.bincomment = self.bincomment+'%NUMBER_OF_SCANS: '+str(self.NSS)+' \n'
		self.bincomment = self.bincomment+'%ASTRONOMICAL_ELEV: '+str(self.unrefracted_elev)+' \n'
		try:
			self.bincomment = self.bincomment+'%BEAMSPLITTER: '+str(self.BMS.strip())+' \n'
		except:
			pass
		if (self.surfacepress == -9999):
			self.bincomment = self.bincomment+' \n'+'RUOA DATA NOT AVAILABLE'+' \n'
		else:
			self.bincomment = self.bincomment+' \n'+'RUOA DATA FROM '+self.hractRUOA+' '+self.fecactRUOA+' \n'
		self.bincomment = self.bincomment+'%SURFACE_PRESSURE: '+str(self.surfacepress)+' \n'
		self.bincomment = self.bincomment+'%SURFACE_TEMPERATURE: '+str(self.surfacetemp)+' \n'
		self.bincomment = self.bincomment+'%RELATIVE_HUMIDITY: '+str(self.relativehum)+' \n'
		self.bincomment = self.bincomment+'%TOTAL_RADIATION: '+str(self.totalradiation)+' \n'
		self.bincomment = self.bincomment+'%WIND_SPEED: '+str(self.windspeed)+' \n'
		self.bincomment = self.bincomment+'%WIND_DIRECTION: '+str(self.winddir)+' \n'

		#for line in open('RADIOSONDEO.TXT','rb'):
		#	if line.strip() != '%02i%02i%02i' % (self.ut_year-2000,self.ut_month,self.ut_day):
		#		print "----------------------------"
		#		print "NO HAY RADIOSONDEO PARA "+'%02i-%02i-%02i' % (self.ut_year-2000,self.ut_month,self.ut_day)+"(FECHA UT)"
		#		self.bincomment = self.bincomment +' \n'+ "SE USO RADIOSONDEO DE "+line+" \n"

		#try:
			#self.bincomment = self.bincomment+'no more question no more comments \n'
		#except:
			#self.bincomment = 'no question no comments \n'

		try:
			self.spc_DCcorr
			self.bincomment = self.bincomment+' \n'+'%DC-CORRECTED'
			print '----------------------------'
			print 'DC-CORRECTED SPECTRA'
		except:
			self.bincomment = self.bincomment+' \n'+'%NOT DC-CORRECTED'
			print '----------------------------'			
			print 'NOT DC-CORRECTED SPECTRA'

		try:
			self.spc_corrSF
			self.bincomment = self.bincomment+' \n'+'%TEM CORRECTED'
			print '----------------------------'
			print 'TEM CORRECTED SPECTRA'
		except:
			pass

		try:
			self.spc_calib
			self.bincomment = self.bincomment+' \n'+'%CALIBRATED'
			print '----------------------------'
			print 'CALIBRATED SPECTRA'
		except:
			self.bincomment = self.bincomment+' \n'+'%UNCALIBRATED'
			print '----------------------------'			
			print 'UNCALIBRATED SPECTRA'

		fbinout.writelines(self.bincomment)

		#####
		fbinout.writelines('\n')
		fbinout.writelines('\n')

		#####
		header = 'binary spec (W[f],dw[f],NPT[i],...)\n$\r\n'
		fbinout.writelines(header)

		#print 'FIRST WAVENUMBER',self.spc_FXV, 'WAVENUMBER STEP', self.spc_dw, 'NUMBER OF POINTS', self.spc_NPT+self.dnpt
		wdwnpt = struct.pack('2d1i',*tuple([self.spc_FXV,self.spc_dw,self.spc_NPT+self.dnpt]))
		fbinout.write(wdwnpt)

		#print 'LENGTH OF SPEC', len(self.spc_org)
		try:
			bspec = struct.pack(str(self.spc_NPT+self.dnpt)+'f',*tuple(intensity for intensity in self.spc_calib))
		except:
			try:
				bspec = struct.pack(str(self.spc_NPT+self.dnpt)+'f',*tuple(intensity for intensity in self.spc_corrSF))
			except:
				try:	
					bspec = struct.pack(str(self.spc_NPT+self.dnpt)+'f',*tuple(intensity for intensity in self.spc_DCcorr))
				except:			
					bspec = struct.pack(str(self.spc_NPT+self.dnpt)+'f',*tuple(intensity for intensity in self.spc_org))
		fbinout.write(bspec)

		fbinout.close()

		print '----------------------------'
		print 'BIN FILE LISTO EN',pathout
		print '----------------------------'

	def plotspc(self,pltpathname):
		self.getspc(write_flag=0)
		w=self.w()		
		plt.figure()
		fname='%02i%02i%02i' % (self.corr_year-2000,self.corr_month,self.corr_day)+'-'+'%02i%02i%02i' % (self.corr_hour,self.corr_minute,self.corr_seconds)+' FILTRO '+self.spc_type+self.filter
		plt.subplot(211)
		try:
			plt.title(fname+' CALIB')
			plt.plot(w,self.spc_calib)
		except:		
			try:
				plt.title(fname+' CORR (SF)')
				plt.plot(w,self.spc_corrSF)
			except:	
				plt.title(fname+' ORG')
				plt.plot(w,self.spc_org)
		plt.subplot(212)
		plt.plot(self.ifg)

		plt.savefig(pltpathname+self.name+'.png')
		plt.savefig(pltpathname+self.spc_type+self.filter+'.png')

	def mandaplot(self,pltpathname):
		orden1 =  "pscp.exe -pw espectro "
		orden2 = " grutter@132.248.8.68:/var/www//espectroscopia/ALTZ/ftir"
		plotpath1 = pltpathname+self.spc_type+self.filter+'.png'
		plotpath2 = pltpathname+self.name+'.png'
		try:
			os.system(orden1+plotpath1+orden2)
			os.system(orden1+plotpath2+orden2)
		except:
			print "NO SE PUDO ENVIAR PLOT A SERVIDOR"

	def mandabin(self,binpathname):
		orden1 = "pscp.exe -pw yaskil "
		orden2 = " wolf@10.20.2.237:/home/DD2_DATA1/bin_spc/altz_bin/online_backup/"
		binfullname = binpathname+self.binname 
		try:
			os.system(orden1+binfullname+orden2)
		except:
			print "NO SE PUDO ENVIAR "+self.binname+" A WOLF"

	def calibHR(self,calibpath):				### BUSCA ESPECTRO CORREGIDO PARA EMISION TERMICA (FILTRO SF)
		w=self.w()		
		PGN=int(self.PGN[0])				### 0,1,2,3
		APT=float(self.APT.split()[0])

		if self.station == 'ALTZ':
			fts = 'HR'
		elif self.station == 'CCA':
			fts = 'VX'

		detectorflag='InSb'        
		if self.filter == 'N':
			detectorflag='NIR'
		if self.filter == 'F':
			detectorflag='MCT'

		lines=[]
		for line in fileinput.input(calibpath+'pregain.dat'):
			lines.append(line)

		for i,line in enumerate(lines):
			if line.split('-')[0]==detectorflag:
				#print detectorflag
				iline=i+1
		pregains=map(float,lines[iline].split())	### 0:A,1:B,2:C,3:Ref
		pregain=pregains[PGN]

		try:
			calibfile='calibf_'+fts+'_'+self.filter+'_'+self.BMS.strip()+'.dat'    
			calibmatrix=np.genfromtxt(calibpath+calibfile)
			wcalib=calibmatrix[:,0]        
			calibf=calibmatrix[:,1]/pregain/APT**2
			self.efficiency=np.interp(w,wcalib,calibf)
			self.spc_calib=self.efficiency*self.spc_corrSF*(10**7) # 10**9nm/100cm
			print "CALIBRACION HECHA SOBRE ESPECTRO SF CORREGIDO POR EMISION TERMICA"
			try:
				self.comment = self.comment + ' Calibration done on TEM corrected spectra'
			except:
				self.comment = 'Calibration done on TEM corrected spectra'
		except:            	
			try:
				calibfile='calibf_'+fts+'_'+self.filter+'_'+self.BMS.strip()+'.dat'    
				calibmatrix=np.genfromtxt(calibpath+calibfile)
				wcalib=calibmatrix[:,0]        
				calibf=calibmatrix[:,1]/pregain/APT**2
				self.efficiency=np.interp(w,wcalib,calibf)
				self.spc_calib=self.efficiency*self.spc_DCcorr*(10**7) # 10**9nm/100cm
				print "CALIBRACION HECHA SOBRE ESPECTRO CORREGIDO DC"
				try:
					self.comment = self.comment + ' Calibration done on DC corrected spectra'
				except:
					self.comment = 'Calibration done on DC corrected spectra'
			except:
				try:
					calibfile='calibf_'+fts+'_'+self.filter+'_'+self.BMS.strip()+'.dat'    
					calibmatrix=np.genfromtxt(calibpath+calibfile)
					wcalib=calibmatrix[:,0]        
					calibf=calibmatrix[:,1]/pregain/APT**2
					self.efficiency=np.interp(w,wcalib,calibf)
					self.spc_calib=self.efficiency*self.spc_org*(10**7) # 10**9nm/100cm
					print "CALIBRACION HECHA SOBRE ESPECTRO ORIGINAL"
					try:
						self.comment = self.comment + ' Calibration done on original spectra'
					except:
						self.comment = 'Calibration done on original spectra'
				except:
					print 'ARCHIVO '+'calibf_'+fts+'_'+self.filter+'_'+self.BMS.strip()+'.dat'+' NO ENCONTRADO'
			
	def corrigeSF(self):
		if ((self.filter == 'F') & (self.station == 'CCA')):
			bkg=np.genfromtxt('bkg_'+self.station+'.dpt')
			wb_bkg = 402.8333333
			dw_bkg = 0.0555555555556
			npt_bkg = 17897
			w_bkg = np.arange(npt_bkg)*dw_bkg+wb_bkg
			if len(w_bkg) != len(self.wavenumber):
				bkg = np.interp(self.wavenumber,w_bkg,bkg)		### REVISAR INTERPOLACION
				w_bkg = self.wavenumber
			index = np.where(((w_bkg > 630.0) & (w_bkg < 708.0)) | (w_bkg > 1370.0) )[0]
			nindex=len(index)

			nparam = 1
			yvec=np.zeros([nindex])
			kmatindex=np.zeros([nindex,nparam*2])
			kmatfull=np.zeros([len(w_bkg),nparam*2])    

			for i in range(nparam):
				jcounter=0
				for jj in index:
					kmatindex[jcounter,i+nparam] = w_bkg[jj]**i
					kmatindex[jcounter,i] = bkg[jj]*w_bkg[jj]**i	
					yvec[jcounter] = self.spc_org[jj]
					jcounter=jcounter+1
				for jjj in range(len(w_bkg)):
					kmatfull[jjj,i+nparam] = w_bkg[jjj]**i
					kmatfull[jjj,i] = bkg[jjj]*w_bkg[jjj]**i

			KT=np.transpose(kmatindex)
			KTK=np.dot(KT,kmatindex)
			KTKinv=np.linalg.inv(KTK)
			KTKinvKT=np.dot(KTKinv,KT)
			xvec=np.dot(KTKinvKT,yvec)

			bkg_actual=np.dot(kmatfull,xvec)
			self.spc_corrSF = self.spc_org-bkg_actual
			print "----------------------------"
			print 'CORRECION DE TEM HECHA'
			print "----------------------------"

	def dccorr(self,ifg):
	    
		#    dcconfig['dccoriter'] 
		#    dcconfig['dccorbox']
		#    dcconfig['dccorrtype']
		#    dcconfig['dcintens']
		#    dcconfig['dcfluctu']
		#    dcconfig['brokenfiles']
		#    dcconfig['dcintensmax']
		#    dcconfig['dcintensmin']
		#    
		#    out['exposure']
		#    out['dcfluctu']
		#    out['qflag']
	
		dcconfig = {}
		dcconfig['dccoriter'] = 5		### DC-Corr Iterations
		dcconfig['dccorbox'] = 2001		### DC-Corr Boxsize
		dcconfig['dccorrtype'] = 1		### DC-Corr Type (correct+use DC)
		dcconfig['dcintens'] = 0.01		### DC-Corr Exposure Min
		dcconfig['dcfluctu'] = 0.1		### DC-Corr Fluctiations
		dcconfig['brokenfiles'] = 0		### Broken files, always 0, necessary
		dcconfig['dcintensmax'] = 0.8		### DC-Corr Exposure Max

		out={}
		out['exposure']=np.nan
		out['dcfluctu']=np.nan
		out['qflag']=20
		out['ifgquality']=np.nan
		out['fwd_exposure']=np.nan
		out['bwd_exposure']=np.nan
	
		out['fwd_dcfluctu']=np.nan
		out['bwd_dcfluctu']=np.nan

		ifg_flag = 0		### ifg_flag: 0=corrected IFG; 1=uncorrected IFG
	
		# check on interferograms if they are correctly read
		dcconfig['brokenfiles'],qflag,ifg_okay=self.check(ifg,dcconfig['dccorrtype'],dcconfig['brokenfiles'])
		if not ifg_okay:
			out['qflag']=qflag
			#self.qflag = 0
			ifg_flag = 1
			ifgOPUS = copy.deepcopy(ifg)
			return ifg_flag,ifg,np.zeros(len(ifg)),ifgOPUS
	
		# check ifg for over exposure
		ifgmax=np.max(abs(ifg))
		if abs(ifgmax) > dcconfig['dcintensmax']:
			print 'Overexposure detected Skipping spectrum',
			try:
				self.comment = self.comment + ' Overexposure detected'
			except:
				self.comment = 'Overexposure detected'
			#self.qflag = 0 
			ifg_flag = 1     
			out['qflag']=10
			out['exposure']=ifgmax
			ifgOPUS = copy.deepcopy(ifg)
			return ifg_flag,ifg,np.zeros(len(ifg)),ifgOPUS

		# smoothing 

		ifg_smooth = copy.deepcopy(ifg)

		for j in range(1, dcconfig['dccoriter'] + 1, 1):
			# smoothing first half of double interferogram
			ifg_smooth = ifgtoolsc.averageIfg(ifg_smooth, dcconfig['dccorbox'],0, len(ifg_smooth)/2 - 1)

			# smoothing second half of double interferogram             
			ifg_smooth = ifgtoolsc.averageIfg(ifg_smooth, dcconfig['dccorbox'],len(ifg_smooth)/2, len(ifg_smooth) - 1)

		fwd=range(int(len(ifg)/2))
		bwd=range(int(len(ifg)/2),len(ifg))
		fwd_smooth=ifg_smooth[fwd]  
		bwd_smooth=ifg_smooth[bwd]
		all_smooth = np.hstack([fwd_smooth,bwd_smooth])
		abs_smooth=abs(all_smooth)

		# quality check
		median=np.median(abs_smooth)
		all_max = np.max(abs_smooth)
		all_min = np.min(abs_smooth)
		delta = (abs(all_max)-abs(all_min))/abs(all_max)

		out['exposure'],out['dcfluctu']=self.qualityCheck(all_smooth)
		out['fwd_exposure'],out['fwd_dcfluctu']=self.qualityCheck(fwd_smooth)
		out['bwd_exposure'],out['bwd_dcfluctu']=self.qualityCheck(bwd_smooth)

		## check underexposure
		if all_max < dcconfig['dcintens']:
			out['qflag']=9
			print 'Underexposure detected Skipping spectrum ',
			try:
				self.comment = self.comment + ' Underexposure detected'
			except:
				self.comment = 'Underexposure detected'
			#self.qflag = 0
			ifg_flag = 1
			ifgOPUS = copy.deepcopy(ifg)
			return ifg_flag,ifg,ifg_smooth,ifgOPUS

		## check dc-fluctuation
		if delta > dcconfig['dcfluctu']:
			out['qflag']=11
			print 'DC-Fluctuation detected Skipping spectrum',
			try:
				self.comment = self.comment + ' DC-Fluctuation detected'
			except:
				self.comment = 'DC-Fluctuation detected'
			#self.qflag = 0
			ifg_flag = 1
			ifgOPUS = copy.deepcopy(ifg)
			return ifg_flag,ifg,ifg_smooth,ifgOPUS

	# start DC-correction
	    
		# selects the centerburst peak position ZeroPathDifference (ZPD). 
		ifgLeft = ifg[0:np.size(ifg)/2]
		ifgRight = ifg[np.size(ifg)/2:np.size(ifg)]

		posMaxAbsLeft = np.argmax(np.abs(ifgLeft))
		maxAbsLeft = np.max(np.abs(ifgLeft)) 
		posMaxAbsRight = np.argmax(np.abs(ifgRight))
		maxAbsRight = np.max(np.abs(ifgRight)) 
	    
		pointsArroundZPD = 100 # number of ifg-samples that should be taken into 
		                    # left and right from centerburst
		if posMaxAbsRight<pointsArroundZPD or posMaxAbsLeft<pointsArroundZPD:
			print 'Centerburst detection failed.'
			try:
				self.comment = self.comment + ' Centerburst detection failed'
			except:
				self.comment = 'Centerburst detection failed'
			#self.qflag = 0
			out['qflag']=7
			posMaxAbsRight+=pointsArroundZPD
			posMaxAbsLeft+=pointsArroundZPD
		
		minAbsAroundLeftZPD = np.min(np.abs(ifgLeft[posMaxAbsLeft - pointsArroundZPD:posMaxAbsLeft + pointsArroundZPD]))

		minAbsAroundRightZPD = np.min(np.abs(ifgRight[posMaxAbsRight - pointsArroundZPD:posMaxAbsRight + pointsArroundZPD]))
	    
		ifgTemp = ifg_smooth
	    
		ifgTempLeft = ifgTemp[(posMaxAbsLeft - pointsArroundZPD):(posMaxAbsLeft + pointsArroundZPD)]
		meanLeftZPD = np.mean(ifgTempLeft)
	    
		ifgTempRight = ifgTemp[(posMaxAbsRight - pointsArroundZPD):(posMaxAbsRight + pointsArroundZPD)]
		meanRightZPD = np.mean(ifgTempRight)

		meanZPD = 0.5 * (meanLeftZPD + meanRightZPD)
	    
		sizeIFGPeakLeft = maxAbsLeft - minAbsAroundLeftZPD
		sizeIFGPeakRight = maxAbsRight - minAbsAroundRightZPD
		s = np.sum(np.absolute(np.log(np.absolute(ifgTemp / meanZPD)))/np.size(ifgTemp))
		ifgQuality = s / (sizeIFGPeakLeft * sizeIFGPeakRight)
		out['ifgquality']=ifgQuality
	    
		if (abs(posMaxAbsRight - posMaxAbsLeft) > 20):
			print 'Max-Position is not symmetric -> bad IFG'
			try:
				self.comment = self.comment + ' Max-Position is not symmetric -> bad IFG'
			except:
				self.comment = 'Max-Position is not symmetric -> bad IFG'
			#self.qflag = 0
			ifg_flag = 1
			out['qflag'] = 8

		ifgC = copy.deepcopy(ifg)
		ifgZPD = copy.deepcopy(ifg)

		if dcconfig['dccorrtype'] == 1:
			ifgC = (ifg * meanZPD) / ifg_smooth - meanZPD
			ifgZPD = (ifg * meanZPD) / ifg_smooth
			ifgZPD[np.size(ifgZPD)/2:np.size(ifgZPD)] = np.flipud(ifgZPD[np.size(ifgZPD)/2:np.size(ifgZPD)])

	    
		return ifg_flag,ifgC,ifg_smooth,ifgZPD

	###############################################################################

	def fft(self,ifgC):
	#    config['phasres']
	#    config['apokind']
	#    config['ssords']
	#    config['filesbroken']
	#    config['ifg_split']

		config = {}
		config['phasres'] = 1.0		### Phase resolution
		config['apokind'] = 1			### Apodisation, 1: boxcar
		config['ssords'] = 0			### Single-sided, 0; Double-sided, 1
		config['filesbroken'] = 0		### Files broken, always 0, necessary
		config['ifg_split'] = 0		### Split scans in separate file, 0: No, 1: Yes

		qflag=20
		fft_flag = 0		### fft_flag: 0=good FFT; 1=bad IFG
	    
		nifgscan = np.size(ifgC) / 2
		nburstfwd = np.argmax(np.abs(ifgC[0:np.size(ifgC)/2]))
		nburstbwd = np.argmax(np.abs(ifgC[np.size(ifgC)/2:np.size(ifgC)]))
		nradiusfwd = min(nburstfwd, nifgscan - nburstfwd - 1)
		nradiusbwd = min(nburstbwd, nifgscan - nburstbwd - 1)
		nradius = min(nradiusfwd, nradiusbwd)
		nss = min(nifgscan - nburstfwd - 1,nifgscan - nburstbwd - 1)

		nuesampling = self.HFL
		if self.LFL > 0:
			print('Warning!!! Low frequency limit > 0 but 0 is expected --> wrong results!')
			try:
				self.comment = self.comment + ' Low frequency limit > 0 but 0 is expected'
			except:
				self.comment = 'Low frequency limit > 0 but 0 is expected'
			#self.qflag = 0
			fft_flag = 1
		phasres = config['phasres']
		apokind = config['apokind']
		ssords = config['ssords']

		ifgC = ifgC.astype(np.float32)
	    
		if nradius==0:
			spec=np.zeros((len(ifgC)/2))
			wn=np.linspace(0,len(spec))
			try:
				self.comment = self.comment + ' nradius == 0'
			except:
				self.comment = 'nradius == 0'
			#self.qflag = 0
			fft_flag = 1
			config['filesbroken']=config['filesbroken']+1
		else:
			specrepcfwd, phasrefwd, phasimfwd,nmax = ifgtoolsc.fftmain(ifgC[0:np.size(ifgC)/2], nuesampling, nburstfwd, apokind, ssords, nss, nradius, phasres)
			specrepcbwd, phasrebwd, phasimbwd,nmax = ifgtoolsc.fftmain(ifgC[np.size(ifgC)/2:np.size(ifgC)], nuesampling, nburstfwd, apokind, ssords, nss, nradius, phasres)

			x = np.arange(0, nuesampling + 10.0**-7, nuesampling/(float(nmax/2)))
			x[0] = 10.0**-10 # to avoid dividing through zero
			wn = x[0:nmax/2 + 1]
		
			spec = 0.5 * specrepcfwd + 0.5 * specrepcbwd
	    
		return fft_flag,wn,spec

	###############################################################################

	def check(self,ifg,dccorrtype,brokenfiles):
		qflag=20;
		if (int(self.GFW) + 
			int(self.GBW)) % 2 != 0:
			print('   >Error: Number of good forward and backward scans is odd!')
			print('   >Skipping interferogram.')
			try:
				self.comment = self.comment + ' Number of good forward and backward scans is odd'
			except:
				self.comment = 'Number of good forward and backward scans is odd'
			#self.qflag = 0
			qflag=2         # Qflag #2  
			brokenfiles+=1
			return brokenfiles,qflag,False

		if dccorrtype != 2:
			if (np.size(np.where(ifg > 0)) > 0) and (np.size(np.where(ifg < 0)) > 0):
				print('   Values change sign. Really DC-Interferogram? Skipping spectrum.')
				try:
					self.comment = self.comment + ' IFG Values change sign'
				except:
					self.comment = 'IFG Values change sign'
				#self.qflag = 0
				qflag=3         # Qflag #3
				brokenfiles+=1
				return brokenfiles,qflag,False
			elif np.size(np.where(ifg == 0)) > 0:
				print('   Zero-entries in IFG. Really DC-Interferogram? Skipping spectrum.')
				try:
					self.comment = self.comment + ' Zero-entries in IFG'
				except:
					self.comment = 'Zero-entries in IFG'
				#self.qflag = 0
				qflag=4         # Qflag #4
				brokenfiles+=1
				return brokenfiles,qflag,False
			elif np.size(ifg) % 2 != 0:
				print('   Number of entries in IFG is odd. Damaged IFG? Skipping spectrum.')
				try:
					self.comment = self.comment + ' Number of entries in IFG is odd'
				except:
					self.comment = 'Number of entries in IFG is odd'
				#self.qflag = 0
				qflag=5         # Qflag #5
				brokenfiles+=1
				return brokenfiles,qflag,False
		        
		return brokenfiles,qflag,True

	###############################################################################
		                        
	def qualityCheck(self,smooth):
		'''
	    performs quality check on smoothed signal:
	    returns exposure,dcval
		'''
		abs_smooth=abs(smooth)
		median=np.median(abs_smooth)
		all_max = np.max(abs_smooth)
		all_min = np.min(abs_smooth)
		delta = (abs(all_max)-abs(all_min))/abs(all_max)
	    
		return median,delta

	###############################################################################

	def DC_FFT(self,station):
		self.readdir()
		self.readOPT()
		self.readINS()
		self.readACQ()
		self.readFFT()
		self.readspec()
		self.getifg(station)
		
		if (station == 'ALTZ') and ('DC' in self.DTC):
			try:
				ifg_flag,ifgCorr,ifgSmooth,ifgZPD = self.dccorr(self.ifg)
				if ifg_flag == 0:
					self.ifgCorr = ifgCorr
					self.ifgSmooth = ifgSmooth
					self.ifgZPD = ifgZPD
					fft_flag,wn,spcCorr = self.fft(self.ifgCorr)
					if fft_flag == 0:
						idx_wn = (wn >= self.spc_FXV)
						idx=self.blockidarr.index('DBL')
						npts=self.blocklenarr[idx]
						dnpt=npts-self.spc_NPT
						spcCorr = spcCorr[idx_wn][0:(self.spc_NPT+dnpt)]
						self.spc_DCcorr = spcCorr
						print 'CORRECCION DC REALIZADA !!! :)'
					else:
						print 'CORRECCION DC NO REALIZADA :('
				else:
					print 'CORRECCION DC NO REALIZADA :('
			except:
				print 'CORRECCION DC NO REALIZADA :('

		



