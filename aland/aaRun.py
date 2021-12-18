# Topic: land constraint (demo)

"""========================================================================="""
"""
Agent-Based Model for Cropland Abandonment and Labor Migration (ABM-CALM)

Project: NSF Coupled Natural and Human Systems
PI: Conghe Song (csong@email.unc.edu), Professor in Geography
Institute: University of North Carolina at Chapel Hill

Copyright: Qi Zhang & Conghe Song, All Rights Reserved

Developer: 
    Qi Zhang (qz@unc.edu;qz@bu.edu)

Module to be installed (conda via command prompt):
    conda install -c conda-forge shapely
    conda install -c conda-forge fiona
    conda install -c anaconda pandas
    conda install -c anaconda scipy

Code sheet for WV-2 satellite image classification:
    1. Residence
    3. Forests (EWFP forests)
    6. Land parcels: 60-Paddyland; 61-Dryland; 69-Abandoned; 99-CCFP
    7. Barren land
    8. Grass
    
Payment schemes:
    EWFP: 8.75 yuan per year per mu
    CCFP (Sch 0): 125 yuan per year per mu (continue)
    CCFP (Sch 1): 800, 300, 400 at the 1st, 3rd, 5th year (discrete)
"""
"""========================================================================="""



# import default modules
import time, sys
import random as rand
import pandas as pd
# import peronalized modules
import aworld, afunc, awrite
import azagents

# --- Run Time (the whole simulations) --- #
start_time_abm = time.time()
# --- Run Time (the whole simulations) --- #

# send to computer cluster: LongLeaf (UNC) or SCC (BU)
#jobid = sys.argv[1]
jobid = 1



                       ###===== Initizalization =====###


## set input file names ##

# social data: csv file
dtFn_pop    = 'dataINs.csv'     # population data (2012)
dtFn_plo    = 'dataPLs.csv'     # plot data (farm + CCFP)
# spatial data: shapefiles
shpFn_vills = 'villBounds.shp'  # village boundaries
shpFn_hhPnt = 'hhPnts.shp'      # household points
shpFn_plPnt = 'plPnts.shp'      # plot points
# validation data
fn_vd_in    = 'dmINs.csv'       # individuals with determined attribtues
fn_vd_hh    = 'dmHHs.csv'       # households with determined attribtues
fn_vd_pl    = 'dmPLs.csv'       # households with determined attribtues

## Set global variables ##

# time steps
ticks    = 20                   # number of time steps (year)
# key experiment control
feedback =  1                   # if has SES feedback? (0=no, 1=yes)
adapt    =  0                   # if policy is adaptive to local SES feedback
validate =  1                   # if all attributes are determined
# probabilities
pReturn  =  0.20                # probability of return-migration
pRent    =  0.10                # probability of rent out a plot
pReclaim =  0.10                # probability of reclaim a plot at 1st aband yr
pRevert  =  0.00                # probability of re-convert ccfp to cultivation
# CCFP scheme & PES factors
scheme   =  0                   # CCFP payment schemes (0=continuous,1=discrete)
fCcfp    =  1.00                # factor of CCFP payment
fEwfp    =  1.00                # factor of EWFP payment
end5yr   =  0                   # if payment ceases after 5th year
# reforestation
thrRG    =  0.00                # threshold of RG limit (0=NoLimit, 1=WithAll)
fRadius  =  1.00                # factor of buffer radius (240m, 175,430 m2)
sn1      =  0.50                # mu  of influencing degree of social norm
sn2      =  0.05                # sig of influencing degree of social norm

# key part of this research (a-land)
violate  =  0.00                # violating policy of maintaining basic land


if validate == 0:
    ## Create agents ##
    
    # individuals
        # (imported)    pid, hhid, rgid, villid
        # (imported)    relateHead, ifFemale, age, ifMarried, numChild
        # (initialized) ifOutMig, ifRetMig, ifEverOut, work, edu
    # households
        # (imported)    hhid, rgid, villid
    # plots
        # (imported)    plid, centerX, centerY, area, code, elev, slope
        # (imported)    aspect, twi, distCcfp, distEwfp
        # (initialized) plPnt
    
    # individuals [afunc.py-I1]
    df = pd.read_csv(dtFn_pop)              # dtFn_pop = dataINs.csv
    aglistINs = afunc.create_agents(df,'individuals')                     # 65"
    # households  [afunc.py-I1]
    df = df.loc[df['relateHead']==1][['hhid','rgid','villid']]
    aglistHHs  = afunc.create_agents(df,'households')                     #  2"
    # plots       [afunc.py-I1]
    df = pd.read_csv(dtFn_plo)              # dtFn_plo = 'dataPLs.csv'
    aglistPLs  = afunc.create_agents(df,'plots')                          #  2"
    
    ## shuffle all lists
    rand.shuffle(aglistINs)
    rand.shuffle(aglistHHs)
    rand.shuffle(aglistPLs)
    
    
    ## Initialize attributes ##
    
    # assign households to roof points, derive 4 characteristics
      # [aworld.py-WF1]
        # (initialized) HHs: hhPnt, hhLocX, hhLocY, hhElev
    aglistHHs = aworld.assign_hhs(aglistHHs, shpFn_hhPnt, shpFn_vills)    #  5"
    
    # initialize 7 household characteristics
      # [afunc.py-I2]
        # (initialized) HHs: hdIfFemale, hdAge, hdEdu, hdIfMarried
        # (initialized) HHs: hhSize, hhNumCurOut, hhNumPreOut, "hhLandOwn"
        # (initialized) HHs: sn
    aglistHHs = afunc.init_hh_char(aglistHHs, aglistINs, sn1, sn2)        # 10"
    
    # assign plots to households
      # [aworld.py-WF2]
        # (initialized) HHs: hhLandOwn, hhLandPlant, areaCcfp, ifCcfp, areaEwfp
        # (initialized) PLs: hhid, rgid, villid, geoDist, abanYr
    aglistPLs = aworld.assign_plots(aglistHHs, aglistPLs)                 # 52'
    
    # vlookup if CCFP of household to corresponding individuals and plots
      # [afunc.py-I3]
        # (initialized) INs: ifCcfp
        # (initialized) PLs: ifCcfp
    aglistINs = afunc.vlookup_ccfp(aglistHHs, aglistINs)                  #  1"
    aglistPLs = afunc.vlookup_ccfp(aglistHHs, aglistPLs)                  #  1"
    
    # define indigenous CCFP households
      # [afunc.py-I4]
        # INs, PLs, HHs: ifCcfpO
    aglistINs = afunc.original_ccfp(aglistINs)
    aglistPLs = afunc.original_ccfp(aglistPLs)
    aglistHHs = afunc.original_ccfp(aglistHHs)


# if all attributes are determined (e.g., Huanghe Village for validation)
else:
    # create list of individual agents
    df = pd.read_csv(fn_vd_in)           # fn_vd_in = 'vdINs.csv'
    aglistINs = []
    for index, row in df.iterrows():
        al = list(row)
        ag = azagents.Individual(*al)
        aglistINs.append(ag)
    # create list of household agents
    df = pd.read_csv(fn_vd_hh)           # fn_vd_hh = 'vdHHs.csv'
    aglistHHs = []
    for index, row in df.iterrows():
        al = list(row)
        ag = azagents.Household(*al)
        aglistHHs.append(ag)
    aglistHHs = azagents.init_hh_demo(aglistHHs, aglistINs, sn1, sn2)
    # create list of plot agents
    df = pd.read_csv(fn_vd_pl)           # fn_vd_pl = 'vdPLs.csv'
    aglistPLs = []
    for index, row in df.iterrows():
        al = list(row)
        ag = azagents.Plot(*al)
        aglistPLs.append(ag)


## Write dataframe headlines ##
# behaviors
df_mig = pd.DataFrame(columns = awrite.df_head('mig'))
df_ret = pd.DataFrame(columns = awrite.df_head('ret'))
df_aba = pd.DataFrame(columns = awrite.df_head('aba'))
df_rec = pd.DataFrame(columns = awrite.df_head('rec'))
df_ren = pd.DataFrame(columns = awrite.df_head('ren'))
df_pla = pd.DataFrame(columns = awrite.df_head('pla'))
df_rev = pd.DataFrame(columns = awrite.df_head('rev'))
# statistics
df_sta_mig = pd.DataFrame(columns = awrite.df_head('staMig'))
df_sta_aba = pd.DataFrame(columns = awrite.df_head('staAba'))
df_sta_pla = pd.DataFrame(columns = awrite.df_head('staPla'))
df_sta_col = pd.DataFrame(columns = awrite.df_head('staCol'))
df_sta_com = pd.DataFrame(columns = awrite.df_head('staCom'))
df_sta_fin = pd.DataFrame(columns = awrite.df_head('staFin'))
# initialized attributes
df_ini_ins = pd.DataFrame(columns = awrite.df_head('iniINs'))
df_ini_pls = pd.DataFrame(columns = awrite.df_head('iniPLs'))
df_ini_hhs = pd.DataFrame(columns = awrite.df_head('iniHHs'))


## write initialized agent attributes
df_ini_ins = awrite.tp_attr(df_ini_ins, aglistINs, aglistPLs, aglistHHs, 'ins')
df_ini_pls = awrite.tp_attr(df_ini_pls, aglistINs, aglistPLs, aglistHHs, 'pls')
df_ini_hhs = awrite.tp_attr(df_ini_hhs, aglistINs, aglistPLs, aglistHHs, 'hhs')
# df_ini_ins.to_csv('aa_ini1_ins_{}.csv'.format(str(jobid)))  # init: individuals
# df_ini_pls.to_csv('aa_ini2_pls_{}.csv'.format(str(jobid)))  # init: plots
# df_ini_hhs.to_csv('aa_ini3_hhs_{}.csv'.format(str(jobid)))  # init: households


## write initial state
al = awrite.tick_final(0, aglistINs, aglistPLs, aglistHHs)
df_sta_fin.loc[len(df_sta_fin)] = al



                    ###===== Iteration =====###

# run ticks
for tick in range(ticks):   # 15' ~ 18'
    
    ## --- Run Time (ticks) --- ##
    start_time_tick = time.time()
    ## --- Run Time (ticks) --- ##
    
    
    ## shuffle all lists ##
    rand.shuffle(aglistINs)
    rand.shuffle(aglistHHs)
    rand.shuffle(aglistPLs)
    
    
    ## new factor of CCFP payment rate ##
    fCCnew = afunc.set_ccfp_rate(s=scheme, t=tick, f=fCcfp) # [afunc.py-T1]
    
    
    ## store key variables at tick start ##
      # individuals
        # [numPop, numPop1, numPop0, numCur, numCur1, numCur0]
    lStatIN = awrite.stat_in_pop(inList=aglistINs)          # [awrite.py-OF1a]
      # plots: for abandonment
        # [arePlo, arePlo1, arePlo0, areCur, areCur1, areCur0]
    lStatFP = awrite.stat_fp_plo(plList=aglistPLs)          # [awrite.py-OF2a]
      # plots: for reforetation
        # [areAPs, areAPs1, areAPs0, areCCs, areCCs1, areCCs0]
    lStatCC = awrite.stat_cc_plo(plList=aglistPLs)          # [awrite.py-OF3aA]
    
    
    ## Store IDs and outputs to update attributes
      # individuals
    upd_mig = []        # element: agIN.pid
    upd_ret = []        # element: agIN.pid
      # plots (abandon)
    upd_aba = []        # element: agPL.plid
    upd_rec = []        # element: agPL.plid
    upd_ren = []        # element: agPL.plid
    opt_ren = []        # element: [agPL.plid, agPL.area, hhidOu, hhidIn]
      # plots (plant)
    upd_pla = []        # element: agPL.plid
    opt_pla = []        # element: [probPla, cRG, ...(6)..., plid2, area2]
    upd_rev = []        # element: agPL.plid
    
    
    ## Deal with Agent Individuals ##
    
    # loop individual agents
    for agIN in aglistINs:
        """ Deal with Agent Individual: Out-Migration and Return-Migration """
        
        # out-migration #
        
        # if qualified, estimate probability of migrating
        if afunc.if_qualify_mig(p=agIN, inList=aglistINs):     # [afunc.py-T2]
            # calcualte probability of out-migration      
            probMig = afunc.pred_mig(p=agIN, hhList=aglistHHs, f1=fCCnew, 
                      f2=fEwfp, t=tick, e=end5yr, fb=feedback) # [afunc.py-T3]
            # decide whether to migrate out
            r = rand.random()
            # if to migrate
            if r < probMig:
                # store person ID to update list
                upd_mig.append(agIN.pid)
                # Write dataframe 'Mig!': attributes of person to migrate out
                lr1 = ['mig!', tick+1]
                lrw = agIN.write_self()
                lrz = [r, probMig]
                df_mig.loc[len(df_mig)] = lr1 + lrw + lrz
        
        # return-migration #
        
        # only if person is current out-migrant
        if agIN.ifOutMig == 1: 
            # decide whether to go home                        # [afunc.py-T4]
            al = afunc.if_return(p=agIN, hhList=aglistINs, pr=pReturn) 
            # if to return (a list: [goHome, r])
            if al[0]: 
                # store person ID to update list
                upd_ret.append(agIN.pid)
                # Write dataframe 'Ret!'"': attributes of people to return home
                lr1 = ['ret!', tick+1]
                lrw = agIN.write_self()
                lrz = [al[1], pReturn]
                df_ret.loc[len(df_ret)] = lr1 + lrw + lrz
    
    
    ## Deal with Agent Plots (Abandonment) ##
    
    # loop plot agents
    for agPL in aglistPLs:
        """ Deal with Agent Plot: Abandonment, Reclaimation, and Rent """
        
        # abandonment #
        
        # if qualified, estimate probability of being abandoned
        if agPL.code in [60,61] and afunc.if_qualify_aba(p=agPL,v=violate): # [afunc.py-T5] # modify (a-land)
            # estimate probability of abandoning the farm plot
            probAba = afunc.pred_aban(p=agPL, hhList=aglistHHs, f1=fCCnew, 
                      f2=fEwfp, t=tick, e=end5yr, fb=feedback)  # [afunc.py-T6]
            # decide whether to be abandoned
            r = rand.random()
            # if to be abandoned
            if r < probAba:
                # store plot ID in update list 
                upd_aba.append(agPL.plid)
                # Write dataframe 'Aba!': features of plot to be abandoned
                lr1 = ['aba!', tick+1]
                lrw = agPL.write_self()
                lrz = [r, probAba]
                df_aba.loc[len(df_aba)] = lr1 + lrw + lrz
        
        # reclaimation #
        
        # only if plot is an abandoned plot
        if agPL.code == 69:
            # decide whether to reclaim
            r = rand.random()
            # if to be reclaimed
            if pReclaim == 1:    # to avoid power of negative value
                aprob = 1
            else:
                aprob = pReclaim*((1-pReclaim)**(agPL.abanYr-1))
            if r < aprob and agPL.abanYr > 0:    # pReclaim=0.00
                # store plot ID to update list
                upd_rec.append(agPL.plid)
                # Write dataframe 'Rec!': features of plot to be reclaimed
                lr1 = ['rec!', tick+1]
                lrw = agPL.write_self()
                lrz = [r, pReclaim]
                df_rec.loc[len(df_rec)] = lr1 + lrw + lrz
        
        # renting-out or -in #
        
        # get list of neighbor hhs
        al = [a for a in aglistHHs if a.rgid==agPL.rgid and a.hhid!=agPL.hhid]
        # Only if (not abandoned) AND (not to be abandoned) AND (has neighbor)
        if agPL.code in [60, 61] and agPL.plid not in upd_aba and len(al) > 0:
            # decide whether to rent
            r = rand.random()
            # if to be rented
            if r < pRent:                                       # pRent=0.16
                # store plot ID to update list
                upd_ren.append(agPL.plid)
                # randomly select an RG neighbor to rent in, get its ID
                hhidOu = agPL.hhid
                hhidIn = rand.choice(al).hhid
                opt_ren.append([agPL.plid, agPL.area, hhidOu, hhidIn])
                # Write dataframe 'Ren!: features of plot to be rented out
                lr1 = ['ren!', tick+1]
                lrw = agPL.write_self()
                lrz = [r, pRent, hhidOu, hhidIn]
                df_ren.loc[len(df_ren)] = lr1 + lrw + lrz
    
    
    ## Deal with Agent Plots (Reforestation) ##
    
    # loop plot agents
    for agPL in aglistPLs:
        """ Deal with Agent Plot: Reforestation """
        
        # reforestation #
        
        # only if for abandoned plots
        if agPL.code in [69] and afunc.if_qualify_aba(p=agPL,v=violate): # modify (a-land)
            # only if abandoned plots, decide if plant trees
                # return: [probPla, cRG]
                # return: [propActPl, areActPl, areTotPl]
                # return: [percActGp, numActGp, numTotGp]
                # return: [plid2, area2, ifCcfp, ifCcfpO]
            al = aworld.prob_plant(ad=adapt, p=agPL, plList=aglistPLs, hhList=aglistHHs,
                                   c=thrRG, f=fRadius, q=sn1) # [aworld.py-WF3]
            # decide whether to plant
            r = rand.random()
            # if to plant
            if r < al[0]:                       # al[0] is probPla
                # store plot ID to update list
                upd_pla.append(agPL.plid)
                # store output list as a list
                opt_pla.append(al)
                # Write dataframe 'Pla!': features of plot to be planted
                lr1 = ['pla!', tick+1]
                lrw = agPL.write_self()
                lrz = [r] + al[0:8]
                df_pla.loc[len(df_pla)] = lr1 + lrw + lrz
        
        # revertion #
        
        # only if for ccfp plots
        if agPL.code in [99]:
            # decide whether to revert
            r = rand.random()
            # if to be reverted for cultivation
            if r < pRevert:                                     # pRevert=0.05
                # store plot ID to update list
                upd_rev.append(agPL.plid)
                # Write dataframe 'Rev!': features of plot to be reverted
                lr1 = ['rev!', tick+1]
                lrw = agPL.write_self()
                lrz = [r, pRevert]
                df_rev.loc[len(df_rev)] = lr1 + lrw + lrz
    
    
    
    ## Write stats for migration, abandonment, and reforestation ##
    
    # migration                                              # [awrite.py-OF1b]
    al = awrite.stat_in_mig(u1=upd_mig, u2=upd_ret, l=aglistINs, ls=lStatIN)
    df_sta_mig.loc[len(df_sta_mig)] = ['staMig!', tick+1] + al
    
    # abandonment                                            # [awrite.py-OF2b]
    al = awrite.stat_fp_aba(u1=upd_aba, u2=upd_rec, l=aglistPLs, ls=lStatFP)
    df_sta_aba.loc[len(df_sta_aba)] = ['staAba!', tick+1] + al
    
    # planting                                               # [awrite.py-OF3b]
    al = awrite.stat_cc_pla(u1=upd_pla, u2=upd_rev, l=aglistPLs, ls=lStatCC)
    df_sta_pla.loc[len(df_sta_pla)] = ['staPla!', tick+1] + al
    
    # collective action                                      # [awrite.py-OF4a]
    al = awrite.stat_cc_col(u=opt_pla, l=aglistPLs)
    df_sta_col.loc[len(df_sta_col)] = ['staCol!', tick+1] + al
    # collective: learned vs indigenous                      # [awrite.py-OF4b]
    al = awrite.stat_cc_com(u=opt_pla, l=aglistPLs)
    df_sta_com.loc[len(df_sta_com)] = ['staCom!', tick+1] + al
    
    
    
    ## Update agent attributes ##
    
    # store pID to die or marry out
    l_in_die     = []       # agIN.pid
    l_in_gone    = []       # agIN.pid
    # store new babies and married-in persons
    l_new_marrys = []       # (obj) agIN
    l_new_babys  = []       # (obj) agIN
    # store PID and PLID to update hh characteristics
    l_in_split   = []       # agIN.pid
    # store hhID to die
    l_hh_die     = []       # agHH.hhid
    # steo new house
    l_new_hhs    = []       # (obj) agHH
    
    # update individual attributes #
    
    # loop individual agents:
    for agIN in aglistINs:
        """ Update Agent Individual (die) """
        
        # to die 
        if agIN.die():          # True or False
            l_in_die.append(agIN.pid)
    
    # remove dead people
    aglistINs = [a for a in aglistINs if a.pid not in l_in_die]
    
    # loop individual agents (again):
    for agIN in aglistINs:
        """ Update Agent Individual (others)"""
        
        # update attributes of out-migrating persons
        if agIN.pid in upd_mig:
            agIN.ifOutMig  = 1
            agIN.ifOutMig  = 0
            agIN.ifEverOut = 1
        # update attributes of returning-home persons
        if agIN.pid in upd_ret:
            agIN.ifOutMig  = 0
            agIN.ifRetMig  = 1
        
        # update age
        agIN.update_age()
        
        # to marry: [ifGone, ifSplit, l_new]=[True or False, True or False, []]
        ifGoneSplit = agIN.marry(inList=aglistINs, l_new=l_new_marrys)
        if ifGoneSplit[0]:          # if gone, will later die this person
            l_in_gone.append(agIN.pid)
            continue        # !! This person is gone. Continue to next people
        else:                       # if not gone, add a new member
            l_new_marrys = ifGoneSplit[2]
        if ifGoneSplit[1]:          # if split household, store person ID
            l_in_split.append(agIN.pid)
        
        # update education: ifGraduate = True or False
        ifGraduate = agIN.update_edu()
        
        # update work
        agIN.update_work(l1=upd_mig, l2=upd_ret, g=ifGraduate)
        
        # to give birth to baby                 # if give birth, add a new baby
        l_new_babys = agIN.give_birth(l_new=l_new_babys)         #[afunc.py-U1]
        
    # remove gone people married out
    aglistINs = [a for a in aglistINs if a.pid not in l_in_gone]
    
    
    # update plot features #
    
    # loop plot agents:
    for agPL in aglistPLs:
        """ Update Agent Plot """
        
        # update attributes of abandoned plots
        if agPL.plid in upd_aba:
            agPL.code   =  69
            agPL.abanYr =   0
        # update attributes of reclaimed plots, AND (not to be planted)
        if agPL.plid in upd_rec and agPL.plid not in upd_pla:
            agPL.code   =  61 if agPL.dry==1 else 60
            agPL.abanYr = -99
        # update attributes of planted plots
        if agPL.plid in upd_pla:
            agPL.code   =  99
            agPL.abanYr = -99
        # update attributes of reverted plots
        if agPL.plid in upd_rev:
            agPL.code   =  61 if agPL.dry==1 else 60
        
    # loop plot agents (again):
    for agPL in aglistPLs:
        """ Update Agent Plot """
        
        # update distance to ccfp forest
        agPL.update_dist_ccfp(plList=aglistPLs)
        
        # update distance to EWFP forest
        agPL.update_dist_ewfp(plList=aglistPLs)
        
        # update abandonment year
        agPL.update_aban_year(u=upd_aba)
    
    
    # update household chracteristics #
    
    # loop household agents:
    for agHH in aglistHHs:
        """ Update Agent Household (die) """
        
        # to die, append household ID to list
        l_hh_die = agHH.hh_die(inList=aglistINs, l_die=l_hh_die)
    
    # loop household agents (again):
    for agHH in aglistHHs:
        """ Update Agent Household (assign plots) """
        
        # if household is to die
        if agHH.hhid in l_hh_die:
            # assing plots
            # !!! Here, modified plot features: hhid, rgid, villid, geoDist !!!
            agHH.pl_to_neighbor(plList=aglistPLs, hhList=aglistHHs, u=l_hh_die)
    
    # remove dead households
    aglistHHs = [a for a in aglistHHs if a.hhid not in l_hh_die]
    
    # help set new ID
    i = 0
    # loop household agents (again, again):
    for agHH in aglistHHs:
        """ Update Agent Household (others) """
        
        # update house split
        # !! Here, may modify person (new spouse) attributes: hhid !!
        # !! Here, may modify plot features: hhid !!
        l_new_hhs = agHH.split_house(u=l_in_split, inList=aglistINs, 
                                     plList=aglistPLs, l_ags=l_new_marrys, 
                                     l_new=l_new_hhs, mu=sn1, sig=sn2, z=i)
        
        # update head information
        # !! Here, modified person attributes: relateHead !!
        agHH.update_head(inList=aglistINs)
        
        # update hh demographics: hhSize, hhNumCurOut, hhNumPreOut
        agHH.update_demographics(inList=aglistINs)
        
        # update hh land: hhLandOwn, hhLandPlant, areaCcfp, ifCcfp
        agHH.update_land(o=opt_ren, plList=aglistPLs)
        
        # new ID help index plus
        i += 1
    
    # Add new individual and households agents #
    
    # add new married-in people and babies in list of individuals
    aglistINs = aglistINs + l_new_babys + l_new_marrys
    
    # add new splitted households in list of households
    aglistHHs = aglistHHs + l_new_hhs
    
    
    # update if participate CCFP for individuals and plots #
    
    # vlookup ifCcfp for individuals and farm plots
        # [afunc.py-I3]
    aglistINs = afunc.vlookup_ccfp(hhList=aglistHHs, aList=aglistINs)
    aglistPLs = afunc.vlookup_ccfp(hhList=aglistHHs, aList=aglistPLs)
    
    
    ## Output final status of each tick ##
    al = awrite.tick_final(tick+1, aglistINs, aglistPLs, aglistHHs)
    df_sta_fin.loc[len(df_sta_fin)] = al
    
    
    
    ## --- Run Time (ticks) --- ##
    print('End of tick: ', tick+1)
    run_time = time.time() - start_time_tick
    if run_time < 60:
        print('Tick, run time: {:.0f} sec \n'.format(run_time))
    elif run_time < 3600:
        min, sec = int(run_time/60), run_time%60
        print('Tick, run time: {} min, {:.0f} sec \n'.format(min, sec))
    else:
        hr, min= int(run_time/3600), run_time%3600/60
        print('Tick, run time: {} hr, {:.0f} min \n'.format(hr, min))
    print('\n')
    ## --- Run Time (tick) --- ##
    
    
    
    ### End of one tick ###

# Write all dataframes out to csv files
    # behaviors
# df_mig.to_csv('aa_out1_mig_{}.csv'.format(str(jobid)))      # ind : migrate
# df_ret.to_csv('aa_out2_ret_{}.csv'.format(str(jobid)))      # ind : return
# df_aba.to_csv('aa_out3_aba_{}.csv'.format(str(jobid)))      # plot: abandon
# df_rec.to_csv('aa_out4_rec_{}.csv'.format(str(jobid)))      # plot: reclaim
# df_ren.to_csv('aa_out5_ren_{}.csv'.format(str(jobid)))      # plot: rent
# df_pla.to_csv('aa_out6_pla_{}.csv'.format(str(jobid)))      # plot: plant
# df_rev.to_csv('aa_out7_rev_{}.csv'.format(str(jobid)))      # plot: revert
    # statistics
# df_sta_mig.to_csv('aa_sta1_mig_{}.csv'.format(str(jobid)))  # ind : migrate
# df_sta_aba.to_csv('aa_sta2_aba_{}.csv'.format(str(jobid)))  # plot: abandon
# df_sta_pla.to_csv('aa_sta3_pla_{}.csv'.format(str(jobid)))  # plot: plant
# df_sta_col.to_csv('aa_sta4_col_{}.csv'.format(str(jobid)))  # plot: collective
# df_sta_com.to_csv('aa_sta5_com_{}.csv'.format(str(jobid)))  # plot: compare
# df_sta_fin.to_csv('aa_sta6_fin_{}.csv'.format(str(jobid)))  # tick: status
## write agent attributes at the end
# df_end_ins = pd.DataFrame(columns = awrite.df_head('iniINs'))
# df_end_pls = pd.DataFrame(columns = awrite.df_head('iniPLs'))
# df_end_hhs = pd.DataFrame(columns = awrite.df_head('iniHHs'))
# df_end_ins = awrite.tp_attr(df_end_ins, aglistINs, aglistPLs, aglistHHs, 'ins')
# df_end_pls = awrite.tp_attr(df_end_pls, aglistINs, aglistPLs, aglistHHs, 'pls')
# df_end_hhs = awrite.tp_attr(df_end_hhs, aglistINs, aglistPLs, aglistHHs, 'hhs')
# df_end_ins.to_csv('aa_end1_ins_{}.csv'.format(str(jobid)))  # init: individuals
# df_end_pls.to_csv('aa_end2_pls_{}.csv'.format(str(jobid)))  # init: plots
# df_end_hhs.to_csv('aa_end3_hhs_{}.csv'.format(str(jobid)))  # init: households



# --- Run Time (the whole simulation) --- #
print('End of ABM-CARO')
run_time = time.time() - start_time_abm
if run_time < 60:
    print('Full model run time: {:.0f} sec \n'.format(run_time))
elif run_time < 3600:
    min, sec = int(run_time/60), run_time%60
    print('Full model run time: {} min, {:.0f} sec \n'.format(min, sec))
else:
    hr, min= int(run_time/3600), run_time%3600/60
    print('Full model run time: {} hr, {:.0f} min \n'.format(hr, min))
print('\n')
# --- Run Time (the whole simulation) --- #
















