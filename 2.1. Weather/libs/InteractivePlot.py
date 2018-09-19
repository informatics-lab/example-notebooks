import matplotlib
import matplotlib.pyplot as plt


class Subplot(object):
    def __init__(self, fn, figsize=(6,4)):
        self.plotfn = fn
        self.fig = plt.figure(figsize=figsize)
    
    def plot(self, cube):
        plt.figure(self.fig.number)
        plt.clf()
        self.plotfn(cube)
    
    def clear(self, cube):
        plt.figure(self.fig.number)
        plt.clf()
        

class InteractivePlot(object):
    def __init__(self, cube, mapfn, initial_slice=(0, slice(None), slice(None)), 
                 figsize=(6,4), xcoord='longitude', ycoord='latitude', *args, **kwargs):
        self.cube = cube
        self.mapfn = mapfn
        self.map_slice = initial_slice
        self.figsize = figsize
        self.xcoord = xcoord
        self.ycoord = ycoord
        
        self.fig = plt.figure(figsize=self.figsize)
        
    def plot(self):
        plt.figure(self.fig.number)
        plt.clf()
        self.mapfn(self.cube[self.map_slice])
        
    def clear(self, cube):
        plt.figure(self.fig.number)
        plt.clf()
        
    def get_event_cube(self, event):
        current_slice = self._mk_inspect_cube(self._get_event_pts(event))
        return self.cube[current_slice]
        
    def add_event_listener(self, event, callback):
        def on_evt(event):
            self._refresh()
            callback(self, event)
        self.fig.canvas.mpl_connect(event, on_evt)
    
    def update_slice(self, new_slice):
        self.map_slice = new_slice
        self._refresh()
            
    def _get_event_pts(self, event):
        try:
            x = int(self.cube.coord(self.xcoord).nearest_neighbour_index(event.xdata))
        except CoordinateNotFoundError:
            x = None
        try:
            y = int(self.cube.coord(self.ycoord).nearest_neighbour_index(event.ydata))
        except CoordinateNotFoundError:
            y = None
        return [y, x]
        
    def _mk_inspect_cube(self, pts):
        s = [slice(None)] * len(self.cube.shape)
        picker_plot_dims = [i for i, v in
                            enumerate(self.map_slice)
                            if type(v) is slice]
        if pts[0]:
            s[picker_plot_dims[0]] = pts[0]
        if pts[1]:
            s[picker_plot_dims[1]] = pts[1]
        return tuple(s)
        
    def _refresh(self):
        plt.figure(self.fig.number)
        plt.clf()
        self.mapfn(self.cube[self.map_slice])
