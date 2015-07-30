def col_labels(df):
    """ Calculate column labels. (internal)
    
    Usage:
    col_labels(df)
    
    Argumments:
    df:         data frame produced by prodcalc()
    
    """
    
def colour_level():
    """ For ggplot2: colour by weight.[sic] """
    
def colour_weight():
    """ For ggplot2: colour by weight."""
    
def ddecker(direction = "h"):
    """ Template for a double decker plot.
    
    A double decker plot is composed of a sequence of spines in the same
    direction, with the final spine in the opposite direction.
    
    Usage: 
    ddecker(direction = "h")
    
    Arguments:
    direction:  direction of first split
    
    """
    
def find_col_level(df):
    """ Find the first level which has columns.
    
    Returns None if no columns at any level.
    
    Usage:
    find_col_level(df)
    
    Arguments:
    df:         data frame of rectangle positions
    
    """
    
def find_row_level(df):
    """ Find the first level which has rows.
    
    Returns None if no rowsat any level.
    
    Usage:
    find_row_level(df)
    
    Arguments:
    df:         data frame of rectangle positions
    
    """
    
def fluct(data, bounds, offset=0.05, max = None):
    """ Fluctation partitioning.
    
    Usage:
    fluct(data, bounds, offset = 0.05, max = None
    
    Arguments:
    data:       bounds data frame
    bounds:     bounds of space to partition
    offset:     space between spines
    max:        maximum value
    
    """
    
def flucts(direction = "h"):
    """ Template for a fluctuation diagram.
    
    Usage:
    flucts(direction = "h")
    
    Arguments:
    direction:  direction of first split
    
    """
    
def hbar(data, bounds, offset = 0.02, max = None):
    """ Horizontal bar partition: width constant, height varies.
    
    Usage:
    hbar(data, bounds, offset = 0.02, max = None)
    
    Arguments:
    data:       bounds data frame
    bounds:     bounds of space to partition
    offset:     space between spines
    max:        maximum value
    
    """

def hspine(data, bounds, offset = 0.01, max = None):
    """ Horizontal spine partition: height constant, width varies.
    
    Usage: 
    hspine(data, bounds, offset = 0.01, max = None)

    Arguments:
    data:       bounds data frame
    bounds:     bounds of space to partition
    offset:     space between spines
    max:        maximum value
    
    """

def mosaic(direction = "h"):
    """ Template for a mosaic plot. 
    
    A mosaic plot is composed of spines in alternating directions.
    
    Usage:
    mosaic(direction = "h")
    
    Arguments:
    direction:  direction of first split

    """
    
def nested(direction = "h"):
    """Template for a nested barchart.
    
    A nested bar is just a sequence of bars in the same direction.
    
    Usage:
    nested(direction = "h")
    
    Arguments:
    direction:  direction of first split
    
    """

def parse_product_formula(f):
    """ Parse product formula into component pieces. (internal)

    Usage:
    parse_product_formula(f)
    
    Arguments:
    f:          formula to parse into component pieces
    
    """
    
def prodcalc(data, formula, divider = mosaic(), cascade = 0,
    scale_max = True, na.rm = False):
    """ Calculate frequencies. (internal)
    
    Usage:
    prodcalc(data, formula, divider = mosaic(), cascade = 0,
        scale_max = True, na.rm = False)

    Arguments:
    data:       input data frame}
    formula:    formula specifying display of plot
    divider:    divider function
    cascade:    cascading amount, per nested layer
    scale_max:  Logical vector of length 1. If True, maximum values within 
                each nested layer will be scaled to take up all available 
                space. If False, areas will be comparable between nested
                layers.
    na.rm:      Logical vector of length 1 - should missing levels be 
                silently removed?
                
    R Examples:
    prodcalc(happy, ~ happy, "hbar")
    prodcalc(happy, ~ happy, "hspine")
    
    """

def prodplot(data, formula, divider = mosaic(), cascade = 0,
    scale_max = True, na.rm = True, levels = -1L, ...)
    """ Create a product plot.
    
    Usage:
    prodplot(data, formula, divider = mosaic(), cascade = 0,
        scale_max = True, na.rm = False, levels = -1L, ...)
        
    Arguments:
    data:       input data frame
    formula:    formula specifying display of plot
    divider:    divider function
    cascade:    cascading amount, per nested layer
    scale_max:  Logical vector of length 1. If True, maximum values within 
                each nested layer will be scaled to take up all available 
                space.  If False, areas will be comparable between nested
                layers.
    na.rm:      Logical vector of length 1 - should missing levels be 
                silently removed?
    levels:     an integer vector specifying which levels to draw.
    
    R examples:
    prodplot(happy, ~ happy, "hbar")
    prodplot(happy, ~ happy, "hspine")

    prodplot(happy, ~ sex + happy, c("vspine", "hbar"))
    prodplot(happy, ~ sex + happy, stacked())

    # The levels argument can be used to extract a given level of the plot
    prodplot(happy, ~ sex + happy, stacked(), level = 1)
    prodplot(happy, ~ sex + happy, stacked(), level = 2)

    """
    
def row_labels(df):
    """ Calculate row labels. (internal)
    
    Usage:
    row_labels(df)

    Arguments:
    df:         data frame produced by prodcalc()
    
    """

def scale_x_product(df):
    """ Generate an x-scale for ggplot2 graphics.

    Usage:
    scale_x_product(df)

    Arguments:
    df:         data frame produced by prodcalc()
    
    """
    
def scale_y_product(df):
    """ Generate a y-scale for ggplot2 graphics.
    
    Usage:
    scale_y_product(df)
    
    Arguments:
    df:         data frame produced by prodcalc()
    
    """
    
def spine(data, bounds, offset = 0.01, max = None):
    """ Spine partition: divide longest dimesion.
    
    Usage:
    spine(data, bounds, offset = 0.01, max = None)
    
    Arguments:
    data:       bounds data frame
    bounds:     bounds of space to partition
    offset:     space between spines
    max:        maximum value
    
    """
    
def stacked(direction = "h"):
    """ Template for a stacked bar chart.
    
    A stacked bar chart starts with a bar and then continues with spines in 
    the opposite direction.
    
    Usage:
    stacked(direction = "h")

    Arguments:
    direction:  direction of first split
    
    """

def tile(data, bounds, max = 1):
    """ Tree map partitioning.}

    Adapated from SquarifiedLayout in
    http://www.cs.umd.edu/hcil/treemap-history/Treemaps-Java-Algorithms.zip
    
    Usage:
    tile(data, bounds, max = 1)
    
    Arguments:
    data:       bounds data frame
    bounds:     bounds of space to partition
    max:        maximum value
    
    """
    
def vbar(data, bounds, offset = 0.02, max = None):
    """ Vertical bar partition: height constant, width varies.
    
    Usage:
    vbar(data, bounds, offset = 0.02, max = None)
    
    Arguments:
    data:       bounds data frame
    bounds:     bounds of space to partition
    offset:     space between spines
    max:        maximum value
    
    """

def vspine(data, bounds, offset = 0.01, max = None):
    """ Vertical spine partition: width constant, height varies.
    
    Usage:
    vspine(data, bounds, offset = 0.01, max = None)
    
    Arguments:
    data:       bounds data frame
    bounds:     bounds of space to partition
    offset:     space between spines
    max:        maximum value
    
    """

