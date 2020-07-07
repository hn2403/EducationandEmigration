# -*- coding: utf-8 -*-
"""
This is Python codes part 1 for my paper "Fast Education and Fast Emigration"
See my website for more details: https://sites.google.com/view/htnguyen2403/home
"""

import pandas as pd
import numpy as np
import matplotlib.pylab as plt
import seaborn as snb


IABFile = "/Users/hieunguyen/Desktop/Dissertation/Gender Differences in International Migration Literature/Gender and Brain Drain/Accounting Exercise/Dataset and Code/IAB Brain Drain/iabbd_8010_v1.dta"
BLFile = "/Users/hieunguyen/Desktop/Dissertation/Gender Differences in International Migration Literature/Gender and Brain Drain/Accounting Exercise/Dataset and Code/Barro-Lee Dataset/BL2013_MF2599_v2.2.dta"
    
def IABclean(filepath):
    # This function loads in the IAB Brain Drain Dataset and clean the dataset 
    data = pd.read_stata(filepath)
    oecd_country = np.unique(data.destination)
    data = data.eval('oecd = origin in @oecd_country')
    print(np.unique(data[data['oecd']== True].origin))
    
    data = data.rename(columns ={"origin":"country","ccode_origin":"code"})
    data = data.groupby(['year', 'code' , 'country','oecd'])['tot','low','med','high'].\
        agg('sum').reset_index()

    data.code = data.code.astype('category').cat.\
        rename_categories({'ZAR':'COD','ROM':'ROU','MDA':'ROM','SIN':'SGP','UAE':'ARE'})

    data.to_stata('/Users/hieunguyen/Desktop/Python code/Data/IABStock19802010.dta', write_index = False)        
    return(data)

def BLclean(filepath):
    # This function loads in the Barro - Lee Dataset and clean the dataset
    data = pd.read_stata(filepath)
    data['lp'] = data['lu'] + data['lp']
    data = data.query('year >= 1980 & year <= 2010')\
        [['country', 'year', 'sex', 'lp' ,'ls', 'lh', 'pop', 'WBcode', 'region_code']]
    data[['pop','lh','lp','ls']] = data[['pop','lh','lp','ls']]*[1000,1/100,1/100,1/100]
    data.sort_values(by=['country', 'year', 'sex'],inplace=True)
    data.rename(columns ={'WBcode':'code'}, inplace = True)
    data = data[['country' , 'code', 'year', 'sex' , 'lh', 'pop','lp','ls','region_code']]
    
    data.to_stata('/Users/hieunguyen/Desktop/Python code/Data/BLIAB19802010scatter.dta', write_index = False)
    return(data)

def label_point(x, y, val, ax):
    # This function label the points in the scatter plot
    a = pd.concat({'x': x, 'y': y, 'val': val}, axis=1)
    for i, point in a.iterrows():
        ax.text(point['x']+ 0.5, point['y']+ 0.5, str(point['val']), size = 'x-small')
 

data1 = IABclean(IABFile)
data2 = BLclean(BLFile)

# Merge the two dataframes
data1 = data1.merge(data2, how = 'inner', on = ['code', 'year'])
data1.rename(columns={'country_y':'origin'}, inplace = True)
data1.sort_values(by=['origin','code'])

# Generate key variables
data1['tothigh'] = data1['high'] + data1['lh']*data1['pop']
data1['totpop'] = data1['tot'] + data1['pop']
data1['highmigrantprop'] = data1['high']/data1['totpop']
data1['emigrate'] = data1['high']/data1['tothigh']
data1['highprop'] = data1['tothigh']/data1['totpop']

data1.to_stata('/Users/hieunguyen/Desktop/Python code/Data/IAB-BLmerged.dta', write_index = False)
    

data1 = data1.query('year == 1980 | year == 1990| year == 2000 | year == 2010')
data1.drop(['lp','ls', 'sex', 'region_code'],axis = 1, inplace = True)

# Reshaping data from long to wide
data1 = data1.set_index(['country_x','origin','code','oecd','year']).unstack('year')
data1.columns = ['{}_{}'.format(var, time) for var, time in data1.columns]
data1.reset_index(inplace = True)



# Generate scatter plots for non-OECD countries for different periods of time
start = ['1980','1990','2000','1980','1980']
end =['1990','2000','2010','2000','2010']
data1 = data1.query('oecd == 0')

for s,e in zip(start,end):
    data1['demigrate_'+ s +'_'+e] = 100*(data1['emigrate_' + e] - data1['emigrate_'+ s])/data1['emigrate_' + s]
    data1['dHSperctg_'+ s +'_'+e] = 100*(data1['highprop_' + e] - data1['highprop_'+ s])/data1['highprop_' + s]
    # Set style of scatterplot
    snb.set_context("notebook", font_scale=1.1)
    snb.set_style("ticks")

    # Create scatterplot of dataframe
    snb.lmplot('demigrate_'+ s +'_'+e, # Horizontal axis
               'dHSperctg_'+ s +'_'+e, # Vertical axis
               data=data1, # Data source
               fit_reg=True, # Don't fix a regression line
               scatter_kws={"marker": "o", # Set marker style
                            "s": 20},# S marker size
               line_kws={'color': 'red'},# color of line
                  ) 

    # Set title
    #plt.title('High-skilled distribution '+e)

    # Set x-axis label
    plt.xlabel("Percentage change of high-skilled percentages")

    # Set y-axis label
    plt.ylabel("Percentage change of high-skilled emigration rates")

    label_point(data1['dHSperctg_'+ s +'_'+e], data1['demigrate_'+ s +'_'+e] , data1['country_x'] , plt.gca()) 
    plt.savefig('Figures/NonOECDChange' + s + '-' + e +'.png')
    plt.clf()
                



