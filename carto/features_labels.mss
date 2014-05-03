Map {
    background-color: @mapcolor;
}

@haloradius: 3;

#statenames {
    [zoom >= 4][zoom < 8][place = 'state'] {
        text-face-name: @book-fonts;
        text-fill: @statenamecolor;
        text-halo-fill: @halocolor;
        text-halo-radius: @haloradius;
        [zoom >= 4][zoom < 5] {
            text-name: [ref];
            text-size: 10;
        }
        [zoom >= 5][zoom < 6] {
            text-name: [name];
            text-size: 12;
        }
        [zoom >= 6][zoom < 8] {
            text-name: [name];
            text-size: 14;
        }
    }
}

#placenames {
    [zoom >= 5][place = 'city'] {
        text-name: [name];
        text-fill: @placenamecolor;
        text-halo-fill: @halocolor;
        text-halo-radius: @haloradius;
        [zoom >=  5][zoom <  8] { text-size:  9; text-face-name: @book-fonts; }
        [zoom >=  8][zoom < 10] { text-size: 10; text-face-name: @bold-fonts; }
        [zoom >= 10]            { text-size: 17; text-face-name: @bold-fonts; }
    }
    [zoom >= 8][place = 'town'],
    [zoom >= 10][place = 'suburb'] {
        text-name: [name];
        text-fill: @placenamecolor;
        text-halo-fill: @halocolor;
        text-halo-radius: @haloradius;
        [zoom >=  8][zoom < 10] { text-size:  9; text-face-name: @book-fonts; }
        [zoom >= 10][zoom < 11] { text-size: 10; text-face-name: @bold-fonts; }
        [zoom >= 11]            { text-size: 13; text-face-name: @bold-fonts; }
    }
    [zoom >= 11][place = 'village'] {
        text-name: [name];
        text-face-name: @bold-fonts;
        text-fill: @placenamecolor;
        text-halo-fill: @halocolor;
        text-halo-radius: @haloradius;
        [zoom >= 11][zoom < 13] { text-size: 10; }
        [zoom >= 13]            { text-size: 12; }
    }
    [zoom >= 13][place = 'locality'],
    [zoom >= 13][place = 'hamlet'],
    [zoom >= 13][place = 'neighbourhood'] {
        text-name: [name];
        text-face-name: @bold-fonts;
        text-fill: @placenamecolor;
        text-halo-fill: @halocolor;
        text-halo-radius: @haloradius;
        text-size: 10;
    }
}

.streetnames {
    [zoom >= 13][highway = 'motorway'],
    [zoom >= 13][highway = 'trunk'],
    [zoom >= 14][highway = 'primary'],
    [zoom >= 14][highway = 'secondary'],
    [zoom >= 14][highway = 'tertiary'],
    [zoom >= 15][highway = 'unclassified'],
    [zoom >= 15][highway = 'residential'],
    [zoom >= 15][highway = 'track'],
    [zoom >= 15][highway = 'service'] {
        text-name: [name];
        text-face-name: @book-fonts;
        text-fill: @streetnamecolor;
        text-halo-radius: 2;
        text-spacing: 300;
        text-placement: line;
        text-max-char-angle-delta: 35;
        text-size: 9;
        text-halo-fill: @smallroadcolor;
        [highway = 'motorway'] {
            text-size: 11;
            text-halo-fill: @interstatecolor;
            [tunnel = 'yes'] { text-halo-fill: @interstatecolortunnel; }
        }
        [highway = 'trunk'] {
            text-size: 11;
            text-halo-fill: @trunkcolor;
            [tunnel = 'yes'] { text-halo-fill: @trunkcolortunnel; }
        }
        [highway = 'primary'] {
            text-size: 10;
            text-halo-fill: @primarycolor;
            [tunnel = 'yes'] { text-halo-fill: @primarycolortunnel; }
        }
        [highway = 'secondary'] {
            text-size: 10;
            text-halo-fill: @secondarycolor;
            [tunnel = 'yes'] { text-halo-fill: @secondarycolortunnel; }
        }
        [highway = 'tertiary'] {
            text-size: 10;
        }
    }
}

.trailnames {
    [zoom >= 15][highway = 'path'],
    [zoom >= 15][highway = 'cycleway'],
    [zoom >= 15][highway = 'footway'],
    [zoom >= 15][highway = 'bridleway'],
    [zoom >= 15][highway = 'steps'],
    [zoom >= 15][highway = 'pedestrian'] {
        text-name: [name];
        text-face-name: @book-fonts;
        text-fill: @streetnamecolor;
        text-halo-fill: @halocolor;
        text-halo-radius: @haloradius;
        text-spacing: 300;
        text-placement: line;
        text-max-char-angle-delta: 40;
        text-size: 9;
    }
}

#shields-very-low-zoom {
    [zoom >= 7][zoom < 10] {
        shield-file: url('/srv/shields/[route_shield]');
        shield-face-name: @bold-fonts;
        shield-placement: line;
        shield-min-distance: 35;
        shield-spacing: 500;
    }
}

#shields-low-zoom {
    [zoom >= 10][zoom < 13][highway = 'motorway'],
    [zoom >= 11][zoom < 13][highway = 'trunk'],
    [zoom >= 11][zoom < 13][highway = 'primary'],
    [zoom >= 12][zoom < 13][highway = 'secondary'] {
        shield-name: [ref];
        shield-file: url('custom-symbols/shield-black-[length].png');
        shield-face-name: @bold-fonts;
        shield-placement: line;
        shield-min-distance: 35;
        shield-spacing: 500;
        shield-size: 10;
        shield-fill: white;
        shield-dy: -1;
        [route_shield != ''] {
            shield-name: '';
            shield-file: url('/srv/shields/[route_shield]');
        }
    }
}

#shields-20px {
    [zoom >= 13][zoom < 15][highway = 'motorway'],
    [zoom >= 13][zoom < 15][highway = 'trunk'],
    [zoom >= 13][zoom < 15][highway = 'primary'],
    [zoom >= 13][zoom < 15][highway = 'secondary'],
    [zoom >= 13][zoom < 15][highway = 'tertiary'] {
        shield-name: [ref];
        shield-file: url('custom-symbols/shield-black-[length].png');
        shield-face-name: @bold-fonts;
        shield-placement: line;
        shield-min-distance: 35;
        shield-spacing: 500;
        shield-size: 10;
        shield-fill: white;
        shield-dy: -1;
        [route_shield != ''] {
            shield-name: '';
            shield-file: url('/srv/shields/[route_shield]');
        }
    }
}

#shields-24px {
    [zoom >= 15] {
        shield-name: [ref];
        shield-file: url('custom-symbols/shield-black-[length].png');
        shield-face-name: @bold-fonts;
        shield-placement: line;
        shield-min-distance: 35;
        shield-spacing: 500;
        shield-size: 10;
        shield-fill: white;
        shield-dy: -1;
        [route_shield != ''] {
            shield-name: '';
            shield-file: url('/srv/shields/[route_shield]');
        }
    }
}

#water-line-names {
    [zoom >= 12][waterway = 'river'],
    [zoom >= 12][waterway = 'canal'][disused != 'yes'],
    [zoom >= 14][waterway = 'canal'],
    [zoom >= 14][waterway = 'derelict_canal'],
    [zoom >= 14][waterway = 'stream'],
    [zoom >= 14][waterway = 'drain'],
    [zoom >= 14][waterway = 'ditch'],
    [zoom >= 14][waterway = 'brook'] {
        text-name: [name];
        text-face-name: @book-fonts;
        text-fill: @waterlinecolor;
        text-halo-radius: @haloradius;
        text-halo-fill: @halocolor;
        text-placement: line;
        text-max-char-angle-delta: 35;
        text-size: 9;
        [zoom >= 14] { text-size: 10; }
    }
}

#water-area-names {
    [natural = 'water'][waterway != 'riverbank'],
    [landuse = 'reservoir'][waterway != 'riverbank'] {
        [zoom >= 10][zoom < 12][way_area > 4000000],
        [zoom >= 12][zoom < 14][way_area > 1000000],
        [zoom >= 14] {
            text-name: [name];
            text-face-name: @oblique-fonts;
            text-fill: @waterlinecolor;
            text-halo-radius: @haloradius;
            text-halo-fill: @halocolor;
            text-size: 10;
            [zoom >= 14] { text-size: 11; }
        }
    }
}

.featurenames {
    [zoom >= 14][feature = 'natural_peak'] {
        text-name: [name];
        text-face-name: @book-fonts;
        text-size: 11;
        text-wrap-width: 100;
        text-fill: @contourcolor;
        text-halo-fill: @halocolor;
        text-halo-radius: @haloradius;
        text-dy: 10;
        b/text-name: [ele_w_unit];
        b/text-face-name: @book-fonts;
        b/text-size: 10;
        b/text-wrap-width: 100;
        b/text-fill: @contourcolor;
        b/text-halo-fill: @halocolor;
        b/text-halo-radius: @haloradius;
        b/text-dy: 22;
    }

    [zoom >= 13][feature = 'aeroway_aerodrome'] {
        text-name: [name];
        text-face-name: @book-fonts;
        text-size: 10;
        text-wrap-width: 150;
        text-fill: @transportationcolor;
        text-halo-fill: @halocolor;
        text-halo-radius: @haloradius;
        text-dy: 10;
    }

    [zoom >= 15][feature = 'railway_station'] {
        text-name: [name];
        text-face-name: @book-fonts;
        text-size: 10;
        text-wrap-width: 150;
        text-fill: @transportationcolor;
        text-halo-fill: @halocolor;
        text-halo-radius: @haloradius;
        text-dy: 10;
    }

    [feature = 'leisure_nature_reserve'],
    [feature = 'boundary_national_park'],
    [feature = 'natural_wood'],
    [feature = 'leisure_park'],
    [feature = 'leisure_common'],
    [feature = 'leisure_playground'],
    [feature = 'leisure_garden'],
    [feature = 'leisure_golf_course'],
    [feature = 'landuse_forest'],
    [feature = 'landuse_vineyard'],
    [feature = 'landuse_conservation'],
    [feature = 'landuse_recreation_ground'],
    [feature = 'leisure_recreation_ground'],
    [feature = 'landuse_village_green'],
    [feature = 'landuse_allotments'] {
        [zoom >=  8][zoom < 10][way_area > 50000000],
        [zoom >= 10][zoom < 12][way_area >  5000000],
        [zoom >= 12][zoom < 14][way_area >   200000],
        [zoom >= 14] {
            text-name: [name];
            text-face-name: @oblique-fonts;
            text-wrap-width: 20;
            text-fill: @naturecolortext;
            text-halo-fill: @halocolor;
            text-halo-radius: @haloradius;
            text-size: 12;
            [zoom >=  8][zoom < 10] { text-size:  9; }
            [zoom >= 10][zoom < 12] { text-size: 10; }
            [zoom >= 12][zoom < 14] { text-size: 11; }
        }
    }

    [feature = 'landuse_residential'] {
        [zoom >= 13][zoom < 14][way_area >  2000000],
        [zoom >= 14][zoom < 15][way_area >   200000],
        [zoom >= 15] {
            text-name: [name];
            text-face-name: @oblique-fonts;
            text-wrap-width: 20;
            text-fill: @residentialcolortext;
            text-halo-fill: @halocolor;
            text-halo-radius: @haloradius;
            text-size: 11;
            [zoom >= 13][zoom < 14] { text-size:  9; }
            [zoom >= 14][zoom < 15] { text-size: 10; }
        }
    }

    [feature = 'amenity_university'],
    [feature = 'amenity_college'],
    [feature = 'amenity_school'] {
        [zoom >= 13][zoom < 14][way_area >  2000000],
        [zoom >= 14][zoom < 15][way_area >   200000],
        [zoom >= 15] {
            text-name: [name];
            text-face-name: @oblique-fonts;
            text-wrap-width: 20;
            text-fill: @schoolcolortext;
            text-halo-fill: @halocolor;
            text-halo-radius: @haloradius;
            text-size: 11;
            [zoom >= 13][zoom < 14] { text-size:  9; }
            [zoom >= 14][zoom < 15] { text-size: 10; }
        }
    }

    [feature = 'landuse_commercial'],
    [feature = 'landuse_retail'],
    [feature = 'amenity_hospital'] {
        [zoom >= 13][zoom < 14][way_area >  2000000],
        [zoom >= 14][zoom < 15][way_area >   200000],
        [zoom >= 15] {
            text-name: [name];
            text-face-name: @oblique-fonts;
            text-wrap-width: 20;
            text-fill: @commercialcolortext;
            text-halo-fill: @halocolor;
            text-halo-radius: @haloradius;
            text-size: 11;
            [zoom >= 13][zoom < 14] { text-size:  9; }
            [zoom >= 14][zoom < 15] { text-size: 10; }
        }
    }

    [feature = 'landuse_industrial'],
    [feature = 'landuse_railway'],
    [feature = 'landuse_brownfield'],
    [feature = 'landuse_landfill'],
    [feature = 'landuse_quarry'] {
        [zoom >= 13][zoom < 14][way_area >  2000000],
        [zoom >= 14][zoom < 15][way_area >   200000],
        [zoom >= 15] {
            text-name: [name];
            text-face-name: @oblique-fonts;
            text-wrap-width: 20;
            text-fill: @industrialcolortext;
            text-halo-fill: @halocolor;
            text-halo-radius: @haloradius;
            [feature = 'landuse_quarry'][zoom >= 15] { text-dy: 10; text-wrap-width: 100; }
            text-size: 11;
            [zoom >= 13][zoom < 14] { text-size:  9; }
            [zoom >= 14][zoom < 15] { text-size: 10; }
        }
    }
}

.icons {
    [feature = 'natural_peak'] {
        [zoom >= 13] {
            point-file: url('custom-symbols/peak.svg');
            point-transform: scale(6, 6);
        }
    }

    [feature = 'power_tower'] {
        [zoom >= 13] {
            point-file: url('custom-symbols/power-tower.svg');
            point-allow-overlap: true;
            [zoom >= 13][zoom < 14] { point-transform: scale(2, 2); }
            [zoom >= 14][zoom < 15] { point-transform: scale(3, 3); }
            [zoom >= 15]            { point-transform: scale(4, 4); }
        }
    }

    [feature = 'aeroway_aerodrome'] {
        [zoom >= 12] {
            point-file: url('custom-symbols/black-svg/airport.svg');
            [zoom >= 12][zoom < 14] { point-transform: scale(0.4, 0.4); }
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'railway_station'],
    [feature = 'railway_halt'],
    [feature = 'railway_tram_station'],
    [feature = 'aerialway_station'] {
        [zoom >= 14] {
            point-file: url('custom-symbols/rail-station.svg');
            [zoom >= 14][zoom < 15] { point-transform: scale( 6,  6); }
            [zoom >= 15]            { point-transform: scale(10, 10); }
        }
    }

    [feature = 'tourism_alpine_hut'] {
        [zoom >= 13] {
            point-file: url('custom-symbols/black-svg/hut.svg');
            [zoom >= 13][zoom < 14] { point-transform: scale(0.4, 0.4); }
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'amenity_shelter'] {
        [zoom >= 13] {
            point-file: url('custom-symbols/black-svg/shelter.svg');
            [zoom >= 13][zoom < 14] { point-transform: scale(0.4, 0.4); }
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'amenity_parking'][access != 'destination'][access != 'private'][access != 'no'][access != 'unknown'] {
        [zoom >= 13] {
            point-file: url('custom-symbols/black-svg/parking.svg');
            [zoom >= 13][zoom < 14] { point-transform: scale(0.4, 0.4); }
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'tourism_viewpoint'] {
        [zoom >= 13] {
            point-file: url('custom-symbols/black-svg/view.svg');
            [zoom >= 13][zoom < 14] { point-transform: scale(0.4, 0.4); }
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'amenity_toilets'],
    [feature = 'amenity_restrooms'] {
        [zoom >= 14] {
            point-file: url('custom-symbols/black-svg/restrooms.svg');
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'tourism_camp_site'] {
        [zoom >= 14] {
            point-file: url('custom-symbols/black-svg/campground.svg');
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'tourism_information'] {
        [zoom >= 14] {
            point-file: url('custom-symbols/black-svg/info.svg');
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'amenity_drinking_water'] {
        [zoom >= 14] {
            point-file: url('custom-symbols/black-svg/water.svg');
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'tourism_picnic_site'] {
        [zoom >= 14] {
            point-file: url('custom-symbols/black-svg/picnic-area.svg');
            [zoom >= 14][zoom < 15] { point-transform: scale(0.5, 0.5); }
            [zoom >= 15]            { point-transform: scale(0.6, 0.6); }
        }
    }

    [feature = 'landuse_quarry'] {
        [zoom >= 15] {
            point-file: url('custom-symbols/black-svg/mine.svg');
            point-transform: scale(0.6, 0.6);
        }
    }
}
