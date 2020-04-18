#Packages
import pandas as pd
import matplotlib.pyplot as plt

#Upload pickle
dfInt = pd.read_pickle('dfInt.pkl')

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
PT_SW['cases_pop'] = PT_SW.Total_cases / (PT_SW.popData2018/1000000)
PT_SW['death_pop'] = PT_SW.Total_deaths / (PT_SW.popData2018/1000000)

#Get the max (latest), exclude small coutries and plot
country_dr = PT_SW.groupby('countriesAndTerritories').death_pop.max().sort_values(ascending=False).dropna()
exclude = ['Cases_on_an_international_conveyance_Japan','San_Marino','Andorra','Sint_Maarten','Guernsey','Gibraltar','Jersey','Monaco','Bermuda']
country_dr[~country_dr.index.isin(exclude)].head(15).plot(kind='bar',color='r',alpha=0.7,rot=70)
plt.savefig(caminho+'/'+'Internacional'+hoje+'jpg')
plt.show()