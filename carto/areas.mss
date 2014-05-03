Map {
    background-color: transparent;
}

#builtup[zoom >= 8] {
    polygon-fill: @builtupcolor;
    polygon-opacity: @areaopacity;
}

#areafills {
    [zoom >= 8][landuse = 'residential'] {
        polygon-fill: @builtupcolor;
        polygon-opacity: @areaopacity;
    }
    [zoom >= 8][leisure = 'nature_reserve'],
    [zoom >= 8][leisure = 'park'],
    [zoom >= 8][leisure = 'common'],
    [zoom >= 8][leisure = 'playground'],
    [zoom >= 8][leisure = 'garden'],
    [zoom >= 8][leisure = 'golf_course'],
    [zoom >= 8][landuse = 'forest'],
    [zoom >= 8][landuse = 'vineyard'],
    [zoom >= 8][landuse = 'conservation'],
    [zoom >= 8][landuse = 'recreation_ground'],
    [zoom >= 8][leisure = 'recreation_ground'],
    [zoom >= 8][landuse = 'village_green'],
    [zoom >= 8][landuse = 'allotment'] {
        polygon-fill: @naturecolor;
        polygon-opacity: @areaopacity;
    }

    [zoom >= 10][landuse = 'cemetery'],
    [zoom >= 10][amenity = 'grave_yard'] {
        polygon-fill: #8b8;
        polygon-opacity: @areaopacity;
    }

    [zoom >= 10][landuse = 'construction'] {
        polygon-fill: #bb3;
        polygon-opacity: @areaopacity;
    }
    [zoom >= 8][landuse = 'military'] {
        polygon-fill: #e55;
        polygon-opacity: @areaopacity;
    }
    [zoom >= 10][natural = 'beach'] {
        polygon-fill: #fec;
        polygon-opacity: @areaopacity;
    }
    [zoom >= 8][landuse = 'salt_pond'] {
        polygon-fill: #abc;
        polygon-opacity: @areaopacity;
    }
    [zoom >= 10][natural = 'glacier'] {
        polygon-fill: #cde;
        polygon-opacity: @areaopacity;
    }
    [zoom >= 10][natural = 'heath'],
    [zoom >= 10][landuse = 'meadow'],
    [zoom >= 10][landuse = 'farm'],
    [zoom >= 10][landuse = 'farmyard'] {
        polygon-fill: #dd3;
        polygon-opacity: @areaopacity;
    }

    // these are basically copied from osm.xml

    [zoom >= 10][landuse = 'industrial'],
    [zoom >= 10][landuse = 'railway'],
    [zoom >= 10][landuse = 'brownfield'],
    [zoom >= 10][landuse = 'landfill'],
    [zoom >= 10][landuse = 'quarry'] {
        polygon-fill: #e69;
        polygon-opacity: @areaopacity;
    }
    [zoom >= 10][landuse = 'commercial'],
    [zoom >= 10][landuse = 'retail'],
    [zoom >= 10][amenity = 'hospital'] {
        polygon-fill: #e96;
        polygon-opacity: @areaopacity;
    }
    [zoom >= 10][amenity = 'university'],
    [zoom >= 10][amenity = 'college'],
    [zoom >= 10][amenity = 'school'] {
        polygon-fill: #aa8;
        polygon-opacity: @areaopacity;
    }
}
