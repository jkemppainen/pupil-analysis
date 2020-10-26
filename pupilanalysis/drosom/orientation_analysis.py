'''
Rhabdomere orientation
'''
import os
import json

import matplotlib.pyplot as plt

from roimarker import Marker

from pupilanalysis.drosom.analysing import MAnalyser
from pupilanalysis.directories import PROCESSING_TEMPDIR


class OAnalyser(MAnalyser):
    '''
    Rhabdomere orientation analyser.

    Inherits from MAnalyser though most of it's methods
    have no meaning.
    
    Measure movement opens Marker to draw lines/arrows

    '''

    def __init__(self, *args, **kwargs):

        self.orientation_savefn = os.path.join(PROCESSING_TEMPDIR, 'MAnalyser_data', args[1], 'orientation_{}_{}.json'.format(args[1], '{}'))
        os.makedirs(os.path.dirname(self.orientation_savefn), exist_ok=True)

        print("Orientation saved in file {}".format(self.orientation_savefn))

        super().__init__(*args, **kwargs)
    


    def measure_movement(self, eye):
        '''
        The measure movement method overridden to meausure the (rhabdomere)
        orientation.

        In the end calls self.load_analysed_movements in order to
        match the MAnalyser behaviour.
        '''
        
        self.movements = {}

        images = []
        rois = []
            
        for angle in self.stacks:
            
            roi = self.ROIs[eye].get(angle, None)            
            
            if roi is not None:
                images.append(self.stacks[angle][0][0])

                widen = 10
                rois.append([roi[0]-widen, roi[1]-widen, roi[2]+2*widen, roi[3]+2*widen])


        fig, ax = plt.subplots()
        marker = Marker(fig, ax, images, self.orientation_savefn.format(eye),
                crops=rois,
                relative_fns_from=os.path.join(self.data_path, self.folder),
                selection_type='arrow',
                callback_on_exit=print)

        marker.run()



    def load_analysed_movements(self):
        '''
        Loads the analysed rhabdomere orientations, drawn with roimarker's
        arrow selection type.
        '''

        self.movements = {}

        for eye in ['left', 'right']:
            
            self.movements[eye] = {}

            with open(self.orientation_savefn.format(eye), 'r') as fp:
                marker_data = json.load(fp)
            
            for angle in self.stacks:
                
                relfn = os.path.relpath(self.stacks[angle][0][0], start=os.path.join(self.data_path, self.folder))
                roi = marker_data.get(relfn, None )
                
                if roi == None:
                    continue
                
                try:
                    self.movements[eye][angle]
                except KeyError:
                    self.movements[eye][angle] = []
                
                # Should be only one arrow per eye
                roi = roi[0]

                x = [roi[2], roi[0]]
                y = [roi[3], roi[1]]

                self.movements[eye][angle].append({'x': x, 'y': y})

    
    def is_measured(self):
        return all([os.path.exists(self.orientation_savefn.format(eye)) for eye in ['left', 'right']])


