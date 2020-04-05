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
general.confirmados.plot(color='b',style='.-', legend = True, rot=70)
general.obitos.plot(color='r',style='.',legend=True, rot=70)
plt.title('Total confirmed and deceased by age')
plt.ylabel('Number of cases')
plt.xlabel('Age')
#plt.yscale('log')
plt.show()


#Percentage of deceased per age group
general['%deceased'].plot(color='g',style='.',legend=True, rot=70)
plt.title('Percentage deceased by age')
plt.ylabel('Deceased')
plt.xlabel('Age')
plt.tight_layout()
plt.show()


#All three values
general.plot(subplots = True)


####################################################################################
##################### Non aggregated Analysis - Daily view #########################
####################################################################################

## 1. Calcular número real de infectados usando a teoria do Buescu

## Calcular taxa de crescimento e taxa de crescimento real

# Projectar número de vitimas, UCI, ventiladores

# Use world meter data to calculate number of new cases versus number of  tests
