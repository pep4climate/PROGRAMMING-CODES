import numpy as np
import pandas as pd

def capacity_brinch_hansen(sl, fd, lat_sl, gw, loads, rvr, sl_fd):
    """
    Function to calculate soil-foundation general bearing capacity according to Appendix D of EN7.
    arg sl: soil object
    arg fd: foundation object
    arg lat_sl: lateral soil object
    arg gw: groundwater object
    arg loads: pier loads object
    arg rvr: river object
    arg sl_fd: soil-foundation object
    """

    # Pier loads
    horizontal_load = loads.horizontal_load
    vertical_load = loads.vertical_load
    moment_longitudinal = loads.moment_longitudinal
    moment_transverse = loads.moment_transverse

    # A_prime
    if vertical_load!=0:
        e_width = moment_longitudinal/vertical_load
        e_length = moment_transverse/vertical_load
    else:
        e_width = 0
        e_length = 0

    B_prime = fd.width - 2 * e_width
    L_prime = fd.length - 2 * e_length

    shape = input("Input foundation shape: 'rectangular' or 'squared' or 'circular'")
    if shape == 'rectangular' or 'squared':
        A_prime = B_prime * L_prime
    elif shape == 'circular':
        A_prime = np.pi * np.power(B_prime, 2)/4

    # Capacity factors
    sl.N_q = np.exp(np.pi * np.tan(np.radians(sl.phi))) * np.power(np.tan(np.radians(45 + sl.phi/2)), 2)
    sl.N_gamma = 2 * (sl.N_q - 1) * np.tan(np.radians(sl.phi)) # for base friction angle at least equal to half friction angle
    if sl.phi != 0:
        sl.N_c = (sl.N_q - 1) * 1/(np.tan(np.radians(sl.phi)))
    elif sl.phi ==0:
        sl.N_c = 2 + np.pi

    # b coefficients
    b_q = np.power(1 - np.radians(sl.alpha) * np.tan(np.radians(sl.phi)), 2)
    if sl.phi == 0:
        b_c = 1 - 2 * np.radians(sl.alpha)/(sl.N_c)
    else:
        b_c = b_q - (1 - b_q)/(sl.N_c * np.tan(np.radians(sl.phi)))
    b_gamma = b_q

    # s coefficients
    if shape == 'rectangular':
        s_q = 1 + (B_prime/L_prime) * np.sin(np.radians(sl.phi))
        s_gamma = 1 - 0.3 * (B_prime/L_prime)
    elif shape == 'circular' or 'squared':
        s_q = 1 + np.sin(np.radians(sl.phi))
        s_gamma = 1 - 0.3

    if sl.phi == 0:
        if shape == 'rectangular':
            s_c = 1 + 0.2 * (B_prime/L_prime)
        elif shape == 'squared' or ' circular':
            s_c = 1 + 0.2
    else:
        s_c = (s_q * sl.N_q - 1)/(sl.N_q - 1)

    # i coefficients
    m_B = (2 + (B_prime/L_prime))/(1 + (B_prime/L_prime))
    m_L = (2 + (L_prime/B_prime))/(1 + (L_prime/B_prime))

    if horizontal_load != 0:
        horizontal_load_direction = input("Input one the following: 'B_prime direction' or 'L_prime direction' or 'Both B_prime and L_prime directions'")
        if horizontal_load_direction == 'B_prime direction':
            m = m_B
        elif horizontal_load_direction == 'L_prime direction':
            m = m_L
        elif horizontal_load_direction == 'Both B_prime and L_prime direction':
            teta = 0
            m = m_L * np.power(np.cos(np.radians(teta)),2) + m_B * np.power(np.sin(np.radians(teta)), 2)

        i_q = np.power(1 - horizontal_load/(vertical_load + A_prime * sl.cohesion * 1/np.tan(np.radians(sl.phi))), m)
        i_gamma = np.power(1 - horizontal_load/(vertical_load + A_prime * sl.cohesion * 1/np.tan(np.radians(sl.phi))), m+1)
    else:
        i_q = 1
        i_gamma = 1

    if sl.phi ==0:
        if horizontal_load <= A_prime * sl.cohesion:
            i_c = 1/2 * (1 + np.sqrt(1-(horizontal_load/(A_prime * sl.cohesion))))
        else:
            horizontal_load = A_prime * sl.cohesion
            i_c = 1/2 * (1 + np.sqrt(1-(horizontal_load/(A_prime * sl.cohesion))))
    else:
        i_c = i_q - (1 - i_q)/(sl.N_c * np.tan(np.radians(sl.phi)))

    # Lateral soil
    D = lat_sl.depth

    # d coefficients
    foundation_depth_effects = input('Would you like to consider foundation depth effects?')
    d_gamma = 1
    if foundation_depth_effects == 'yes':
        if D <= B_prime:
            k = D/B_prime
        else:
            k = 1/np.tan(D/B_prime)
        if sl.phi == 0:
            d_c = 0.4 * k
        else:
            d_c = 1.0 + 0.4 * k
        d_q = 1 + 2 * np.tan(np.radians(sl.phi)) * np.power((1 - np.sin(np.radians(sl.phi))),2) * k
    else:
        d_c = 1
        d_q = 1

    # g coefficients
    lateral_soil_slope_effects = input('Would you like to consider lateral soil slope effects?')
    if lateral_soil_slope_effects == 'yes':
        if sl.phi == 0:
            g_c = np.radians(lat_sl.beta)/(5.14/2)
        else:
            g_c = 1 - np.radians(lat_sl.beta)/(5.14/2) 
        g_q = np.power(1 - 1/2 * np.tan(np.radians(lat_sl.beta)), 2)
        g_gamma = g_q
    else:
        g_c = 1
        g_q = 1
        g_gamma = 1

    # Groundwater
    D_w = gw.depth 

    if D_w > D:
       lat_sl.unit_weight = sl.dry_unit_weight
    elif 0 < D_w <=D:
        lat_sl.unit_weight = (sl.dry_unit_weight * D_w) + (sl.sat_unit_weight - gw.unit_weight) * (D - D_w)/D_w
    elif D_w == 0:
        lat_sl.unit_weight = sl.sat_unit_weight - gw.unit_weight

    q = lat_sl.unit_weight * D # overburden pressure

    # River pressure
    h = rvr.mean_level
    q_river = gw.unit_weight * h

    # Foundation soil
    if D_w > (B_prime + D):
        sl.prime_unit_weight = sl.dry_unit_weight
    elif D < D_w <= (B_prime + D):
        sl.prime_unit_weight = (sl.dry_unit_weight * D_w) + (sl.sat_unit_weight - gw.unit_weight) * (D + B_prime - D_w)/(D_w)
    elif D_w <= D:
        sl.prime_unit_weight = sl.sat_unit_weight - gw.unit_weight

    # Capacity
    river_level_effects = input('Would you like to consider river level pressure effects?')
    q_ult_first_term = sl.cohesion * sl.N_c * b_c * s_c * i_c * d_c * g_c
    q_ult_second_term = q * sl.N_q * b_q * s_q * i_q * d_q * g_q
    q_ult_third_term = 1/2 * sl.prime_unit_weight * B_prime * sl.N_gamma * b_gamma * s_gamma * i_gamma * d_gamma * g_gamma
    if river_level_effects == 'yes':
        sl_fd.q_ult = (q_ult_first_term + q_ult_second_term + q_ult_third_term + q_river)
    else:
        sl_fd.q_ult = (q_ult_first_term + q_ult_second_term + q_ult_third_term)

    
    # Output printing
    print("The first term of general bearing capacity is ", round(q_ult_first_term, 2), " kPa.")
    print("The second term of general bearing capacity is ", round(q_ult_second_term, 2), " kPa.")
    print("The third term of general bearing capacity is ", round(q_ult_third_term, 2), " kPa.")
    print("The general bearing capacity is ", round(sl_fd.q_ult, 2), " kPa.")
    print("The general bearing capacity force is ", round(sl_fd.q_ult * A_prime, 2), " kN.", "\n")

    # Code verification
    print("Variables of the first therm of q_ult")
    print("c is ", round(sl.cohesion, 2), " kPa")
    print("N_c is ", round(sl.N_c, 2))
    print("b_c is ", round(b_c, 2))
    print("s_c is ", round(s_c, 2))
    print("i_c is ", round(i_c, 2))
    print("d_c is ", round(d_c, 2))
    print("g_c is ", round(g_c, 2), "\n")

    print("Variables of the second therm of q_ult")
    print("q is ", round(q, 2), " kPa")
    print("N_q is ", round(sl.N_q, 2))
    print("b_q is ", round(b_q, 2))
    print("s_q is ", round(s_q, 2))
    print("i_q is ", round(i_q, 2))
    print("d_q is ", round(d_q, 2))
    print("g_q is ", round(g_q, 2), "\n")

    print("Variables of the third therm of q_ult")
    print("Equivalent soil unit weight is ", sl.prime_unit_weight, f"kN/m\N{superscript three}")
    print("N_gamma is ", round(sl.N_gamma, 2))
    print("B_prime is ", round(B_prime, 2), ' m')
    print("b_gamma is ", round(b_gamma, 2))
    print("s_gamma is ", round(s_gamma, 2))
    print("i_gamma is ", round(i_gamma, 2))
    print("d_gamma is ", round(d_gamma, 2))
    print("g_gamma is ", round(g_gamma, 2))

    # Store input data and results
    storing_input_dictionary = {"B_prime": B_prime,
                          "shape": shape,
                          "D": D,
                          "friction angle": sl.phi,
                          "cohesion": sl.cohesion,
                          "dry unit weight": sl.dry_unit_weight,
                          "saturated unit weight": sl.sat_unit_weight,
                          "beta": lat_sl.beta,
                          "alpha": sl.alpha,
                          "groundwater level": D_w,
                          "horizontal load": horizontal_load,
                          "vertical load": vertical_load,
                          "moment transverse": moment_transverse,
                          "moment longitudinal": moment_longitudinal,
                          }
    
    storing_input_df = pd.DataFrame.from_dict([storing_input_dictionary])
    file_name_input_data = input("Input file name of input data.csv")
    storing_input_df.to_csv(file_name_input_data)

    storing_output_dictionary = {"c": sl.cohesion,
                                 "N_c": round(sl.N_c, 2),
                                 "b_c": round(b_c, 2),
                                 "s_c": round(s_c, 2),
                                 "i_c": round(i_c, 2),
                                 "d_c": round(d_c, 2),
                                 "g_c": round(g_c, 2),
                                 "q": round(q, 2),
                                 "N_q": round(sl.N_q, 2),
                                 "b_q": round(b_q, 2),
                                 "s_q": round(s_q, 2),
                                 "i_q": round(i_q, 2),
                                 "d_q": round(d_q, 2),
                                 "g_q": round(g_q, 2),
                                 "N_gamma": round(sl.N_gamma, 2),
                                 "B_prime": round(B_prime, 2),
                                 "b_gamma": round(b_gamma, 2),
                                 "s_gamma": round(s_gamma, 2),
                                 "i_gamma": round(i_gamma, 2),
                                 "d_gamma": round(d_gamma, 2),
                                 "g_gamma": round(g_gamma, 2)}
    
    storing_output_df = pd.DataFrame.from_dict([storing_output_dictionary])
    file_name_output_data = input("Input file name of output data.csv")
    storing_output_df.to_csv(file_name_output_data)
    
    #return sl_fd.q_ult