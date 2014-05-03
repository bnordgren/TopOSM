#highway-lowzoom {
    [zoom >= 5][zoom < 9][highway = 'motorway'] {
        line-color: @interstatecolorlowzoom;
        line-join: round;
        line-cap: round;
        [zoom >= 5][zoom < 6] { line-width: 0.8; }
        [zoom >= 6][zoom < 7] { line-width: 1.0; }
        [zoom >= 7][zoom < 8] { line-width: 1.3; }
        [zoom >= 8][zoom < 9] { line-width: 1.8; }
    }
    [zoom >= 5][zoom < 9][highway = 'trunk'] {
        line-color: @trunkcolorlowzoom;
        line-join: round;
        line-cap: round;
        [zoom >= 5][zoom < 6] { line-width: 0.5; }
        [zoom >= 6][zoom < 7] { line-width: 0.7; }
        [zoom >= 7][zoom < 8] { line-width: 1.0; }
        [zoom >= 8][zoom < 9] { line-width: 1.5; }
    }
    [zoom >= 6][zoom < 9][highway = 'primary'] {
        line-color: @primarycolorlowzoom;
        line-join: round;
        line-cap: round;
        [zoom >= 6][zoom < 7] { line-width: 0.3; }
        [zoom >= 7][zoom < 8] { line-width: 0.5; }
        [zoom >= 8][zoom < 9] { line-width: 0.7; }
    }
}

#highway-outlines {
    [zoom >= 9][highway = 'motorway'],
    [zoom >= 9][highway = 'trunk'] {
        [tunnel != 'yes'] {
            line-color: black;
            line-join: round;
            line-cap: round;
        }
        [tunnel = 'yes'] {
            line-color: @tunneloutlinecolor;
        }
        [zoom >=  9][zoom < 12] {
            line-width:  4.0; [tunnel = 'yes'] { line-dasharray:  4,2; }
        }
        [zoom >= 12][zoom < 15] {
            line-width:  7.0; [tunnel = 'yes'] { line-dasharray:  6,3; }
        }
        [zoom >= 15] {
            line-width: 13.0; [tunnel = 'yes'] { line-dasharray: 10,5; }
        }
    }

    [zoom >= 9][zoom < 10][highway = 'primary'] {
        line-color: @primarycolorlowzoom;
        line-join: round;
        line-cap: round;
        line-width: 1.2;
    }
    [zoom >= 10][highway = 'primary'] {
        [tunnel != 'yes'] {
            line-color: black;
            line-join: round;
            line-cap: round;
        }
        [tunnel = 'yes'] {
            line-color: @tunneloutlinecolor;
        }
        [zoom >= 10][zoom < 12] {
            line-width:  3.0; [tunnel = 'yes'] { line-dasharray:  4,2; }
        }
        [zoom >= 12][zoom < 15] {
            line-width:  5.5; [tunnel = 'yes'] { line-dasharray:  6,3; }
        }
        [zoom >= 15] {
            line-width: 10.0; [tunnel = 'yes'] { line-dasharray: 10,5; }
        }
    }
    
    [zoom >= 9][zoom < 10][highway = 'secondary'] {
        line-color: @secondarycolorlowzoom;
        line-join: round;
        line-cap: round;
        line-width: 0.9;
    }
    [zoom >= 9][zoom < 10][highway = 'tertiary'] {
        line-color: @smallroadcolorlowzoom;
        line-join: round;
        line-cap: round;
        line-width: 0.6;
    }
    [zoom >= 10][highway = 'secondary'],
    [zoom >= 10][highway = 'tertiary'] {
        [tunnel != 'yes'] {
            line-color: black;
            line-join: round;
            line-cap: round;
        }
        [tunnel = 'yes'] {
            line-color: @tunneloutlinecolor;
        }
        [zoom >= 10][zoom < 12] {
            line-width:  2.5; [tunnel = 'yes'] { line-dasharray:  4,2; }
        }
        [zoom >= 12][zoom < 14] {
            line-width:  4.0; [tunnel = 'yes'] { line-dasharray:  6,3; }
        }
        [zoom >= 14][zoom < 16] {
            line-width:  5.5; [tunnel = 'yes'] { line-dasharray:  6,3; }
        }
        [zoom >= 16] {
            line-width: 10.0; [tunnel = 'yes'] { line-dasharray: 10,5; }
        }
    }

    [zoom >= 10][zoom < 12][highway = 'unclassified'],
    [zoom >= 10][zoom < 12][highway = 'residential'] {
        line-color: #444;
        line-join: round;
        line-cap: round;
        [zoom >= 10][zoom < 11] { line-width: 0.5; }
        [zoom >= 11][zoom < 12] { line-width: 0.6; }
    }
    [zoom >= 12][zoom < 14][highway = 'unclassified'],
    [zoom >= 12][zoom < 14][highway = 'residential'] {
        line-width: 1.2;
        [tunnel = 'yes'] {
            line-color: @tunneloutlinecolor;
            line-dasharray: 6,3;
        }
        [tunnel != 'yes'] {
            line-color: #444;
            line-join: round;
            line-cap: round;
        }
    }
    [zoom >= 14][highway = 'unclassified'],
    [zoom >= 14][highway = 'residential'] {
        [tunnel != 'yes'] {
            line-color: black;
            line-join: round;
            line-cap: round;
        }
        [tunnel = 'yes'] {
            line-color: @tunneloutlinecolor;
        }
        [zoom >= 14][zoom < 16] {
            line-width:  4.0; [tunnel = 'yes'] { line-dasharray:  6,3; }
        }
        [zoom >= 16] {
            line-width:  7.0; [tunnel = 'yes'] { line-dasharray: 10,5; }
        }
    }

    [zoom >= 10][highway = 'motorway_link'],
    [zoom >= 10][highway = 'trunk_link'],
    [zoom >= 10][highway = 'primary_link'],
    [zoom >= 10][highway = 'secondary_link'],
    [zoom >= 10][highway = 'tertiary_link'] {
        [tunnel = 'yes'] {
            line-color: @tunneloutlinecolor;
        }
        [tunnel != 'yes'] {
            line-color: black;
            line-join: round;
            line-cap: round;
        }
        [zoom >= 10][zoom < 11] {
            line-width:  0.5;
        }
        [zoom >= 11][zoom < 12] {
            line-width:  0.6;
        }
        [zoom >= 12][zoom < 16] {
            line-width:  4.0; [tunnel = 'yes'] { line-dasharray:  6,3; }
        }
        [zoom >= 16] {
            line-width:  7.0; [tunnel = 'yes'] { line-dasharray:  6,3; }
        }
    }

    [zoom >= 12][zoom < 14][highway = 'service'] {
        line-color: #444;
        line-join: round;
        line-cap: round;
        line-width: 0.8;
    }
    [zoom >= 14][highway = 'service'] {
        [tunnel = 'yes'] {
            line-color: @tunneloutlinecolor;
        }
        [tunnel != 'yes'] {
            line-color: black;
            line-join: round;
            line-cap: round;
        }
        [zoom >= 14][zoom < 16] {
            line-width:  2.5; [tunnel = 'yes'] { line-dasharray:  6,3; }
        }
        [zoom >= 16] {
            line-width:  4.0; [tunnel = 'yes'] { line-dasharray: 10,5; }
        }
    }

    [zoom >= 12][highway = 'unsurfaced'],
    [zoom >= 12][highway = 'unimproved'],
    [zoom >= 12][highway = 'track'][bicycle != 'designated'] {
        [zoom >= 12][zoom < 14] {
            line-color: #444;
            line-width: 1.2;
            line-dasharray: 4,2;
        }
        [zoom >= 14] {
            line-color: black;
            line-dasharray: 5,2;
            [zoom >= 14][zoom < 16] { line-width: 4.0; }
            [zoom >= 16]            { line-width: 7.0; }
        }
    }

    [zoom >= 13][highway = 'cycleway'],
    [zoom >= 13][highway = 'bikeway'],
    [zoom >= 13][highway = 'bridleway'],
    [zoom >= 13][highway = 'track'][bicycle = 'designated'] {
        line-color: black;
        [zoom >= 13][zoom < 15] {
            line-width: 1.0;
            [tunnel =  'yes'] { line-dasharray: 0,6,5,1; }
            [tunnel != 'yes'] { line-dasharray: 5,1; }
        }
        [zoom >= 15] {
            line-width: 2.0;
            [tunnel =  'yes'] { line-dasharray: 0,7,6,1; }
            [tunnel != 'yes'] { line-dasharray: 6,1; }
        }
    }

    [zoom >= 13][highway = 'path'],
    [zoom >= 13][highway = 'trail'],
    [zoom >= 13][highway = 'footway'],
    [zoom >= 13][highway = 'steps'],
    [zoom >= 13][highway = 'pedestrian'] {
        line-color: black;
        [zoom >= 13][zoom < 15] {
            line-width: 0.8;
            [tunnel =  'yes'] { line-dasharray: 0,5,3,2; }
            [tunnel != 'yes'] { line-dasharray: 3,2; }
        }
        [zoom >= 15] {
            line-width: 1.5;
            [tunnel =  'yes'] { line-dasharray: 0,7,4,3; }
            [tunnel != 'yes'] { line-dasharray: 4,3; }
        }
    }
}

#highway-fills {
    [zoom >= 9][highway = 'motorway'] {
        line-join: round;
        line-cap: round;
        line-color: @interstatecolor;
        [tunnel = 'yes'] { line-color: @interstatecolortunnel; }
        [zoom >=  9][zoom < 12] { line-width:  2.5; }
        [zoom >= 12][zoom < 15] { line-width:  4.5; }
        [zoom >= 15]            { line-width: 10.0; }
    }

    [zoom >= 9][highway = 'trunk'] {
        line-join: round;
        line-cap: round;
        line-color: @trunkcolor;
        [tunnel = 'yes'] { line-color: @trunkcolor; }
        [zoom >=  9][zoom < 12] { line-width:  2.5; }
        [zoom >= 12][zoom < 15] { line-width:  4.5; }
        [zoom >= 15]            { line-width: 10.0; }
    }

    [zoom >= 10][highway = 'primary'] {
        line-join: round;
        line-cap: round;
        line-color: @primarycolor;
        [tunnel = 'yes'] { line-color: @primarycolortunnel; }
        [zoom >= 10][zoom < 12] { line-width:  1.8; }
        [zoom >= 12][zoom < 15] { line-width:  3.5; }
        [zoom >= 15]            { line-width:  8.0; }
    }

    [zoom >= 10][highway = 'secondary'] {
        line-join: round;
        line-cap: round;
        line-color: @secondarycolor;
        [tunnel = 'yes'] { line-color: @secondarycolortunnel; }
        [zoom >= 10][zoom < 12] { line-width:  1.5; }
        [zoom >= 12][zoom < 14] { line-width:  2.0; }
        [zoom >= 14][zoom < 16] { line-width:  3.5; }
        [zoom >= 16]            { line-width:  8.0; }
    }

    [zoom >= 10][highway = 'tertiary'] {
        line-join: round;
        line-cap: round;
        line-color: @smallroadcolor;
        [tunnel = 'yes'] { line-color: @smallroadcolortunnel; }
        [zoom >= 10][zoom < 12] { line-width:  1.0; }
        [zoom >= 12][zoom < 14] { line-width:  2.0; }
        [zoom >= 14][zoom < 16] { line-width:  3.5; }
        [zoom >= 16]            { line-width:  8.0; }
    }

    [zoom >= 14][highway = 'unclassified'],
    [zoom >= 14][highway = 'residential'],
    [zoom >= 14][highway = 'unsurfaced'],
    [zoom >= 14][highway = 'unimproved'],
    [zoom >= 14][highway = 'track'][bicycle != 'designated'] {
        line-join: round;
        line-cap: round;
        line-color: @smallroadcolor;
        [tunnel = 'yes'] { line-color: @smallroadcolortunnel; }
        [zoom >= 14][zoom < 16] { line-width:  2.0; }
        [zoom >= 16]            { line-width:  5.0; }
    }

    [zoom >= 14][highway = 'service'] {
        line-join: round;
        line-cap: round;
        line-color: @smallroadcolor;
        [tunnel = 'yes'] { line-color: @smallroadcolortunnel; }
        [zoom >= 14][zoom < 16] { line-width:  1.3; }
        [zoom >= 16]            { line-width:  2.0; }
    }

    [zoom >= 12][highway = 'motorway_link'],
    [zoom >= 12][highway = 'trunk_link'],
    [zoom >= 12][highway = 'primary_link'],
    [zoom >= 12][highway = 'secondary_link'],
    [zoom >= 12][highway = 'tertiary_link'] {
        line-join: round;
        line-cap: round;
        [highway = 'motorway_link'] {
            line-color: @interstatecolor;
            [tunnel = 'yes'] { line-color: @interstatecolortunnel; }
        }
        [highway = 'trunk_link'] {
            line-color: @trunkcolor;
            [tunnel = 'yes'] { line-color: @trunkcolortunnel; }
        }
        [highway = 'primary_link'] {
            line-color: @primarycolor;
            [tunnel = 'yes'] { line-color: @primarycolortunnel; }
        }
        [highway = 'secondary_link'] {
            line-color: @secondarycolor;
            [tunnel = 'yes'] { line-color: @secondarycolortunnel; }
        }
        [highway = 'tertiary_link'] {
            line-color: @smallroadcolor;
            [tunnel = 'yes'] { line-color: @smallroadcolortunnel; }
        }
        line-color: @smallroadcolor;
        [zoom >= 12][zoom < 16] { line-width: 2.0; }
        [zoom >= 16]            { line-width: 4.0; }
    }
}

#turning-circles-outlines {
    [int_tc_type = 'tertiary'] {
        [zoom >= 15][zoom < 16] {
            point-file: url('custom-symbols/turning_circle-tertiary-z15-casing.png');
        }
        [zoom >= 16] {
            point-file: url('custom-symbols/turning_circle-tertiary-z16-casing.png');
        }
    }
    [int_tc_type = 'unclassified'],
    [int_tc_type = 'residential'] {
        [zoom >= 15][zoom < 16] {
            point-file: url('custom-symbols/turning_circle-minor-z15-casing.png');
        }
        [zoom >= 16] {
            point-file: url('custom-symbols/turning_circle-minor-z16-casing.png');
        }
    }
    [int_tc_type = 'service'] {
        [zoom >= 15][zoom < 16] {
            point-file: url('custom-symbols/turning_circle-service-z15-casing.png');
        }
        [zoom >= 16] {
            point-file: url('custom-symbols/turning_circle-service-z16-casing.png');
        }
    }
}

#turning-circles-fills {
    [int_tc_type = 'tertiary'] {
        [zoom >= 15][zoom < 16] {
            point-file: url('custom-symbols/turning_circle-tertiary-z15-fill.png');
        }
        [zoom >= 16] {
            point-file: url('custom-symbols/turning_circle-tertiary-z16-fill.png');
        }
    }
    [int_tc_type = 'unclassified'],
    [int_tc_type = 'residential'] {
        [zoom >= 15][zoom < 16] {
            point-file: url('custom-symbols/turning_circle-minor-z15-fill.png');
        }
        [zoom >= 16] {
            point-file: url('custom-symbols/turning_circle-minor-z16-fill.png');
        }
    }
    [int_tc_type = 'service'] {
        [zoom >= 15][zoom < 16] {
            point-file: url('custom-symbols/turning_circle-service-z15-fill.png');
        }
        [zoom >= 16] {
            point-file: url('custom-symbols/turning_circle-service-z16-fill.png');
        }
    }
}

#parking-outlines {
    [zoom >= 14][amenity = 'parking'] {
        line-color: black;
        line-join: round;
        line-cap: round;
        [zoom >= 14][zoom < 16] {
            line-width: 2;
        }
        [zoom >= 16] {
            line-width: 3.5;
        }
    }
}

#parking-fills {
    [zoom >= 14][amenity = 'parking'] {
        polygon-fill: @smallroadcolor;
    }
}
