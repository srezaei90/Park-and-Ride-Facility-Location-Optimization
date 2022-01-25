""" 
Created on Mon Jun 21 18:24:13 2021

@author: Dr. Anahita Khojandi, Shahrbanoo Rezaei

Please contact the authors using "khojandi@utk.edu" or "srezaei@vols.utk.edu" if you have any questions.
"""

"""
This code analyzes Approach 2 to estimate the coefficients of variables in the P&R utility function in the context of the coefficients of attributes for the existing modes. 
"""
#### Import required packages
import pandas as pd
import numpy as np
import time
import os
from pyomo.environ import *

#### User Inputs
user_alph = float(input("Please enter a value between 0 and 1 for Alpha in Approach 2: \n"))
solv = input("Please identify the solver. You can enter gurobi, cbc or glpk \n")
print('*************** The model is running ***************')

#### Data Directory
path_parent = os. path. dirname(os. getcwd())
os. chdir(path_parent)
data_dir = os. getcwd()

#### Import datasets
df = pd.read_csv(data_dir+'\data_P&R.csv') 
df_array = np.array(df)

df2 = pd.read_csv(data_dir+'\MNL_bal_Coef_output.csv')
res = np.array(df2)
result = np.median(res,axis=0).reshape(1,-1) ## Get the median of coefficients over 10 fold

df3 = pd.read_csv(data_dir+'\Transit_time_P&R_CBD.csv')
T_Time_P_CBD = np.array(df3).tolist()[0]


#### Identifying “representatives” who presented the median characteristics of those individuals in each zone. 
unique_elements, count_elements = np.unique(df_array[:,-1],return_counts=True)
it = -1
fc=0
for i in unique_elements:
    da = df_array[df_array[:,-1]==i]
    u, c = np.unique(da[:,0],return_counts=True)
    fc = fc+u.shape[0]

data = np.zeros((fc,df_array[:,1:-5].shape[1]+1))
it = -1
demand=[]
for i in unique_elements:
    da = df_array[df_array[:,-1]==i]
    u, c = np.unique(da[:,0],return_counts=True)
    it2=-1
    for j in u:
        it = it+1
        a = da[da[:,0]==j]
        da_median = np.median(a[:,1:-5],axis=0)
        it2=it2+1
        data[it,1:] = da_median
        data[it,0] = i
        demand.append(c[it2])

#### number of individuals
I = data.shape[0]
### number of other modes
om =3
#### number of Existing PR
ep = 14
#### number of Candidate PR
cp = len(T_Time_P_CBD)-ep
#### number of TPR
PR = len(T_Time_P_CBD)
#### number of modes
N_M = om + PR


#### manually recalculated and adjusted the estimated P&R "travel time" which obtained from dataset
Y=[[1]*(PR) for i in range(I)]
Y=np.zeros((I,PR))
it=-1
for taz in data[:,0]:
    it=it+1
    OrNa = df_array[df_array[:,-1]==taz][0,-2]
    if OrNa == 'Maury':
        Y[it,:] = [1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0,  0,0,1,1,1,1,1, 1,1,1,1]
    elif OrNa == 'Robertson':
        Y[it,:] = [0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1,  1,1,0,0,0,0,0, 0,0,0,0]
    elif OrNa == 'Rutherford':
        Y[it,:] = [1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0,  0,0,1,1,1,1,1, 1,1,1,1]
    elif OrNa == 'Wilson':
        Y[it,:] = [0, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1,  1,1,1,1,1,1,1, 0,0,0,0]
    elif OrNa == 'Sumner':
        Y[it,:] = [0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1,  1,1,0,0,0,0,0, 0,0,0,0]
    elif OrNa == 'Williamson':
        Y[it,:] = [1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0,  0,0,1,1,1,1,1, 1,1,1,1]
    elif OrNa == 'Far South':
        Y[it,:] = [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,0,0,0,0,0,0, 0,0,0,1]
    elif OrNa == 'Far NE':
        Y[it,:] = [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0,  1,1,0,0,0,0,0, 0,0,0,0]    
    elif OrNa == 'Far North':
        Y[it,:] = [0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0,  0,0,0,0,0,0,0, 0,0,0,0]
    elif OrNa == 'Far West':
        Y[it,:] = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0,0,0,0,0,0,0, 0,0,0,0]
    elif OrNa == 'East':
        Y[it,:] = [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,  0,0,0,0,1,1,1, 0,0,1,1]   
    elif OrNa == 'Far SE':
        Y[it,:] = [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0,  0,0,0,0,1,1,1, 0,0,1,1]
        
for i in range(data.shape[0]):
    data[i,26:] = data[i,26:]+(1-Y[i,:])*100
Y = Y.tolist()

#### define cost or utility of modes
cost=[[0]*N_M for i in range(I)]

for i in range(I):
    #SOV
    cost[i][0] = result[0,46] * data[i,23] 
    #HOV
    cost[i][1] = result[0,0] + result[0,2] * data[i,1] + result[0,4] *data[i,2] + result[0,6] * data[i,3] + result[0,8] * data[i,4] + result[0,10] * data[i,5] + result[0,12] * data[i,6] + result[0,14] * data[i,7] + result[0,16] * data[i,8] + result[0,18] *data[i,9] + result[0,20] * data[i,10] + result[0,22] * data[i,11] + result[0,24] * data[i,12] + result[0,26] * data[i,13] + result[0,28] *data[i,14] + result[0,30] * data[i,15]  + result[0,32] * data[i,16] + result[0,34] * data[i,17] + result[0,36] * data[i,18] + result[0,38] * data[i,19] + result[0,40] * data[i,20] + result[0,42] * data[i,21] + result[0,44] * data[i,22] + result[0,47] * data[i,24]  
    #Transit
    cost[i][2] = result[0,1] + result[0,3] * data[i,1] + result[0,5] *data[i,2] + result[0,7] * data[i,3] + result[0,9] * data[i,4] + result[0,11] * data[i,5] + result[0,13] * data[i,6] + result[0,15] * data[i,7] + result[0,17] * data[i,8] + result[0,19] *data[i,9] + result[0,21] * data[i,10] + result[0,23] * data[i,11] + result[0,25] * data[i,12] + result[0,27] * data[i,13] + result[0,29] *data[i,14] + result[0,31] * data[i,15]  + result[0,33] * data[i,16] + result[0,35] * data[i,17] + result[0,37] * data[i,18] + result[0,39] * data[i,19] + result[0,41] * data[i,20] + result[0,43] * data[i,21] + result[0,45] * data[i,22] + result[0,48] * data[i,25] 
       
# Utility of P&R using Approach 2
alph = user_alph #HOV
bet = 1-alph   #Transit

for k in range(PR):
    for i in range(I):
        cost[i][k+3] =  alph*(result[0,0] + result[0,2] * data[i,1] + result[0,4] *data[i,2] + result[0,6] * data[i,3] + result[0,8] * data[i,4] + result[0,10] * data[i,5] + result[0,12] * data[i,6] + result[0,14] * data[i,7] + result[0,16] * data[i,8] + result[0,18] *data[i,9] + result[0,20] * data[i,10] + result[0,22] * data[i,11] + result[0,24] * data[i,12] + result[0,26] * data[i,13] + result[0,28] *data[i,14] + result[0,30] * data[i,15]  + result[0,32] * data[i,16] + result[0,34] * data[i,17] + result[0,36] * data[i,18] + result[0,38] * data[i,19] + result[0,40] * data[i,20] + result[0,42] * data[i,21] + result[0,44] * data[i,22]) \
                        +bet*( result[0,1] + result[0,3] * data[i,1] + result[0,5] *data[i,2] + result[0,7] * data[i,3] + result[0,9] * data[i,4] + result[0,11] * data[i,5] + result[0,13] * data[i,6] + result[0,15] * data[i,7] + result[0,17] * data[i,8] + result[0,19] *data[i,9] + result[0,21] * data[i,10] + result[0,23] * data[i,11] + result[0,25] * data[i,12] + result[0,27] * data[i,13] + result[0,29] *data[i,14] + result[0,31] * data[i,15]  + result[0,33] * data[i,16] + result[0,35] * data[i,17] + result[0,37] * data[i,18] + result[0,39] * data[i,19] + result[0,41] * data[i,20] + result[0,43] * data[i,21] + result[0,45] * data[i,22]) \
                        +(alph*result[0,47] + bet*result[0,48] ) * (data[i,26+k] + T_Time_P_CBD[k])           
cost=np.around(cost, decimals=2)
cost=cost.tolist()

#### the number of candidate P&R can be opened:
pp=0 #As in this stage, we just want to evaluate Approach 2, we set pp=0

print(' ******************************** optimization model (MILP) ********************************')
#### Construct the model
print('\n','Constructing the MILP model variables and constraints')
st=time.time()

# Defining concrete model in pyomo
model = ConcreteModel()

# Defining decision variables
model.OM = range(om)
model.EP = range(ep)
model.CP = range(cp)
model.nCP = range(om+ep)
model.PR = range(PR)
model.kk = range(N_M)
model.I = range(I)
model.x = Var(model.kk, within=Binary)
model.p = Var(model.I, model.kk, within=NonNegativeReals, bounds=(0,None))

# Defining objective function
model.obj = Objective( expr = sum( demand[i]*model.p[i,k+3] for i in model.I for k in model.PR ),sense=maximize ) #-200*sum( model.x[i+17] for i in model.CP )

# Defining constraints
model.c1 = ConstraintList()
for i in model.I:
    model.c1.add( sum( model.p[i,k] for k in model.kk ) == 1.0 )

model.c2 = ConstraintList()
for i in model.I:
    for k in model.kk:
        model.c2.add( model.p[i,k] <= model.x[k] )    

model.c3 = ConstraintList()
for i in model.I:
    for k in model.kk:
        for k2 in model.kk:
            model.c3.add( model.p[i,k]<=((np.exp(cost[i][k])/np.exp(cost[i][k2]))*model.p[i,k2])+(1-model.x[k2])) 
            
model.c5 = Constraint( expr=sum( model.x[k+3+14] for k in model.CP ) == pp ) 

model.c6 = ConstraintList()
for k in model.nCP:
     model.c6.add( model.x[k] == 1.0 )
    
ft=time.time()
print('\n','Time to model MILP:',round(ft-st),'seconds')

#### Find the MILP solution
print('\n','Solving the MILP model')
st=time.time()

if solv == 'glpk':
    opt = SolverFactory('glpk')
elif solv == 'cbc':
    opt = SolverFactory('cbc', executable="cbc.exe")
elif solv == 'gurobi':
    opt = SolverFactory('gurobi')

opt.solve(model) 

ft=time.time()
print('\n','Time to solve the MILP:',round(ft-st),'seconds')

print('\n','**************************** Analyazing the model output ****************************')
np.random.seed(0)
n_origin=I
kk=N_M

### take optimal solutions from the optimization model
x_Att=[model.x[a].value for a in range(kk)]
p_Att_a=[model.p[i,0].value for i in range(n_origin)]
p_Att_h=[model.p[i,1].value for i in range(n_origin)] 
p_Att_t=[model.p[i,2].value for i in range(n_origin)]
p_Att_k=[[model.p[i,k].value for k in range(3,3+PR)] for i in range(n_origin)]
p_Att=[[model.p[i,k].value for k in range(N_M)] for i in range(n_origin)]

p = np.array(p_Att)

#### post processing
for i in range(p.shape[0]):
    c=0
    for k in range(p.shape[1]):
        if p[i,k] < 0.02:
            if k >=3:
                c = c+p[i,k]
                p[i,k]=0
    v=[]
    for k in range(p.shape[1]):
        if k >=3:
            if p[i,k] >0:
                v.append(k)
    cc = c/(len(v)+0.00000006)
    for k in v:
        p[i,k] = p[i,k] + cc

aa = np.sum(p,axis=1).reshape(3759,1)
p = p/aa

#### Saving results (modes' usage) of the MILP model based on each county and each mode
demand = np.array(demand).reshape(3759,1)
cpp = p*demand

dd = np.zeros((data.shape[0],cpp.shape[1]+1))
dd[:,0] = data[:,0]
dd[:,1:] = cpp


df = pd.read_csv(data_dir+'\data_P&R.csv')
df_array = np.array(df)

sz = np.zeros((12,kk))
it=-1
for Name in ['Robertson','Sumner','Wilson','Rutherford','Maury','Williamson','Far North','Far NE','East','Far SE','Far South','Far West']:
    it=it+1
    a = df_array[df_array[:,-2]==Name][:,-1]
    unique_el, count_el = np.unique(a, return_counts=True)
    
    for i in unique_el:
        v = dd[dd[:,0]==i]
        for k in range(kk):
            sz[it,k] = sz[it,k] +np.sum(v[:,k+1])

sz2 = np.transpose(sz)
df = pd.DataFrame(sz2)
df.columns = ['Robertson','Sumner','Wilson','Rutherford','Maury','Williamson','Far North','Far NE','East','Far SE','Far South','Far West']
df['Mode'] = [['SOV'],['HOV'],['Transit'],['PR1'],['PR2'],['PR3'],['PR4'],['PR5'],['PR6'],['PR7'],['PR8'],['PR9'],['PR10'],['PR11'],['PR12'],['PR13'],['PR14'],
       ['PR15'],['PR16'],['PR17'],['PR18'],['PR19'],['PR20'],['PR21'],['PR22'],['PR23'],['PR24'],['PR25']]
df = df[['Mode','Robertson','Sumner','Wilson','Rutherford','Maury','Williamson','Far North','Far NE','East','Far SE','Far South','Far West']]
df.to_csv('Optimization_model_Approach_2\Approach2_'+'alph_'+str(alph)+'.csv', index =False)


#### Display the summary result
print('\n','The total usage of each mode when Alpha = ',str(alph),'\n')
d = 0
for i in range( kk):
    if i==0:
        print('SOV: '+''+str(int(np.sum(sz[:,i]))))
        a = int(np.sum(sz[:,i]))
    if i==1:
        print('HOV: '+''+str(int(np.sum(sz[:,i]))))
        b = int(np.sum(sz[:,i]))
    if i==2:
        print('Transit: '+''+str(int(np.sum(sz[:,i]))))
        c = int(np.sum(sz[:,i]))
    if i>=3:
        print('PR'+str(i-2)+': '+''+str(np.round(np.sum(sz[:,i]))))
        d = d+int(np.sum(sz[:,i]))

print('\n','The percentage usage of each mode when Alpha = ',str(alph),'\n')
s = a+b+c+d
for i in range( kk):
    if i==0:
        print('SOV: '+''+str(round(100*(a/s),2)))
    if i==1:
        print('HOV: '+''+str(round(100*(b/s),2)))
    if i==2:
        print('Transit: '+''+str(round(100*(c/s),2)))
    if i==3:
        print('PR'+str(i-2)+': '+''+str(round(100*(d/s),2)))
