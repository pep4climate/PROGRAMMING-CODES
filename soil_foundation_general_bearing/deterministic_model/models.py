class Groundwater():
    unit_weight = 9.81

class Soil():
    N_c = 0
    N_q = 0
    N_gamma = 0
    prime_unit_weight = 0

class Foundation():
    pass

class LateralSoil():
    pass

class River():
    pass

class Loads():
    pass

class Soil_Foundation():
    q_ult = 0.0

def create_groundwater(groundwater_depth):
    """
    Function to create a groundwater object.
    """
    a_groundwater = Groundwater()
    a_groundwater.depth = groundwater_depth # ground water level from mean riverbed level
    return a_groundwater

def create_lateral_soil(lateral_soil_depth, beta):
    """
    Function to create a lateral soil object.
    """
    a_lateral_soil = LateralSoil()
    a_lateral_soil.depth = lateral_soil_depth
    a_lateral_soil.beta = beta
    return a_lateral_soil

def create_foundation(longitudinal_width, transverse_width, foundation_depth):
    """
    Function to define a foundation object having longitudinal_width in the bridge longitudinal plane,
    and foundation_depth measured from mean riverbed level.
    """
    a_foundation = Foundation()
    a_foundation.width = longitudinal_width
    a_foundation.length = transverse_width
    a_foundation.depth = foundation_depth
    return a_foundation

def create_soil(friction_angle, cohesion, dry_unit_weight, saturated_unit_weight, alpha):
    """
    Function to define a soil object.
    """
    a_soil = Soil()
    a_soil.phi = friction_angle
    a_soil.cohesion = cohesion
    a_soil.dry_unit_weight = dry_unit_weight
    a_soil.sat_unit_weight = saturated_unit_weight
    a_soil.alpha = alpha
    return a_soil

def create_river(river_level):
    """
    Function to define a river object.
    """
    a_river = River()
    a_river.mean_level = river_level
    return a_river

def create_loads(horizontal_load, vertical_load, 
                 moment_bridge_transverse, moment_bridge_longitudinal):
    """
    Function to define pier loads object.
    """
    a_loads = Loads()
    a_loads.horizontal_load = horizontal_load
    a_loads.vertical_load = vertical_load
    a_loads.moment_transverse = moment_bridge_transverse
    a_loads.moment_longitudinal = moment_bridge_longitudinal
    return a_loads

def create_soil_foundation():
    """
    Function to define soil_foundation object.
    """
    a_soil_foundation = Soil_Foundation()
    return a_soil_foundation