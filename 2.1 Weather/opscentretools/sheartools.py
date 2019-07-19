import intake
import iris
import datetime
import matplotlib.pyplot as plt
import iris.quickplot as qplt
import holoviews as hv
import geoviews as gv
import cartopy.crs as ccrs
import cartopy.feature as cf
import numpy as np
import sys
# Suppress warnings
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")
    

def vertical_boundary_levels(cube, vertical='pressure'):
    # Calculate the level values between each pair of levels
    if vertical=='pressure':
        return boundary_pressure_levels(cube)
    elif vertical=='height':
        return boundary_height_levels(cube)
    else:
        raise Exception('Vertical boundary layers cannot be calculated for "{}"'.format(vertical))


def boundary_pressure_levels(cube):
    upper = cube.extract(
                iris.Constraint(
                    pressure=lambda p:p < cube.coord('pressure').points[0]))
    lower = cube.extract(
                iris.Constraint(
                    pressure=lambda p:p > cube.coord('pressure').points[-1]))
    
    new_levels = (upper.coord('pressure').points +  lower.coord('pressure').points )/2
    for cube in [upper, lower]:
        cube.coord('pressure').points = new_levels
        cube.coord('pressure').bounds = None
    return upper, lower


def boundary_height_levels(cube):
    upper = cube.extract(
                iris.Constraint(
                    height=lambda h:h > cube.coord('height').points[0]))
    lower = cube.extract(
                iris.Constraint(
                    height=lambda h:h < cube.coord('height').points[-1]))
    
    new_levels = (upper.coord('height').points +  lower.coord('height').points )/2
    for cube in [upper, lower]:
        cube.coord('height').points = new_levels
        cube.coord('height').bounds = None
    return upper, lower


def calculate_shear(wind_speed, wind_dir):
    # Calculate shear of cubes after asserting whether they have vertical 
    
    # determine whether vertical dims are pressure or height
    dir_dims = [dim.var_name for dim in wind_dir.dim_coords]
    speed_dims = [dim.var_name for dim in wind_speed.dim_coords]
    
    # calculate shear if either pressure or height are present in the supplied cubes
    if 'pressure' in (dir_dims and speed_dims):
        return vertical_shear_calculation(wind_speed, wind_dir, vertical='pressure')
    elif 'height' in (dir_dims and speed_dims):
        return vertical_shear_calculation(wind_speed, wind_dir, vertical='height')
    else:
        raise Exception('Cubes do not contain either "pressure" or "height" dim_coords')
    
    
def vertical_shear_calculation(wind_speed, wind_dir, vertical='pressure'):
    # Calculate the cross-product of wind vectors between consecutive pressure or height levels
    # lets ensure we are working on the same coords on both cubes
    assert wind_speed.coord_dims(vertical) == wind_dir.coord_dims(vertical)
    
    # make copies of cubes
    speed = wind_speed.copy()
    direction = wind_dir.copy()
    
    # work out the parameters for the 
    speed_lower, speed_upper = vertical_boundary_levels(speed, vertical)
    dir_lower, dir_upper = vertical_boundary_levels(direction, vertical)
    
    x_lower = speed_lower * iris.analysis.maths.apply_ufunc(np.cos, dir_lower)
    y_lower = speed_lower * iris.analysis.maths.apply_ufunc(np.sin, dir_lower)
    x_upper = speed_upper * iris.analysis.maths.apply_ufunc(np.cos, dir_upper)
    y_upper = speed_upper * iris.analysis.maths.apply_ufunc(np.sin, dir_upper)

    x_diff = x_upper - x_lower
    y_diff = y_upper - y_lower
    shear = (x_diff**2 + y_diff**2)**0.5
    
    # rename cube and add units
    shear.long_name = "Wind Shear"
    shear.units = "m s-1"
    
    return shear


def calculate_ensemble_exceedence(wind_shear, threshold=15):
    # Calculate the proportion of ensemble members which have shear values exceeding the threshold
    
    # make a copy of the cube
    shear = wind_shear.copy()
    
    # collapse the cube along the 'realization' dimension according to proportional analysis
    exceedance = shear.collapsed('realization', iris.analysis.PROPORTION,
                                       function=lambda values: values > threshold)
    
    # rename cube and remove units
    exceedance.long_name = "Wind Shear > {}".format(threshold)
    exceedance.units = "1"
    
    return exceedance


def estimate_cube_size(cube):
    # Return the estimated size of a cube without realising its data
    return iris_tools.estimate_cube_size(cube)
