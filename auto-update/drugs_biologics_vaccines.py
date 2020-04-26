import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
#import requests
from io import StringIO
import sys
import matplotlib.pyplot as plt
import re

#reload(sys)
#sys.setdefaultencoding('utf8')

## query directly from googlesheet 
df = pd.read_csv('https://docs.google.com/spreadsheets/d/1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw/export?format=csv&id=1-kTZJZ1GAhJ2m4GAIhw1ZdlgO46JpvX0ZQa232VWRmw&gid=1410737911')


##########generate country plot

def dropna_col(df, col=None):
    df.reset_index(drop=True, inplace=True)
    if col is None:
        return df.dropna()
    else:
        df_s1 = df[[col]]
        indlist = list(df_s1.dropna().index)
        return df.loc[indlist]
        
#find country of sponsor, if multiple countries, count multiple times
a = list(df['Country of Sponsor/Collaborator'].unique())
b = [len(df[df['Country of Sponsor/Collaborator']==x]) for x in a]
df_cos = pd.DataFrame(data={'Country of Sponsor/Collaborator':a, 'count':b}).sort_values(by='count', ascending=False)

new_data = []
for i in range(0, len(df_cos)):
    
    stop = False
    while stop is False:
        s1 = str(df_cos.iloc[i,0]).find(';')
        if s1 == -1:
            stop = True
        else:
            s2 = df_cos.iloc[i,0][0:s1]
            df_cos.iloc[i,0] = df_cos.iloc[i,0][s1+2:]
            if s2 in df_cos.iloc[i,0]:
                stop = False
            else:
                new_data.append([s2, df_cos.iloc[i,1]])
df_new = pd.DataFrame(data=new_data, columns=['Country of Sponsor/Collaborator', 'count'])

df_cos = pd.concat([df_cos, df_new])
df_cos.reset_index(drop=True, inplace=True)

for name in list(df_cos['Country of Sponsor/Collaborator'].unique()):
    df_s1 = df_cos[df_cos['Country of Sponsor/Collaborator']==name]
    s1 = np.sum(df_s1['count'])
    df_cos['count'].loc[list(df_s1.index)] = s1
df_cos = df_cos.drop_duplicates(subset='Country of Sponsor/Collaborator').dropna()
        
df_cos.sort_values(by='count', ascending=False, inplace=True)
df_cos.reset_index(drop=False, inplace=True)
#remove for obvious reasons:
df_cos.drop(list(df_cos[df_cos['Country of Sponsor/Collaborator'].str.contains('Taiwan')].index), axis=0, inplace=True)
df_cos.drop(list(df_cos[df_cos['Country of Sponsor/Collaborator'].str.contains('Maca')].index), axis=0, inplace=True)

fig, ax = plt.subplots(figsize=(15,8))
bars = ax.bar(np.arange(len(df_cos)), df_cos['count'], 0.75)
ax.set_ylabel('Trial Count', fontdict={'fontsize': 16})
ax.set_title('Countries', fontdict={'fontsize': 16})
ax.set_xticks(np.arange(len(df_cos)))
ax.set_xticklabels(list(df_cos['Country of Sponsor/Collaborator']), rotation='vertical')
ax.set_xlabel(' ')

for bar in bars:
    height = bar.get_height()
    ax.annotate('{}'.format(height),
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points", ha='center', va='bottom')

fig.savefig('figure_countries.png', bbox_inches='tight')


df1 = df #make copy of original dataframe
df1['Abstract'] = df1['Abstract'].str.lower()
df1['Brief title'] = df1['Brief title'].str.lower()
df1['Intervention'] = df1['Intervention'].str.lower()
df1.fillna(value='None', inplace=True)
df1.reset_index(drop=True, inplace=True)

#count of vaccines
df_v = pd.concat([df1[df1['Intervention'].str.contains('vaccine')], df1[df1['Brief title'].str.contains('vaccine')]]).drop_duplicates(subset='Trial ID')
print('Number of vaccine trials:', len(df_v))

##########lurong
df_v[["Trial ID","Title","Phase","Intervention"]].to_csv('vaccine.csv', index=False)


#count of biologics
df_i2 = pd.concat([df1[df1['Intervention'].str.contains('mab')], df1[df1['Intervention'].str.contains('biolog')], 
                   df1[df1['Abstract'].str.contains('mab')], df1[df1['Abstract'].str.contains('biolog')],
                   df1[df1['Intervention'].str.contains('antibod')], df1[df1['Abstract'].str.contains('antibod')],
                   df1[df1['Abstract'].str.contains('protein')], df1[df1['Intervention'].str.contains('cell')],
                   df1[df1['Abstract'].str.contains('cell')], df1[df1['Intervention'].str.contains('protein')], df1[df1['Intervention'].str.contains('plasma')]]).drop_duplicates(subset='Trial ID')

#remove vaccines from biologics
for i in range(0, len(df_v)):
    try:
        df_i2.drop(list(df_v.index)[i], axis=0, inplace=True)
    except:
        pass

#get clinical trials from 'mab' keyword
biologics = []
biologic_trials = []
for i in range(0, len(df_i2)):
    s1 = df_i2['Intervention'].iloc[i].replace(';', '').replace('(', '').replace(')', '').replace(',', '').replace('+', ' ').replace('-', ' ').replace('/', ' ').split()
    substring = 'mab'
    substring_in_list = list(dict.fromkeys([string for string in s1 if substring in string]))
    
    if substring_in_list != []:
        biologic_trials.append(i)
    biologics.extend(substring_in_list)

#get clinical trials based on key words
df_i3 = df_i2[df_i2['Intervention'].str.contains('cell')]
df_i4 = df_i2[df_i2['Intervention'].str.contains('plasma')]
df_i5 = df_i2.iloc[biologic_trials, :]

df_b = pd.concat([df_i3, df_i4, df_i5]).drop_duplicates(subset='Trial ID')
print('Number of biological drug trials:', len(df_b))

############lurong
df_b[["Trial ID","Title","Phase","Intervention"]].to_csv('biologics.csv', index=False)

###################DRUG LIST##############################################
druglist = pd.read_excel('nlp_drug_disease.xlsx', sheet_name=1)
#druglist = pd.read_csv('integrity_all_drugname_smile_unique_mergeddb.csv')
druglist['DRUG_NAME'] = druglist['DRUG_NAME'].str.lower()

druglist['length'] = [len(str(x)) for x in druglist['DRUG_NAME'].tolist()]
druglist.dropna(inplace=True)
ct_idx = []
drug = []
drugcount = []
dates = []
idx = []
druglist = druglist[druglist['length'] >= 5] #from kaggle, keep only names >5


df1['Intervention1'] = df1['Intervention'].str.lower()
for i in range(0, len(df1)):
    s1 = df1['Intervention1'].iloc[i].replace('(', '( ').replace(')', ') ').replace('/', ' ').replace('+', ' + ').replace('-', ' - ')
    df1['Intervention1'].iloc[i] = ' ' + s1 + ' '
    
df1.sort_values(by='Date added', ascending=False, inplace=True)

df1.drop(list(df1[df1['Intervention1'].str.contains('supplement')].index), axis=0, inplace=True)
df1.drop(list(df1[df1['Intervention1'].str.contains('traditional')].index), axis=0, inplace=True)
df1.drop(list(df1[df1['Intervention1'].str.contains('water')].index), axis=0, inplace=True)
df1.drop(list(df1[df1['Intervention1'].str.contains('vaccine')].index), axis=0, inplace=True)
df1.sort_values(by='Date added', ascending=False, inplace=True)
df1.reset_index(drop=True, inplace=True)

####  TODO (DONE)
### should have better way than nested loop (fixed by using inner merge of 2 sets of lists)

for i in range(0, len(df1)):
    s1 = list(dict.fromkeys(df1['Intervention1'].iloc[i].split(' ')))
    s2 = list(set(s1) & set(list(druglist['DRUG_NAME'])))
    if len(s2) > 0:
        ct_idx.extend(s2)
        drugcount.append(1)
        dates.append(df1['Date added'].iloc[i])
        idx.append(i)

print('Number of drugs (all) Trials:', np.sum(drugcount))
df_d = df1.loc[idx, :].drop_duplicates(subset='Trial ID').reset_index(drop=True)
df_d2 = pd.DataFrame(data={'Treatment':ct_idx, 'Count':1}) #merged changes to column names

for all1 in list(df_d2['Treatment'].unique()):
    i1 = list(df_d2[df_d2['Treatment'] == all1].index)
    df_d2['Count'].loc[i1] = int(len(df_d2[df_d2['Treatment'] == all1]))


#create blacklist, some borrowed from kaggle list, keep 'mab' in final list
blacklist = ['plasma', 'serum', 'cell', 'biolog', 'vaccine', 'honey', 'injection', 'glucose', 'perform', 'ethanol', 'methanol', 'paraffin', 'soybean', 'horseradish', 'ginger',' mouthwash', 'oregano', 'formaldehyde', 'alcohol']
for words in blacklist:
    df_d2.drop(list(df_d2[df_d2['Treatment'].str.contains(words)].index), axis=0, inplace=True)
    df_d.drop(list(df_d[df_d['Intervention1'].str.contains(words)].index), axis=0, inplace=True)
#df_d2.drop(list(df_d2[df_d2['drug'].str.contains('mab')].index), axis=0, inplace=True) #(let's add antibody)
print('Number of all drug trials (corrected):', len(df_d)) #after dropping keywords from blacklist

#change first letter to uppercase (for loop is most effective method, df[].str[0].upper() cannot batch operate)
for i in range(0, len(df_d2)):
    s1 = df_d2['Treatment'].iloc[i][0].upper()
    df_d2['Treatment'].iloc[i] = s1 + df_d2['Treatment'].iloc[i][1:]

df_d_clean=df_d2.drop_duplicates().sort_values(by='Treatment').sort_values(by='Count', ascending=False)
df_d_clean.to_csv('druglist.csv', index=False)
df_d[["Trial ID","Title","Phase","Intervention"]].to_csv('all_drugs.csv', index=False)

######lurong plot
ax = df_d_clean.plot.barh(figsize=(13, 50), x='Treatment', y='Count', color='green')
ax.invert_yaxis()
for i in ax.patches:
    ax.text(i.get_width()+.3, i.get_y()+.38, str(int(i.get_width())), fontsize=8, color='black')
plt.title('Number of clinical trials on each treatment ')
plt.xlabel('Number of Clinical Trials')
plt.ylabel(' ')
ax.get_legend().remove()
plt.savefig("figure_drugs_treatment.png", bbox_inches='tight')

####### pie plot - merged implementations
# Pie chart, where the slices will be ordered and plotted counter-clockwise:
clinical_trial_type = ['Small Molecule Drugs', 'Biologics', 'Vaccines']
clinical_trial_count = [len(df1.loc[idx].drop_duplicates(subset='Trial ID')), len(df_b), len(df_v)]
explode = (0, 0, 0.1)  # only "explode" the vaccine

fig, ax = plt.subplots(figsize=(8,8))

def func(pct, allvals):
    absolute = int(pct/100.*np.sum(allvals))
    return "{:.1f}%\n({:d})".format(pct, absolute)

wedges, texts, autotexts = ax.pie(clinical_trial_count, labels=clinical_trial_type, 
                                  explode=explode, shadow=True, startangle=90,
                                  autopct=lambda pct: func(pct, clinical_trial_count),
                                  textprops={'fontsize':10})
ax.set_title('Number of Trials in each Therapeutic Area', fontdict={'fontsize':14})
ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
fig.savefig('figure_types.png', bbox_inches='tight')


##update daily directly to the website (TODO)

'''
README:
#Input: 
    1. Google Doc dimensions.ai Clinical Trials csv output object into pandas dataframe
    2. nlp_drug_disease.xlsx, sheet='drug_name' as drugs list lookup table

#Output: 
    1. DataFrame subsets of biologics, vaccines, and drugs
    2. Bar graph of clinical trial by location
    3. Bar graph of therapeutics
    4. Pie chart of 3 different types of treatments
    5. Therapeutics used/counts table

# TODO LIST
1. Generate Drug List and figures (DONE)
2. Generate updated figures using format matploblib can support on terminal (DONE)
3. Use csv2md.py to generate md table? (Available, not implemented in script. Currently implemented manually on website)
4. Update figures and markdown using shell/python scripts
5. Update website using git push, mkdocs automatically, likely once every 24 hours

'''
print('Done')
