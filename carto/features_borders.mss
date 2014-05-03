#nature-borders {
    [zoom >= 7][zoom < 10][way_area > 50000000] {
        polygon-fill: @naturecolorlight;
        polygon-opacity: 0.05;
        line-color: @naturecolorlight;
        line-width: 1;
        line-dasharray: 5,2;
        line-opacity: 0.7;
    }
    [zoom >= 10][zoom < 12][way_area > 10000000] {
        polygon-fill: @naturecolorlight;
        polygon-opacity: 0.05;
        line-color: @naturecolorlight;
        line-width: 1.8;
        line-dasharray: 7,3;
        line-opacity: 0.7;
    }

    /*
     * High zoom: Outline large areas, shade small areas.
     * This is a workaround for the fact that some large areas,
     * like some national parks, are just tagged as 'park'.
     */
    [zoom >= 12] {
        [way_area > 5000000] {
            line-color: @naturecolorlight;
            line-width: 3;
            line-dasharray: 8,3;
            line-opacity: 0.7;
        }
        [way_area <= 5000000] {
            polygon-fill: @naturecolorlight;
            polygon-opacity: 0.1;
        }
    }
}

#misc-borders {
    [zoom >= 6][landuse = 'military'] {
        line-color: #f00;
        [zoom >= 6][zoom < 14] {
            line-width: 1;
            polygon-pattern-file: url('custom-symbols/hatch-red-10.png');
        }
        [zoom >= 14] {
            line-width: 1.5;
            polygon-pattern-file: url('custom-symbols/hatch-red-16.png');
        }
    }

    [zoom >= 10][landuse = 'cemetery'],
    [zoom >= 10][amenity = 'grave_yard'] {
        polygon-fill: #8b8;
        polygon-opacity: @areaopacity;
        line-color: #8b8;
        line-width: 1;
    }

    [zoom >= 10][landuse = 'construction'] {
        polygon-fill: #bb3;
        polygon-opacity: @areaopacity;
        line-color: #bb3;
        line-width: 1;
    }

    [zoom >= 10][natural = 'beach'] {
        polygon-fill: #fec;
        polygon-opacity: @areaopacity;
        line-color: #fec;
        line-width: 1;
    }
}

.county-borders {
    [zoom >= 9][boundary = 'administrative'][admin_level = '6'] {
        line-color: black;
        [zoom >=  9][zoom < 11] { line-width: 0.4; line-dasharray: 10,3,2,3; }
        [zoom >= 11]            { line-width: 0.7; line-dasharray: 20,5,4,5; }
    }
}

.state-borders {
    [zoom >= 0][zoom < 11][boundary = 'administrative'][admin_level = '4'] {
        line-color: black;
        [zoom >= 0][zoom <  6] { line-width: 0.5; line-dasharray: 8,3,2,3; }
        [zoom >= 6][zoom < 11] { line-width: 0.8; line-dasharray: 10,3,2,3; }
    }
    [zoom >= 11][boundary = 'administrative'][admin_level = '4'] {
        line-color: #825;
        line-width: 8;
        line-opacity: 0.5;
        b/line-color: black;
        b/line-width: 1.5;
        b/line-dasharray: 20,5,4,5;
    }
}

.country-borders {
    [boundary = 'administrative'][admin_level = '2'] {
        line-color: black;
        [zoom >=  0][zoom <  6] { line-width: 1.0; line-dasharray: 10,3,2,3; }
        [zoom >=  6][zoom < 11] { line-width: 1.5; line-dasharray: 15,3,2,3; }
        [zoom >= 11]            { line-width: 3.0; line-dasharray: 30,5,4,5; }
    }
}
