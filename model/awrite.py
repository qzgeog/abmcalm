""" ABM-CARO: Qi Zhang (qz@unc.edu) """

### Output Functions [awrite.py] ####

"""
O-Function 0a: Write dataframe headlines
O-Function 0b: Write initialized agent attributes

O-Function 1a: Derive stats for population
O-Function 1b: Write out stats for migration

O-Function 2a: Store stats of farm plot (area)
O-Function 2b: Write out stats for abandonment (area)

O-Function 3a: Store stats of ccfp plots (area)
O-Function 3b: Write out stats for planting (area)

O-Function 4a: Write out stats for collective action
O-Function 4b: Compare collective stats for learned and indigenous

O-Function 5: Derive and write status of each tick
"""


""" O-Function 0a: Write dataframe headlines """
def df_head(dfType):
    # dfType = 'mig', 'ret', 'aba', 'rec', 'ren', 'pla', 'rev'
    # dfType = 'staMig', 'staAba', 'staPla', 'staCol', 'staFin'
    
    # b1 - individual: migrate
    if dfType == 'mig':
        l1 = ['Mig!', 'tick', 'pid', 'hhid', 'rgid', 'villid']
        l2 = ['relateHead', 'ifFemale', 'age', 'ifMarried', 'numChild']
        l3 = ['ifOutMig', 'ifRetMig', 'ifEverOut', 'work', 'edu']
        l4 = ['ifCcfp', 'ifCcfpO', 'rand', 'probMig']
        rl   = l1 + l2 + l3 + l4
    # b2 - individual: return
    if dfType == 'ret':
        l1 = ['Ret!', 'tick', 'pid', 'hhid', 'rgid', 'villid']
        l2 = ['relateHead', 'ifFemale', 'age', 'ifMarried', 'numChild']
        l3 = ['ifOutMig', 'ifRetMig', 'ifEverOut', 'work', 'edu']
        l4 = ['ifCcfp', 'ifCcfpO', 'r', 'pReturn']
        rl   = l1 + l2 + l3 + l4
    # b3 - plot: be abandoned
    if dfType == 'aba':
        l1 = ['Aba!', 'tick', 'plid', 'hhid', 'rgid', 'villid']
        l2 = ['centerX', 'centerY', 'area', 'code', 'dry', 'elev', 'slope']
        l3 = ['aspect', 'twi', 'distCcfp', 'distEwfp', 'distEwfpO']
        l4 = ['geoDist', 'abanYr', 'ifCcfp', 'ifCcfpO', 'rand', 'probAba']
        rl   = l1 + l2 + l3 + l4
    # b4 - plot: be reclaimed
    if dfType == 'rec':
        l1 = ['Rec!', 'tick', 'plid', 'hhid', 'rgid', 'villid']
        l2 = ['centerX', 'centerY', 'area', 'code', 'dry', 'elev', 'slope']
        l3 = ['aspect', 'twi', 'distCcfp', 'distEwfp', 'distEwfpO']
        l4 = ['geoDist', 'abanYr', 'ifCcfp', 'ifCcfpO', 'r', 'pReclaim']
        rl   = l1 + l2 + l3 + l4
    # b5 - plot: be rented-out or -in
    if dfType == 'ren':
        l1 = ['Ren!', 'tick', 'plid', 'hhid', 'rgid', 'villid']
        l2 = ['centerX', 'centerY', 'area', 'code', 'dry', 'elev', 'slope']
        l3 = ['aspect', 'twi', 'distCcfp', 'distEwfp', 'distEwfpO']
        l4 = ['geoDist', 'abanYr', 'ifCcfp', 'ifCcfpO', 'r', 'pRent']
        l5 = ['hhidOu', 'hhidIn']
        rl   = l1 + l2 + l3 + l4 + l5
    # b6 - plot: be planted
    if dfType == 'pla':
        l1 = ['Pla!', 'tick', 'plid', 'hhid', 'rgid', 'villid']
        l2 = ['centerX', 'centerY', 'area', 'code', 'dry', 'elev', 'slope']
        l3 = ['aspect', 'twi', 'distCcfp', 'distEwfp', 'distEwfpO']
        l4 = ['geoDist', 'abanYr', 'ifCcfp', 'ifCcfpO', 'rand','probPla','cRG']
        l5 = ['propActPl', 'areActPl', 'areTotPl']
        l6 = ['percActGp', 'numActGp', 'numTotGp']
        rl   = l1 + l2 + l3 + l4 + l5 + l6
    # b7 - plot: be reverted
    if dfType == 'rev':
        l1 = ['Rev!', 'tick', 'plid', 'hhid', 'rgid', 'villid']
        l2 = ['centerX', 'centerY', 'area', 'code', 'dry', 'elev', 'slope']
        l3 = ['aspect', 'twi', 'distCcfp', 'distEwfp', 'distEwfpO']
        l4 = ['geoDist', 'abanYr', 'ifCcfp', 'ifCcfpO', 'r', 'pRevert']
        rl   = l1 + l2 + l3 + l4
    
    # s1 - demographics for migration(individual)
    if dfType == 'staMig':
        l1 = ['StaMig!' ,'tick']
        l2 = ['percMig' ,'percMig1','percMig0']
        l3 = ['numMig'  ,'numMig1' ,'numMig0', 'numPop' ,'numPop1','numPop0']
        l4 = ['percRet' ,'percRet1','percRet0']
        l5 = ['numRet'  ,'numRet1' ,'numRet0', 'numCur' ,'numCur1','numCur0']
        l6 = ['percMigL','percMigI','numMigL', 'numMigI','numPopL','numPopI']
        l7 = ['percRetL','percRetI','numRetL', 'numRetI','numCurL','numCurI']
        rl   = l1 + l2 + l3 + l4 + l5 + l6 + l7
    # s2 - lands for abandonment (plot)
    if dfType == 'staAba':
        l1 = ['StaAba!' ,'tick']
        l2 = ['propAba' ,'propAba1','propAba0']
        l3 = ['areAba'  ,'areAba1' ,'areAba0', 'arePlo' ,'arePlo1','arePlo0']
        l4 = ['propRec' ,'propRec1','propRec0']
        l5 = ['areRec'  ,'areRec1' ,'areRec0', 'areCur' ,'areCur1','areCur0']
        l6 = ['propAbaL','propAbaI','areAbaL', 'areAbaI','arePloL','arePloI']
        l7 = ['propRecL','propRecI','areRecL', 'areRecI','areCurL','areCurI']
        rl   = l1 + l2 + l3 + l4 + l5 + l6 + l7
    # s3 - lands for tree planting (plot)
    if dfType == 'staPla':
        l1 = ['StaPla!' ,'tick']
        l2 = ['propPla' ,'propPla1','propPla0']
        l3 = ['arePla'  ,'arePla1' ,'arePla0', 'areAPs' ,'areAPs1','areAPs0']
        l4 = ['propRev' ,'propRev1','propRev0']
        l5 = ['areRev'  ,'areRev1' ,'areRev0', 'areCCs' ,'areCCs1','areCCs0']
        l6 = ['propPlaL','propPlaI','arePlaL', 'arePlaI','areAPsL','areAPsI']
        l7 = ['propRevL','propRevI','areRevL', 'areRevI','areCCsL','areCCsI']
        rl   = l1 + l2 + l3 + l4 + l5 + l6 + l7
    # s4 - collective action of reforestation (social norm)
    if dfType == 'staCol':
        l1 = ['StaCol!','tick','rPlAb','arePl','areAb','m_probPla','m_cRG']
        l2 = ['m_propActPl', 'm_areActPl', 'm_areTotPl']
        l3 = ['m_percActGp', 'm_numActGp', 'm_numTotGp']
        rl   = l1 + l2 + l3
    # s5 - collective: learned vs indigenous
    if dfType == 'staCom':
        l1 = ['StaCom!', 'tick']
        l2 = ['rPlAbL' , 'arePlL', 'areAbL', 'm_probPlaL' , 'm_cRGL']
        l3 = ['m_propActPlL', 'm_areActPlL', 'm_areTotPlL']
        l4 = ['m_percActGpL', 'm_numActGpL', 'm_numTotGpL']
        l5 = ['rPlAbI', 'arePlI', 'areAbI' , 'm_probPlaI' , 'm_cRGI']
        l6 = ['m_propActPlI', 'm_areActPlI', 'm_areTotPlI']
        l7 = ['m_percActGpI', 'm_numActGpI', 'm_numTotGpI']
        rl   = l1 + l2 + l3 + l4 + l5 + l6 + l7
    # s6 - final status of each tick
    if dfType == 'staFin':
        l1 = ['staFin!', 'tick']
        l2 = ['ind' , 'pop', 'cur', 'ret' , 'ever']
        l3 = ['land', 'cul', 'aba', 'ccf' , 'zcul', 'zaba', 'zccf']
        l4 = ['hhs' , 'hh1', 'hh0', 'zhh1', 'zhh0']
        l5 = [        'hhL', 'hhI', 'zhhL', 'zhhI']
        rl   = l1 + l2 + l3 + l4 + l5
    
    # i1 - initilized individual attributes
    if dfType == 'iniINs':
        l1 = ['pid', 'hhid', 'rgid', 'villid', 'relateHead', 'ifFemale']
        l2 = ['age', 'ifMarried', 'numChild', 'ifOutMig', 'ifRetMig']
        l3 = ['ifEverOut', 'work', 'edu', 'ifCcfp', 'ifCcfpO']
        rl   = l1 + l2 + l3
    # i2 - initilized plot features
    if dfType == 'iniPLs':
        l1 = ['plid', 'hhid', 'rgid', 'villid', 'centerX','centerY', 'area']
        l2 = ['code', 'dry', 'elev', 'slope', 'aspect', 'twi', 'distCcfp']
        l3 = ['distEwfp','distEwfpO','geoDist','abanYr','ifCcfp','ifCcfpO']
        rl = l1 + l2 + l3
    # i3 - initilized household characteristics
    if dfType == 'iniHHs':
        l1 = ['hhid', 'rgid', 'villid', 'hhLocX', 'hhLocY', 'hhElev']
        l2 = ['hdIfFemale', 'hdAge', 'hdEdu', 'hdIfMarried']
        l3 = ['hhSize', 'hhNumCurOut', 'hhNumPreOut', 'hhLandOwn']
        l4 = ['hhLandPlant', 'areaCcfp', 'areaEwfp', 'ifCcfp', 'ifCcfpO', 'sn']
        rl = l1 + l2 + l3 + l4
    
    # return to column names
    return rl


""" O-Function 0b: Write initialized agent attributes """ 
def tp_attr(df, inList, plList, hhList, agType):
    # df = df_ini_ins, df_ini_pls, df_ini_hhs
    # inList=aglistINs, plList=aglistPLs, hhList=aglistHHs
    # agType = 'ins', 'pls', 'hhs'
    
    # inidividuals
    if agType == 'ins':
        for aIN in inList:
            df.loc[len(df)] = aIN.write_self()
    # plots
    if agType == 'pls':
        for aPL in plList:
            df.loc[len(df)] = aPL.write_self()
    # households
    if agType == 'hhs':
        for aHH in hhList:
            df.loc[len(df)] = aHH.write_self()
    
    # return to dataframe
    return df





""" O-Function 1a: Derive stats for population """
def stat_in_pop(inList):
    # inList=aglistINs
    
    # demographics: 
        # numPop,  numPop1, numPop0, numCur, numCur1, numCur0
        #          numPopL, numPopI,         numCurL, numCurI
    
    # get list of non-migrants only
    l_non   = [a for a in inList if a.ifOutMig==0]
    # stats: population of non-migrants, by CCFP
    numPop  = len(l_non)                                  # total
    numPop1 = len([a for a in l_non if a.ifCcfp==1])      # ccfp = 1
    numPop0 = len([a for a in l_non if a.ifCcfp==0])      # ccfp = 0
    
    # get list of current migrants only
    l_cur   = [a for a in inList  if a.ifOutMig==1]
    # stats: population of non-migrants, by CCFP
    numCur  = len(l_cur)                                  # total
    numCur1 = len([a for a in l_cur if a.ifCcfp==1])      # ccfp = 1
    numCur0 = len([a for a in l_cur if a.ifCcfp==0])      # ccfp = 0
    
    # derive indigenous and learned CCFP household population
    numPopL = len([a for a in l_non if a.ifCcfp==1 and a.ifCcfpO==0])
    numPopI = len([a for a in l_non if a.ifCcfp==1 and a.ifCcfpO==1])
    numCurL = len([a for a in l_cur if a.ifCcfp==1 and a.ifCcfpO==0])
    numCurI = len([a for a in l_cur if a.ifCcfp==1 and a.ifCcfpO==1])
    
    # add all to list
    rl1 = [numPop, numPop1, numPop0, numCur, numCur1, numCur0]
    rl2 = [        numPopL, numPopI,         numCurL, numCurI]
    
    # return to lStatIN
    return rl1 + rl2



""" O-Function 1b: Write out stats for migration """
def stat_in_mig(u1, u2, l, ls):
    # u1=upd_mig, u2=upd_ret, l=aglistINs, ls=lStatIN
    
    # ls=lStatIn = 
        # [numPop,  numPop1, numPop0, numCur, numCur1, numCur0
        #           numPopL, numPopI,         numCurL, numCurI]
    
    # demographics: 
        # percMig , percMig1, percMig0, numMig, numMig1, numMig0,
        # numPop  , numPop1 , numPop0
        # percRet , percRet1, percRet0, numRet, numRet1, numRet0, 
        # numCur  , numCur1 , numCur0
        # percMigL, percMigI, numMigL, numMigI, numPopL, numPopI
        # percRetL, percRetI, numRetL, numRetI, numCurL, numCurI
        
    # number of people who decide to migrate out
    numMig   = len(u1)
    numMig1  = len([a for a in l if a.pid in u1 and a.ifCcfp==1])
    numMig0  = len([a for a in l if a.pid in u1 and a.ifCcfp==0])
    # percent
    percMig  = numMig  / ls[0] if ls[0] > 0 else -9     # numPop
    percMig1 = numMig1 / ls[1] if ls[1] > 0 else -9     # numPop1
    percMig0 = numMig0 / ls[2] if ls[2] > 0 else -9     # numPop0
    
    # number of people who decide to return home
    numRet   = len(u2)
    numRet1  = len([a for a in l if a.pid in u2 and a.ifCcfp==1])
    numRet0  = len([a for a in l if a.pid in u2 and a.ifCcfp==0])
    # percent
    percRet  = numRet  / ls[3] if ls[3] > 0 else -9     # numCur
    percRet1 = numRet1 / ls[4] if ls[4] > 0 else -9     # numCur1
    percRet0 = numRet0 / ls[5] if ls[5] > 0 else -9     # numCur0
    
    # derive stats for indigenous vs learned
    # number of migrating out
    numMigL=len([a for a in l if a.pid in u1 and a.ifCcfp==1 and a.ifCcfpO==0])
    numMigI=len([a for a in l if a.pid in u1 and a.ifCcfp==1 and a.ifCcfpO==1])
    # percent
    percMigL = numMigL / ls[6] if ls[6] > 0 else -9     # numPopL
    percMigI = numMigI / ls[7] if ls[7] > 0 else -9     # numPopI
    # number of returning home
    numRetL=len([a for a in l if a.pid in u2 and a.ifCcfp==1 and a.ifCcfpO==0])
    numRetI=len([a for a in l if a.pid in u2 and a.ifCcfp==1 and a.ifCcfpO==1])
    # percent
    percRetL = numRetL / ls[8] if ls[8] > 0 else -9     # numCurL
    percRetI = numRetI / ls[9] if ls[9] > 0 else -9     # numCurI
    
    
    # store in a list: 9 + 9      # !! note the order !!
        # migrate out
    rl1 = [percMig, percMig1, percMig0, numMig, numMig1, numMig0] + ls[0:3]
        # return home
    rl2 = [percRet, percRet1, percRet0, numRet, numRet1, numRet0] + ls[3:6]
        # indigenous vs learned
    rl3 = [percMigL, percMigI, numMigL, numMigI] + ls[6:8]
    rl4 = [percRetL, percRetI, numRetL, numRetI] + ls[8: ]
    
    # return to al
    return rl1 + rl2 + rl3 + rl4





""" O-Function 2a: Store stats of farm plot (area) """
def stat_fp_plo(plList):
    # plList = aglistPLs
    
    # plots (area): 
        # arePlo , arePlo1, arePlo0, areCur, areCur1, areCur0
        #          arePloL, arePloI,         areCurL, areCurI
    
    # get list of cultivated plots only
    l_cul = [a for a in plList if a.code in [60,61]]
    # stats: area of planted plots, by CCFP
    arePlo  = sum([a.area for a in l_cul])                    # total
    arePlo1 = sum([a.area for a in l_cul if a.ifCcfp==1])     # ccfp = 1
    arePlo0 = sum([a.area for a in l_cul if a.ifCcfp==0])     # ccfp = 0
    
    # get list of abandoned plots only
    l_cur = [a for a in plList if a.code in [69]]
    # stats: area of non-migrants, by CCFP
    areCur  = sum([a.area for a in l_cur])                    # total
    areCur1 = sum([a.area for a in l_cur if a.ifCcfp==1])     # ccfp = 1
    areCur0 = sum([a.area for a in l_cur if a.ifCcfp==0])     # ccfp = 0
    
    # derive indigenous and learned CCFP household land area
    arePloL = sum([a.area for a in l_cul if a.ifCcfp==1 and a.ifCcfpO==0])
    arePloI = sum([a.area for a in l_cul if a.ifCcfp==1 and a.ifCcfpO==1])
    areCurL = sum([a.area for a in l_cur if a.ifCcfp==1 and a.ifCcfpO==0])
    areCurI = sum([a.area for a in l_cur if a.ifCcfp==1 and a.ifCcfpO==1])
    
    # add all to list
    rl1 = [arePlo , arePlo1, arePlo0, areCur, areCur1, areCur0]
    rl2 = [arePloL, arePloI, areCurL, areCurI]
    
    # return to lStatFP
    return rl1 + rl2


""" O-Function 2b: Write out stats for abandonment (area) """
def stat_fp_aba(u1, u2, l, ls):
    # u1=upd_aba, u2=upd_rec, l=aglistPLs, ls=lStatFP
    
    # ls=lStatFP = 
        # [arePlo, arePlo1, arePlo0, areCur, areCur1, areCur0
        #          arePloL, arePloI,         areCurL, areCurI]
    
    # land: 
        # propAba , propAba1, propAba0, areAba, areAba1, areAba0,
        # arePlo  , arePlo1 , arePlo0
        # propRec , propRec1, propRec0, areRec, areRec1, areRec0,
        # areCur  , areCur1 , areCur0
        # propAbaL, propAbaI, areAbaL, areAbaI, arePloL, arePloI
        # propRecL, propRecI, areRecL, areRecI, areCurL, areCurI
    
    # area of plots to be abandoned
    areAba   = sum([a.area for a in l if a.plid in u1])
    areAba1  = sum([a.area for a in l if a.plid in u1 and a.ifCcfp==1])
    areAba0  = sum([a.area for a in l if a.plid in u1 and a.ifCcfp==0])
    # percent
    propAba  = areAba  / ls[0] if ls[0] > 0 else -9     # arePlo
    propAba1 = areAba1 / ls[1] if ls[1] > 0 else -9     # arePlo1
    propAba0 = areAba0 / ls[2] if ls[2] > 0 else -9     # arePlo0
    
    # area of plots to be reclaimed
    areRec   = sum([a.area for a in l if a.plid in u2])
    areRec1  = sum([a.area for a in l if a.plid in u2 and a.ifCcfp==1])
    areRec0  = sum([a.area for a in l if a.plid in u2 and a.ifCcfp==0])
    # percent
    propRec  = areRec  / ls[3] if ls[3] > 0 else -9     # areCur
    propRec1 = areRec1 / ls[4] if ls[4] > 0 else -9     # areCur1
    propRec0 = areRec0 / ls[5] if ls[5] > 0 else -9     # areCur0
    
    # derive stats for indigenous vs learned
    # area of being abandoned
    l1      = [a for a in l if a.plid in u1]
    areAbaL = sum([a.area for a in l1 if a.ifCcfp==1 and a.ifCcfpO==0])
    areAbaI = sum([a.area for a in l1 if a.ifCcfp==1 and a.ifCcfpO==1])
    # percent
    propAbaL = areAbaL / ls[6] if ls[6] > 0 else -9     # arePloL
    propAbaI = areAbaI / ls[7] if ls[7] > 0 else -9     # arePloI
    # area of being reclaimed
    l2      = [a for a in l if a.plid in u2]
    areRecL = sum([a.area for a in l2 if a.ifCcfp==1 and a.ifCcfpO==0])
    areRecI = sum([a.area for a in l2 if a.ifCcfp==1 and a.ifCcfpO==1])
    # percent
    propRecL = areRecL / ls[8] if ls[8] > 0 else -9     # areCurL
    propRecI = areRecI / ls[9] if ls[9] > 0 else -9     # areCurI
    
    # store in a list: 9 + 9      # !! note the order !!
        # abandoned
    rl1 = [propAba, propAba1, propAba0, areAba, areAba1, areAba0] + ls[0:3]
        # reclaimed
    rl2 = [propRec, propRec1, propRec0, areRec, areRec1, areRec0] + ls[3:6]
        # indigenous vs learned
    rl3 = [propAbaL, propAbaI, areAbaL, areAbaI] + ls[6:8]
    rl4 = [propRecL, propRecI, areRecL, areRecI] + ls[8: ]
    
    # return to al
    return rl1 + rl2 + rl3 + rl4





""" O-Function 3a: Store stats of ccfp plots (area) """
def stat_cc_plo(plList):
    # plList = aglistPLs
    
    # ccfp plots (area): 
        # areAPs, areAPs1, areAPs0, areCCs, areCCs1, areCCs0
        #         areAPsL, areAPsI,         areCCsL, areCCsI
    
    # get list of abandoned plots only
    l_aba  = [a for a in plList if a.code in [69]]
    # stats: area of abandoned plots, by CCFP
    areAPs  = sum([a.area for a in l_aba])
    areAPs1 = sum([a.area for a in l_aba if a.ifCcfp==1])
    areAPs0 = sum([a.area for a in l_aba if a.ifCcfp==0])
    
    # get list of ccfp plots only
    l_ccf   = [a for a in plList if a.code in [99]]
    # stats: area of ccfp plots, by CCFP
    areCCs  = sum([a.area for a in l_ccf])
    areCCs1 = sum([a.area for a in l_ccf if a.ifCcfp==1])
    areCCs0 = sum([a.area for a in l_ccf if a.ifCcfp==0])
    
    # derive indigenous and learned CCFP household land area
    areAPsL = sum([a.area for a in l_aba if a.ifCcfp==1 and a.ifCcfpO==0])
    areAPsI = sum([a.area for a in l_aba if a.ifCcfp==1 and a.ifCcfpO==1])
    areCCsL = sum([a.area for a in l_ccf if a.ifCcfp==1 and a.ifCcfpO==0])
    areCCsI = sum([a.area for a in l_ccf if a.ifCcfp==1 and a.ifCcfpO==1])
    
    # add all to list
    rl1 = [areAPs, areAPs1, areAPs0, areCCs, areCCs1, areCCs0]
    rl2 = [        areAPsL, areAPsI,         areCCsL, areCCsI]
    
    # return to lStatCC
    return rl1 + rl2



""" O-Function 3b: Write out stats for planting (area)"""
def stat_cc_pla(u1, u2, l, ls):
    # u1=upd_pla, u2=upd_rev, l=aglistPLs, ls=lStatCCa
    
    # ls=lStatCCa = 
        # [areAPs, areAPs1, areAPs0, areCCs, areCCs1, areCCs0
        #          areAPsL, areAPsI,         areCCsL, areCCsI]
    
    # ccfp plots (area): 
        # propPla, propPla1, propPla0, arePla, arePla1, arePla0,
        # areAPs , areAPs1 , areAPs0
        # propRev, propRev1, propRev0, areRev, areRev1, areRev0,
        # areCCs , areCCs1 , areCCs0
        # propPlaL, propPlaI, arePlaL, arePlaI, areAPsL, areAPsI
        # propRevL, propRevI, areRevL, areRevI, areCCsL, areCCsI
    
    # area of plots to be planted
    arePla   = sum([a.area for a in l if a.plid in u1])
    arePla1  = sum([a.area for a in l if a.plid in u1 and a.ifCcfp==1])
    arePla0  = sum([a.area for a in l if a.plid in u1 and a.ifCcfp==0])
    # proportion
    propPla  = arePla  / ls[0] if ls[0] > 0 else -9     # ls[0]: areAPs
    propPla1 = arePla1 / ls[1] if ls[1] > 0 else -9     # ls[1]: areAPs1
    propPla0 = arePla0 / ls[2] if ls[2] > 0 else -9     # ls[2]: areAPs0
    
    # area of plots to be reverted
    areRev   = sum([a.area for a in l if a.plid in u2])
    areRev1  = sum([a.area for a in l if a.plid in u2 and a.ifCcfp==1])
    areRev0  = sum([a.area for a in l if a.plid in u2 and a.ifCcfp==0])
    # percent
    propRev  = areRev  / ls[3] if ls[3] > 0 else -9     # ls[3]: areCCs
    propRev1 = areRev1 / ls[4] if ls[4] > 0 else -9     # ls[4]: areCCs1
    propRev0 = areRev0 / ls[5] if ls[5] > 0 else -9     # ls[5]: areCCs0
    
    # derive stats for indigenous vs learned
    # area of being planted
    l1      = [a for a in l if a.plid in u1]
    arePlaL = sum([a.area for a in l1 if a.ifCcfp==1 and a.ifCcfpO==0])
    arePlaI = sum([a.area for a in l1 if a.ifCcfp==1 and a.ifCcfpO==1])
    # percent
    propPlaL = arePlaL / ls[6] if ls[6] > 0 else -9     # areAPsL
    propPlaI = arePlaI / ls[7] if ls[7] > 0 else -9     # areAPsI
    # area of being reverted
    l2      = [a for a in l if a.plid in u2]
    areRevL = sum([a.area for a in l2 if a.ifCcfp==1 and a.ifCcfpO==0])
    areRevI = sum([a.area for a in l2 if a.ifCcfp==1 and a.ifCcfpO==1])
    # percent
    propRevL = areRevL / ls[8] if ls[8] > 0 else -9     # areCCsL
    propRevI = areRevI / ls[9] if ls[9] > 0 else -9     # areCCsI
    
    # store in a list: 9 + 9      # !! note the order !!
        # planted
    rl1 = [propPla, propPla1, propPla0, arePla, arePla1, arePla0] + ls[0:3]
        # reverted
    rl2 = [propRev, propRev1, propRev0, areRev, areRev1, areRev0] + ls[3:6]
        # indigenous vs learned
    rl3 = [propPlaL, propPlaI, arePlaL, arePlaI] + ls[6:8]
    rl4 = [propRevL, propRevI, areRevL, areRevI] + ls[8: ]
    
    # return to al
    return rl1 + rl2 + rl3 + rl4





""" O-Function 4a: Write out stats for collective action """
def stat_cc_col(u, l):
    # u=opt_pla, l=aglistPLs
    
    # opt_pla's one element is
        # 0 [probPla, cRG]
        # 2  propActPl, areActPl, areTotPl, percActGp, numActGp, numTotGp 
        # 8  plid2, hhid2, area2, ifCcfp2, ifCcfpO2]
    
    # collective
      # all participants
        # rPlAb , arePl , areAb ,    m_probPla , m_cRG
        # m_propActPl , m_areActPl , m_areTotPl
        # m_percActGp , m_numActGp , m_numTotGp
    
    # calculate planted area
    u_ids = list(set([a[9] for a in u]))                    # hhid to plant
    l_aba = [a for a in l if a.code==69]                    # abandoned plots
    # get abandoned area for planted, and those (NOT planted) and (CCFP)
    areAb1= sum([a.area for a in l_aba if a.hhid in u_ids])
    areAb2= sum([a.area for a in l_aba if a.hhid not in u_ids and a.ifCcfp==1])
    areAb = (areAb1 + areAb2)
    # get planted area
    arePl = sum([a[10] for a in u])                     # a[10]:area2
    rPlAb = arePl / areAb if areAb > 0 else -9
    rl1a  = [rPlAb, arePl, areAb]
    # dervie mean of collective variables, excluding: plid2, area2, ...
    rl1b = []
    for i in range(8):
        rl1b.append(sum([a[i] for a in u]) / len(u) if len(u) > 0 else -9)
    
    # return to al
    return rl1a + rl1b


""" O-Function 4b: Compare collective stats for learned and indigenous """
def stat_cc_com(u, l):
    # u=opt_pla, l=aglistPLs
    
    # opt_pla's one element is
        # 0 [probPla, cRG]
        # 2  propActPl, areActPl, areTotPl, percActGp, numActGp, numTotGp 
        # 8  plid2, hhid2, area2, ifCcfp2, ifCcfpO2]
    
    # collective
      # learned
        # rPlAbL, arePlL, areAbL,    m_probPlaL, m_cRGL
        # m_propActPlL, m_areActPlL, m_areTotPlL
        # m_percActGpL, m_numActGpL, m_numTotGpL
      # indigenous
        # rPlAbI, arePlI, areAbI,    m_probPlaI, m_cRGI
        # m_propActPlI, m_areActPlI, m_areTotPlI
        # m_percActGpI, m_numActGpI, m_numTotGpI
    
    # derive learned CCFP participants collective action
    u_ids = list(set([a[9] for a in u]))                   # hhid to plant
    l_aba = [a for a in l if a.code==69 and a.ifCcfpO==0]  # abandoned, learned
    # get abandoned area from two parts of learned CCFP households
    areAb1= sum([a.area for a in l_aba if a.hhid in u_ids])
    areAb2= sum([a.area for a in l_aba if a.hhid not in u_ids and a.ifCcfp==1])
    areAb = areAb1 + areAb2
    # calculate existing abandoned area
    arePl = sum([a[10] for a in u if a[12]==0])   # a[9]:area2, a[12]:ifCcfpO2
    # ratio of planted on abandoned areas
    rPlAb = arePl / areAb if areAb > 0 else -9
    # add to list
    rl2a = [rPlAb, arePl, areAb]
    # dervie mean of collective variables, excluding: plid2, area2, ...
    u2   = [a for a in u if a[12]==0]                   # a[12]:ifCcfpO2
    rl2b = []
    for i in range(8):
        rl2b.append(sum([a[i] for a in u2]) / len(u2) if len(u2) > 0 else -9)
    
    # derive indigenous CCFP participants collective action
    u_ids = list(set([a[9] for a in u]))                  #hhid to plant
    l_aba = [a for a in l if a.code==69 and a.ifCcfpO==1] #abandoned,indigenous
    # get abandoned area from two parts of learned CCFP households
    areAb1= sum([a.area for a in l_aba if a.hhid in u_ids])
    areAb2= sum([a.area for a in l_aba if a.hhid not in u_ids and a.ifCcfp==1])
    areAb = areAb1 + areAb2
    # calculate existing abandoned area
    arePl = sum([a[10] for a in u if a[12]==1])   # a[9]:area2, a[12]:ifCcfpO2
    # ratio of planted on abandoned areas
    rPlAb = arePl / areAb if areAb > 0 else -9
    # add to list
    rl3a = [rPlAb, arePl, areAb]
    # dervie mean of collective variables, excluding: plid2, area2, ...
    u2   = [a for a in u if a[12]==1]                   # a[12]:ifCcfpO2
    rl3b = []
    for i in range(8):
        rl3b.append(sum([a[i] for a in u2]) / len(u2) if len(u2) > 0 else -9)
    
    # reminder
        # 0 [probPla, cRG]
        # 2  propActPl, areActPl, areTotPl, percActGp, numActGp, numTotGp 
        # 8  plid2, hhid2, area2, ifCcfp2, ifCcfpO2]
    
    # return to 
    return rl2a + rl2b + rl3a +rl3b







""" O-Function 5: Derive and write status of each tick """
def tick_final(t, inList, plList, hhList):
    # t=tick+1, inList=aglistINs, plList=aglistPLs, hhList=aglistHHs
    
    # individuals
    ind  = len(inList)
    pop  = len([a for a in inList if a.ifOutMig==0])
    cur  = len([a for a in inList if a.ifOutMig==1])
    ret  = len([a for a in inList if a.ifOutMig==0 and a.ifRetMig ==1])
    ever = len([a for a in inList if a.ifOutMig==0 and a.ifEverOut==1])
        # plots
    land = sum([a.area for a in plList])
    cul  = sum([a.area for a in plList if a.code in [60,61]])
    aba  = sum([a.area for a in plList if a.code in [69   ]])
    ccf  = sum([a.area for a in plList if a.code in [99   ]])
    zcul = cul / land if land > 0 else -9
    zaba = aba / land if land > 0 else -9
    zccf = ccf / land if land > 0 else -9
        # households
    hhs  = len(hhList)
    hh1  = len([a for a in hhList if a.ifCcfp==1])
    hh0  = len([a for a in hhList if a.ifCcfp==0])
    zhh1 = hh1 / hhs if hhs > 0 else -9
    zhh0 = hh0 / hhs if hhs > 0 else -9
    hhL  = len([a for a in hhList if a.ifCcfp==1 and a.ifCcfpO==0])
    hhI  = len([a for a in hhList if a.ifCcfp==1 and a.ifCcfpO==1])
    zhhL = hhL / hh1 if hh1 > 0 else -9
    zhhI = hhI / hh1 if hh1 > 0 else -9
        # write to dataframe
    rl1 = ['staFin!', t]
    rl2 = [ind , pop, cur, ret , ever]
    rl3 = [land, cul, aba, ccf , zcul, zaba, zccf]
    rl4 = [hhs , hh1, hh0, zhh1, zhh0]
    rl5 = [      hhL, hhI, zhhL, zhhI]
    
    rl = rl1 + rl2 + rl3 + rl4 + rl5
    
    # return to write dataframe of df_sta_fin
    return rl
    
    

















