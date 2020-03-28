# -*- coding: utf-8 -*-
import dash
import plotly.express as px
import pandas as pd
import numpy as np
from urllib.request import urlopen
import json
import os
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)



class DrawPicture:
    def __init__(self,filename,icufactor):
        self.updata = pd.read_csv('./update_data/{}'.format(filename))
        self.icudata = pd.read_csv('./data/icu_fips.csv')
        self.icufactor = icufactor
    def cleandata(self):
        fipsconfirm = self.updata  # FIPS, Confirmed
        fipsconfirm = fipsconfirm.dropna()
        datause = fipsconfirm[['FIPS', 'Confirmed']]
        datause_index = datause.set_index('FIPS')
        confirmedfips = datause['FIPS'].to_list()

        icubeds = self.icudata  # STCOUNTYFP icu_beds
        icubeds_dropzero = icubeds.replace(0, np.nan).dropna()
        icubeds_index = icubeds_dropzero.set_index('STCOUNTYFP')
        icubedsfips = icubeds_dropzero['STCOUNTYFP'].to_list()

        unknownlist = list(set(confirmedfips) - set(icubedsfips))
        knowlist = list(set(confirmedfips) - (set(confirmedfips) - set(icubedsfips)))

        data1 = datause_index.loc[knowlist]
        data1 = data1.groupby('FIPS').sum()
        data2 = datause_index.loc[unknownlist]
        data1use = data1.reset_index()
        data2use = data2.reset_index()

        icubeds_index_adjust = icubeds_index.loc[knowlist]

        def cleandata1(utility):
            icu_bedslist = []
            utilitylist = []
            for j, k in data1use.iterrows():
                fipscode = k['FIPS']
                confirm = k['Confirmed']
                icubedsamount = icubeds_index_adjust.loc[fipscode]['icu_beds']
                utilitynum = confirm * utility / icubedsamount
                icu_bedslist.append(icubedsamount)
                utilitylist.append(utilitynum)
            data1use['icu_beds'] = icu_bedslist
            data1use['utility'] = utilitylist
            data2use['icu_beds'] = np.zeros(len(data2use))

            unknownlist = []
            for i in range(len(data2use)):
                unknownlist.append('Unknown')
            data2use['utility'] = unknownlist
            newdata = pd.concat([data1use, data2use])
            return newdata

        data = cleandata1(self.icufactor)
        data = data.reset_index()

        for i in range(len(data)):
            confirmcases = data.loc[i]['Confirmed']
            if confirmcases == 0:
                data.loc[i, 'utility'] = 0

        data.to_csv('utility.csv')

    def drawconfirmed(self, up_ceil, colorstyle):
        df_sample = pd.read_csv('utility.csv')
        df_sample = df_sample.dropna()
        fip_list = df_sample['FIPS'].to_list()
        utility_list = df_sample['Confirmed'].tolist()
        fip_list_str = []
        for i in fip_list:
            new = int(i)
            new = str(new)
            if len(new) < 5:
                new = '0' * (5 - len(new)) + new
            fip_list_str.append(new)
        df_sample['fipss'] = fip_list_str
        if colorstyle == 1:
            colorscale = ['#ffffff', '#ffeff0', '#ffdfe0', '#ffcfd1', '#ffbfc1', '#ffafb2', '#ff9fa2',
                          '#ff8f93', '#ff8083', '#ff7074', '#ff6064', '#ff5055', '#ff4045', '#ff3036',
                          '#ff2026', '#ff1017', '#ff0007']
        else:
            colorscale = ['#ffffff',
                          '#edfff5',
                          '#dbffea',
                          '#c8ffe0',
                          '#b6ffd5',
                          '#a4ffcb',
                          '#92ffc0',
                          '#80ffb6',
                          '#6dffac',
                          '#5bffa1',
                          '#49ff97',
                          '#37ff8c',
                          '#24ff82',
                          '#12ff77',
                          '#00ff6d',
                          '#12f565',
                          '#24eb5d',
                          '#37e156',
                          '#49d74e',
                          '#5bcd46',
                          '#6dc33e',
                          '#80b937',
                          '#92ae2f',
                          '#a4a427',
                          '#b69a1f',
                          '#c89017',
                          '#db8610',
                          '#ed7c08',
                          '#ff7200',
                          '#fd6a00',
                          '#fa6301',
                          '#f85b01',
                          '#f65302',
                          '#f44b02',
                          '#f14403',
                          '#ef3c03',
                          '#ed3403',
                          '#ea2d04',
                          '#e82504',
                          '#e61d05',
                          '#e41505',
                          '#e10e06',
                          '#df0606', ]

        fig = px.choropleth(df_sample, geojson=counties, locations='fipss', color='Confirmed',
                            color_continuous_scale=colorscale,
                            range_color=(0, up_ceil),
                            scope="usa",
                            labels={'Confirmw cases': 'Confirmed cases'},
                            title='Confirmed Cases'
                            )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

        fig.show()

    def drawicuutility(self, up_ceil, colorstyle):
        df_sample = pd.read_csv('utility.csv')
        df_sample = df_sample.dropna()
        fip_list = df_sample['FIPS'].to_list()
        utility_list = df_sample['utility'].tolist()
        fip_list_str = []
        for i in fip_list:
            new = int(i)
            new = str(new)
            if len(new) < 5:
                new = '0' * (5 - len(new)) + new
            fip_list_str.append(new)
        df_sample['fipss'] = fip_list_str
        if colorstyle == 1:
            colorscale = ['#ffffff', '#ffeff0', '#ffdfe0', '#ffcfd1', '#ffbfc1', '#ffafb2', '#ff9fa2',
                          '#ff8f93', '#ff8083', '#ff7074', '#ff6064', '#ff5055', '#ff4045', '#ff3036',
                          '#ff2026', '#ff1017', '#ff0007']
        else:
            colorscale = ['#ffffff',
                          '#edfff5',
                          '#dbffea',
                          '#c8ffe0',
                          '#b6ffd5',
                          '#a4ffcb',
                          '#92ffc0',
                          '#80ffb6',
                          '#6dffac',
                          '#5bffa1',
                          '#49ff97',
                          '#37ff8c',
                          '#24ff82',
                          '#12ff77',
                          '#00ff6d',
                          '#12f565',
                          '#24eb5d',
                          '#37e156',
                          '#49d74e',
                          '#5bcd46',
                          '#6dc33e',
                          '#80b937',
                          '#92ae2f',
                          '#a4a427',
                          '#b69a1f',
                          '#c89017',
                          '#db8610',
                          '#ed7c08',
                          '#ff7200',
                          '#fd6a00',
                          '#fa6301',
                          '#f85b01',
                          '#f65302',
                          '#f44b02',
                          '#f14403',
                          '#ef3c03',
                          '#ed3403',
                          '#ea2d04',
                          '#e82504',
                          '#e61d05',
                          '#e41505',
                          '#e10e06',
                          '#df0606', ]

        fig = px.choropleth(df_sample, geojson=counties, locations='fipss', color='utility',
                            color_continuous_scale=colorscale,
                            range_color=(0, up_ceil),
                            scope="usa",
                            labels={'Utility': 'Utility'},
                            title='Serious patient per Icu bed'
                            )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

        fig.show()

        # filenamelist = ['03-22-2020.csv','03-23-2020.csv','03-24-2020.csv','03-25-2020.csv','03-26-2020.csv',]
        # for i in filenamelist:

    def drawicubeds(self,up_ceil,colorstyle):
        df_sample = pd.read_csv('utility.csv')
        df_sample = df_sample.dropna()
        fip_list = df_sample['FIPS'].to_list()
        utility_list = df_sample['utility'].tolist()
        fip_list_str = []
        for i in fip_list:
            new = int(i)
            new = str(new)
            if len(new) < 5:
                new = '0' * (5 - len(new)) + new
            fip_list_str.append(new)
        df_sample['fipss'] = fip_list_str
        if colorstyle == 1:
            colorscale = ['#ffffff', '#ffeff0', '#ffdfe0', '#ffcfd1', '#ffbfc1', '#ffafb2', '#ff9fa2',
                          '#ff8f93', '#ff8083', '#ff7074', '#ff6064', '#ff5055', '#ff4045', '#ff3036',
                          '#ff2026', '#ff1017', '#ff0007']
        else:
            colorscale = ['#ffffff',
                          '#edfff5',
                          '#dbffea',
                          '#c8ffe0',
                          '#b6ffd5',
                          '#a4ffcb',
                          '#92ffc0',
                          '#80ffb6',
                          '#6dffac',
                          '#5bffa1',
                          '#49ff97',
                          '#37ff8c',
                          '#24ff82',
                          '#12ff77',
                          '#00ff6d',
                          '#12f565',
                          '#24eb5d',
                          '#37e156',
                          '#49d74e',
                          '#5bcd46',
                          '#6dc33e',
                          '#80b937',
                          '#92ae2f',
                          '#a4a427',
                          '#b69a1f',
                          '#c89017',
                          '#db8610',
                          '#ed7c08',
                          '#ff7200',
                          '#fd6a00',
                          '#fa6301',
                          '#f85b01',
                          '#f65302',
                          '#f44b02',
                          '#f14403',
                          '#ef3c03',
                          '#ed3403',
                          '#ea2d04',
                          '#e82504',
                          '#e61d05',
                          '#e41505',
                          '#e10e06',
                          '#df0606', ]

        fig = px.choropleth(df_sample, geojson=counties, locations='fipss', color='icu_beds',
                            color_continuous_scale=colorscale,
                            range_color=(0, up_ceil),
                            scope="usa",
                            labels={'Confirmw cases': 'Confirmed cases'},
                            title ='Total ICU beds'
                            )
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

        fig.show()



if __name__ == '__main__':

    drawpicture = DrawPicture('03-25-2020.csv',0.1)
    #first parameter is the files name in data folder
    #second parameter is the ICU factor, is an estimate propotion of confirmed cases who need ICU beds.
    drawpicture.cleandata()
    drawpicture.drawconfirmed(150,2)
    #the first prameter 150 is the ceil of picture
    #the second prameter is the color style of picture,1 is single color red, 2 is multiple color
    drawpicture.drawicuutility(0.5,2)
    drawpicture.drawicubeds(100,2)

    dirlist = os.listdir('./update_data/')
    for i in dirlist:
        drawpicture = DrawPicture(i, 0.1)
        drawpicture.cleandata()
        drawpicture.drawicuutility(0.5,2)



