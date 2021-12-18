""" ABM-CARO: Qi Zhang (qz@bu.edu) """

### Classes [agents.py] ###
"""
    1. Household  (self + 19 attributes)
    2. Individual (self + 15 attributes)
    3. Plot       (self + 20 attributes)
"""

# import functions
import random as rand
import numpy as np
import scipy.stats as stats
from shapely.geometry import Point
# import personalized modules
import afunc, agents



### define class: Plot ###
class Plot():
    """ Agent Class: Plot """
    
    ## define plot features ##
    def __init__(self, plid, centerX, centerY, area, code, dry, elev, slope, 
                 aspect, twi, distCcfp, distEwfp, distEwfpO):
        self.__plid    =   int(plid)
        self.centerX   = float(centerX)
        self.centerY   = float(centerY)
        self.area      = float(area)
        self.code      =   int(code)
        self.dry       =   int(dry)
        self.elev      = float(elev)
        self.slope     = float(slope)
        self.aspect    = float(aspect)
        self.twi       = float(twi)
        self.distCcfp  = float(distCcfp)
        self.distEwfp  = float(distEwfp)
        self.distEwfpO = float(distEwfpO)
        # generate point
        self.plPnt    = Point(self.centerX, self.centerY)
    # make ids private
    @property
    def plid(self):
        return self.__plid
    
    ## define methods ##
    
    # write features of plot self
    def write_self(self):
        lr1 = [self.plid    , self.hhid    , self.rgid  , self.villid]
        lr2 = [self.centerX , self.centerY , self.area  , self.code, self.dry]
        lr3 = [self.elev    , self.slope   , self.aspect, self.twi]
        lr4 = [self.distCcfp, self.distEwfp, self.distEwfpO]
        lr5 = [self.geoDist , self.abanYr  , self.ifCcfp, self.ifCcfpO]
        return lr1 + lr2 + lr3 + lr4 + lr5
    
    # update distance to nearest CCFP forest
    def update_dist_ccfp(self, plList):
        # plList=aglistPLs
        # calculate minmum distance
        min_dist = self.distCcfp
        # get ccfp list
        ccList = [a for a in plList if a.code in [99]]
        # loop CCFP plots
        for cc in ccList:
            dist     = self.plPnt.distance(cc.plPnt)
            min_dist = dist if dist < min_dist else min_dist
        # set new distance to CCFP
        self.distCcfp = min_dist
    
    # update distance to nearest EWFP forest
    def update_dist_ewfp(self, plList):
        # plList=aglistPLs
        # get a list of farm plots abandoned longer than 10 years
        l_aba = [a for a in plList if a.abanYr >= 10]
        # list of abandoned within buffer
        buf = self.plPnt.buffer(self.distEwfp)
        l_inside = [a for a in l_aba if buf.intersects(a.plPnt)]
        # update distance
        min_dist = self.distEwfp
        # if there is any 10+ year-old abandoned plot within buffer
        if len(l_inside) > 0:
            # loop the abandoned list within the buffer
            for pl in l_inside:
                dist     = pl.plPnt.distance(self.plPnt)
                min_dist = dist if dist < min_dist else min_dist
        else:
            min_dist = self.distEwfpO
        # set new distance to EWFP
        self.distEwfp = min_dist
    
    # update abandonment year for existing abandoned plots
    def update_aban_year(self, u):
        # u=upd_aba
        # if existing abandoned plot, AND (not in newly abandoned plots)
        if self.code in [69] and self.plid not in u:
            self.abanYr += 1



### define class: Household ###
class Household():
    """ Agent Class: Household """
    
    ## define hh characteristics ##
    def __init__(self, hhid, rgid, villid):
        self.hhid     = int(hhid)
        self.__rgid   = int(rgid)
        self.__villid = int(villid)
    # make ids private, except hhid
    @property
    def rgid(self):
        return self.__rgid
    @property
    def villid(self):
        return self.__villid
    
    
    ## define methods ##
    
    # write characteristics of household self
    def write_self(self):
        lr1 = [self.hhid, self.rgid, self.villid]
        lr2 = [self.hhLocX, self.hhLocY, self.hhElev]
        lr3 = [self.hdIfFemale, self.hdAge, self.hdEdu, self.hdIfMarried]
        lr4 = [self.hhSize, self.hhNumCurOut,self.hhNumPreOut]
        lr5 = [self.hhLandOwn, self.hhLandPlant, self.areaCcfp, self.areaEwfp]
        lr6 = [self.ifCcfp, self.ifCcfpO, self.sn]
        return lr1 + lr2 + lr3 + lr4 + lr5 + lr6
    
    # to die
    def hh_die(self, inList, l_die):
        # inList=aglistINs, l_die=l_hh_die
        if len([a for a in inList if a.hhid==self.hhid]) == 0:
            l_die.append(self.hhid)
        return l_die
    
    # assign plot to neighbor
    def pl_to_neighbor(self, plList, hhList, u):
        # plList=aglistPLs, hhList=aglistHHs, u=l_hh_die
        # select households not in list of to die
        l_live = [a for a in hhList if a.hhid not in u]
        # select alive neighbors within buffer, excluding itself
        b  = self.hhPnt.buffer(480)
        ln = [a for a in l_live if b.intersects(a.hhPnt) and a.hhid!=self.hhid]
        # if no alive neighbor within buffer, get RG neighbor
        if len(ln) == 0:
            ln = [a for a in l_live if a.rgid==self.rgid and a.hhid!=self.hhid]
        # if still no neighbor, get the nearest neighbor
        if len(ln) == 0:
            distMin = 999999.9
            for aHH in [a for a in l_live if a.hhid!=self.hhid]:
                dist = aHH.hhPnt.distance(self.hhPnt)
                if dist < distMin:
                    distMin = dist
                    theHH   = aHH
            ln.append(theHH)
        # message: check if any neighbor
        # print('{} neighbors available to assign plots! \n'.format(len(ln)))
        # loop plots owned
        for pl in [a for a in plList if a.hhid==self.hhid]:
            # randomly pick an RG neighbor hh
            aHH = rand.choice(ln)
            # update attributes               # !!! plot attributes changed !!!
            pl.hhid    = aHH.hhid
            pl.rgid    = aHH.rgid
            pl.villid  = aHH.villid
            pl.geoDist = pl.plPnt.distance(aHH.hhPnt)
    
    # to build a new house
    def split_house(self, u, inList, plList, l_ags, l_new, mu, sig, z):
        # u=l_in_split, inList=aglistINs, plList=aglistPLs
        # l_ags=l_new_marrys, l_new=l_new_hhs, mu=sn1, sig=sn2, z=i
        
        # check if need to build new house
        ag = next((a for a in inList if a.hhid==self.hhid and a.pid in u),None)
        # if to split
        if ag != None:
            # message: check if household split
            # print('household split: hhid = {}! \n'.format(ag.hhid))
            # set new household id
            nhhid = max([a.hhid for a in inList]) + z + 1 + 10000
            # update person's household ID
            ag.hhid       = nhhid                  # !!! agent hhid changed !!!
            ag.relateHead = 1                # !!! agent realteHead changed !!!
            # find this person's spouse
            ag2  = next((a for a in l_ags if a.pid==ag.pid+100000), None)
            # modify spouse hhid to newHH.hhid
            if ag2 != None:
                ag2.hhid       = nhhid      # !!! agent spouse hhid changed !!!
                ag2.relateHead = 2    # !!! agent spouse relateHead changed !!!
            else:
                print('WARNING! split hhid {}, NO spouse?\n'.format(self.hhid))
            # create new hh agent
            newHH = agents.Household(nhhid, ag.rgid, ag.villid) # [agents.py]
            # set up location (X, Y, Pnt) and elevation
            newHH.hhLocX = self.hhLocX + rand.uniform(-1, 1)
            newHH.hhLocY = self.hhLocY + rand.uniform(-1, 1)
            newHH.hhPnt  = Point(newHH.hhLocX, newHH.hhLocY)
            newHH.hhElev = self.hhElev
            # set up head information
            newHH.hdIfFemale  = ag.ifFemale
            newHH.hdAge       = ag.age
            newHH.hdEdu       = ag.edu
            newHH.hdIfMarried = ag.ifMarried
            # set up demographic composition
            newHH.hhSize      = 2
            newHH.hhNumCurOut = 0
            newHH.hhNumPreOut = 0
            if ag.ifOutMig == 1:
                newHH.hhNumCurOut = 2
                newHH.hhNumPreOut = 2
            # set up farm plots
            newHH.hhLandOwn   = 0.0
            newHH.hhLandPlant = 0.0
            l = [a for a in plList if a.hhid==self.hhid and a.code not in [99]]
            if len(l) > 1:
                fp = rand.choice(l)
                fp.hhid = newHH.hhid                # !!! plot hhID changed !!!
                newHH.hhLandOwn   = fp.area
                newHH.hhLandPlant = fp.area if fp.code in [60,61] else 0.0
            # customize pmf for ewfp area claimed by hh (low elevation)
            xk = np.arange(18)
            pk = (0.009493671, 0.199367089, 0.272151899, 0.234177215, 
                  0.094936709,0.063291139, 0.03164557, 0.03164557, 0.015822785, 
                  0.018987342, 0.006329114, 0.009493671, 0.006329114, 
                  0.003164557, 0, 0, 0, 0.003164557)
            custm_ewfp_low = stats.rv_discrete(name='custm', values=(xk, pk))
            # pmf of ewfp (high elevation)
            xk = np.arange(14)
            pk = (0.006060606, 0.315151515, 0.193939394, 0.157575758, 
                  0.096969697, 0.072727273, 0.042424242, 0.024242424, 
                  0.03030303, 0.03030303, 0.018181818, 0.006060606, 
                  0, 0.006060606)
            custm_ewfp_high = stats.rv_discrete(name='custm', values=(xk, pk))
            # set up CCFP and EWFP area
            newHH.areaCcfp = 0.0
            newHH.ifCcfp   = 0
            newHH.ifCcfpO  = self.ifCcfpO
            if newHH.hhElev < 700:
                rvs = custm_ewfp_low.rvs()
                newHH.areaEwfp = 10.0*[rvs-rand.random(),0][rvs==0]
            else:
                rvs = custm_ewfp_high.rvs()
                newHH.areaEwfp = 30.0*[rvs-rand.random(),0][rvs==0]
            newHH.areaEwfpO = newHH.areaEwfp
            # social norm, degree of being influenced by neighbors
            custm_sn = stats.truncnorm((0.0-mu)/sig,(0.9999-mu)/sig,loc=mu,scale=sig)
            newHH.sn = custm_sn.rvs()
            # append to l_new_hhs
            # print('hh split: {}\n'.format(newHH.hhid))
            # print('{}, {}\n'.format(newHH.ifCcfp, newHH.ifCcfpO))
            l_new.append(newHH)
        # return list of new hhs
        return l_new
    
    # to get a new head and update head information, if no existing head
    def update_head(self, inList):
        # inList=aglistINs
        # get household member list
        l_mem = [a for a in inList if a.hhid==self.hhid]
        # if no head exists, nominate a new head
        if len([a for a in l_mem if a.relateHead==1]) == 0:
            # set default to None
            theHead = None
            for mem in l_mem:
                if mem.relateHead == 2:
                    theHead = mem
                    break
            # if no spouse exists
            if theHead == None:
                l2 = [a for a in l_mem if a.age>=18 and a.age<=60]
                l3 = [a for a in l_mem if a.age<18 or a.age>60]
                # if adults exist, select the oldest
                if len(l2) >= 1:
                    max_age = max([a.age for a in l2])
                    for mem in l2:
                        if mem.age == max_age:
                            theHead = mem
                            break
                elif len(l3) >= 1:
                    max_age = max([a.age for a in l3])
                    for mem in l3:
                        if mem.age == max_age:
                            theHead = mem
                            break
            # nominate the member as the head
            theHead.relateHead = 1
            # update head information
            self.hdIfFemale  = theHead.ifFemale
            self.hdAge       = theHead.age
            self.hdEdu       = theHead.edu
            self.hdIfMarried = theHead.ifMarried
            
    
    # to update demographics
    def update_demographics(self, inList):
        # inList=aglistINs
        # get family member list
        l_fam = [a for a in inList if a.hhid==self.hhid]
        # update household size
        self.hhSize      = len([a for a in l_fam if a.ifOutMig ==0])
        # update number of current migrants
        self.hhNumCurOut = len([a for a in l_fam if a.ifOutMig ==1])
        # update number of previous migrants
        self.hhNumPreOut = len([a for a in l_fam if a.ifEverOut==1])
        
    # to update land
    def update_land(self, o, plList):
        # o=opt_ren, plList=aglistPLs
        # opt_ren's one element is [agPL.plid, agPL.area, hhidOu, hhidIn]
        # get all plots
        l_pl = [a for a in plList if a.hhid==self.hhid]
        # land owned
        self.hhLandOwn   = sum([a.area for a in l_pl if a.code in [60,61,69]])
        # land planted
        self.hhLandPlant = sum([a.area for a in l_pl if a.code in [60,61   ]])
        # get list of plID, hhidOut, hhidIn
        l_ren_area  = [a[1] for a in o]
        l_ren_hhidO = [a[2] for a in o]
        l_ren_hhidI = [a[3] for a in o]
        # check if any Rent-Out
        for index, item in enumerate(l_ren_hhidO):
            # if rent out hhid list has its hhid
            if item == self.hhid:
                # substract the plot's area
                self.hhLandPlant = self.hhLandPlant - l_ren_area[index]
        # check if any Rent-In
        for index, item in enumerate(l_ren_hhidI):
            # if rent in hhid list has its hhid
            if item == self.hhid:
                # add the plot's area
                self.hhLandPlant = self.hhLandPlant + l_ren_area[index]
        # update CCFP land
        self.areaCcfp = sum([a.area for a in l_pl if a.code in [99]])
        self.ifCcfp   = [0,1][self.areaCcfp>0]



### define class: Individual ###
class Individual():
    """ Agent Class: Individual """
    
    ## define attributes ##
    def __init__(self, pid, hhid, rgid, villid, relateHead, ifFemale, age, 
                 ifMarried, numChild):
        self.__pid      = int(pid)
        self.hhid       = int(hhid)
        self.__rgid     = int(rgid)
        self.__villid   = int(villid)
        self.relateHead = int(relateHead)
        self.ifFemale   = int(ifFemale)
        self.age        = int(age)
        self.ifMarried  = int(ifMarried)
        self.numChild   = int(numChild)
        
        ## initialize 5 more attributes:
            # ifOutMig, ifRetMig, ifEverOut, work, edu
        
        # initialize if an out-migrant
        if self.age <= 15 or self.age > 65:
            self.ifOutMig = 0
        else:
            self.ifOutMig = [0,1][rand.random()<0.3749] # 547/1459
        
        # initialize if a return-migrant
        if self.age <= 15:
            self.ifRetMig = 0
        else:
            if self.ifOutMig == 0:
                self.ifRetMig = [0,1][rand.random()<0.1324] # 180/1359
            else:
                self.ifRetMig = [0,1][rand.random()<0.2841] # 77/271
        
        # initialize if an ever out-migrant
        self.ifEverOut = [0,1][self.ifOutMig==1 or self.ifRetMig==1]
        
        # initialize work: 1-farm, 3-nonfarm, 5-student, 6-NotWork
         # customize education year for people aged 23-65
        xk = np.arange(7)
        pk = (0, 0.599051008, 0, 0.259786477, 0, 0, 0.141162515)
        custm_works = stats.rv_discrete(name='custm', values=(xk, pk))
        # start to initialize work
        if self.age <= 6:
            self.work = 6
        elif self.age <= 15:
            self.work = 5
        elif self.age <= 22:
            if self.ifOutMig == 1:
                self.work = [3,5][rand.random()<0.3678] # 32/87
            else:
                self.work = [3,5][rand.random()<0.5753] # 42/73
        elif self.age <= 65:
            if self.ifOutMig == 1:
                self.work = 3
            else:
                self.work = custm_works.rvs() # customized pmf
        else:
            self.work = 6
    
        # initialize education
         # customize education year for non-student people aged 6-22
        xk = np.arange(7)
        pk = (0.119047619, 0.178571429, 0.392857143, 0.154761905, 0.023809524, 
              0.083333333, 0.047619048)
        custm_edu0 = stats.rv_discrete(name='custm', values=(xk, pk))        
         # customize education year for people aged 23-35
        xk = np.arange(17)
        pk = (0.014450867, 0.002890173, 0.00867052, 0.014450867, 0.011560694, 
		      0.057803468, 0.026011561, 0.034682081, 0.335260116, 0.028901734, 
			  0.037572254, 0.176300578, 0.10982659, 0.014450867, 0.014450867, 
			  0.092485549, 0.020231214)
        custm_edu1 = stats.rv_discrete(name='custm', values=(xk, pk))
         # customize education year for people aged 36-45
        xk = np.arange(17)
        pk = (0.057401813, 0.003021148, 0.048338369, 0.036253776, 0.060422961, 
		      0.229607251, 0.060422961, 0.072507553, 0.359516616, 0.009063444, 
			  0.009063444, 0.036253776, 0.006042296, 0, 0.003021148, 0.006042296, 
			  0.003021148)
        custm_edu2 = stats.rv_discrete(name='custm', values=(xk, pk))
         # customize education year for people aged 46-55
        xk = np.arange(16)
        pk = (0.118589744, 0.022435897, 0.048076923, 0.070512821, 0.064102564, 
		      0.21474359, 0.03525641, 0.048076923, 0.298076923, 0, 0.022435897, 
			  0.038461538, 0, 0, 0.016025641, 0.003205128)
        custm_edu3 = stats.rv_discrete(name='custm', values=(xk, pk))
         # customize education year for people aged 56-65
        xk = np.arange(14)
        pk = (0.316981132, 0.026415094, 0.101886792, 0.098113208, 0.067924528, 
		      0.135849057, 0.045283019, 0.01509434, 0.124528302, 0.011320755, 
			  0.00754717, 0.030188679, 0.01509434, 0.003773585)
        custm_edu4 = stats.rv_discrete(name='custm', values=(xk, pk))
         # customize education year: for people aged >65
        xk = np.arange(13)
        pk = (0.512437811, 0.034825871, 0.059701493, 0.07960199, 0.049751244, 
		      0.104477612, 0.07960199, 0.014925373, 0.044776119, 0, 0.014925373, 
			  0, 0.004975124)
        custm_edu9 = stats.rv_discrete(name='custm', values=(xk, pk))
        # start to initialize education
        if self.age <= 6:
            self.edu = 0
        elif self.age <= 22:
            if self.work == 5:
                self.edu = int(self.age-6)
            else:
                self.edu = custm_edu0.rvs() + 9 # customized pmf (age 6-22)
        elif self.age <= 35:
            self.edu = custm_edu1.rvs() # customized pmf (age 23-35)
        elif self.age <= 45:
            self.edu = custm_edu2.rvs() # customized pmf (age 36-45)
        elif self.age <= 55:
            self.edu = custm_edu3.rvs() # customized pmf (age 46-55)
        elif self.age <= 65:
            self.edu = custm_edu4.rvs() # customized pmf (age 56-65)
        else:
            self.edu = custm_edu9.rvs() # customized pmf (age >65)
    
    # make ids private, except hhid due to household split      
    @property
    def pid(self):
        return self.__pid
    @property
    def rgid(self):
        return self.__rgid
    @property
    def villid(self):
        return self.__villid
    
    ## define methods ##
    
    # print out personal attributes
    def write_self(self):
        lr1 = [self.pid, self.hhid, self.rgid, self.villid]
        lr2 = [self.relateHead, self.ifFemale, self.age]
        lr3 = [self.ifMarried, self.numChild]
        lr4 = [self.ifOutMig, self.ifRetMig, self.ifEverOut]
        lr5 = [self.work, self.edu, self.ifCcfp, self.ifCcfpO]
        return lr1 + lr2 + lr3 + lr4 + lr5
    
    # to update age
    def update_age(self):
        self.age += 1
        
    # to die
    def die(self):        
        # age-specific death rate (Anhui, Rural, male, female)
        agesM = [None,0.0003590308,0.0004320849,0.0007452565,0.0011585146,
                 0.0013078976,0.0017026676,0.0021850419,0.0029720823,
                 0.0036585493,0.0066489194,0.0083712094,0.0134331415,
                 0.0223279436,0.0408888688,0.0649397791,0.1104633438,
                 0.1487513729,0.2142640134,0.2253344482]
        agesF = [None,0.0002227685,0.0002321814,0.0003570154,0.0004428864,
                 0.0005044343,0.0007868403,0.0010084619,0.0014188907,
                 0.0018402321,0.0035780269,0.0046505188,0.0073269549,
                 0.0130117882,0.0261202665,0.043541005,0.0805830058,
                 0.1135917605,0.1654193327,0.1969557801]
        # age bins: 0, 1-4, 5-9, 10-14, ..., 95-99, 100+
        if self.age == 0:
            probDie = [0.0050977469,0.0052104443][self.ifFemale==1]
        elif self.age <= 4:
            probDie = [0.0006766144,0.0004521422][self.ifFemale==1]
        elif self.age <= 99:
            ageIndex = int(self.age/5)
            probDie = [agesM[ageIndex],agesF[ageIndex]][self.ifFemale==1]
        else:
            probDie = [0.4008438819,0.2771285476][self.ifFemale==1]
        # return True or False
        return [False,True][rand.random()<probDie]
    
    # to update education (for student)
    def update_edu(self):
        # set default as not graduate
        ifGraduate = False
        # probabilities of graduation by education year
        pList = [0.01186, 0.01779, 0.03915, 0.01542, 0.00237, 0.00830, 0.00475]
        # only for students
        if self.work == 5:
            # if exceeds 16 yrs, must graduate
            if self.edu >=16:
                ifGraduate = True
            # if below 16 yrs, test if graduate
            else:
                # education +1
                self.edu += 1
                # if education years between 9 and 15
                if 9 <= self.edu <= 15:
                    ifGraduate = [False,True][rand.random()<pList[self.edu-9]]
        # return if to graduate
        return ifGraduate
    
    # to update work
    def update_work(self, l1, l2, g):
        # l1=upd_mig, l2=upd_ret, g=ifGraduate
        # if age 65+, change to not work
        if self.age > 65:
            self.work = 6
        # if graduated, find a job
        elif g:
            # if (migrant) OR (to migrate), change to off-farm work
            if self.ifOutMig == 1 or self.pid in l1:
                self.work = 3
            # if (non-migrant) AND (not to migrate), sample distribution
            else:
                aRand = rand.random()
                if aRand < 0.5991:
                    self.work = 1
                elif aRand < 0.8588:
                    self.work = 3
                else:
                    self.work = 6
        # if (not graduate) AND (not student) AND (age below 65)
        elif self.work != 5:
            # if change a job
            if rand.random() < 0.05:
                l = [1,3,6]
                l.remove(self.work)
                self.work = rand.choice(l)
                
    # to give birth a baby (for female)
    def give_birth(self, l_new):
        # l_new=l_new_babys
        # check if qualified
        ifQualified = True
        if   self.ifMarried == 0:                   # single,    NOT qualified
            ifQualified = False
        elif self.ifFemale == 0:                    # male,      NOT qualified
            ifQualified = False
        elif self.age < 20 or self.age > 49:        # young/old, NOT qualified
            ifQualified = False
        elif self.numChild >= 2:                    # 2 kids,    NOT qualified
            ifQualified = False
        # if qualified, decide whether to give birth
        if ifQualified:
            # set default as NOT to give birth
            ifGiveBirth = False
            # age-specific give birth to 1st and 2nd baby (China, Rural)
            birth1 = [None,None,None,0.00872,0.08026,0.04654,0.01162,0.00381, 
                      0.00192,0.00133]
            birth2 = [None,None,None,0.00062,0.0148,0.04173,0.03225,0.01196, 
                      0.00386,0.00208]
            # age bins: 15-19, 20-24, ..., 45-49
            ageIndex = int(self.age/5)
            if   self.numChild == 0:
                probGiveBirth = birth1[ageIndex]
            elif self.numChild == 1:
                probGiveBirth = birth2[ageIndex]
            else:        # End of 'if' either 0 or 1 baby already
                probGiveBirth = 0
            # make the decision
            ifGiveBirth = [False,True][rand.random()<probGiveBirth]
            # if to give birth
            if ifGiveBirth:
                # update number of children
                self.numChild += 1
                # add baby to agindividual list
                ag_baby = afunc.agent_baby_born(self)           #[afunc.py-U1]
                # append new agent to list of new
                l_new.append(ag_baby)
        # return the list of new individual agents
        return l_new
                
    # to marry (first marriage)
    def marry(self, inList, l_new):
        # inList=aglistINs, l_new=l_new_marrys
        # set default of gone & NOT split household
        ifGone  = False
        ifSplit = False
        # check if qualified to marry
        ifQualified = True
        if   self.ifMarried == 1:               # married, NOT qualified
            ifQualified = False
        elif self.age < 20 or self.age > 64:    # young/old, NOT qualified
            ifQualified = False
        # ifQualified, decide whether to marry (1st marriage)
        if ifQualified:
            # set deafult of probability of marry as 0 (1st marriage)
            probMarry = 0
            # age-specific 1st marry rate (China, Rural, male, female)
            agesM = [None,None,None,0.0085196133,0.011754881,0.0143142846,
                     0.0168828524,0.0232527121,0.0231216419,0.0210653134]
            agesF = [None,None,None,0.0093540583,0.0140434102,0.0167937911,
                     0.0200345754,0.0261572826,0.0229037726,0.0242424242]
            # age bins: <15, 15-19, ..., 45-49, 50+
            if self.age < 15:
                probMarry = [0.0009753502,0.0029112592][self.ifFemale==1]
            elif self.age < 50:
                ageIndex  = int(self.age/5)
                probMarry = [agesM[ageIndex],agesF[ageIndex]][self.ifFemale==1]
            else:
                probMarry = [0.0009753502,0.0029112592][self.ifFemale==1]
            # if to marry (1st marriage)
            if rand.random() < probMarry:
                # decide if gone or stay
                ifGone = [False,True][rand.random()<0.5]
                # if not gone, decide if to split
                if ifGone == False:                 # stay
                    # update marital status
                    self.ifMarried = 1         # !!!person ifMarried changed!!!
                    # add a new agent married in
                    ag_new  = afunc.agent_marry_in(self)
                    # if qualified to split the household
                    ifSplit = afunc.if_new_house(self, inList)
                    # append new agent to list of new
                    l_new.append(ag_new)
        # return to list ifGoneSplit
        return [ifGone, ifSplit, l_new]















