import pandas as pd
import numpy as np
import scipy.stats as stats, math

def split_dataframe(df):
    df1 = df.between_time('06:00:01', '11:00:00')
    df2 = df.between_time('11:00:01', '15:00:00')
    df3 = df.between_time('15:00:01', '19:00:00')
    df4 = df.between_time('19:00:01', '23:00:00')
    df5 = df.between_time('23:00:01', '06:00:00')

    capacity = []
    df1_cap_mean = df1.Capacity.mean()
    df2_cap_mean = df2.Capacity.mean()
    df3_cap_mean = df3.Capacity.mean()
    df4_cap_mean = df4.Capacity.mean()
    df5_cap_mean = df5.Capacity.mean()
    capacity = [df1_cap_mean,df2_cap_mean,df3_cap_mean,df4_cap_mean,df5_cap_mean]

    mean = []
    df1_mean = df1.PASSENGER.mean()
    df2_mean = df2.PASSENGER.mean()
    df3_mean = df3.PASSENGER.mean()
    df4_mean = df4.PASSENGER.mean()
    df5_mean = df5.PASSENGER.mean()
    mean = [df1_mean,df2_mean,df3_mean,df4_mean,df5_mean]

    std = []
    df1_std = df1.PASSENGER.std()
    df2_std = df2.PASSENGER.std()
    df3_std = df3.PASSENGER.std()
    df4_std = df4.PASSENGER.std()
    df5_std = df5.PASSENGER.std()
    std = [df1_std,df2_std,df3_std,df4_std,df5_std]

    k = []
    k1 = df1_std/df1_mean
    k2 = df2_std/df2_mean
    k3 = df3_std/df3_mean
    k4 = df4_std/df4_mean
    k5 = df5_std/df5_mean 
    k = [k1,k2,k3,k4,k5]

    list_demand = []
    list_demand_factor = []
    list_load_factor = []
    list_spill_factor = []
    list_spill = []
    percent_spill = []
    spill_df = []

    time = 0
    for i in range(5):
        demand_list = []
        demand_factor_list = []
        load_factor_list = []
        spill_factor_list = []
        spill_list = []
        spill_percent = []

        if (pd.isna(mean[i]) or pd.isna(std[i]) == True):
            continue
        k_factor =  k[i]

        #n = 0
        for j in np.arange(mean[i]-math.ceil(std[i]), mean[i]+200,1):
            demand_list.append(j)
            demand_factor = j/capacity[i]
            demand_factor_list.append(demand_factor)

            kd_group = ((1/(k_factor * demand_factor)) - (1/k_factor))
            cdf = 0.5*(1+math.erf(kd_group/math.sqrt(2)))
            norm = 1/(math.sqrt(2*math.pi)) * math.exp(-(kd_group*kd_group)/2)

            load_factor = ((demand_factor - 1) * (cdf)) - (k_factor*demand_factor*norm) + 1
            load_factor_list.append(load_factor*100)

            spill_factor = demand_factor - load_factor
            spill_factor_list.append(spill_factor)

            spill = capacity[i] * spill_factor
            spill_list.append(spill)

            spill_percent.append((spill/j)*100)
            #demand_factor_list.append(spill_calculate(i, k1, df1_cap_mean)[0]) 
            #load_factor_list.append(spill_calculate(i, k1, df1_cap_mean)[1])
            #spill_factor_list.append(spill_calculate(i, k1, df1_cap_mean)[2])
            #spill_list.append(spill_calculate(i, k1, df1_cap_mean)[3])
            #spill_percent.append((spill_list[n]/demand_list[n])*100)
            #n = n + 1
        
        list_demand.append(demand_list)
        list_demand_factor.append(demand_factor_list)
        list_load_factor.append(load_factor_list)
        list_spill_factor.append(spill_factor_list)
        list_spill.append(spill_list)
        percent_spill.append(spill_percent)

        data = {'Demand': list_demand, 
        'Demand_Factor(D)': list_demand_factor, 
        'Load_Factor(L)': list_load_factor, 
        'Spill_Factor(S)': list_spill_factor, 
        'Spill': list_spill, 
        'Spill as % of demand': percent_spill}
        spill_dataframe = pd.DataFrame(data=data)

        spill_df.append(spill_dataframe)
        time += 1
    return k, spill_df, time

def resample_df(df):
    resam = df.resample('15Min')['PASSENGER'].sum().dropna()
    resam_cap = df.resample('15Min')['Capacity'].sum().dropna()
    dff = resam.to_frame(name = 'Passenger')
    dfc = resam_cap.to_frame(name = 'Capacity')
    dft = dff.join(dfc)
    dft['Capacity'] = dft['Capacity'].fillna(0)

    return dft

