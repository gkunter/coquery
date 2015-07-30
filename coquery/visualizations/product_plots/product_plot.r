library(plyr)
library(ggplot2)

# https://github.com/hadley/productplots


#' Calculate frequencies.
#'
#' @param data input data frame
#' @param formula formula specifying display of plot
#' @param divider divider function
#' @param cascade cascading amount, per nested layer
#' @param scale_max Logical vector of length 1. If \code{TRUE} maximum values
#'   within each nested layer will be scaled to take up all available space.
#'   If \code{FALSE}, areas will be comparable between nested layers.
#' @param na.rm Logical vector of length 1 - should missing levels be
#'   silently removed?
#' @keywords internal
#' @export
#' @examples
#' prodcalc(happy, ~ happy, "hbar")
#' prodcalc(happy, ~ happy, "hspine")
prodcalc <- function(data, formula, divider = mosaic(), cascade = 0, scale_max = TRUE, na.rm = FALSE) {
  vars <- parse_product_formula(formula)

  if (length(vars$wt) == 1) {
    data$.wt <- data[[vars$wt]]
  } else {
    data$.wt <- 1
  }

  wt <- margin(data, vars$marg, vars$cond)
  if (na.rm) {
    wt <- wt[complete.cases(wt), ]
  }

  if (is.function(divider)) divider <- divider(ncol(wt) - 1)
  if (is.character(divider)) divider <- llply(divider, match.fun)

  max_wt <- if (scale_max) NULL else 1

  divide(wt, divider = rev(divider), cascade = cascade, max_wt = max_wt)
}
  
### divide.r

divide <- function(data, bounds = bound(), divider = list(hbar), level = 1, cascade = 0, max_wt = NULL) {
  d <- partd(divider[[1]])
  if (ncol(data) == d + 1) {
    return(divide_once(data, bounds, divider[[1]], level, max_wt))
  }

  # In divide we work with the opposite order of variables to margin -
  # so we flip and then flip back
  parent_data <- margin(data, rev(seq_len(d)))
  parent_data <- parent_data[, c(rev(seq_len(d)), d + 1)]

  parent <- divide_once(parent_data, bounds, divider[[1]], level, max_wt)
  parentc <- parent
  parentc$l <- parent$l + cascade
  parentc$b <- parent$b + cascade
  parentc$r <- parent$r + cascade
  parentc$t <- parent$t + cascade

  # browser()
  if (is.null(max_wt)) {
    max_wt <- max(margin(data, d + 1, seq_len(d))$.wt, na.rm = TRUE)
  }

  pieces <- as.list(dlply(data, seq_len(d)))
  children <- ldply(seq_along(pieces), function(i) {
    piece <- pieces[[i]]
    partition <- divide(piece[, -seq_len(d)], parentc[i, ], divider[-1],
      level = level + 1, cascade = cascade, max = max_wt)

    labels <- piece[rep(1, nrow(partition)), 1:d, drop = FALSE]
    cbind(labels, partition)
  })
  rbind.fill(parent, children)
}

# @param data data frame giving partitioning variables and weights.  Final
#   column should be called .wt and contain weights
divide_once <- function(data, bounds, divider, level = 1, max_wt = NULL) {
  d <- partd(divider)
  # Convert into vector/matrix/array for input to divider function
  if (d > 1) {
    data[-ncol(data)] <- lapply(data[-ncol(data)], addNA, ifany = TRUE)
    wt <- tapply(data$.wt, data[-ncol(data)], identity)
    # This ensures that the order of the data matches the order tapply uses
    data <- as.data.frame.table(wt, responseName = ".wt")
  } else {
    wt <- data$.wt
  }

  wt <- prop(wt)
  if (is.null(max_wt)) max_wt <- max(wt, na.rm = TRUE)

  partition <- divider(wt, bounds, max = max_wt)
  cbind(data, partition, level = level)
}
  
### labels.r
  
# Want to label first set of columns and rows.
#
# A block of rectangles occupies a column if they line up with a gap
# (possibly zero width) between them.  Should be within a single level.
#
# A row/column can be created with a bar, fluct, or spine with constant p.
#
# Find r vals of col 1 should be less than l vals of col 2

#' Generate an x-scale for ggplot2 graphics.
#'
#' @param df list of data frame produced by \code{\link{prodcalc}}, formula and divider
#' @export
scale_x_product <- function(df) {
  data <- df$data
  vars <- parse_product_formula(df$formula)

  ## horizontal axis there if dividers contain "h":
  col <- c(vars$cond, vars$marg)[grep("h", df$divider)]
  ##  col <- find_col_level(data)
  if (length(col) == 0) {
    # No columns, so just scatter a few tick marks around
    breaks <- seq(0, 1, length = 5)
#    labels <- rep("", 5)
    scale_x_continuous("", breaks = breaks, labels = round(breaks,2))
  } else {
#    labels <- col_labels(data[data$level == col, ])
    labels <- subset(data, (level = max(level)) & (b==0))
    labels$pos <- with(labels, (l+r)/2)
    labels$label <- ldply(1:nrow(labels), function(x) paste(unlist(labels[x,col]), collapse=":"))$V1
    xlabel <- paste(col, collapse=":")

    scale_x_continuous(xlabel, breaks = labels$pos, labels =labels$label)
  }
}

#' Find the first level which has columns.
#'
#' Returns \code{NA} if no columns at any level.
#' @param df data frame of rectangle positions
#' @export
find_col_level <- function(df) {
  levels <- unique(df$level)
  cols <- sapply(levels, function(i) has_cols(df[df$level == i, ]))

  levels[which(cols)[1]]
}

#' Calculate column labels.
#'
#' @keywords  internal
#' @param df data frame produced by \code{\link{prodcalc}}
#' @export
col_labels <- function(df) {
  vars <- setdiff(names(df), c(".wt", "l", "r", "t", "b", "level"))

  ddply(df, "l", function(df) {
    # If width is constant, draw in the middle, otherwise draw on the left.
    widths <- df$r - df$l
    widths <- widths[widths != 0]
    constant <- length(widths) != 0 &&
      (length(unique(widths)) <= 1 || cv(widths, T) < 0.01)

    if (constant) {
      pos <- df$l[1] + widths[1] / 2
    } else {
      pos <- df$l[1]
    }

    data.frame(pos, label = uniquecols(df[vars])[, 1])
  })
}

has_cols <- function(df) {
  vars <- setdiff(names(df), c(".wt", "l", "r", "t", "b", "level"))

  cols <- ddply(df, "l", function(df) {
    data.frame(r = max(df$r), nvars = ncol(uniquecols(df[vars])))
  })

  n <- nrow(cols)

  # Has colums if:
  #  * more than 1 column
  #  * right boundary of each column less than left boundary of next column
  #  * number of variables in each column is the same
  n > 1 &&
    all(cols$l[-1] >= cols$r[-n]) &&
    length(unique(cols$nvars)) == 1
}

# Functions for rows

#' Generate a y-scale for ggplot2 graphics.
#'
#' @param df list of data frame produced by \code{\link{prodcalc}}, formula and divider
#' @export
# scale_y_product <- function(df) {
#   scale <- scale_x_product(rotate(df))
#   scale$.input <- "y"
#   scale$.output <- "y"
#   scale
# }
scale_y_product <- function(df) {
  data <- df$data
  vars <- parse_product_formula(df$formula)

  ## horizontal axis there if dividers contain "v":
  col <- c(vars$cond, vars$marg)[grep("v", df$divider)]
  ##  col <- find_col_level(data)
  if (length(col) == 0) {
    # No columns, so just scatter a few tick marks around
    breaks <- seq(0, 1, length = 5)
    scale_y_continuous("", breaks = breaks, labels = round(breaks,2))
  } else {
    labels <- subset(data, (level = max(level)) & (l==0))
    labels$pos <- with(labels, (b+t)/2)
    labels$label <- ldply(1:nrow(labels), function(x) paste(unlist(labels[x,col]), collapse=":"))$V1
    ylabel <- paste(col, collapse=":")

    scale_y_continuous(ylabel, breaks = labels$pos, labels =labels$label)
  }
}

#' Find the first level which has rows.
#'
#' Returns \code{NA} if no rows at any level.
#' @param df data frame of rectangle positions
#' @export
find_row_level <- function(df) find_col_level(rotate(df))

#' Calculate row labels.
#'
#' @param df data frame produced by \code{\link{prodcalc}}
#' @keywords  internal
#' @export
row_labels <- function(df) col_labels(rotate(df))
has_rows <- function(df) has_cols(rotate(df))

### margin.r

margin <- function(table, marginals = c(), conditionals = c()) {
  if (is.numeric(marginals))    marginals    <- names(table)[marginals]
  if (is.numeric(conditionals)) conditionals <- names(table)[conditionals]

  marginals <- rev(marginals)
  conditionals <- rev(conditionals)

  marg <- weighted.table(table[c(conditionals, marginals)], table$.wt)

  if (length(conditionals) > 0) {
    # Work around bug in ninteraction
    cond <- marg[conditionals]
    cond[] <- lapply(cond, addNA, ifany = TRUE)
    marg$.wt <- ave(marg$.wt, id(cond), FUN = prop)
  }

  marg$.wt[is.na(marg$.wt)] <- 0
  marg
}

weighted.table <- function(vars, wt = NULL) {
  # If no weight column, give constant weight
  if (is.null(wt)) wt <- prop(rep(1, nrow(vars)))

  # Ensure missing values are counted
  vars[] <- lapply(vars, addNA, ifany = TRUE)

  # Need to reverse order of variables because as.data.frame works in the
  # opposite way to what I want
  sums <- tapply(wt, rev(vars), sum, na.rm = TRUE)

  df <- as.data.frame.table(sums, responseName = ".wt")
  # Missing values represent missing combinations in the original dataset,
  # i.e. they have zero weight
  df$.wt[is.na(df$.wt)] <- 0
  df[, c(rev(seq_len(ncol(df) - 1)), ncol(df)) ]
}

# weighted.table.accurate <- function(vars, wt) {
#   marg2 <- ddply(table, c(conditionals, marginals), function(df) sum(df$.wt), .drop = FALSE)
#   names(marg2)[ncol(marg2)] <- ".wt"
#   margs
# }

### parse.r

#' Parse product formula into component pieces
#'
#' @return
#'   \item{wt}{the weighting variable}
#'   \item{cond}{condition variables}
#'   \item{margin}{margining variables}
#' @param f function to parse into component pieces
#' @keywords internal
#' @export
parse_product_formula <- function(f) {

  # Figure out weighting
  wt <- if (is.binary.op(f)) all.vars(lhs(f)) else character()
  mc <- rhs(f)

  if (identical(op(mc), as.name("|"))) {
    # Has conditioning
    cond <- all.vars(rhs(mc))
    marg <- all.vars(lhs(mc))
  } else {
    cond <- character()
    marg <- all.vars(mc)
  }

  marg <- marg[marg != "."]
  list(wt = wt, marg = marg, cond = cond)
}


lhs <- function(x) {
  stopifnot(is.call(x) || is.name(x))
  if (length(x) == 3) x[[2]]
}

rhs <- function(x) {
  stopifnot(is.call(x) || is.name(x))
  if (length(x) == 2) {
    x[[2]]
  } else if (length(x) == 3) {
    x[[3]]
  }
}
op <- function(x) {
  stopifnot(is.call(x) || is.name(x))
  if (length(x) == 3 || length(x) == 2) x[[1]]
}

is.binary.op <- function(x) {
  (is.call(x)) && length(x) == 3
}

### partition-1d.r

rotate <- function(data) {
  rename(data, c("l" = "b", "r" = "t", "b" = "l", "t" = "r"))
}

#' Spine partition: divide longest dimesion.
#'
#' @param data bounds data frame
#' @param bounds bounds of space to partition
#' @param offset space between spines
#' @param max maximum value
#' @export
spine <- function(data, bounds, offset = 0.01, max = NULL) {
  w <- bounds$r - bounds$l
  h <- bounds$t - bounds$b

  if (w > h) {
    hspine(data, bounds, offset, max)
  } else {
    vspine(data, bounds, offset, max)
  }
}


#' Horizontal spine partition: height constant, width varies.
#'
#' @param data bounds data frame
#' @param bounds bounds of space to partition
#' @param offset space between spines
#' @param max maximum value
#' @export
hspine <- function(data, bounds, offset = 0.01, max = NULL) {
  n <- length(data)
  # n + 1 offsets
  offsets <- c(0, rep(1, n - 1), 0) * offset

  data <- data * (1 - sum(offsets))

  widths <- as.vector(t(cbind(data, offsets[-1])))
  widths[is.na(widths)] <- 0

  pos <- c(offsets[1], cumsum(widths)) / sum(widths)
  locations <- data.frame(
    l = pos[seq(1, 2 * n - 1, by = 2)],
    r = pos[seq(2, 2 * n, by = 2)],
    b = 0,
    t = 1
  )
  squeeze(locations, bounds)
}

#' Vertical spine partition: width constant, height varies.
#'
#' @param data bounds data frame
#' @param bounds bounds of space to partition
#' @param offset space between spines
#' @param max maximum value
#' @export
vspine <- function(data, bounds, offset = 0.01, max = NULL) {
  rotate(hspine(data, rotate(bounds), offset, max = max))
}

#' Horizontal bar partition: width constant, height varies.
#'
#' @param data bounds data frame
#' @param bounds bounds of space to partition
#' @param offset space between spines
#' @param max maximum value
#' @export
hbar <- function(data, bounds, offset = 0.02, max = NULL) {
  if (is.null(max)) max <- 1

  n <- length(data)
  # n + 1 offsets
  offsets <- c(0, rep(1, n - 1), 0) * offset

  width <- (1 - sum(offsets)) / n
  heights <- data / max

  widths <- as.vector(t(cbind(width, offsets[-1])))
  pos <- c(offsets[1], cumsum(widths)) / sum(widths)
  locations <- data.frame(
    l = pos[seq(1, 2 * n - 1, by = 2)],
    r = pos[seq(2, 2 * n, by = 2)],
    b = 0,
    t = heights
  )
  squeeze(locations, bounds)
}

#' Vertical bar partition: height constant, width varies.
#'
#' @param data bounds data frame
#' @param bounds bounds of space to partition
#' @param offset space between spines
#' @param max maximum value
#' @export
vbar <- function(data, bounds, offset = 0.02, max = NULL) {
  rotate(hbar(data, rotate(bounds), offset, max = max))
}

### partition-2d.r


#' Fluctation partitioning.
#'
#' @param data bounds data frame
#' @param bounds bounds of space to partition
#' @param offset space between spines
#' @param max maximum value
#' @export
fluct <- function(data, bounds, offset = 0.05, max = NULL) {
  if (is.null(max)) max <- 1

  # Size should be number between 0 and 1, reflecting total amount of cell to
  # take up
  sizes <- sqrt(data / max) * (1 - offset)

  l <- (col(data) - 1) / ncol(data)
  b <- (row(data) - 1) / nrow(data)
  width <- sizes / ncol(data)
  height <- sizes / nrow(data)

  locations <- data.frame(
    l = as.vector(l),
    b = as.vector(b),
    r = as.vector(l + width),
    t = as.vector(b + height)
  )
  squeeze(locations, bounds)

}
attr(fluct, "d") <- 2


### partition-tile.r

#' Tree map partitioning.
#'
#' Adapated from SquarifiedLayout in
#' \url{http://www.cs.umd.edu/hcil/treemap-history/Treemaps-Java-Algorithms.zip}
#' @param data bounds data frame
#' @param bounds bounds of space to partition
#' @param max maximum value
#' @export
tile <- function(data, bounds, max = 1) {
  if (length(data) == 0) return()
  if (length(data) <= 2) {
    return(spine(data, bounds, offset = 0))
  }

  h <- bounds$t - bounds$b
  w <- bounds$r - bounds$l
  x <- bounds$l
  y <- bounds$b

  mid <- 1

  a <- data[1]
  b <- a

  if (w < h) { # Tall and skinny
    while (mid <= length(data)) {
      q <- data[mid]

      if (normAspect(h, w, a, b + q) > normAspect(h, w, a, b)) break
      mid <- mid + 1
      b <- b + q
    }

    b <- sum(data[(1:mid)])
    rbind(
      spine(prop(data[1:mid]),   bound(y + h * b, x + w, y, x), offset = 0),
      tile(prop(data[-(1:mid)]), bound(y + h, x + w, y + h * b, x)))

  } else {  # Short and fat
    while (mid <= length(data)) {
      q <- data[mid]
      if (normAspect(w, h, a, b + q) > normAspect(w, h, a, b)) break
      mid <- mid + 1
      b <- b + q
    }

    b <- sum(data[-(1:mid)])
    rbind(
      spine(prop(data[1:mid]),   bound(y + h, x + w,     y, x + w * b), offset = 0),
      tile(prop(data[-(1:mid)]), bound(y + h, x + w * b, y, x)))
  }
}

normAspect <- function(big, small, a, b) {
  aspect <- (big * b) / (small * a / b)
  max(aspect, 1 / aspect)
}

### partition.r

partd <- function(x) {
  d <- attr(x, "d")
  if (!is.null(d)) d else 1
}

add_area <- function(df) {
  df$area <- (df$r - df$l) * (df$t - df$b)
  df
}

# Squeeze pieces to lie within specified bounds
squeeze <- function(pieces, bounds = bound()) {
  scale_x <- function(x) x * (bounds$r - bounds$l) + bounds$l
  scale_y <- function(y) y * (bounds$t - bounds$b) + bounds$b

  pieces$l <- scale_x(pieces$l)
  pieces$r <- scale_x(pieces$r)
  pieces$b <- scale_y(pieces$b)
  pieces$t <- scale_y(pieces$t)
  pieces
}

# Convenience function to create bounds
bound <- function(t = 1, r = 1, b = 0, l = 0) {
  data.frame(t = t, r = r, b = b, l = l)
}


set_offset <- function(dividers, offset = 0) {
  if (length(offset) < length(dividers)) {
    offset <- rep(offset, length = length(dividers))
  }

  lapply(seq_along(dividers), function(i) {
    div <- dividers[[i]]
    if (is.character(div)) div <- match.fun(div)
    f <- function(...) div(..., offset = offset[[i]])
    mostattributes(f) <- attributes(div)
    f
  })
}
  
### plot.r

#' Create a product plot
#'
#' @param data input data frame
#' @param formula formula specifying display of plot
#' @param divider divider function
#' @param cascade cascading amount, per nested layer
#' @param scale_max Logical vector of length 1. If \code{TRUE} maximum values
#'   within each nested layer will be scaled to take up all available space.
#'   If \code{FALSE}, areas will be comparable between nested layers.
#' @param na.rm Logical vector of length 1 - should missing levels be
#'   silently removed?
#' @param levels an integer vector specifying which levels to draw.
#' @param ... other arguments passed on to \code{draw}
#' @export
#' @examples
#' if (require("ggplot2")) {
#' prodplot(happy, ~ happy, "hbar")
#' prodplot(happy, ~ happy, "hspine")
#'
#' prodplot(happy, ~ sex + happy, c("vspine", "hbar"))
#' prodplot(happy, ~ sex + happy, stacked())
#'
#' # The levels argument can be used to extract a given level of the plot
#' prodplot(happy, ~ sex + happy, stacked(), level = 1)
#' prodplot(happy, ~ sex + happy, stacked(), level = 2)
#' }
prodplot <- function(data, formula, divider = mosaic(), cascade = 0, scale_max = TRUE, na.rm = FALSE, levels = -1L, ...) {
  require("ggplot2")

  vars <- parse_product_formula(formula)
  p <- length(c(vars$cond, vars$marg))

  if (is.function(divider)) divider <- divider(p)
  div_names <- divider
  if (is.character(divider)) divider <- llply(divider, match.fun)


  res <- prodcalc(data, formula, divider, cascade, scale_max, na.rm = na.rm)
  if (!(length(levels) == 1 && is.na(levels))) {
    levels[levels < 0] <-  max(res$level) + 1 + levels[levels < 0]
    res <- res[res$level %in% levels, ]
  }

  print(list(data=res, formula=formula, divider=div_names))
  draw(list(data=res, formula=formula, divider=div_names), ...)
}

draw <- function(df, alpha = 1, colour = "grey30", subset = NULL) {
  require("ggplot2")
  data <- df$data
  print(data)
  plot <- ggplot(data,
    aes_string(xmin = "l", xmax = "r", ymin = "b", ymax = "t")) +
    scale_y_product(df) +
    scale_x_product(df)

  levels <- split(data, data$level)
  for (level in levels) {
    plot <- plot + geom_rect(data = level, colour = colour, alpha = alpha)
  }

  plot
}

#' For ggplot2: colour by weight.
#'
#' @keywords internal hplot
#' @export
colour_weight <- function() {
  require("ggplot2")
  list(
    aes_string(fill = ".wt"),
    scale_fill_gradient("Weight", low = "grey80", high = "black"))
}

#' For ggplot2: colour by weight.
#'
#' @keywords internal hplot
#' @export
colour_level <- function() {
  require("ggplot2")
  list(
    aes_string(fill = "factor(level)"),
    scale_fill_brewer("Level", pal = "Blues"))
}
  
### productplots.r

#' Data related to happiness from the general social survey.
#'
#' The data is a small sample of variables related to happiness from the
#' general social survey (GSS). The GSS is a yearly cross-sectional survey of
#' Americans, run from 1976. We combine data for 25 years to yield 51,020
#' observations, and of the over 5,000 variables, we select nine related to
#' happiness:
#'
#' \itemize{
#'  \item age. age in years: 18--89.
#'  \item degree. highest education: lt high school, high school, junior
#'     college, bachelor, graduate.
#'  \item finrela. relative financial status: far above, above average,
#'     average, below average, far below.
#'  \item happy. happiness: very happy, pretty happy, not too happy.
#'  \item health. health: excellent, good, fair, poor.
#'  \item marital. marital status:  married, never married, divorced,
#'    widowed, separated.
#'  \item sex. sex: female, male.
#'  \item wtsall. probability weight. 0.43--6
#' }
#'
#' @docType data
#' @keywords datasets
#' @name happy
#' @usage data(happy)
#' @format A data frame with 51020 rows and 10 variables
NULL

#' @import plyr
NULL

### templates.r

.directions <- c("vertical", "horizontal")

#' Template for a mosaic plot.
#' A mosaic plot is composed of spines in alternating directions.
#'
#' @param direction direction of first split
#' @export
mosaic <- function(direction = "v") {
  direction <- match.arg(direction, .directions)
  if (direction == "horizontal") {
    splits <- c("hspine", "vspine")
  } else {
    splits <- c("vspine", "hspine")
  }

  function(n) rep(splits, length = n)
}

#' Template for a stacked bar chart.
#' A stacked bar chart starts with a bar and then continues with spines in the
#' opposite direction.
#'
#' @param direction direction of first split
#' @export
stacked <- function(direction = "h") {
  direction <- match.arg(direction, .directions)
  if (direction == "horizontal") {
    splits <- c("hbar", "vspine")
  } else {
    splits <- c("vbar", "hspine")
  }

  function(n) c(splits[1], rep(splits[2], length = n - 1))
}

#' Template for a nested barchart.
#' A nested bar is just a sequence of bars in the same direction.
#'
#' @param direction direction of first split
#' @export
nested <- function(direction = "h") {
  direction <- match.arg(direction, .directions)
  if (direction == "horizontal") {
    splits <- c("hbar")
  } else {
    splits <- c("vbar")
  }

  function(n) rep(splits, length = n)
}

#' Template for a double decker plot.
#' A double decker plot is composed of a sequence of spines in the same
#' direction, with the final spine in the opposite direction.
#'
#' @param direction direction of first split
#' @export
ddecker <- function(direction = "h") {
  direction <- match.arg(direction, .directions)
  if (direction == "horizontal") {
    splits <- c("hspine", "vspine")
  } else {
    splits <- c("vspine", "hspine")
  }

  function(n) c(rep(splits[1], length = n - 1), splits[2])
}

#' Template for a fluctuation diagram.
#'
#' @param direction direction of first split
#' @export
flucts <- function(direction = "h") {
  direction <- match.arg(direction, .directions)
  if (direction == "horizontal") {
    splits <- c("hspine", "vspine")
  } else {
    splits <- c("vspine", "hspine")
  }
  function(n) c(rep(splits, length = n - 2), "fluct")
}

### utils.r

prop <- function(x) x / sum(x, na.rm = TRUE)

cv <- function(x, na.rm = FALSE) sd(x, na.rm = na.rm) / mean(x, na.rm = na.rm)

uniquecols <- function(df) {
  one_val <- vapply(df, function(x) length(unique(x)) == 1, logical(1))
  unrowname(df[, one_val, drop = FALSE])
}
