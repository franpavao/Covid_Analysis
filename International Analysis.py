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

#Change the name of some countries
def change_name(x):
    if x =='United_States_of_America':
        return 'USA'
    elif x in ['United_Kingdom','Guernsey','Gibraltar','Jersey','Isle_of_Man','Bermuda']:
        return 'UK'
    elif x in ['France','Monaco','Sint_Maarten']:
        return 'France'
    elif x in ['Italy','San_Marino']:
        return 'Italy'
    elif x in ['Japan','Cases_on_an_international_conveyance_Japan']:
        return 'Japan'
    elif x in ['Spain','Andorra']:
        return 'Spain'
    else:
        return x

#Create a copy of the dataframe
PT_SW =dfInt.copy()
#Set date as index and create number of death per 1M inhabitants
PT_SW.dateRep = pd.to_datetime(PT_SW.dateRep,dayfirst=True)
PT_SW.set_index('dateRep',inplace=True)
PT_SW=PT_SW.sort_index()
PT_SW['Total_deaths']=PT_SW.groupby('countriesAndTerritories').deaths.transform('cumsum')
PT_SW['Total_cases']=PT_SW.groupby('countriesAndTerritories').cases.transform('cumsum')
PT_SW.countriesAndTerritories = PT_SW.countriesAndTerritories.apply(change_name)
PT_SW = PT_SW[['countriesAndTerritories','Total_cases','Total_deaths','popData2018']]
PT_SW = PT_SW[PT_SW.index == PT_SW.index.max()]

#Get the max (latest), exclude small coutries and plot
country_dr = PT_SW.groupby(by='countriesAndTerritories')[['Total_cases','Total_deaths','popData2018']].sum().dropna()
country_dr['cases_pop'] = country_dr.Total_cases / (country_dr.popData2018/1000000)
country_dr['death_pop'] = country_dr.Total_deaths / (country_dr.popData2018/1000000)
country_dr = country_dr.dropna()
country_dr = country_dr.sort_values('death_pop', ascending=True)
plt.style.use('seaborn')
country_dr.death_pop.tail(15).plot(kind='barh',color='r',alpha=0.7)
plt.title('Ranking de países em termos de mortos por milhão de habitante')
plt.xlabel('Mortos por milhão de habitante')
plt.ylabel('')
plt.savefig(caminho+'/'+'Internacional'+hoje+'jpg')
plt.show()