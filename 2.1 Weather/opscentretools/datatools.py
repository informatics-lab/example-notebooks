import jade_utils.iris_tools as iris_tools
import sys
# Suppress warnings
if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

def estimate_cube_size(cube):
    # Return the estimated size of a cube without realising its data
    return iris_tools.estimate_cube_size(cube)
