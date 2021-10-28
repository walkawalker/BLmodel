import pandas as pd
import numpy as np
import math
from pathlib import Path
#set default
pd.set_option('display.max_colwidth', None)
fileno = input("Please provide a case number:")
marketweights = pd.DataFrame({'US MKT RATE':[0.5],
                              'Foreign MKT RATE':[0.4],
                              'Emerging MKT RATE':[0.1]})

managersview = pd.DataFrame({'US Equity':[1,0],
                            'Foreign Equity':[0,1],
                            'Emerging Equity':[0,-1]})
qmatrix = pd.DataFrame({'Q':[0.015,0.03]})


aversion = 3
taucov = 0.1
tauomega = 0.1
#define function
def BlackLitterman(fileno, aversion, taucov, tauomega, marketweights, managersview, qmatrix):
    xlsx_datafile = Path(Path.home(), 'anaconda3' ,'datafiles', 'BL -returndata.xlsx')
    datacols = [1,2,3,4]
    returndata = pd.read_excel(xlsx_datafile, sheet_name='data', usecols=(datacols))


    returndata['Excess Ret Us Equity']=returndata['US Equity']-returndata['T-Bill']
    returndata['Excess Ret Foreign Equity']=returndata['Foreign EQ']-returndata['T-Bill']
    returndata['Excess Ret Emerging Equity']=returndata['Emerging EQ']-returndata['T-Bill']

    del returndata['T-Bill']
    del returndata['US Equity']
    del returndata['Foreign EQ']
    del returndata['Emerging EQ']

    identity = pd.DataFrame({'I1':[1,0],
                         'I2':[0,1]})
#do calculations

    datacov = returndata.cov()
    standarddev = math.sqrt(np.dot(np.dot(marketweights, datacov),marketweights.transpose()))
    marketweights = marketweights.transpose() #marketweights need to be transposed 
    covtimesweights = np.dot(datacov, marketweights) #covariance matrix times marketweights
    priorreturns = aversion * covtimesweights #calculate prior returns matrix before marketvar calc
    marketweights = marketweights.transpose()
    covtimesweights = marketweights @ covtimesweights
    expectedmarketexcessreturn = aversion*covtimesweights
    covariancetau = taucov*datacov 
    omega = tauomega*(np.dot(managersview, np.dot(datacov, managersview.transpose())))
    diagonalomega = identity*omega
    priorprecision = np.dot(managersview, np.dot(covariancetau, managersview.transpose()))
    priorandomegainv = np.linalg.inv(priorprecision+omega)
    posteriorreturns = priorreturns + np.dot(np.dot(covariancetau, np.dot(managersview.transpose(), priorandomegainv)), qmatrix- np.dot(managersview, priorreturns))
    distributionposterior = datacov + (covariancetau - np.dot(np.dot(np.dot(covariancetau, managersview.transpose()), priorandomegainv), np.dot(managersview, covariancetau)))
    unconstraintedopt = np.dot(posteriorreturns.transpose(), np.linalg.inv(aversion*distributionposterior))
    sumunconopt = unconstraintedopt.sum()
    weightconstrained = np.true_divide(unconstraintedopt, sumunconopt)
    expectedreturnBL = np.dot(posteriorreturns.transpose(), weightconstrained.transpose())
    varianceBL = np.dot(np.dot(weightconstrained, distributionposterior), weightconstrained.transpose())
    sdBL = math.sqrt(varianceBL)
    sharpeBL = expectedreturnBL/sdBL


#print the data

    filename = 'BLoutput' + fileno + '.txt'
    filepath = Path(Path.home(), 'anaconda3' ,'datafiles', filename)
    with open(filepath, 'w')as f:
        f.write('The output of the BL Model is as follows\n')
        f.write('Market Weights:\n')
        f.write(marketweights.to_string(index = False))
        f.write('\nPrior Returns:\n')
        f.write(str(priorreturns))
        f.write('\nThe risk aversion parameter\n')
        f.write(str(aversion))
        f.write('\nTau Prior\n')
        f.write(str(taucov))
        f.write('\nTau Omega\n')
        f.write(str(tauomega))
        f.write('\nManagers Views:\n')
        f.write(managersview.to_string(index = False))
        f.write('\nManagers Views Q Values:\n')
        f.write(qmatrix.to_string(index = False))
        f.write('\nPosterior Distribution\n')
        f.write(distributionposterior.to_string(index = False, show_dimensions = False))
        f.write('\nOptimal Weights\n')
        f.write(str(weightconstrained))
        f.write('\nOptimal Expected Return\n')
        f.write(str(expectedreturnBL))
        f.write('\nOptimal SD\n')
        f.write(str(sdBL))
        f.write('\nOptimal Sharpe Ratio\n')
        f.write(str(sharpeBL))
#user input change default test case
check = input("Would you like to change the variables? (Y/N): ")
if check == "Y":
    userinputmw1 = float(input("Enter the US Market Weight: "))
    userinputmw2 = float(input("Enter the Foreign Market Weight: "))
    userinputmw3 = float(input("Enter the Emerging Market Weight: "))
    managersview01 = float(input("Enter the first value in the manager's view matrix [[x,0],[0,1],[0,-1]]: "))
    managersview02 = float(input("Enter the second value in the manager's view matrix [[1,x],[0,1],[0,-1]]: "))
    managersview11 = float(input("Enter the third value in the manager's view matrix [[1,0],[x,1],[0,-1]]: "))
    managersview12 = float(input("Enter the fourth value in the manager's view matrix [[1,0],[0,x],[0,-1]]: "))
    managersview21 = float(input("Enter the fifth value in the manager's view matrix [[1,0],[0,1],[x,-1]]: "))
    managersview22 = float(input("Enter the sixth value in the manager's view matrix [[x,0],[0,1],[0,x]]: "))
    qmatrix1 = float(input("Enter the value for Q1: "))
    qmatrix2 = float(input("Enter the value for Q2: "))
    aversion = float(input("Change the aversion value: "))
    taucov = float(input("Change the Covariance Scalar: "))
    tauomega = float(input("Change the omega scalar: "))
    qmatrix['Q'][0]=qmatrix1
    qmatrix['Q'][1]=qmatrix2
    marketweights['US MKT RATE'][0]= userinputmw1
    marketweights['Foreign MKT RATE'][0]= userinputmw2
    marketweights['Emerging MKT RATE'][0]=userinputmw3
    managersview['US Equity'][0]= managersview01
    managersview['US Equity'][1]= managersview02
    managersview['Foreign Equity'][0]= managersview11
    managersview['Foreign Equity'][1]=managersview12
    managersview['Emerging Equity'][0]=managersview21
    managersview['Emerging Equity'][1]= managersview22
    BlackLitterman(fileno, aversion, taucov, tauomega, marketweights, managersview, qmatrix)
else:
    BlackLitterman(fileno, aversion, taucov, tauomega, marketweights, managersview, qmatrix)
    
