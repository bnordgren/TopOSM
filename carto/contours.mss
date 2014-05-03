Map {
    background-color: transparent;
}

#contours {
    [zoom >= 10][zoom < 11] {
        [class = 3] {
            line-color: @contourcolor;
            line-width: 0.2;
        }
    }
    [zoom >= 11][zoom < 13] {
        [class = 3] {
            line-color: @contourcolor;
            line-width: 0.4;
        }
        [class = 2] {
            line-color: @contourcolor;
            line-width: 0.2;
        }
    }
    [zoom >= 13][zoom < 14] {
        [class = 2], [class = 3] {
            line-color: @contourcolor;
            line-width: 0.4;
        }
        [class = 1] {
            line-color: @contourcolor;
            line-width: 0.15;
        }
    }
    [zoom >= 14] {
        [class = 2], [class = 3] {
            line-color: @contourcolor;
            line-width: 0.5;
        }
        [class = 1] {
            line-color: @contourcolor;
            line-width: 0.2;
        }
    }
}
