.aeroway-outlines {
    [zoom >= 14][aeroway = 'runway'] {
        line-color: @aerowayoutlinecolor;
        line-cap: square;
        [zoom >= 14][zoom < 15] { line-width: 11.0; }
        [zoom >= 15][zoom < 16] { line-width: 19.0; }
        [zoom >= 16]            { line-width: 33.0; }
    }

    [zoom >= 14][aeroway = 'taxiway'] {
        line-color: @aerowayoutlinecolor;
        line-join: round;
        [zoom >= 14][zoom < 15] { line-width:  5.0; }
        [zoom >= 15][zoom < 16] { line-width:  7.0; }
        [zoom >= 16]            { line-width: 13.0; }
    }
}

.aeroway-fills {
    [zoom >= 11][aeroway = 'runway'] {
        line-color: @aerowaycolor;
        line-cap: square;
        [zoom >= 11][zoom < 12] { line-width:  2.0; }
        [zoom >= 12][zoom < 13] { line-width:  3.0; }
        [zoom >= 13][zoom < 14] { line-width:  5.0; }
        [zoom >= 14][zoom < 15] { line-width:  9.0; }
        [zoom >= 15][zoom < 16] { line-width: 17.0; }
        [zoom >= 16]             { line-width: 30.0; }
    }

    [zoom >= 11][aeroway = 'taxiway'] {
        line-color: @aerowaycolor;
        line-join: round;
        [zoom >= 11][zoom < 12] { line-width:  0.8; }
        [zoom >= 12][zoom < 13] { line-width:  1.0; }
        [zoom >= 13][zoom < 14] { line-width:  2.0; }
        [zoom >= 14][zoom < 15] { line-width:  3.0; }
        [zoom >= 15][zoom < 16] { line-width:  5.0; }
        [zoom >= 16]             { line-width: 10.0; }
    }
}
