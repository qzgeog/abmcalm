""" ABM-CARO: Qi Zhang (qz@unc.edu) """

### World Fucntions [aworld.py] ####
"""
Vector:
    1. Roof locations (point)
    2. Tiantangzhai boundary (polygon)
"""

# import built-in modules
import time
import fiona
import math
import random as rand
import numpy  as np
import scipy.stats as stats
from   shapely.geometry import shape


""" W-Function 1: Initialize hh point locations """
def assign_hhs(hhList, fn1, fn2):
    # hhList=aglistHHs, fn1=shpFn_hhPnt, fn2=shpFn_vills
    
    ## Households: initialize 4 attributes
        # hhPnt, hhLocX, hhLocY, hhElev
    
    # read hh points
    hhPntList = []
    with fiona.open(fn1) as c:          # shpFn_hhPnt = 'hhPnts.shp'
        for i in range(len(c)):
            hhPntList.append(next(c))
    
    # read village boundary polygons
    vilList = []
    with fiona.open(fn2) as c:          # shpFn_vills = 'villBounds.shp'
        for i in range(len(c)):
            vilList.append(next(c))
    
    # sample points for each village
    hhList_new = []
    # loop 7 villages
    for vil in vilList:
        geom  = shape(vil['geometry'])
        # select hhs and hh points within this village
        l_hhs = [a for a in hhList    if a.villid==vil['properties']['villid']]
        l_pts = [a for a in hhPntList if geom.intersects(shape(a['geometry']))]
        # shuffle hh and hh points
        rand.shuffle(l_hhs)
        rand.shuffle(l_pts)
        # derive household's point, X and Y, and elevation
        for hh in l_hhs:                       # !!! hh attrs initialized !!! #
            pt        = l_pts.pop()
            ptGeom    = shape(pt['geometry'])        # point geometry
            ptElev    = pt['properties']['hhElev']   # elevation
            hh.hhPnt  = ptGeom
            hh.hhLocX = ptGeom.x
            hh.hhLocY = ptGeom.y
            hh.hhElev = ptElev
        # append within-village household list to the new household list
        hhList_new = hhList_new + l_hhs
    
    # message
    # print('Success WF1! hh points are scattered over roofs within villages.')
    # print('\t hhPnt, hhLocX, hhLocY, hhElev.')
    
    return hhList_new



""" W-Function 2: Assign plots to hhs """
def assign_plots(hhList, plList):
    # hhList=aglistHHs, plList=aglistPLs
    
    ## --- Run Time --- ##
    start_time = time.time()
    ## --- Run Time --- ##
    
    
    ## Part I: assign farm plots to hhs
    
    # customize pmf for distance from farm plot to hh
    xk = np.arange(24)
    pk = (0, 0.288832914, 0.285474391, 0.162048699, 0.092359362, 0.058774139, 
          0.036943745, 0.021830395, 0.01511335, 0.005877414, 0.003358522, 
          0.006717045, 0.003358522, 0.003358522, 0.001679261, 0.001679261, 
          0.000839631, 0, 0.005037783, 0, 0.001679261, 0.002518892, 
          0.001679261, 0.000839631)
    custm_dist = stats.rv_discrete(name='custm', values=(xk, pk))
    
    # select farm plots only
    fpList = [a for a in plList if a.code in [60,61,69]]
    
    # 1) link most farm plots to households 
    # message
    # print('Here, start to assign most farm plots to households... \n')
    
    fpList_new = []
    
    # loop households
    for hh in hhList:
       
        # if no available farm plots, no land; Continue to next household
        if len(fpList) == 0:
            hh.hhLandOwn = 0.0
            continue
        
        # initiate land owned and assigned for this household
        pt            = hh.hhPnt
        area_limited  = [hh.hhLandOwn,hh.hhLandOwn-1.0][hh.hhLandOwn>1.0]
        area_assigned = 0.0
        hh.hhLandOwn  = 0.0
        timesUp       = 0
        
        # loop until assigned enough land OR time's up
        while area_assigned < area_limited:
            # if (NO available plot) OR (time's up), no need to search next plot
            if len(fpList) == 0 or timesUp > 20:
                break
            else:
                # get a search distance
                d = 100.0*(custm_dist.rvs()-rand.random())   # customized pmf
                d = [d,5.0][d<5.0]                           # set minimum 5m
                # get farm plot points at this distance
                l = [a for a in fpList if (d-5)<pt.distance(a.plPnt)<(d+5)]
                # if NO farm plot at distance, times add 1; Continue to search
                if len(l) == 0:
                    timesUp += 1
                    continue
                else:
                    # randomly select one plot 
                    aFP = rand.choice(l)
                    # assign plot IDs          # !!! pl attrs initialized !!! #
                    aFP.hhid   = hh.hhid
                    aFP.rgid   = hh.rgid
                    aFP.villid = hh.villid
                    # add to new farm plot list
                    fpList_new.append(aFP)
                    # add plot area to total area assigned
                    area_assigned += aFP.area
                    # remove plot from old farm plot list
                    fpList.remove(aFP)
    
    # message
    # print('A number of {} plots have been assigned. '.format(len(fpList_new)))
    # print('\t The rest {} of 12,236 plots remain. \n'.format(len(fpList)))
    
    # 2) link households to the rest of farm plots        
    # message
    # print('Here, start to assign households to remaining farm plots... \n')
    
    # shuffle hhs and farm plots
    rand.shuffle(hhList)
    rand.shuffle(fpList)
    
    # loop farm plots
    for aFP in fpList:
        
        # an empty list to store searched hhs
        pt      = aFP.plPnt
        l_hhs   = []
        timesUp = 0
        
        # while loop until find at least one household
        while len(l_hhs) == 0:
            # if times up, assign the nearest household, break while loop
            if timesUp > 100:
                distMin = 999999.9
                for aHH in hhList:
                    dist = aHH.hhPnt.distance(pt)
                    if dist < distMin:
                        distMin = dist
                        theHH   = aHH
                l_hhs.append(theHH)
                break
            # grab distance from farm plot to its household
            d = 100*(custm_dist.rvs()-rand.random())       # customized pmf
            d = [d,5.0][d<5.0]
            # get a list of household points at this distance
            l_hhs = [a for a in hhList if (d-5.0)<pt.distance(a.hhPnt)<(d+5.0)]
            timesUp += 1
        
        # randomly select one household from household list
        theHH      = rand.choice(l_hhs)
        # link household to farm plot          # !!! pl attrs initialized !!! #
        aFP.hhid   = theHH.hhid
        aFP.rgid   = theHH.rgid
        aFP.villid = theHH.villid
    
    # combine list of remaining farm plots to new list of farm plots
    fpList_new = fpList_new + fpList
    
    # message
    # print('The rest {} plots have been assigned. \n'.format(len(fpList)))
    # print('All farm plots have been assigned. ')
    # print('\t Total number of farm plots: {} \n'.format(len(fpList_new)))
    
    
    ## Part II: assign ccfp plots to households
    # message
    # print('Here, start to assign to ccfp plots to households... \n')
    
    # customize pmf of distance from ccfp plot to household
    xk = np.arange(19)
    pk = (0, 0.105555556, 0.233333333, 0.166666667, 0.122222222, 0.127777778, 
          0.066666667, 0.061111111, 0.055555556, 0.016666667, 0, 0, 0.011111111, 
          0, 0.011111111, 0.005555556, 0.005555556, 0.005555556, 0.005555556)
    custm_distCcfp = stats.rv_discrete(name='custm', values=(xk, pk))
    
    # select ccfp plots only
    ccList = [a for a in plList if a.code in [99]]
    
    # shuffle hhs and ccfp plots
    rand.shuffle(hhList)
    rand.shuffle(ccList)
    
    # loop ccfp plots
    for aCC in ccList:
        
        # an empty list to store searched hhs
        pt      = aCC.plPnt
        l_hhs   = []
        timesUp = 0
        
        # while loop until find at least one household
        while len(l_hhs) == 0:
            # if times up, assign the nearest hh, break the while loop
            if timesUp > 50:
                distMin = 999999.9
                for aHH in hhList:
                    dist = aHH.hhPnt.distance(pt)
                    if dist < distMin:
                        distMin = dist
                        theHH   = aHH
                l_hhs.append(theHH)
                break
            # grab geo-distance for ccfp to hh
            d = 100*(custm_distCcfp.rvs()-rand.random())    # customized pmf
            d = [d,5.0][d<5.0]
            # get a list of household points at this distance
            l_hhs = [a for a in hhList if (d-5.0)<pt.distance(a.hhPnt)<(d+5.0)]
            timesUp += 1
        
        # link household to ccfp plot          # !!! pl attrs initialized !!! #
        theHH      = rand.choice(l_hhs)
        aCC.hhid   = theHH.hhid
        aCC.rgid   = theHH.rgid
        aCC.villid = theHH.villid
    
    # message
    # print('All ccfp plots have been assigned. ')
    # print('\t Total number of ccfp plots: {} \n'.format(len(ccList)))
    
    # !!DON'T FORGET: combine new lists back to the entire list
    plList = fpList_new + ccList
    
    # message
    # print('At this point, all plots have been assigned to hhs.')
    # print('\t Total number of plots: {}'.format(len(plList)))
    # print('\t hhid, rgid, villid. \n')
    
    
    ## Part III: derive household attributes
        # hhLandOwn, hhLandPlant, areaCcfp, areaEwfp, ifCcfp
        # code: [60=paddy, 61=dry, 69=abandoned, 99=ccfp]

    # customize pmf for ewfp area claimed by hh (low elevation)
    xk = np.arange(18)
    pk = (0.009493671, 0.199367089, 0.272151899, 0.234177215, 0.094936709, 
          0.063291139, 0.03164557, 0.03164557, 0.015822785, 0.018987342, 
          0.006329114, 0.009493671, 0.006329114, 0.003164557,0,0,0,0.003164557)
    custm_ewfp_low = stats.rv_discrete(name='custm', values=(xk, pk))
    # pmf of ewfp (high elevation)
    xk = np.arange(14)
    pk = (0.006060606, 0.315151515, 0.193939394, 0.157575758, 0.096969697, 
          0.072727273, 0.042424242, 0.024242424, 0.03030303, 0.03030303, 
          0.018181818, 0.006060606, 0, 0.006060606)
    custm_ewfp_high = stats.rv_discrete(name='custm', values=(xk, pk))
    
    # loop households
    for aHH in hhList:
        # set default attributes to zeros       # !!! hh attrs changed !!! #
        aHH.hhLandOwn   = 0.0                                    # hhLandOwn
        aHH.hhLandPlant = 0.0                                    # hhLandPlant
        aHH.areaCcfp    = 0.0                                    # areaCcfp
        aHH.areaEwfp    = 0.0                                    # areaEwfp
        aHH.ifCcfp      = 0                                      # ifCcfp
        # area of farm plots owned
        l = [a for a in plList if a.hhid==aHH.hhid and a.code in [60,61,69]]
        aHH.hhLandOwn   = sum([a.area for a in l])          # hhLandOwn
        # area of farm plots planted
        l = [a for a in plList if a.hhid==aHH.hhid and a.code in [60,61   ]]
        aHH.hhLandPlant = sum([a.area for a in l])          # hhLandPlant
        # area of ccfp plots
        l = [a for a in plList if a.hhid==aHH.hhid and a.code in [99      ]]
        aHH.areaCcfp    = sum([a.area for a in l])         # areaCcfp
        # whether participating in ccfp
        aHH.ifCcfp      = [0,1][aHH.areaCcfp>0]               # ifCcfp
        # area of ewfp
        if aHH.hhElev < 700:
            rvs = custm_ewfp_low.rvs()
            aHH.areaEwfp = 10.0*[custm_ewfp_low.rvs() -rand.random(),0][rvs==0]
        else:
            rvs = custm_ewfp_high.rvs()
            aHH.areaEwfp = 30.0*[custm_ewfp_high.rvs()-rand.random(),0][rvs==0]
    
    # numN1 = len([a for a in hhList if a.hhLandOwn==0 and a.areaCcfp==0])
    # perN1 = (100.0*numN1) / 3597.0
    # numN2 = len([a for a in hhList if a.areaEwfp==0])
    # perN2 = (100.0*numN2) / 3597.0
    
    # message
    # print('Derived household characteristics. ')
    # print('\t HHs: hhLandOwn, hhLandPlant, areaCcfp, areaEwfp, ifCcfp. ')
    # print('Note: {} ({:.1f}%) households have no land. \n'.format(numN1,perN1))
    # print('Note: {} ({:.1f}%) households have no EWFP. \n'.format(numN2,perN2))
    
    
    ## Part IV: derive plot attributes
        # geoDist, abanYr
    
    # customize abandoned years (survey 2013)
    xk = np.arange(11)
    pk = (0.279475983, 0.174672489, 0.148471616, 0.113537118, 0.043668122, 
          0.087336245, 0.03930131, 0.021834061, 0.021834061, 0, 0.069868996)
    custm_abanYr = stats.rv_discrete(name='custm', values=(xk, pk))
    
    # loop plots 
    for aPL in plList:
        # find its hh
        theHH = next((x for x in hhList if x.hhid==aPL.hhid), None)
        # calculate geo-distance from plot to household
        aPL.geoDist = aPL.plPnt.distance(theHH.hhPnt)
        # grab abandonment years for abandoned plots
        aPL.abanYr = [-99,custm_abanYr.rvs()][aPL.code==69]    # customized pmf
    
    # message
    # print('Derived plot features. ')
    # print('\t PLs: geoDist, abanYr. \n')
    
    # message
    # print('Success WF2! Assigned all plots to hhs. ')
    # print('\t HHs: hhLandOwn, hhLandPlant, areaCcfp, areaEwfp, ifCcfp. ')
    # print('\t PLs: hhid, rgid, villid, geoDist, abanYr. \n')
    
    
    ## --- Run Time --- ##
    run_time = time.time() - start_time
    if   run_time < 60:
        print('Assing plots, run time: {:.0f} sec \n'.format(run_time))
    elif run_time < 3600:
        mins, secs = int(run_time/60), run_time%60
        print('Assing plots, run time: {}min, {:.0f}sec \n'.format(mins, secs))
    else:
        hrs, mins = int(run_time/3600), int(run_time%3600/60)
        print('Assing plots, run time: {}hr, {:.0f}min \n'.format(hrs, mins))
    ## --- Run Time --- ##
    
    # return list of plots
    return plList
        

""" W-Function 3: if plant trees to participate in CCFP """
def prob_plant(ad, p, plList, hhList, c, f, q):
    # ad=adapt, p=agPL, plList=aglistPLs, hhList=aglistHHs
    # c=thrRG, f=fRadius, q=sn1
    
    # concepts
        # thrRG: threshold of RG limit (0=NoLimit, 1=WithAll)
        # sn   : influencing degree of social norm
        # cRG  : level of RG involvement (area of in-RG plots / area of plots)
    
    # return list of values
        # [probPla, rand, cRG]
        # [propActPl, areActPl, areTotPl]
        # [percActGp, numActGp, numTotGp]
        # [plid2, area2, ifCcfp2, ifCcfpO2]
    
    # set buffer radius (240)
    d = 240 * f
    
    # set default as to NOT plant
    probPla   = -9
    cRG       = -9
    propActPl = -9
    areActPl  = -9
    areTotPl  = -9
    percActGp = -9
    numActGp  = -9
    numTotGp  = -9
    
    # get plots within buffer distance, excluding itself
    buf = p.plPnt.buffer(d)
    l_n = [a for a in plList if buf.intersects(a.plPnt) and a.plid!=p.plid]
    # get sn of hh for this plot
    aHH = next((a for a in hhList if a.hhid==p.hhid),None)
    q   = aHH.sn
    if aHH == None:
        print('this plot has no household manage, set q as average')
    
    # only if there are 2+ plots nearby
    if len(l_n) >= 2:
        # calcualte level of RG involvement
        area1 = sum([a.area for a in l_n if a.rgid==p.rgid])     # same-RG plots
        area2 = sum([a.area for a in l_n])                       # all plots
        cRG   = area1 / area2
        # only if exceeds RG limit of collective action
        if cRG >= c:                                        # c=thrRG
            # calcualte stats of land areas
            areTotPl  = sum([a.area for a in l_n])
            areActPl  = sum([a.area for a in l_n if a.code in [69,99]])
            propActPl = areActPl / areTotPl       # key variable
            # calculate stats of corresponding households
            numTotGp  = len(set([a.hhid for a in l_n]))
            numActGp  = len(set([a.hhid for a in l_n if a.code in [69,99]]))
            percActGp = numActGp / numTotGp 
            # estimate probability of planting
            probPla   = math.pow(propActPl,(1/(1-q)))
    # add to return list
    rl1 = [probPla, cRG]
    rl2 = [propActPl, areActPl, areTotPl, percActGp, numActGp, numTotGp]
    rl3 = [p.plid, p.hhid, p.area, p.ifCcfp, p.ifCcfpO]
    
    # if policy is not adaptive to local SES feedback (reference model)
    if ad == 0:
        rl1[0] = 0.0            # set probPla = 0.0
    
    # return to ls
    return rl1 + rl2 + rl3






        
    
    
    


    

        
    
    
    






