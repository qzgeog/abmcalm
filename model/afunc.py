""" ABM-CARO: Qi Zhang (qz@unc.edu) """

### Functions [afunc.py] ### 
                        
"""
Function I1: Import data files to create agents
Function I2: Initialize household characteristics (part)
...
"""

# import built-in modules
# import time
import math
import numpy as np
import scipy.stats as stats
import random as rand
# import module: agents
import agents



### Interation



""" Function I1: Import data files to create agents """
def create_agents(df, ag_type):
    # df=df, ag_type='individuals' or 'households' or 'plots'
    
    ## Individuals: imported 9 attributes and initialize 5 attributes
        # pid, hhid, rgid, villid, 
        # relateHead, ifFemale, age, ifMarried, numChild
        # ifOutMig, ifRetMig, ifEverOut, work, edu
    ## Households: imported 3 attributes
        # hhid, rgid, villid
    ## Plots: imported 13 attributes
        # plid, centerX, centerY, area, code, dry, elev, slope
        # aspect, twi, distCcfp, distEwfp, plPnt
    
    agList = []
    
    # individuals
    if ag_type == 'individuals':
        for index, row in df.iterrows():
            al = list(row)
            ag = agents.Individual(*al)
            agList.append(ag)
        # message
        # print('Success FI1a! Individual agents have been substantiated. ')
        # print('\t pid, hhid, rgid, villid, ')
        # print('\t relateHead, ifFemale, age, ifMarried, numChild, ')
        # print('\t ifOutMig, ifRetMig, ifEverOut, work, edu. ')
    
    # households
    elif ag_type == 'households':
        for index, row in df.iterrows():
            al = list(row)
            ag = agents.Household(*al)
            agList.append(ag)
        # message
        # print('Success FI1b! Household agents have been substantiated. ')
        # print('\t hhid, rgid, villid. ')
        
    # plots
    elif ag_type == 'plots':
        for index, row in df.iterrows():
            al = list(row)
            ag = agents.Plot(*al)
            agList.append(ag)
        # message
        # print('Success FI1c! Plot agents have been substantiated.')
        # print('\t plid, centerX, centerY, ')
        # print('\t area, code, dry, elev, slope, aspect, twi, ')
        # print('\t distCcfp, distEwfp.')
    
    # return agent list: aglistINs, aglistHHs, aglistPLs
    return agList



""" Function I2: Initialize household characteristics (part) """
def init_hh_char(hhList, inList, mu, sig):
    # hhList=aglistHHs, inList=aglistINs, mu=sn1, sig=sn2
    
    # customize pmf for land area initially claimed by hhs
    xk = np.arange(41)
    pk = (0, 0.018099548, 0.042986425, 0.022624434, 0.031674208, 0.040723982, 
             0.074660633, 0.063348416, 0.092760181, 0.058823529, 0.088235294, 
             0.061085973, 0.06561086 , 0.052036199, 0.042986425, 0.027149321, 
             0.027149321, 0.038461538, 0.045248869, 0.015837104, 0.024886878, 
             0.009049774, 0.009049774, 0.004524887, 0.009049774, 0.009049774, 
             0.002262443, 0.00678733 , 0, 0.002262443, 0, 0.002262443, 0, 0, 
             0.004524887, 0.002262443, 0.002262443, 0, 0, 0, 0.002262443)
    custm_land = stats.rv_discrete(name='custm', values=(xk, pk))
    
    # customize social norm (sn) of a household
    custm_sn = stats.truncnorm((0.0-mu)/sig,(0.9999-mu)/sig,loc=mu,scale=sig)
    
    ## Household: initialized 7 attributes
        # hdIfFemale, hdAge, hdEdu, hdIfMarried
        # hhSize, hhNumCurOut, hhNumPreOut, "hhLandOwn"
        
    # loop households
    for hh in hhList:
        
        # get list of family members
        l_fam = [a for a in inList if a.hhid==hh.hhid]
        
        # derive hh head attributes
        aIN = next((a for a in l_fam if a.relateHead==1),None)
        hh.hdIfFemale  = int(aIN.ifFemale)                # hdIfFemale
        hh.hdAge       = int(aIN.age)                     # hdAge
        hh.hdEdu       = int(aIN.edu)                     # hdEdu
        hh.hdIfMarried = int(aIN.ifMarried)               # hdIfMarried
        
        # calcualte hh size
        hh.hhSize = len([a for a in l_fam if a.ifOutMig==0])      #hhSize
        # if no one at home, randomly pick a member to go home, set hh size 1 
        if hh.hhSize == 0:
            aIN = next((a for a in l_fam), None)
            if aIN != None:                     # !!! person attrs changed !!!
                aIN.ifOutMig  = 0
                aIN.ifEverOut = 0
                aIN.work      = rand.choice([1,3])
                hh.hhSize     = 1
        
        # calculate numbers of current & previous out-migrants
        hh.hhNumCurOut = len([a for a in l_fam if a.ifOutMig ==1]) #hhNumCurOut
        hh.hhNumPreOut = len([a for a in l_fam if a.ifEverOut==1]) #hhNumPreOut
        
        # area of land to claim
        hh.hhLandOwn = 0.5*(custm_land.rvs()-rand.random())       # "hhLandOwn"

        # social norm, degree of being influenced by neighbors
        hh.sn = custm_sn.rvs()
    
    # message
    # print('Success FI2! HH characteristics have been initialized (part). ')
    # print('\t hdIfFemale, hdAge, hdEdu, hdIfMarried, ')
    # print('\t hhSize, hhNumCurOut, hhNumPreOut, "hhLandOwn", sn. ')
    # print('Note: aglistINs may be modified.')
    
    # return aglistHHs
    return hhList



""" Function I3: vlookup ifCcfp of households to individuals or plots """
def vlookup_ccfp(hhList, aList):
    # hhList=aglistHHs, aList=aglistINs or aglistPLs
    
    for ag in aList:
        theHH = next((a for a in hhList if a.hhid==ag.hhid), None)
        if theHH != None:
            ag.ifCcfp = 1 if theHH.areaCcfp > 0 else 0
        else:
            ag.ifCcfp = 0
            print('WARNING!: This plot has no corresponding household. \n')
    
    # return to aglistINs or aglistPLs
    return aList



""" Function I4: define indigenous CCFP participants """
def original_ccfp(agList):
    # agList = aglistINs, aglistPLs, aglistHHs
    
    for ag in agList:
        ag.ifCcfpO = ag.ifCcfp
    
    return agList





                            ### Interation ###


""" Function T1: Set CCFP scenarios """
def set_ccfp_rate(s, t, f):
    # s=scheme, t=tick, f=factor
    
    f_adj = 1.0*f
    if s == 1:
        if   t == 0:
            f_adj = (500.0*f)/125.0
        elif t == 2:
            f_adj = (300.0*f)/125.0
        elif t == 4:
            f_adj = (400.0*f)/125.0
        else:
            f_adj = 0.0*f
    
    return f_adj



""" Function T2: Check if household member is qualified for migrating """
def if_qualify_mig(p, inList):
    # p=agIN, inList=aglistINs
    
    # set defualt to as qualified
    ifQualified = True
    # if this person is a current migrant, NOT qualified
    if p.ifOutMig == 1:
        ifQualified = False
    # if this person is the only one left in the family, NOT qualified
    elif len([a for a in inList if a.hhid==p.hhid]) <= 1:
        ifQualified = False
    # if this person is a kid or erlderly, NOT qualified
    elif p.age < 15 or p.age > 59:
        ifQualified = False
    
    # return Ture or False
    return ifQualified



""" Function T3: Estimate probability of migrating """
def pred_mig(p, hhList, f1, f2, t, e, fb):
    # p=agIN,hhList=aglistHHs,f1=fCCnew,f2=fEwfp,t=tick,e=end5yr,fb=feedback
    
    # find person's hh
    tHH = next((a for a in hhList if a.hhid==p.hhid), None)
    
    # derive payment amounts of ccfp and ewfp 
    payCcfp = tHH.areaCcfp * 125.00 * f1 / 1000.0     # unit: 1,000 yuan
    payEwfp = tHH.areaEwfp *   8.75 * f2 / 1000.0     # unit: 1,000 yuan
    
    # if payments end
    if e == 1 and t > 5:
        payCcfp = 0.0
        payEwfp = 0.0
    
    # equation of estimation for rural out-migration
    y = ((-1.210*p.ifFemale) + (-0.138*p.age) +  
         ( 0.096*tHH.hdAge ) + ( 1.321*tHH.hhNumPreOut) + 
         (-0.164*tHH.hhLandPlant) + 
         ( 1.056*payCcfp)    + (-0.435*payEwfp) + 0.663)
    pr = math.exp(y) / (1 + math.exp(y))
    
    # estimation with no feedback (reference model)
    if fb == 0:
        
# =============================================================================
#         y = ((-1.0876120*p.ifFemale)     +(-0.1373481*p.age)        + 
#              ( 0.0673858*p.edu)          +( 0.3431992*p.ifMarried)  + 
#              (-1.1622390*tHH.hdIfFemale) +( 0.0860925*tHH.hdAge)    + 
#              (-0.0386499*tHH.hdEdu)      +(-0.1027333*tHH.hhSize)   + 
#              ( 1.3678460*tHH.hhNumPreOut)+(-0.0261252*tHH.hhLandOwn)+ 
#              ( 0.9099114*payCcfp)        +(-0.5592378*payEwfp)      +0.4684275)
#         pr = math.exp(y) / (1 + math.exp(y))
# =============================================================================
        
        # alternative
        y = ((-1.155*p.ifFemale) + (-0.136*p.age) +  
             ( 0.087*tHH.hdAge ) + ( 1.361*tHH.hhNumPreOut) + 
             
             ( 0.887*payCcfp)    + (-0.526*payEwfp) + 0.284)
        
    # return to probMig
    return pr
    


""" Function T4: if migrant decides to return home """
def if_return(p, hhList, pr):
    # p=agIN, hhList=aglistINs, pr=pReturn
    
    # set default as to go home
    goHome = False
    # if this person is the only one living in family, must go home
    if len([a for a in hhList if a.hhid==p.hhid]) <= 1:
        rval   = -9
        goHome = True
    else:
        rval   = rand.random()
        goHome = [False,True][rval<pr]              # pReturn=0.23
    
    return [goHome, rval]



""" Fucntion T5: Check if farm plot is qualified for being abandoned """
def if_qualify_aba(p):
    # p=agPL
    
    # set default to as qualified
    ifQualified = True
    # set up thresholds
    areaThr     =   9.0
    slopeThr    =   3.0
    distEwfpThr = 150.0
    if   p.dry == 0:
        elevThr     = 420.0
        twiThr      =  12.0
        distCcfpThr = 900.0
    elif p.dry == 1:
        elevThr     = 450.0
        twiThr      =  10.0
        distCcfpThr = 800.0
    # if the other side of threshold
    if   p.area     >= areaThr:
        ifQualified = False
    elif p.elev     <= elevThr:
        ifQualified = False
    elif p.slope    <= slopeThr:
        ifQualified = False
    elif p.twi      >= twiThr:
        ifQualified = False
    elif p.distCcfp >= distCcfpThr:
        ifQualified = False
    elif p.distEwfp >= distEwfpThr:
        ifQualified = False
        
    if ifQualified:
        ifQualified = [False,True][rand.random()<0.2]
        
    # return True or False
    return ifQualified
    


""" Function P2: Estimate probability of being abandoned """
def pred_aban(p, hhList, f1, f2, t, e, fb):
    # p=agPL,hhList=aglistHHs,f1=fCCnew,f2=fEwfp,t=tick,e=end5yr,fb=feedback
    
    # find plot's household
    tHH = next((a for a in hhList if a.hhid==p.hhid), None)
    
    # derive plot variables, convert units
    area    = p.area
    dry     = [0,1][p.code==61]
    geoDist = p.geoDist  / 100.0                        # unit: 100 m
    elev    = p.elev     / 100.0                        # unit: 100 m
    slope   = p.slope
    dCcfp   = p.distCcfp / 100.0
    dEwfp   = p.distEwfp / 100.0   
    
    # payment amounts of ccfp and ewfp
    payCcfp = tHH.areaCcfp * 125.00 * f1 / 1000.0       # unit: 1,000 yuan
    payEwfp = tHH.areaEwfp *   8.75 * f2 / 1000.0       # unit: 1,000 yuan
    
    # if payments end
    if e == 1 and t > 5:
        payCcfp = 0.0
        payEwfp = 0.0
    
    # equation of estimation for cropland abandonment
    y = ((-0.875*dry  )   + ( 0.050*geoDist) + 
         (-0.064*dCcfp)   + (-0.643*dEwfp  ) + 
         ( 0.103*tHH.hhNumCurOut) + 
         (-0.441*payCcfp) + ( 0.591*payEwfp) + (-0.897))
    pr = math.exp(y) / (1 + math.exp(y))
    
    # estimation with no feedback (reference model)
    if fb == 0:
        
# =============================================================================
#         famSize = tHH.hhSize + tHH.hhNumCurOut
#         y = ((-0.0108365*area)  + (-0.9230951*dry)   + (0.0525844*geoDist) + 
#              ( 0.0341965*elev)  + ( 0.0256130*slope) + 
#              (-0.0595267*dCcfp) + (-0.5843475*dEwfp) + 
#              ( 0.2571838*tHH.hdIfFemale) + (-0.0092263*tHH.hdAge)+ 
#              (-0.0275211*tHH.hdEdu)      + ( 0.0457248*famSize)  +
#              (-0.3777017*payCcfp)        + ( 0.4998079*payEwfp)  +(-0.7896672))
#         pr = math.exp(y) / (1 + math.exp(y))
# =============================================================================
        
        # alternative
        y = ((-0.878*dry  )   + ( 0.050*geoDist) + 
             (-0.060*dCcfp)   + (-0.640*dEwfp  ) + 
             
             (-0.394*payCcfp) + ( 0.569*payEwfp) + (-0.752))
        pr = math.exp(y) / (1 + math.exp(y))
    
    # return to probAba
    return pr








""" Function UI1: Give birth to a baby """
def agent_baby_born(agMom):
    # agMom=self(agents.py)=agIN(main.py)
    
    import random as rand
    
    # set attributes for the baby born
    pid        = agMom.pid+700000 if agMom.numChild == 0 else agMom.pid+900000
    hhid       = agMom.hhid
    rgid       = agMom.rgid
    villid     = agMom.villid
    if agMom == 1:
        relateHead = 3
    elif agMom == 3:
        relateHead = 6
    else:
        relateHead = 10 * agMom.relateHead + 3
    ifFemale   = rand.choice([0,1])
    age        = 0
    ifMarried  = 0
    numChild   = 0 if ifFemale == 1 else -99
    
    # create agent
    alist = [pid,hhid,rgid,villid, relateHead,ifFemale,age,ifMarried,numChild]
    new_agent = agents.Individual(*alist)                       # [agents.py-I]
    
    # get the other attibutes right
    new_agent.ifOutMig = 0
    new_agent.ifRetMig = 0
    new_agent.work     = 6
    new_agent.edu      = 0 
    new_agent.ifCcfp   = agMom.ifCcfp
    new_agent.ifCcfpO  = agMom.ifCcfpO
    
    return new_agent


""" Function UI2: Create agent married in """
def agent_marry_in(ag):
    # ag=self(agents.py)=agIN(main.py)
    
    import scipy.stats as stats
    import random as rand
    import agents
    
    # customize age difference for a people married in, compared to the male
    low = -5
    upp = 11
    mu  = 1.1811
    sig = 2.8071
    dif = stats.truncnorm((low-mu)/sig,(upp-mu)/sig,loc=mu,scale=sig)
    age = ag.age - 1 - int(dif.rvs())
    
    # customize education year for people aged 23-65
    xk = np.arange(16)
    pk = (0.163701068, 0.017793594, 0.068801898, 0.066429419, 0.06405694, 
          0.182680902, 0.052194543, 0.043890866, 0.240806643, 0.011862396, 
          0.017793594, 0.039145907, 0.015421115, 0.002372479, 0.008303677, 
          0.004744958)
    custm_edu2 = stats.rv_discrete(name='custm', values=(xk, pk))
    
    # set attributes for the person married in
    pid        = ag.pid + 100000
    hhid       = ag.hhid
    rgid       = ag.rgid
    villid     = ag.villid
    if ag.relateHead == 1:
        relateHead = 2
    else:
        relateHead = 10 * ag.relateHead + 2
    ifFemale   = 1 if ag.ifFemale == 0 else 0
    age        = age
    ifMarried  = 1
    numChild   = 0 if ifFemale == 1 else -99
    # create agent
    alist = [pid,hhid,rgid,villid, relateHead,ifFemale,age,ifMarried,numChild]
    new_agent = agents.Individual(*alist)                       # [agents.py-I]
    
    # make the other attibutes right
    new_agent.ifOutMig  = ag.ifOutMig
    new_agent.ifRetMig  = 0
    new_agent.ifEverOut = ag.ifEverOut
    new_agent.work      = 3 if new_agent.ifOutMig == 1 else rand.choice([1,3])
    new_agent.edu       = custm_edu2.rvs()
    new_agent.ifCcfp    = ag.ifCcfp
    new_agent.ifCcfpO   = ag.ifCcfpO
    
    return new_agent


""" Function UI3: Check if split household """
def if_new_house(ag, l_ins):
    # ag=self(agents.py)=agIN(main.py)
    # l_ins=inList(agents.py)=aglistINs(main.py)
    
    # set default as to NOT split new house
    ifNewHouse = False
    # if the person is a daughter or son of head
    if ag.relateHead == 3:
        # get a list of married sisters or brothers
        l_fam     = [a for a in l_ins if a.hhid==ag.hhid and a.pid!=ag.pid]
        l_msisbro = [a for a in l_fam if a.relateHead==3 and a.ifMarried==1]
        if len(l_msisbro) > 0:    # if have married sisters or brothers
            ifNewHouse = True
    elif ag.relateHead == 6:
        # get a list of married sisters or brothers
        l_fam     = [a for a in l_ins if a.hhid==ag.hhid and a.pid!=ag.pid]
        l_msisbro = [a for a in l_fam if a.relateHead==6 and a.ifMarried==1]
        if len(l_msisbro) > 0:    # if have married sisters or brothers
            ifNewHouse = True
    
    return ifNewHouse








        
    
    
    
    
    
    
























