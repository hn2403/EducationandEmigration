#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This is Python codes part 2 for my paper "Fast Education and Fast Emigration"
See my website for more details: https://sites.google.com/view/htnguyen2403/home
@author: hieunguyen
"""

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as snb
import statsmodels.api as sm
import statsmodels.formula.api as smf
from linearmodels.iv import IV2SLS

# World Development Indicators and IAB-BL merged file path
WDIDataFile = "/Users/hieunguyen/Desktop/Dissertation/Gender Differences in International Migration Literature/Gender and Brain Drain/Accounting Exercise/Dataset and Code/WDI_csv/WDIData.dta"
IABBLFile = "/Users/hieunguyen/Desktop/Dissertation/Gender Differences in International Migration Literature/Gender and Brain Drain/Accounting Exercise/Dataset and Code/Accounting Exercise Code/IAB and Baro-Lee/IAB-BLmerged.dta"

# Read in the data files and clean up some variables
data1 = pd.read_stata(WDIDataFile).rename(columns = {'countrycode':'code'})
data1.code = data1.code.astype('category').cat.\
        rename_categories({'MDA':'ROM'})
        

data2 = pd.read_stata(IABBLFile)        
keep = ['origin','code','year', 'oecd', 'region_code', 'highprop', 'emigrate', 'highmigrantprop', 'pop', 'tot']        
data2 = data2[keep]

# Merge the two datasets
data1 = data1.merge(data2, how = 'inner', on = ['code', 'year'])     
data1.dropna(axis=1, how='all', inplace=True)

# Only keeping data for years 2000 and 2010 
#data1 = data1.query('year == 1980 | year == 1990 | year == 2000 | year == 2010').reset_index()
data1 = data1.query('year == 2000 | year == 2010').reset_index()

#Generate percentage changes of variables
def pct_change(var,name,data): 
    for v,n in zip(var,name):
        vlag = v + '_lag'  
        data[vlag] = (data.groupby('code',as_index=False) \
                              .apply(lambda x: x.shift(1)[v]) \
                              .reset_index(level=0, drop=True))
        
        #data = data.eval('@name = (@var - @varlag)/@varlag')
        data[n] = (data[v] -  data[vlag] )/(data1[vlag] )  
        data.drop(vlag,axis = 1, inplace = True)
    
    return (data)

# Variable lists to calculate percentage changes and the names of the new variables
var = ['emigrate','highprop','NY_GDP_PCAP_KD','NE_TRD_GNFS_ZS','SL_UEM_TOTL_NE_ZS' \
       ,'pop','tot','EN_ATM_CO2E_PC','SE_XPD_TOTL_GB_ZS','SE_XPD_TOTL_GD_ZS']
name = ['demigrate','dhighprop','dGDPpc','dtrade','dunemployment','dpop', \
        'dtot','dCO2','dtotalexp1','dtotalexp2']    
data1 = pct_change(var,name,data1)

#Reshaping data from long to wide
data1 = data1.set_index(['countryname','origin','code','oecd','region_code','year']).unstack('year')
data1.columns = ['{}_{}'.format(var, time) for var, time in data1.columns]
data1.reset_index(inplace = True)



# Regression Results
data1 = data1.query('oecd == 0').reset_index()
results = smf.ols('demigrate2010 ~ dhighprop2010', data=data1).fit()
print(results.summary())

results = smf.ols('demigrate2010 ~ dhighprop2010 + NY_GDP_PCAP_KD2000 + dGDPpc2010 + NE_TRD_GNFS_ZS2000 + dtrade2010 + dpop2010 + pop2000 + tot2000 + dCO22010 + EN_ATM_CO2E_PC2000 +SP_POP_GROW2000 ', data=data1).fit()
print(results.summary())

results = smf.ols('demigrate ~ dhighprop2010 + dGDPpc2010 + dtrade2010 + dpop2010 + dCO22010', data=data1).fit()
print(results.summary())

results = smf.ols('demigrate ~ dhighprop2010 + NY_GDP_PCAP_KD2000 + NE_TRD_GNFS_ZS2000 + pop2000 + tot2000 + EN_ATM_CO2E_PC2000 + SP_POP_GROW2000', data=data1).fit()
print(results.summary())


   
