import numpy as np

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

    #Capacity factors
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
    if sl.phi == 0:
        if shape == 'rectangular':
            s_c = 1 + 0.2 * (B_prime/L_prime)
        elif shape == 'squared' or ' circular':
            s_c = 1 + 0.2
    else:
        if shape == 'rectangular':
            s_q = 1 + (B_prime/L_prime) * np.sin(np.radians(sl.phi))
            s_gamma = 1 - 0.3 * (B_prime/L_prime)
        elif shape == 'circular' or 'squared':
            s_q = 1 + np.sin(np.radians(sl.phi))
            s_gamma = 1 - 0.3
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

    # d coefficients
    foundation_depth_effects = input('Would you like to consider foundation depth effects?')
    if foundation_depth_effects == 'yes':
        d_gamma = 1
        if D <= B_prime:
            k = D/B_prime
        else:
            k = 1/np.tan(D/B_prime)
        d_c = 1.0 + 0.4 * k
        d_q = 1 + 2 * np.tan(np.radians(sl.phi)) * np.power((1 - np.sin(np.radians(sl.phi))),2) * k
    else:
        d_gamma = 1
        d_c = 1
        d_q = 1

    # g coefficients
    lateral_soil_slope_effects = input('Would you like to consider lateral soil slope effects?')
    if lateral_soil_slope_effects == 'yes':
        if sl.phi == 0:
            g_c = np.radians(lat_sl.beta)/5.14
        else:
            g_c = i_q - (1 - i_q)/(5.14 * np.tan(np.radians(sl.phi)))
        g_q = np.power(1 - np.tan(np.radians(lat_sl.beta)), 2)
        g_gamma = g_q
    else:
        g_c = 1
        g_q = 1
        g_gamma = 1

    # Lateral soil
    D = lat_sl.depth
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
        sl.prime_unit_weight = (sl.sat_unit_weight - gw.unit_weight) + (D_w - D)/(B_prime) * gw.unit_weight
    elif D_w <= D:
        sl.prime_unit_weight = sl.sat_unit_weight - gw.unit_weight

    # Capacity
    river_level_effects = input('Would you like to consider river level pressure effects?')
    if river_level_effects == 'yes':
        sl_fd.q_ult = (sl.cohesion * sl.N_c * b_c * s_c * i_c * d_c * g_c +
                    q * sl.N_q * b_q * s_q * i_q * d_q * g_q +
                    1/2 * sl.prime_unit_weight * B_prime * sl.N_gamma * b_gamma * s_gamma * i_gamma * d_gamma * g_gamma +
                    q_river)
    else:
        sl_fd.q_ult = (sl.cohesion * sl.N_c * b_c * s_c * i_c * d_c * g_c +
                    q * sl.N_q * b_q * s_q * i_q * d_q * g_q +
                    1/2 * sl.prime_unit_weight * B_prime * sl.N_gamma * b_gamma * s_gamma * i_gamma * d_gamma * g_gamma)
    
    # Output printing
    print("The general bearing capacity is ", round(sl_fd.q_ult, 2), " kPa.")
    print("The general bearing capacity force is ", round(sl_fd.q_ult * A_prime, 2), " kN.")