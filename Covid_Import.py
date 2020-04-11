#### Extract data ###
import pandas as pd
import os, sys
from datetime import date
from selenium import webdriver
import re

######## Portugal ################

# Import data from Git Hub for Portugal
portugal = 'https://raw.githubusercontent.com/dssg-pt/covid19pt-data/master/data.csv'

# Transform Portugal data in a df
df = pd.read_csv(portugal)

#Change the format of columns
df.data = pd.to_datetime(df.data, dayfirst=True)
df.data_dados = pd.to_datetime(df.data_dados, dayfirst=True)

#Change NA values to 0

#Set function
def NA_zero(df,l):
    for i in l:
        df[i] = df[i].fillna(0)
    return df

#Define columns to be cleansed
cleansePT =  ['obitos_0_9_f','obitos_0_9_m','confirmados_0_9_f', 'confirmados_0_9_m', 'confirmados_10_19_f', 'confirmados_10_19_m', 'confirmados_20_29_f',
            'confirmados_20_29_m', 'confirmados_30_39_f', 'confirmados_30_39_m', 'confirmados_40_49_f', 'confirmados_40_49_m',
            'confirmados_50_59_f', 'confirmados_50_59_m', 'confirmados_60_69_f', 'confirmados_60_69_m', 'confirmados_70_79_f',
            'confirmados_70_79_m', 'confirmados_80_plus_f', 'confirmados_80_plus_m', 'obitos_10_19_f', 'obitos_10_19_m',
            'obitos_20_29_f','obitos_20_29_m','obitos_30_39_f','obitos_30_39_m','obitos_40_49_f', 'obitos_40_49_m',
            'obitos_50_59_f', 'obitos_50_59_m', 'obitos_60_69_f', 'obitos_60_69_m','obitos_70_79_f', 'obitos_70_79_m',
            'obitos_80_plus_f', 'obitos_80_plus_m','suspeitos', 'confirmados', 'confirmados_novos', 'recuperados', 'obitos',
            'internados', 'internados_uci','lab', 'vigilancia', 'n_confirmados','confirmados_f', 'confirmados_m', 'obitos_f',
            'obitos_m']

#Run function on list of cleansed columns
dfPT = NA_zero(df,cleansePT)

#hopkins_df = pd.read_csv(hopkins_git)

# First batch of columns to keep
keepPT1 = ['data', 'suspeitos', 'confirmados', 'confirmados_novos', 'recuperados', 'obitos', 'internados', 'internados_uci',
        'lab', 'vigilancia', 'n_confirmados','confirmados_f', 'confirmados_m', 'obitos_f', 'obitos_m']

dfPT1 = df[keepPT1]

#Set the index
dfPT1 = dfPT1.set_index(dfPT1.data)

#Batch of columns for melt confirmed and deceased
keep_meltPT2 = ['data', 'confirmados_0_9_f', 'confirmados_0_9_m', 'confirmados_10_19_f', 'confirmados_10_19_m', 'confirmados_20_29_f',
            'confirmados_20_29_m', 'confirmados_30_39_f', 'confirmados_30_39_m', 'confirmados_40_49_f', 'confirmados_40_49_m',
            'confirmados_50_59_f', 'confirmados_50_59_m', 'confirmados_60_69_f', 'confirmados_60_69_m', 'confirmados_70_79_f',
            'confirmados_70_79_m', 'confirmados_80_plus_f', 'confirmados_80_plus_m', 'obitos_0_9_f','obitos_0_9_m', 'obitos_10_19_f', 'obitos_10_19_m','obitos_20_29_f','obitos_20_29_m','obitos_30_39_f','obitos_30_39_m',
                    'obitos_40_49_f', 'obitos_40_49_m', 'obitos_50_59_f', 'obitos_50_59_m', 'obitos_60_69_f', 'obitos_60_69_m',
                    'obitos_70_79_f', 'obitos_70_79_m', 'obitos_80_plus_f', 'obitos_80_plus_m']

dfPT_agg = df[keep_meltPT2]

## Save files as pickles
dfPT_agg.to_pickle('dfPT_agg.pkl')
dfPT1.to_pickle('dfPT1.pkl')

###########################################################################################
############################ Total tests for Portugal #####################################
###########################################################################################

class Coronavirus():
  def __init__(self):
    self.driver = webdriver.Chrome()

bot = Coronavirus()
bot.driver.get('https://www.worldometers.info/coronavirus/')

table = bot.driver.find_element_by_xpath('//*[@id="main_table_countries_today"]/tbody[1]')
country_element = table.find_element_by_xpath("//td[contains(., 'Portugal')]")
row = country_element.find_element_by_xpath("./..")
data = row.text.split(" ")

bot.driver.close()

# Cleanse the data received
colunas = ['Country','total_cases','new_cases','total_deaths','new_deaths', 'active_cases', 'total_recovered', 'serious_critical',
              'Total_cases_pop', 'Total_deaths_pop', 'Total_tests', 'Total_tests_pop', 'Timestamp']

num = ['total_cases','new_cases','total_deaths','new_deaths', 'active_cases', 'total_recovered', 'serious_critical',
              'Total_cases_pop', 'Total_deaths_pop', 'Total_tests', 'Total_tests_pop']

novo = [re.sub('\+','',re.sub(',','',i)) for i in data]
novo = novo + [date.today()]
PT_wm = pd.DataFrame(novo).T
PT_wm.columns = colunas
PT_wm = PT_wm.set_index(PT_wm.Timestamp)
for i in num:
  PT_wm[i] = pd.to_numeric(PT_wm[i])

#Read existing pickle
old_wm = pd.read_pickle(r'PT_wm.pkl')

#Append new data to existing pickle
PT_wm = PT_wm.append(old_wm)
PT_wm = PT_wm.drop_duplicates()

## Save files as pickles
PT_wm.to_pickle('PT_wm.pkl')

########################################################################################
################################# International ####################################
########################################################################################

# Extract data from the website
#save url. Save it as data frame
csv_url = 'https://opendata.ecdc.europa.eu/covid19/casedistribution/csv'
dfInt = pd.read_csv(csv_url, sep = ',', encoding='latin-1') #2. To a dataframe
#today = date.today()

#Save International file in a Pickle
dfInt.to_pickle('dfInt.pkl')