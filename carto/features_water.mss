#waterlines {
    ::mainline {
        // rivers/canals
        [zoom >= 7][waterway = 'river'],
        [zoom >= 7][waterway = 'canal'][disused != 'yes'] {
            line-color: @waterlinecolor;
            line-join: round;
            line-cap: round;
            [zoom >= 7][zoom < 10] {
                line-width: 0.5;
            }
            [zoom >= 10][zoom < 14] {
                line-width: 0.8;
            }
            [zoom >= 14] {
                line-width: 5;
            }
        }
    
        // derelict canals
        [zoom >= 14][waterway = 'derelict_canal'],
        [zoom >= 14][waterway = 'canal'][disused = 'yes'] {
            line-color: @waterlinecolor;
            line-join: round;
            line-cap: round;
            [zoom >= 14][zoom < 15] {
                line-width: 2;
                line-dasharray: 15,5;
            }
            [zoom >= 15] {
                line-width: 2;
                line-dasharray: 30,10;
            }
        }

        // streams
        [zoom >= 10][waterway = 'stream'] {
            line-color: @waterlinecolor;
            line-join: round;
            line-cap: round;
            [zoom >= 10][zoom < 14] {
                line-width: 0.5;
            }
            [zoom >= 14] {
                line-width: 1.5;
            }
        }

        // minor waterways
        [zoom >= 14][waterway = 'drain'],
        [zoom >= 14][waterway = 'ditch'],
        [zoom >= 14][waterway = 'brook'] {
            line-color: @waterlinecolor;
            line-join: round;
            line-cap: round;
            line-width: 0.8;
        }
    }
    ::tunnels[tunnel = 'yes'] {
        [zoom >= 11][waterway = 'river'],
        [zoom >= 11][waterway = 'canal'][disused != 'yes'] {
            line-color: @waterlinecolor;
            line-join: round;
            line-cap: round;
            [zoom >= 11][zoom < 14] {
                line-width: 1.6;
                line-dasharray: 1.6,10;
            }
            [zoom >= 14] {
                line-width: 8;
                line-dasharray: 8,30;
            }
        }
    
        [zoom >= 11][waterway = 'stream'] {
            line-color: @waterlinecolor;
            line-join: round;
            line-cap: round;
            [zoom >= 11][zoom < 14] {
                line-width: 1;
                line-dasharray: 2,15;
            }
            [zoom >= 14] {
                line-width: 3;
                line-dasharray: 3,20;
            }
        }
        
        [zoom >= 14][waterway = 'drain'],
        [zoom >= 14][waterway = 'ditch'],
        [zoom >= 14][waterway = 'brook'] {
            line-color: @waterlinecolor;
            line-join: round;
            line-cap: round;
            line-width: 1.6;
            line-dasharray: 1.6,10;
        }
    }
}

/*
 * The water area rules are split into multiple layers for efficiency reasons.
 * Each zoom level group has a clause in the selection SQL that excludes any
 * polygons with an area less than the size of a single pixel.  This is really
 * important for the outline layers because the ST_Union() done on them gets
 * more expensive the more polygons it hat to consider.  It also helps the speed
 * of the water fill layers, though the performance improvement isn't as marked.
 */

.waterareas_z2[zoom >= 2][zoom < 7] {
    polygon-fill: @waterfillcolor;
}

.waterareas_z7[zoom >= 7][zoom < 9] {
    polygon-fill: @waterfillcolor;
}

.waterareas_z9[zoom >= 9][zoom < 11] {
    polygon-fill: @waterfillcolor;
}

.waterareas_z11[zoom >= 11][zoom < 14] {
    polygon-fill: @waterfillcolor;
}

.waterareas_z14[zoom >= 14] {
    polygon-fill: @waterfillcolor;
}

.waterareaoutlines_z7[zoom >= 7][zoom < 9] {
    [way_area > 8000000] {
        line-color: @waterlinecolor;
        line-width: 0.4;
    }
}

.waterareaoutlines_z9[zoom >= 9][zoom < 11] {
    [way_area > 4000000] {
        line-color: @waterlinecolor;
        line-width: 0.5;
    }
}

.waterareaoutlines_z11[zoom >= 11][zoom < 14] {
    line-color: @waterlinecolor;
    line-width: 0.8;
}

.waterareaoutlines_z14[zoom >= 14] {
    line-color: @waterlinecolor;
    line-width: 1.5;
}

.waterareaoutlines_intermittent[zoom >= 12] {
    line-color: @waterlinecolor;
    [zoom >= 12][zoom < 14] {
        line-width: 0.8;
        line-dasharray: 4,2;
    }
    [zoom >= 14] {
        line-width: 1.5;
        line-dasharray: 8,4;
    }
}

#waterlinefills {
    [zoom >= 14][waterway = 'river'],
    [zoom >= 14][waterway = 'canal'][disused != 'yes'] {
        line-color: @waterfillcolor;
        line-width: 2;
        line-join: round;
        line-cap: round;
    }
}

#water-features {
    [zoom >= 13][natural = 'wetland'] {
        polygon-pattern-file: url('symbols/marsh.png');
    }
    [zoom >= 10][natural = 'glacier'] {
        polygon-fill: #ffe0c0;
        line-color: #888;
        line-width: 0.7;
        line-dasharray: 5,5;
    }
}