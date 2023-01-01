from __future__ import division 
from CoolProp.CoolProp import PropsSI 

class Compressor():
    """
    Compressor Model based on 10-coefficient Model from `ANSI/AHRI standard 540
    
    Required Parameters:
        
    ===========   ==========  ===================================================
    Variable      Units       Description
    ===========   ==========  ===================================================
    M             Ibm/hr      Compressor map coefficients for mass flow
    P             Watts       Compressor map coefficients for electrical power
    Ref           R410A       A string representing the refrigerant
    T_evap        K           Evaporation temperature of the refrigerant
    T_cond        K           Condenstaion temperature of the refrigerant
    P1            Pa          Refrigerant suction pressure (absolute)
    P2            Pa          Refrigerant discharge pressure (absolute)
    fp            --          Fraction of electrical power lost as heat to ambient
    Vdot_ratio    --          Displacement Scale factor
    ===========   ==========  ===================================================
    
        
    """
    def __init__(self,**kwargs):
        #Load up the parameters passed in
        # using the dictionary
        self.__dict__.update(kwargs)
    def Update(self,**kwargs):
        #Update the parameters passed in
        # using the dictionary
        self.__dict__.update(kwargs)
        
    def OutputList(self):
        """
            Return a list of parameters for this component for further output
            
            It is a list of tuples, and each tuple is formed of items with indices:
                [0] Description of value
                
                [1] Units of value
                
                [2] The value itself
        """
        
        return [
            ('M1','-',self.M[0]),
            ('M2','-',self.M[1]),
            ('M3','-',self.M[2]),
            ('M4','-',self.M[3]),
            ('M5','-',self.M[4]),
            ('M6','-',self.M[5]),
            ('M7','-',self.M[6]),
            ('M8','-',self.M[7]),
            ('M9','-',self.M[8]),
            ('M10','-',self.M[9]),
            ('P1','-',self.P[0]),
            ('P2','-',self.P[1]),
            ('P3','-',self.P[2]),
            ('P4','-',self.P[3]),
            ('P5','-',self.P[4]),
            ('P6','-',self.P[5]),
            ('P7','-',self.P[6]),
            ('P8','-',self.P[7]),
            ('P9','-',self.P[8]),
            ('P10','-',self.P[9]),
            ('Heat Loss Fraction','-',self.fp),
            ('Displacement scale factor','-',self.Vdot_ratio),
            ('Power','W',self.W),
            ('Mass flow rate','kg/s',self.mdot_r_r),
            ('Inlet Temperature','K',self.Tin_r),
            ('Outlet Temperature','K',self.Tout_r),
            ('Inlet Enthalpy','J/kg',self.hin_r),
            ('Outlet Enthalpy','J/kg',self.hout_r),
            ('Overall isentropic efficiency','-',self.eta_oi),
            ('Pumped flow rate','m^3/s',self.Vdot_pumped),
            ('Ambient heat loss','W',self.Q_amb),
         ]
        
    def compressor_calculation(self, T_evap, T_cond, DT_sh_K):
        #Local copies of coefficients
        P = self.P
        M = self.M
        
        #Calculate suction superheat and dew temperatures
        # self.T_evap = PropsSI('T','P',self.pin_r,'Q',1.0,self.Ref)
        # self.T_cond = PropsSI('T','P',self.pout_r,'Q',1.0,self.Ref)
        # self.DT_sh_K = self.Tin_r-self.T_evap
        
        #Convert saturation temperatures in K to F
        Tsat_s = T_evap * 9/5 - 459.67
        Tsat_d = T_cond * 9/5 - 459.67
    
        #Apply the 10 coefficient ARI map to saturation temps in F
        power_map = P[0] + P[1] * Tsat_s + P[2] * Tsat_d + P[3] * Tsat_s**2 + P[4] * Tsat_s * Tsat_d + P[5] * Tsat_d**2 + P[6] * Tsat_s**3 + P[7] * Tsat_d * Tsat_s**2 + P[8] * Tsat_d**2*Tsat_s + P[9] * Tsat_d**3
        mdot_r_map = M[0] + M[1] * Tsat_s + M[2] * Tsat_d + M[3] * Tsat_s**2 + M[4] * Tsat_s * Tsat_d + M[5] * Tsat_d**2 + M[6] * Tsat_s**3 + M[7] * Tsat_d * Tsat_s**2 + M[8] * Tsat_d**2*Tsat_s + M[9] * Tsat_d**3
    
        # Convert mass flow rate to kg/s from lbm/h
        mdot_r_map *= 0.000125998 
    
        # Add more mass flow rate to scale
        mdot_r_map*=self.Vdot_ratio
        power_map*=self.Vdot_ratio
        
        Pe = PropsSI('P','T',T_evap,'Q',1.0, self.Ref)
        Pc = PropsSI('P','T',T_cond,'Q',1.0, self.Ref)
        
        T1_actual = T_evap + DT_sh_K
    
        v_map = 1 / PropsSI('D', 'T', T_evap + 20.0/9.0*5.0, 'P', Pe, self.Ref)
        v_actual = 1 / PropsSI('D', 'T', T_evap + DT_sh_K, 'P', Pe, self.Ref)
        F = 0.75
        mdot_r = (1 + F * (v_map / v_actual - 1)) * mdot_r_map
    
        T1_map = T_evap + 20 * 5 / 9
        s1_map = PropsSI('S', 'T', T1_map, 'P', Pe, self.Ref)
        h1_map = PropsSI('H', 'T', T1_map, 'P', Pe, self.Ref)
        h2s_map = PropsSI('H','P',Pc,'S',s1_map,self.Ref)
        #h2s_map = h_sp(self.Ref, s1_map, P2, T1_map + 20) #+20 for guess value
    
        s1_actual = PropsSI('S', 'T', T1_actual, 'P', Pe, self.Ref)
        h1_actual = PropsSI('H', 'T', T1_actual, 'P', Pe, self.Ref)
        h2s_actual = PropsSI('H','P',Pc,'S',s1_actual,self.Ref)
        #h2s_actual = h_sp(self.Ref, s1_actual, P2, T1_actual + 20) #+20 for guess value
    
        #Shaft power based on 20F superheat calculation from fit overall isentropic efficiency
        power = power_map * (mdot_r / mdot_r_map) * (h2s_actual - h1_actual) / (h2s_map - h1_map)
    
        h2 = power * (1 - self.fp) / mdot_r + h1_actual #/1000
        self.eta_oi = mdot_r*(h2s_actual-h1_actual)/(power) #/1000
        self.Tout_r = PropsSI('T','H',h2,'P',Pc,self.Ref)
        #self.Tout_r = T_hp(self.Ref, h2, P2, T1_map + 20) #Plus 20 for guess value for discharge temp
        # self.sout_r = PropsSI('S','T',self.Tout_r,'P',P2,self.Ref) #* 1000
        # self.sin_r = PropsSI('S','T',self.Tin_r,'P',P1,self.Ref) #* 1000

        self.W = power
        self.CycleEnergyIn=power*(1-self.fp)
        # self.Vdot_pumped=mdot_r/PropsSI('D','T',self.Tin_r,'P',P1,self.Ref)
        Q_amb = -self.fp*power
        
        return mdot_r, power, h2, Pc, Q_amb 
    
if __name__=='__main__':        
    for i in range(1):
        kwds={
               'M':[286.0294022, 6.46433508,   0,  0.05532,   0,  0,  0.000193, 0,  0, - 5.87E-06],
               'P':[164.8544636, - 23.78595375, 40.8715546, - 0.51419805, 0.641107197, - 0.282310738, - 0.002174527, 0.00475791, - 0.002897174, 0.001476432],
               'Ref':'R410A',
               'fp':0.15, #Fraction of electrical power lost as heat to ambient
               'Vdot_ratio': 1.0 #Displacement Scale factor
              }

        Comp = Compressor(**kwds)
        T_evap = 20+273.15
        T_cond = 55+273.15
        DT_sh_K = 11.11
        mdot_r, power, h2, P2, Q_amb  = Comp.compressor_calculation(T_evap, T_cond, DT_sh_K)
        print("mdot_r",mdot_r, "W_dot", power, "houtr",h2, "P2", P2, "Q_amb", Q_amb) 
        # I deleted comment from here which was added from laptop. 



