#railway-outlines {
    // Heavy rail.
    [zoom >= 10][railway = 'rail'][service != 'spur'],
    [zoom >= 13][railway = 'rail'],
    [zoom >= 10][railway = 'preserved'][service != 'spur'],
    [zoom >= 13][railway = 'preserved'],
    [zoom >= 10][railway = 'disused'][service != 'spur'],
    [zoom >= 13][railway = 'disused'],
    [zoom >= 10][railway = 'abandoned'] [service != 'spur'],
    [zoom >= 13][railway = 'abandoned'] {
        line-color: black;
        [railway = 'abandoned'] { line-color:  #333; }
        [zoom >= 10][zoom < 15] {
            line-width: 1.7;
            [service = 'spur'] { line-width: 1.0; }
            [tunnel = 'yes'] { line-dasharray: 4,4; }
        }
        [zoom >= 15] {
            line-width: 3.5;
            [service = 'spur'] { line-width: 2.0; }
            [tunnel = 'yes'] { line-dasharray: 10,10; }
        }
    }

    // light rail, subways, etc.
    [zoom >=11][railway = 'light_rail'][service != 'spur'],
    [zoom >=13][railway = 'light_rail'],
    [zoom >=11][railway = 'tram'][service != 'spur'],
    [zoom >=13][railway = 'tram'],
    [zoom >=11][railway = 'subway'][service != 'spur'],
    [zoom >=13][railway = 'subway'],
    [zoom >=11][railway = 'monorail'][service != 'spur'],
    [zoom >=13][railway = 'monorail'],
    [zoom >=11][railway = 'funicular'] [service != 'spur'],
    [zoom >=13][railway = 'funicular'] {
        line-color: @lightrailcolor;
        [zoom >= 11][zoom < 15] {
            line-width: 1.3;
            [service = 'spur'] { line-width: 0.8; }
            [tunnel = 'yes'] { line-dasharray: 2,2; }
        }
        [zoom >= 15] {
            line-width: 2.5;
            [service = 'spur'] { line-width: 1.5; }
            [tunnel = 'yes'] { line-dasharray: 5,5; }
        }
    }
}

#railway-fills {
    // Heavy rail.
    [zoom >= 10][railway = 'rail'][service != 'spur'],
    [zoom >= 13][railway = 'rail'],
    [zoom >= 10][railway = 'preserved'][service != 'spur'],
    [zoom >= 13][railway = 'preserved'],
    [zoom >= 10][railway = 'disused'][service != 'spur'],
    [zoom >= 13][railway = 'disused'],
    [zoom >= 10][railway = 'abandoned'] [service != 'spur'],
    [zoom >= 13][railway = 'abandoned'] {
        line-color: white;
        [railway = 'abandoned'],
        [railway = 'disused']   { line-color:  #999; }
        [zoom >= 10][zoom < 15] {
            line-width: 0.9;
            [service = 'spur'] { line-width: 0.5; }
            line-dasharray: 4,4;
            [railway = 'preserved'][tunnel != 'yes'] { line-dasharray: 4,1; }
        }
        [zoom >= 15] {
            line-width: 2;
            [service = 'spur'] { line-width: 1.5; }
            line-dasharray: 10,10;
            [railway = 'preserved'][tunnel != 'yes'] { line-dasharray: 0,1,8,1; }
        }
    }
}
