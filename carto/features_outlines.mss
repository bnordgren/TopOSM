Map {
    background-color: transparent;
}

#ferry-routes {
    [zoom >= 8][route = 'ferry'] {
        line-color: @waterlinecolor;
        [zoom >= 8][zoom < 11] {
            line-width: 0.4;
            line-dasharray: 4,4;
        }
        [zoom >= 11] {
            line-width: 0.8;
            line-dasharray: 6,6;
        }
    }
}

#buildings {
    [zoom >= 12] {
        polygon-fill: black;
        polygon-opacity: 0.6;
    }
}