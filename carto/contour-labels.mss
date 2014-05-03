Map {
    background-color: @mapcolor;
}

#contours {
    [zoom >= 11][class = 3] {
        text-name: "[height]";
        text-face-name: @book-fonts;
        text-fill: @contourcolor;
        text-placement: line;
        text-halo-fill: @halocolor;
        text-min-distance: 100;
        text-max-char-angle-delta: 30;
        [zoom < 12] {
            text-size: 8;
            text-halo-radius: 2;
        }
        [zoom >= 12][zoom < 13] {
            text-size: 9;
            text-halo-radius: 3;
        }
    }
    [zoom >= 13][class = 3],
    [zoom >= 13][class = 2] {
        text-size: 9;
        text-halo-radius: 3;
        text-spacing: 550;
        text-name: "[height]";
        text-face-name: @book-fonts;
        text-fill: @contourcolor;
        text-placement: line;
        text-halo-fill: @halocolor;
        text-min-distance: 100;
        text-max-char-angle-delta: 30;
    }
    [zoom >= 16][class = 1] {
        text-size: 8;
        text-halo-radius: 2;
        text-spacing: 750;
        text-name: "[height]";
        text-face-name: @book-fonts;
        text-fill: @contourcolor;
        text-placement: line;
        text-halo-fill: @halocolor;
        text-min-distance: 100;
        text-max-char-angle-delta: 30;
    }
}
