Map {
    background-color: @mapcolor;
}

#contours-medium [zoom >= 13][zoom < 15] {
    text-size: 8;
    text-halo-radius: 2;
    text-name: "[ele_ft]";
    text-face-name: @book-fonts;
    text-fill: @contourcolor;
    text-placement: line;
    text-halo-fill: @halocolor;
    text-min-distance: 100;
    text-max-char-angle-delta: 30;
}
#contours-high [zoom >= 15] {
    text-size: 9;
    text-halo-radius: 3;
    text-spacing: 550;
    text-name: "[ele_ft]";
    text-face-name: @book-fonts;
    text-fill: @contourcolor;
    text-placement: line;
    text-halo-fill: @halocolor;
    text-min-distance: 100;
    text-max-char-angle-delta: 30;
}
