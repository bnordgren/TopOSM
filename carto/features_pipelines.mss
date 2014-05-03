#pipelines {
    ::main[zoom >= 13] {
        line-color: @pipelinecolor;
        [zoom >= 13][zoom < 14] {
            line-width: 1;
        }
        [zoom >= 14][zoom < 15] {
            line-width: 1.5;
        }
        [zoom >= 15] {
            line-width: 2;
        }
    }
    ::underground[zoom >= 13] {
        [location = 'underground'],
        [location = 'underwater'],
        [location != ''] {
            line-color: @pipelinecolor;
            [zoom >= 13][zoom < 14] {
                line-width: 2;
                line-dasharray: 2,15;
            }
            [zoom >= 14][zoom < 15] {
                line-width: 3;
                line-dasharray: 3,20;
            }
            [zoom >= 15] {
                line-width: 4;
                line-dasharray: 4,28;
            }
        }
    }
}