#Packages
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime

#Upload pickle
dfInt = pd.read_pickle('dfInt.pkl')

#Set a new working directory
hoje=datetime.today().strftime('%Y-%m-%d')
caminho=os.getcwd()+'/Graphs/'+hoje
if os.path.exists(caminho) == 0:
    os.mkdir(caminho)

#Create a copy of the dataframe
PT_SW =dfInt.copy()

#Change the name of some countries
def change_name(x):
    if x =='United_States_of_America':
        return 'USA'
    elif x == 'United_Kingdom':
        return 'UK'
    else:
        return x

#Set date as index and create number of death per 1M inhabitants
PT_SW.dateRep = pd.to_datetime(PT_SW.dateRep,dayfirst=True)
PT_SW.set_index('dateRep',inplace=True)
PT_SW=PT_SW.sort_index()
PT_SW.countriesAndTerritories = PT_SW.countriesAndTerritories.apply(change_name)
PT_SW = PT_SW[['countriesAndTerritories','cases','deaths','popData2018']]
PT_SW['Total_deaths']=PT_SW.groupby('countriesAndTerritories').deaths.transform('cumsum')
PT_SW['Total_cases']=PT_SW.groupby('countriesAndTerritories').cases.transform('cumsum')
#Fix UK, Italy, France and Spain numbers
PT_SW[PT_SW['countriesAndTerritories']=='UK'].loc[:,['Total_cases','Total_deaths','popData2018']] = PT_SW[PT_SW['countriesAndTerritories'].isin(['UK','Guernsey','Gibraltar','Jersey','Isle_of_Man'])].groupby('dateRep')[['Total_cases','Total_deaths','popData2018']].sum()
PT_SW[PT_SW['countriesAndTerritories']=='France'].loc[:,['Total_cases','Total_deaths','popData2018']] = PT_SW[PT_SW['countriesAndTerritories'].isin(['France','Monaco'])].groupby('dateRep')[['Total_cases','Total_deaths','popData2018']].sum()
PT_SW[PT_SW['countriesAndTerritories']=='Italy'].loc[:,['Total_cases','Total_deaths','popData2018']] = PT_SW[PT_SW['countriesAndTerritories'].isin(['Italy','San_Marino'])].groupby('dateRep')[['Total_cases','Total_deaths','popData2018']].sum()
PT_SW[PT_SW['countriesAndTerritories']=='Spain'].loc[:,['Total_cases','Total_deaths','popData2018']] = PT_SW[PT_SW['countriesAndTerritories'].isin(['Spain','Andorra'])].groupby('dateRep')[['Total_cases','Total_deaths','popData2018']].sum()
#Calculate ratios
PT_SW['cases_pop'] = PT_SW.Total_cases / (PT_SW.popData2018/1000000)
PT_SW['death_pop'] = PT_SW.Total_deaths / (PT_SW.popData2018/1000000)

#Get the max (latest), exclude small coutries and plot
country_dr = PT_SW.groupby('countriesAndTerritories').death_pop.max().sort_values(ascending=True).dropna()
exclude = ['Cases_on_an_international_conveyance_Japan','San_Marino','Andorra','Sint_Maarten','Guernsey','Gibraltar','Jersey','Monaco','Bermuda','Isle_of_Man']
plt.style.use('seaborn')
country_dr[~country_dr.index.isin(exclude)].tail(15).plot(kind='barh',color='r',alpha=0.7)
plt.title('Ranking de países em termos de mortos por milhão de habitante')
plt.xlabel('Mortos por milhão de habitante')
plt.ylabel('')
plt.savefig(caminho+'/'+'Internacional'+hoje+'jpg')
plt.show()