Map {
    background-color: transparent;
}

/*
Contours are generally grouped into three classes:
 * Index contours.  Periodically spaced, thicker, labeled.
 * Intermediate contours.  Thinner, not normally labeled.
 * Supplementary contours.  Thinner, dashed, only present in flatter areas.

I didn't like the way the dashed ones looked, so this just does a
two-tiered system.  The index and intermediate contours roughly double
their intervals on alternate zoom levels.  Here's what I mean:
  
  | Zoom | Index | Inter. | Ratio |
  |------+-------+--------+-------|
  |   10 |       |    200 |       |
  |   11 |   500 |    100 |   1:5 |
  |   12 |   500 |     50 |  1:10 |
  |   13 |   250 |     50 |   1:5 |
  |   14 |   250 |     25 |  1:10 |
  |   15 |   100 |     20 |   1:5 |
  |   16 |   100 |     10 |  1:10 |

Note that the zoom 11 and 12 index contours are the same weight as the
intermediate contours.  That's because they're not labeled, and they
looked kind of weird being set apart without labels.

*/

#contours-verylow {
    [zoom = 10] {
        line-color: @contourcolor;
        line-width: 0.2;
    }
}
#contours-low {
    [zoom = 11] {
        [class = 3], [class = 2] {
            line-color: @contourcolor;
            [class = 3] { line-width: 0.2; }
            [class = 2] { line-width: 0.2; }
        }
    }
    [zoom = 12] {
        line-color: @contourcolor;
        [class = 3] { line-width: 0.2; }
        [class = 2] { line-width: 0.2; }
        [class = 1] { line-width: 0.2; }
    }
}
#contours-medium {
    [zoom = 13] {
        [class = 3], [class = 2] {
            line-color: @contourcolor;
            [class = 3] { line-width: 0.5; }
            [class = 2] { line-width: 0.2; }
        }
    }
    [zoom = 14] {
        line-color: @contourcolor;
        [class = 3] { line-width: 0.5; }
        [class = 2] { line-width: 0.2; }
        [class = 1] { line-width: 0.2; }
    }
}
#contours-high {
    [zoom = 15] {
        [class = 3], [class = 2] {
            line-color: @contourcolor;
            [class = 3] { line-width: 0.5; }
            [class = 2] { line-width: 0.2; }
        }
    }
    [zoom >= 16] {
        line-color: @contourcolor;
        [class = 3] { line-width: 0.5; }
        [class = 2] { line-width: 0.2; }
        [class = 1] { line-width: 0.2; }
    }
}
