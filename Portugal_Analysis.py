#Import relevante packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime
import matplotlib.ticker as ticker


### Read Pickle Files

dfPT_agg = pd.read_pickle('dfPT_agg.pkl')
dfPT1 = pd.read_pickle('dfPT1.pkl')
PT_wm = pd.read_pickle(r'PT_wm.pkl')

#Set a new working directory
hoje=datetime.today().strftime('%Y-%m-%d')
caminho=os.getcwd()+'/Graphs/'+hoje
if os.path.exists(caminho) == 0:
    os.mkdir(caminho)

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

general['%deceased_total'] = (general.obitos / general.obitos.sum())*100
gender['%deceased_total'] = (gender.obitos / gender.obitos.sum())*100

print(general)
print(gender)

#Print current death ration
print('Current death ration: ' + str((general.obitos.sum()/general.confirmados.sum())*100) + '%')

#Plot Results
#Total number of confirmed and deceased per age group
plt.style.use('seaborn')
plt.barh(general.index, general.confirmados, color='gray')
plt.barh(general.index,general.obitos,color='red')
plt.title('Infectados e óbitos')
plt.legend(['Infectados','Óbitos'])
plt.ylabel('Faixa etária')
plt.xlabel('Número de casos')
plt.savefig(caminho+'/'+'deceased_'+hoje+'jpg')
plt.show()

#Obitos por faixa etária
bola = general[general.obitos!=0][['obitos','%deceased_total']]
explode = (0, 0, 0, 0, 0.05)
plt.pie(bola.obitos, explode=explode,labels=bola.index,autopct='%1.1f%%')
plt.title('Percentagem de mortos por faixa etária')
plt.savefig(caminho+'/'+'Percentagem_mortos_total'+hoje+'jpg')
plt.show()

#Percentage of deceased per age group
#Create Men and Women dataframe
woman = gender.loc[pd.IndexSlice[:,'f'],:]
woman.columns = ['confirmados', 'obitos', 'Women', '%deceased_total']
woman = woman['Women']
woman = woman.reset_index().set_index('age')['Women']
man = gender.loc[pd.IndexSlice[:,'m'],:]
man.columns = ['confirmados', 'obitos', 'Men', '%deceased_total']
man = man['Men']
man = man.reset_index().set_index('age')['Men']

plt.style.use('seaborn')
#To see all plot styles print(plt.style.available)
pd.concat([general['%deceased'],woman,man],axis=1).plot(kind='bar',rot=0,color=['green','orange','blue'])
plt.title('Rácio óbitos / infectados por faixa etária')
plt.legend(['Total','Mulheres','Homens'])
plt.xlabel('Faixa etária')
plt.savefig(caminho+'/'+'deceased_gender_'+hoje+'jpg')
plt.show()

####################################################################################
##################### Non aggregated Analysis - Daily view #########################
####################################################################################

#Casos novos
plt.style.use('seaborn')
plt.bar(dfPT1.index,dfPT1.confirmados_novos)
plt.title('Novos infectados')
plt.ylabel('Casos')
plt.xlabel('Data')
plt.savefig(caminho+'/'+'infectados'+hoje+'jpg')
plt.show()

## Calcular taxa de crescimento
plt.style.use('seaborn')
dfPT1['novos casos rate'] = dfPT1.confirmados.pct_change()*100
dfPT1.loc['2020-03-15':,'novos casos rate'].plot(rot=70, title='Rácio de novos infectados \ total de infectados')
plt.xlabel('Data')
plt.ylabel('Rácio')
plt.savefig(caminho+'/'+'Racio_infectados'+hoje+'jpg')
plt.show()

# Use world meter data to calculate number of new cases versus number of  tests
PT_wm['new_tests'] = PT_wm.Total_tests - PT_wm.shift(-1).Total_tests
PT_wm['new_tests'] = PT_wm['new_tests'].fillna(0)
dfPT1['Total_tests'] = PT_wm.Total_tests
dfPT1['Total_tests'] = dfPT1['Total_tests'].fillna(0)
dfPT1['new_tests'] = PT_wm.new_tests
dfPT1['new_tests'] = dfPT1['new_tests'].apply(lambda a: (abs(a)+a)/2 )
dfPT1['new_tests'] = dfPT1['new_tests'].fillna(0)
dfPT1['new tests rate'] = (dfPT1.confirmados_novos / dfPT1.new_tests)*100
dfPT1['Total test rate'] = (dfPT1.confirmados / dfPT1['Total_tests'])*100

#Total number of tests per day
plt.style.use('seaborn')
#Fix the xlabel issue
ticklabels = ['']*len(dfPT1.loc['2020-04-04':].index)
# Every 4th ticklable shows the month and day
ticklabels[::4] = [item.strftime('%b %d') for item in dfPT1.loc['2020-04-04':].index[::4]]
#To see all plot styles print(plt.style.available)
dfPT1.loc['2020-04-04':,'Total_tests'].plot(kind='bar',color='blue',rot=0,title='Número de testes por dia',alpha=0.5).xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
dfPT1.loc['2020-04-04':,'new_tests'].plot(kind='bar',color='brown',rot=0,title='Número de testes por dia').xaxis.set_major_formatter(ticker.FixedFormatter(ticklabels))
plt.ylabel('Número de testes')
plt.xlabel('Data')
plt.legend(['Total de testes','Testes novos'])
plt.savefig(caminho+'/'+'Testes'+hoje+'jpg')
plt.show()

#Plot Rate of new cases per test
plt.style.use('seaborn')
dfPT1.loc['2020-04-04':,['new tests rate','Total test rate']].plot(style='.-',rot=70,title='Rácio de infectados / Número de testes')
plt.ylabel('Rácio')
plt.xlabel('Data')
plt.legend(['Rácio diário','Rácio total infectados/testes'])
plt.tight_layout()
plt.savefig(caminho+'/'+'Racio_testes'+hoje+'jpg')
plt.show()

## Analysis on the portuguese NHS workload / strain (SNS)
#Face Value
plt.style.use('seaborn')
dfPT1[['internados_uci','internados']].plot(legend=True,rot=70,kind='area',color=['r','y'])
plt.title('Casos internados e cuidados intensivos')
plt.ylabel('Casos')
plt.xlabel('Data')
plt.title('Casos Internados e em cuidados intensivos')
plt.legend(['Cuidados Intensivos','Internados'])
plt.savefig(caminho+'/'+'Internados e UCI'+hoje+'jpg')
plt.show()

#Percentage
#Hospitalized
dfPT1['new internados'] = dfPT1.internados - dfPT1.shift(1).internados
dfPT1['internados rates'] = dfPT1.internados.pct_change()*100

#Intensive care
dfPT1['new UCI'] = dfPT1.internados_uci - dfPT1.shift(1).internados_uci
dfPT1['UCI rates'] = dfPT1.internados_uci.pct_change()*100

# Hospitalized and in intensive care
dfPT1['rate internados em UCI'] = (dfPT1.internados_uci / dfPT1.internados)*100

#UCI rate plot
dfPT1['rate internados em UCI'].plot(legend=False, rot=70)
plt.title('Rácio cuidados intensivos / internados')
plt.ylabel('Rácio')
plt.xlabel('Data')
plt.savefig(caminho+'/'+'Racio UCI'+hoje+'jpg')
plt.show()

#Casos activos recuperados e mortos
dfPT1[['obitos','recuperados']].plot(color=['r','g'], rot=70, title='Recuperados e Óbitos')
plt.legend(['Óbitos','Recuperados'])
plt.xlabel('Data')
plt.ylabel('Casos')
plt.savefig(caminho+'/'+'Recuperados_Obitos'+hoje+'jpg')
plt.show()

#Casos Activos
dfPT1['Ativos']=dfPT1.confirmados-dfPT1.obitos-dfPT1.recuperados
dfPT1[['recuperados','obitos','Ativos']].plot(kind='area',color=['g','r','b'],title='Ativos, recuperados e óbitos',rot=70,alpha=0.7)
plt.legend(['Recuperados','Óbitos','Ativos'])
plt.xlabel('Data')
plt.ylabel('Casos')
plt.savefig(caminho+'/'+'Ativos'+hoje+'jpg')
plt.show()