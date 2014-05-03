@bridgeopacity: 0.6;

Map {
    background-color: transparent;
}

#bridges {
    /* NOTE: These must be in the same style as highway fills, since they are
     * often drawn "inbetween" different level roads.  Outlines at the same
     * level will draw before fills, however, thanks to "pass".
     */

    [zoom >= 14][waterway = 'river'],
    [zoom >= 14][waterway = 'canal'][disused != 'yes'] {
        [pass = 1] {
            line-width: 8.0;
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
        }
        [pass = 2] {
            line-color: @waterfillcolor;
            line-width: 2;
            line-join: round;
            line-cap: round;
        }
    }
    [zoom >= 14][waterway = 'derelict_canal'],
    [zoom >= 14][waterway = 'canal'][disused = 'yes'] {
        [pass = 1] {
            line-width: 5.0;
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
        }
        [pass = 2] {
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
    }
    [zoom >= 14][waterway = 'stream'] {
        [pass = 1] {
            line-width: 4.5;
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
        }
        [pass = 2] {
            line-color: @waterlinecolor;
            line-join: round;
            line-cap: round;
            line-width: 1.5;
        }
    }
    [zoom >= 14][waterway = 'ditch'],
    [zoom >= 14][waterway = 'drain'],
    [zoom >= 14][waterway = 'brook'] {
        [pass = 1] {
            line-width: 2.5;
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
        }
        [pass = 2] {
            line-color: @waterlinecolor;
            line-join: round;
            line-cap: round;
            line-width: 0.8;
        }
    }

    [zoom >= 14][highway = 'motorway'],
    [zoom >= 14][highway = 'trunk'] {
        [pass = 1] {
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
            [zoom >= 14][zoom < 15] { line-width:  9.0; }
            [zoom >= 15]            { line-width: 16.0; }
        }
        [pass = 2] {
            line-join: round;
            line-cap: round;
            [highway = 'motorway'] { line-color: @interstatecolor; }
            [highway = 'trunk']    { line-color: @trunkcolor; }
            [zoom >= 12][zoom < 15] { line-width:  4.5; }
            [zoom >= 15]            { line-width: 10.0; }
        }
    }

    [zoom >= 14][highway = 'primary'] {
        [pass = 1] {
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
            [zoom >= 14][zoom < 15] { line-width:  7.5; }
            [zoom >= 15]            { line-width: 13.0; }
        }
        [pass = 2] {
            line-join: round;
            line-cap: round;
            line-color: @primarycolor;
            [zoom >= 12][zoom < 15] { line-width:  3.5; }
            [zoom >= 15]            { line-width:  8.0; }
        }
    }

    [zoom >= 14][highway = 'secondary'],
    [zoom >= 14][highway = 'tertiary'] {
        [pass = 1] {
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
            [zoom >= 14][zoom < 16] { line-width:  7.5; }
            [zoom >= 16]            { line-width: 13.0; }
        }
        [pass = 2] {
            line-join: round;
            line-cap: round;
            [highway = 'secondary'] { line-color: @secondarycolor; }
            [highway = 'tertiary']  { line-color: @smallroadcolor; }
            [zoom >= 12][zoom < 16] { line-width:  3.5; }
            [zoom >= 16]            { line-width:  8.0; }
        }
    }

    [zoom >= 14][highway = 'unclassified'],
    [zoom >= 14][highway = 'residential'] {
        [pass = 1] {
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
            [zoom >= 14][zoom < 16] { line-width:  6.0; }
            [zoom >= 16]            { line-width: 10.0; }
        }
        [pass = 2] {
            line-join: round;
            line-cap: round;
            line-color: @smallroadcolor;
            [zoom >= 14][zoom < 16] { line-width:  2.0; }
            [zoom >= 16]            { line-width:  5.0; }
        }
    }

    [zoom >= 14][highway = 'motorway_link'],
    [zoom >= 14][highway = 'trunk_link'],
    [zoom >= 14][highway = 'primary_link'],
    [zoom >= 14][highway = 'secondary_link'],
    [zoom >= 14][highway = 'tertiary_link'] {
        [pass = 1] {
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
            [zoom >= 14][zoom < 16] { line-width:  6.0; }
            [zoom >= 16]            { line-width: 10.0; }
        }
        [pass = 2] {
            line-join: round;
            line-cap: round;
            line-color: @smallroadcolor;
            [highway = 'motorway_link']  { line-color: @interstatecolor; }
            [highway = 'trunk_link']     { line-color: @trunkcolor; }
            [highway = 'primary_link']   { line-color: @primarycolor; }
            [highway = 'secondary_link'] { line-color: @secondarycolor; }
            [zoom >= 12][zoom < 16] { line-width: 2.0; }
            [zoom >= 16]            { line-width: 4.0; }
        }
    }

    [zoom >= 14][highway = 'service'] {
        [pass = 1] {
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
            [zoom >= 14][zoom < 16] { line-width:  4.0; }
            [zoom >= 16]            { line-width:  6.0; }
        }
        [pass = 2] {
            line-join: round;
            line-cap: round;
            line-color: @smallroadcolor;
            [zoom >= 12][zoom < 16] { line-width: 1.3; }
            [zoom >= 16]            { line-width: 2.0; }
        }
    }

    [zoom >= 14][highway = 'path'],
    [zoom >= 14][highway = 'trail'],
    [zoom >= 14][highway = 'footway'],
    [zoom >= 14][highway = 'steps'],
    [zoom >= 14][highway = 'pedestrian'],
    [zoom >= 14][highway = 'cycleway'],
    [zoom >= 14][highway = 'bikeway'],
    [zoom >= 14][highway = 'bridleway'],
    [zoom >= 14][highway = 'track'][bicycle = 'designated'] {
        [pass = 1] {
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
            [zoom >= 14][zoom < 15] { line-width:  2.5; }
            [zoom >= 15]            { line-width:  4.0; }
        }
        [pass = 2] {
            line-color: black;
            [highway = 'cycleway'],
            [highway = 'bikeway'],
            [highway = 'bridleway'],
            [highway = 'track'][bicycle = 'designated'] {
                [zoom >= 14][zoom < 15] { line-width: 1.0; line-dasharray: 5,1; }
                [zoom >= 15]            { line-width: 2.0; line-dasharray: 6,1; }
            }
            [highway = 'path'],
            [highway = 'trail'],
            [highway = 'footway'],
            [highway = 'steps'],
            [highway = 'pedestrian'] {
                [zoom >= 14][zoom < 15] { line-width: 0.8; line-dasharray: 3,2; }
                [zoom >= 15]            { line-width: 1.5; line-dasharray: 4,3; }
            }
        }
    }

    [zoom >= 14][railway = 'rail'],
    [zoom >= 14][railway = 'preserved'],
    [zoom >= 14][railway = 'disused'],
    [zoom >= 14][railway = 'abandoned'] {
        [pass = 1] {
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
            [zoom >= 14][zoom < 15] { line-width:  3.7; }
            [zoom >= 15]            { line-width:  7.0; }
        }
        [pass = 2] {
            line-color: black;
            b/line-color: white;
            [railway = 'abandoned'],
            [railway = 'disused'] { b/line-color: #999; }
            [zoom >= 14][zoom < 15] {
                line-width: 0.9; b/line-width: 0.9;
                [service = 'spur'] { line-width: 0.5; b/line-width: 0.5; }
                b/line-dasharray: 4,4;
                [railway = 'preserved'] { b/line-dasharray: 4,1; }
            }
            [zoom >= 15] {
                line-width: 2.0; b/line-width: 2.0;
                [service = 'spur'] { line-width: 1.5; b/line-width: 1.5; }
                b/line-dasharray: 10,10;
                [railway = 'preserved'] { b/line-dasharray: 0,1,8,1; }
            }
        }
    }

    [zoom >= 14][railway = 'light_rail'],
    [zoom >= 14][railway = 'tram'],
    [zoom >= 14][railway = 'subway'],
    [zoom >= 14][railway = 'monorail'],
    [zoom >= 14][railway = 'funicular'] {
        [pass = 1] {
            line-color: black;
            line-opacity: @bridgeopacity;
            line-cap: butt;
            [zoom >= 14][zoom < 15] { line-width:  3.3; }
            [zoom >= 15]            { line-width:  5.5; }
        }
        [pass = 2] {
            line-color: @lightrailcolor;
            [zoom >= 14][zoom < 15] {
                line-width: 1.3;
                [service  = 'spur'] { line-width: 0.8; }
            }
            [zoom >= 15] {
                line-width: 2.5;
                [service  = 'spur'] { line-width: 1.5; }
            }
        }
    }
}

#aerialways {
    [zoom >= 12][aerialway = 'cable_car'],
    [zoom >= 12][aerialway = 'gondola'],
    [zoom >= 12][aerialway = 'chair_lift'],
    [zoom >= 12][aerialway = 'drag_lift'] {
        line-pattern-file: url('symbols/chair_lift.png');
    }
}

#power-lines {
    ::main {
        /* at zoom 13, only the lines' existence is shown */
        [zoom >= 13][zoom < 14][power = 'line'] {
            line-color: black;
            line-width: 0.5;
        }
        /* at zoom 14 and 15, the lines' voltage and wire count are shown */
        [zoom >= 14][zoom < 16][power = 'line'] {
            [voltage >= 115000] {
                [zoom >= 14][zoom < 15] { line-width: 2.1; }
                [zoom >= 15][zoom < 16] { line-width: 3.0; }
                [voltage >= 115000][voltage < 230000] { line-color: #ffff00; }
                [voltage >= 230000][voltage < 500000] { line-color: #ffa500; }
                [voltage >= 500000][voltage < 768000] { line-color: #bb3333; }
                [voltage >= 768000]                   { line-color: #ff0000; }
            }
            [zoom >= 14][zoom < 15] { b/line-width: 0.7; }
            [zoom >= 15][zoom < 16] { b/line-width: 1.0; }
            [wires = 'single'] { b/line-dasharray: 93,2,5,2; }
            [wires = 'double'] { b/line-dasharray: 86,2,5,2,5,2; }
            [wires = 'triple'] { b/line-dasharray: 79,2,5,2,5,2,5,2; }
            [wires = 'quad']   { b/line-dasharray: 72,2,5,2,5,2,5,2,5,2; }
        }

    }

    ::busbar-voltage {
        [zoom >= 14][power = 'busbar'] {
            line-color: #ccc;
            [voltage >= 115000][voltage < 230000] { line-color: #ffff00; }
            [voltage >= 230000][voltage < 500000] { line-color: #ffa500; }
            [voltage >= 500000][voltage < 768000] { line-color: #bb3333; }
            [voltage >= 768000]                   { line-color: #ff0000; }
            [zoom >= 14][zoom < 15] { line-width: 3.4; }
            [zoom >= 15]            { line-width: 4.0; }
        }
    }
    ::busbar-line {
        [zoom >= 13][power = 'busbar'] {
            [zoom >= 13][zoom < 14] { line-color: #ccc; line-width: 1.0; }
            [zoom >= 14][zoom < 15] { line-color: #ccc; line-width: 1.4; }
            [zoom >= 15]            { line-color: #ddd; line-width: 2.0; }
        }
    }

    /* at zoom 16, voltage, circuit count, and wire count are all shown */
    ::clear {
        [zoom >= 16][power = 'line'] {
            line-comp-op: dst-out;
            line-width: 3;
            [cables =~ '^[345]$']    { line-width:  3; }
            [cables =~ '^[678]$']    { line-width:  6; }
            [cables =~ '^9|1[01]$']  { line-width:  9; }
            [cables =~ '^1[234]$']   { line-width: 12; }
            [cables =~ '^1[567]$']   { line-width: 15; }
            [cables =~ '^1[89]|20$'] { line-width: 18; }
        }
    }
    ::five-six {
        [zoom >= 16][power = 'line'] {
            /* six circuits */
            [cables =~ '^1[89]|20$'] {
                line-width: 16;
                [wires = 'single'] { line-dasharray: 93,2,5,2; }
                [wires = 'double'] { line-dasharray: 86,2,5,2,5,2; }
                [wires = 'triple'] { line-dasharray: 79,2,5,2,5,2,5,2; }
                [wires = 'quad']   { line-dasharray: 72,2,5,2,5,2,5,2,5,2; }
                b/line-width: 14;
                b/line-comp-op: dst-out;
            }
            /* five circuits */
            [cables =~ '^1[567]$'] {
                line-width: 13;
                [wires = 'single'] { line-dasharray: 93,2,5,2; }
                [wires = 'double'] { line-dasharray: 86,2,5,2,5,2; }
                [wires = 'triple'] { line-dasharray: 79,2,5,2,5,2,5,2; }
                [wires = 'quad']   { line-dasharray: 72,2,5,2,5,2,5,2,5,2; }
                b/line-width: 11;
                b/line-comp-op: dst-out;
            }
        }
    }
    ::three-four {
        [zoom >= 16][power = 'line'] {
            /* four circuits */
            [cables =~ '^1[23489]|20$'] {
                line-width: 10;
                [wires = 'single'] { line-dasharray: 93,2,5,2; }
                [wires = 'double'] { line-dasharray: 86,2,5,2,5,2; }
                [wires = 'triple'] { line-dasharray: 79,2,5,2,5,2,5,2; }
                [wires = 'quad']   { line-dasharray: 72,2,5,2,5,2,5,2,5,2; }
                b/line-width: 8;
                b/line-comp-op: dst-out;
            }
            /* three circuits */
            [cables =~ '^9|1[01567]$'] {
                line-width: 7;
                [wires = 'single'] { line-dasharray: 93,2,5,2; }
                [wires = 'double'] { line-dasharray: 86,2,5,2,5,2; }
                [wires = 'triple'] { line-dasharray: 79,2,5,2,5,2,5,2; }
                [wires = 'quad']   { line-dasharray: 72,2,5,2,5,2,5,2,5,2; }
                b/line-width: 5;
                b/line-comp-op: dst-out;
            }
        }
    }
    ::one-two {
        [zoom >= 16][power = 'line'] {
            /* two circuits */
            [cables =~ '^[678]|1[23489]|20$'] {
                line-width: 4;
                [wires = 'single'] { line-dasharray: 93,2,5,2; }
                [wires = 'double'] { line-dasharray: 86,2,5,2,5,2; }
                [wires = 'triple'] { line-dasharray: 79,2,5,2,5,2,5,2; }
                [wires = 'quad']   { line-dasharray: 72,2,5,2,5,2,5,2,5,2; }
                b/line-width: 2;
                b/line-comp-op: dst-out;
            }
            /* one circuit */
            [cables =~ '^[3459]|1[01567]$'] {
                line-width: 1;
                [wires = 'single'] { line-dasharray: 93,2,5,2; }
                [wires = 'double'] { line-dasharray: 86,2,5,2,5,2; }
                [wires = 'triple'] { line-dasharray: 79,2,5,2,5,2,5,2; }
                [wires = 'quad']   { line-dasharray: 72,2,5,2,5,2,5,2,5,2; }
            }
        }
    }
    ::color {
        [zoom >= 16][power = 'line'][voltage >= 115000] {
            line-comp-op: dst-over;
            [voltage >= 115000][voltage < 230000] { line-color: #ffff00; }
            [voltage >= 230000][voltage < 500000] { line-color: #ffa500; }
            [voltage >= 500000][voltage < 768000] { line-color: #bb3333; }
            [voltage >= 768000]                   { line-color: #ff0000; }
            line-width: 3;
            [cables =~ '^[345]$']    { line-width:  3; }
            [cables =~ '^[678]$']    { line-width:  6; }
            [cables =~ '^9|1[01]$']  { line-width:  9; }
            [cables =~ '^1[234]$']   { line-width: 12; }
            [cables =~ '^1[567]$']   { line-width: 15; }
            [cables =~ '^1[89]|20$'] { line-width: 18; }
        }
    }
}
