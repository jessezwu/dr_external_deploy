import pandas as pd
import numpy as np

df = pd.read_csv('raw_data.csv')

filtrd = df[ ~(df['DATE'].isnull()) ].copy()
 
filtrd['ClaimDate'] = pd.to_datetime( filtrd['DATE'], format='%d/%m/%Y' )

# CHECK OUT THE NUMBER OF DATA POINTS PER LEVEL
# filtrd['ClaimDate'].value_counts()

keep_cols = [ 'FRAUD', 'ClaimDate', 'LOCALITY', 'REGION',  'GENDER', 'NUM_PI_CLAIM', 'RULE_MATCHES' ]

reducd = filtrd.loc[:, keep_cols] 

train = reducd[ reducd['ClaimDate']<'2013-04-01' ]

test = reducd[ reducd['ClaimDate']>='2013-04-01']
 
test['SCORE'] = np.random.randint(0,1000,size=( len(test) ))  /1000 

train.to_csv('train.csv', index=False)
test.to_csv('scored.csv', index=False)

