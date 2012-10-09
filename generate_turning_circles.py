#!/usr/bin/python

import subprocess

# Fill is 2.5 times the width of the corresponding road fills.
metrics = { 'tertiary': { 15: { 'fill':  8.75, 'border': 1.0 },
                          16: { 'fill': 20.00, 'border': 1.0 } },
            'minor': { 15: { 'fill':  5.0, 'border': 1.0 },
                       16: { 'fill': 12.5, 'border': 1.0 } },
            'service': { 15: { 'fill': 3.25, 'border': 0.6 },
                         16: { 'fill': 5.00, 'border': 1.0 } } }
colors = { 'border': 'black', 'fill': 'white' }

def save_circle(diameter, color, file_name):
    img_size = int(diameter + 4)  # Two pixels on either side of the circle.
    circle_center = img_size / 2.0
    circle_edge = (img_size - diameter) / 2
    file_path = 'custom-symbols/' + file_name
    subprocess.call(['convert',
                     '-size', '{0}x{0}'.format(img_size), 'xc:none',
                     '-fill', color,
                     '-draw', 'circle {0},{0} {0},{1}'.format(circle_center, circle_edge),
                     file_path])

for classification, zooms in metrics.items():
    for zoom, dimensions in zooms.items():
        save_circle(dimensions['fill'], colors['fill'], 
                    'turning_circle-{0}-z{1}-fill.png'.format(classification, zoom))
        save_circle(dimensions['fill'] + dimensions['border'] * 2, colors['border'], 
                    'turning_circle-{0}-z{1}-casing.png'.format(classification, zoom))
