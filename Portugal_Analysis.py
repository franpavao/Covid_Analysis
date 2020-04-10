#Import relevante packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### Read Pickle Files

dfPT_agg = pd.read_pickle('dfPT_agg.pkl')
dfPT1 = pd.read_pickle('dfPT1.pkl')
PT_wm = pd.read_pickle(r'PT_wm.pkl')

####################################################################################
##################### Aggregated Analysis - Age and gender #########################
####################################################################################

# Melt data and analyse it
def melt_cleanse(df):
    df_melt = pd.melt(df, id_vars='data', var_name='desc', value_name='#cases')
    df_melt['#cases'] = df_melt['#cases'].fillna(0)
    df_melt['desc_split'] = df_melt['desc'].str.split('_')
    df_melt['status'] = df_melt['desc_split'].str.get(0)
    df_melt['gender'] = df_melt['desc_split'].str.get(-1)
    df_melt['age'] = df_melt['desc_split'].str.get(1) + '-' + df_melt['desc_split'].str.get(2)
    #df_melt['mid_age'] = (pd.to_numeric(df_melt['desc_split'].str.get(2),errors='coerce') + 1 + pd.to_numeric(df_melt['desc_split'].str.get(1),errors='coerce'))/2
    #df_melt['mid_age'] = df_melt['mid_age'].fillna(85)
    df_melt = df_melt.drop(columns=['desc_split', 'desc'])
    df_melt = df_melt.groupby(['status', 'gender', 'age'])['#cases'].max().reset_index()
    pivot_general = df_melt.pivot_table(values='#cases', columns='status', index='age', aggfunc=np.sum)
    pivot_gender = df_melt.pivot_table(values='#cases', columns='status', index=['age', 'gender'],
                                      aggfunc=np.sum)
    pivot_general['%deceased'] = (pivot_general['obitos'] / pivot_general['confirmados']) * 100
    pivot_gender['%deceased'] = (pivot_gender['obitos'] / pivot_gender['confirmados']) * 100
    return pivot_gender, pivot_general

#Run melt function on imported data

gender, general = melt_cleanse(dfPT_agg)

print(general)
print(gender)

#Print current death ration
print('Current death ration: ' + str((general.obitos.sum()/general.confirmados.sum())*100) + '%')

#Plot Results
#Total number of confirmed and deceased per age group
figure, axis = plt.subplots(nrows=2, ncols = 1)
general.confirmados.plot(color='b',style='.-', legend = True, ax = axis[0], title = 'Confirmed and deceased cases per age group' )
general[general.obitos!=0].obitos.plot(color='r',style='.-',legend=True, ax = axis[1], rot = 70)
plt.xlabel('Age')
plt.show()
#plt.ylabel('Number of deceased')

#Percentage of deceased per age group
figure2,axis2 = plt.subplots(nrows = 3, ncols=1)
general['%deceased'].plot(style='go',legend=True, ax = axis2[0], title='Percentage deceased per age group')
gender.loc[(slice(None),'f'),'%deceased'].plot(style = 'r*', legend = False, ax=axis2[1], title = 'Women')
gender.loc[(slice(None),'m'),'%deceased'].plot(style = 'cs', legend = False, ax=axis2[2], title = 'Men')
plt.xlabel('Age')
plt.show()

####################################################################################
##################### Non aggregated Analysis - Daily view #########################
####################################################################################

#Casos novos
dfPT1['confirmados_novos'].plot()
plt.title('Confirmados novos')
#plt.xlabel('Data')
plt.ylabel('Casos')
plt.show()

## Calcular taxa de crescimento
dfPT1['novos casos rate'] = dfPT1.confirmados.pct_change()*100
dfPT1.loc['2020-03-15':,'novos casos rate'].plot()
plt.title('Taxa de crescimento')
#plt.xlabel('Data')
plt.ylabel('Taxa')
plt.show()

# Use world meter data to calculate number of new cases versus number of  tests
PT_wm['new_tests'] = PT_wm.Total_tests - PT_wm.shift(-1).Total_tests
PT_wm['new_tests'] = PT_wm['new_tests'].fillna(0)
dfPT1['Total_tests'] = PT_wm.Total_tests
dfPT1['Total_tests'] = dfPT1['Total_tests'].fillna(0)
dfPT1['new_tests'] = PT_wm.new_tests
dfPT1['new_tests'] = dfPT1['new_tests'].fillna(0)
dfPT1['new tests rate'] = (dfPT1.confirmados_novos / dfPT1.new_tests)*100
dfPT1['Total test rate'] = (dfPT1.confirmados / dfPT1['Total_tests'])*100

#Total number of tests per day
dfPT1[dfPT1['new_tests'] != 0]['new_tests'].plot(style='.-')
plt.title('Number of tests per day')
plt.tight_layout()
plt.show()

#Plot Rate of new cases per test
dfPT1[dfPT1['new_tests'] != 0][['new tests rate','Total test rate']].plot(style='.-')
plt.title('Test positive rate')
plt.ylabel('Rate')
plt.tight_layout()
plt.show()

## Analysis on the portuguese NHS workload / strain (SNS)
#Face Value
dfPT1[['internados_uci','internados']].plot(legend=True,rot=70,kind='area',color=['r','y'])
#dfPT1[].plot(legend=True, rot=70,kind='area')
plt.title('Casos internados e cuidados intensivos')
plt.ylabel('Casos')
plt.show()

#Percentage
#Hospitalized
dfPT1['new internados'] = dfPT1.internados - dfPT1.shift(1).internados
dfPT1['internados rates'] = dfPT1.internados.pct_change()*100

#Intensive care
dfPT1['new UCI'] = dfPT1.internados_uci - dfPT1.shift(1).internados_uci
dfPT1['UCI rates'] = dfPT1.internados_uci.pct_change()*100

#Plot
dfPT1[['internados rates','UCI rates']].plot(legend = True, color=['y','r'])
plt.title('Internados e UCI rates')
plt.ylabel('rate')
plt.show()

#Casos activos recuperados e mortos
dfPT1[['obitos','recuperados']].plot(color=['r','g'], title = 'Mortos e Recuperados')
plt.show()

dfPT1['Ativos']=dfPT1.confirmados-dfPT1.obitos-dfPT1.recuperados
dfPT1[['recuperados','obitos','Ativos']].plot(kind='area',legend=True,color=['g','r','b'])
plt.show()
