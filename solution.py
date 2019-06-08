# -*- coding: utf-8 -*-
"""
Created on Sat Feb 03 18:12:41 2018

"""

import pandas as pd
import datetime
import math
from scipy.optimize import minimize
import numpy as np

#Task 1
def conv(x):
   return pd.Period(year = x // 10000, month = x//100 % 100, day = x%100, freq='D')

df = pd.read_csv('all_transactions.csv',header = None,names = ['cust_id','trans_date'])
df['trans_date']=df['trans_date'].apply(conv)
df['month'] = df['trans_date'].dt.month
df['year'] = df['trans_date'].dt.year
df.drop_duplicates(keep='first',inplace=True)
df1 = df.query('month<10 and year==1997')
df1 = df1[['cust_id','trans_date']]
df1.to_csv('cal_period_transactions.csv',index=False)

#Task 2
df2 = pd.read_csv('cal_period_transactions.csv')
df2['trans_date'] = df2['trans_date'].astype('datetime64[ns]')
df2['day_of_year'] = df2['trans_date'].dt.dayofyear
calibaration_date = datetime.datetime(1997, 10, 1)
calibaration_dayofyear = calibaration_date.timetuple().tm_yday
df3 = df2.groupby(['cust_id']).count()
df3['cust_id'] = df2['cust_id'].unique()
df3.columns = ['x1','x2','cust_id']
df3['x'] = df3['x1']-1
df3['tx'] = (df2.groupby(['cust_id'])['day_of_year'].max() - df2.groupby(['cust_id'])['day_of_year'].min())/7
df3['T'] = (calibaration_dayofyear - df2.groupby(['cust_id'])['day_of_year'].min())/7
df3 = df3[['cust_id','x','tx','T']]
df3.to_csv('summary_customers1.csv',index=False)


#Task 3
def objective(x):
    nll=0
    r=x[0]
    alpha=x[1]
    a=x[2]
    b=x[3]
    for i in range(1,df3.shape[0]):
        x = df3.loc[i,'x']
        tx = df3.loc[i,'tx']
        T = df3.loc[i,'T']
        try:
            if x>0:
                if r<0 or alpha<0 or a<0 or b<0:
                    return float('inf')
                else:
                    nll=nll+ -(math.lgamma(r+x)+ (r * (math.log(alpha))) - math.lgamma(r) + math.lgamma(a+b) + math.lgamma(b+x) - math.lgamma(b) - math.lgamma(a+b+x) + math.log(math.exp(-(r+x)*math.log(alpha+T)) + math.exp(math.log(a) - math.log(b + x -1) - (r+x)*(math.log(alpha+tx))))) 
            else:
                if r<0 or alpha<0 or a<0 or b<0:
                    return float('inf')
                else:
                    nll=nll+ -(math.lgamma(r+x)+ (r * (math.log(alpha))) - math.lgamma(r) + math.lgamma(a+b) + math.lgamma(b+x) - math.lgamma(b) - math.lgamma(a+b+x) + math.log(math.exp(-(r+x)*math.log(alpha+T)) ))  
        except OverflowError:
                 nll=float('inf')
    return nll/df3.shape[0]
    
#Task 4
x0 = np.array([1.10,1.00,0.95,0.90])
sol = minimize(objective,x0,method='nelder-mead',options={'xtol': 1e-8, 'disp': True})

np.savetxt("estimated_parameters.csv",sol.x,delimiter=",")





