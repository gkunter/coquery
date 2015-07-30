### test-plotting.r

library(testthat)

context("Plot ui")

test_that("margins & conditions extracted", {

  expect_that(parse_product_formula(~ a)$marg, equals(c("a")))
  expect_that(parse_product_formula(~ a)$cond, equals(character()))

  expect_that(parse_product_formula(~ a + c + d)$marg,
    equals(c("a", "c", "d")))
  expect_that(parse_product_formula(~ a | b + c + d)$cond,
    equals(c("b", "c", "d")))

  expect_that(parse_product_formula(wt ~ a + c + d)$marg,
    equals(c("a", "c", "d")))
  expect_that(parse_product_formula(wt ~ a | b + c + d)$cond,
    equals(c("b", "c", "d")))

})

test_that("dummy margin variable is ignored", {
  expect_that(parse_product_formula(~ . | b + c + d)$cond,
    equals(c("b", "c", "d")))
  expect_that(parse_product_formula(~ . | b + c + d)$marg,
    equals(character()))
})

test_that("weighting variable determined correctly", {
  expect_that(parse_product_formula(wt ~ a)$wt, equals("wt"))
  expect_that(parse_product_formula( ~ a)$wt, equals(character()))
})

### test-division.r

library(testthat)

context("Division algorithm")

test_that("2d areas are proportional to weights", {
  rand3x4 <- rand_array(3, 4)

  types <- list(
    c(hbar, hbar),
    c(hspine, hbar),
    c(hbar, vspine),
    c(vspine, hbar),
    c(vspine, vspine),
    c(fluct),
    c(hbar, tile)
  )

  for(type in types) {
    expect_that(calc_area(rand3x4, type), has_proportional_areas())
  }
})

test_that("3d areas are proportional to weights", {
  rand2x3x4 <- rand_array(2, 3, 4)

  types <- list(
    c(hbar, hbar, hbar),
    c(hbar, hbar, vspine),
    c(hbar, vspine, hbar),
    c(hbar, vspine, vspine),
    c(hbar, fluct),
    c(vspine, hbar, hbar),
    c(vspine, hbar, vspine),
    c(vspine, vspine, hbar),
    c(vspine, vspine, vspine),
    c(vspine, fluct),
    c(fluct, hbar, hbar),
    c(fluct, hbar, vspine)
  )

  for(type in types) {
    expect_that(calc_area(rand2x3x4, type), has_proportional_areas())
  }
})

test_that("4d areas are proportional to weights", {
  rand2x3x4x5 <- array(runif(2 * 3 * 4 * 5), dim = c(2, 3, 4, 5))

  types <- list(
    c(fluct, hbar, hbar),
    c(hbar, fluct, hbar),
    c(hbar, hbar, fluct),
    c(fluct, fluct),
    c(hbar, vspine, hbar, vspine),
    c(fluct, hbar, vspine)
  )

  for(type in types) {
    expect_that(calc_area(rand2x3x4x5, type), has_proportional_areas())
  }
})


test_that("missing values are handled correctly", {
  expect_that(add_area(prodcalc(happy, ~ age + year)),
    has_proportional_areas())

  expect_that(add_area(prodcalc(happy, ~ age + year, div = "fluct")),
    has_proportional_areas())


})

### test-labels.r

context("Labelling")

test_that("hbar, hspine, and fluct all have columns", {
  div_has_cols <- function(div, level = 1) {
    df <- prodcalc(happy, ~ happy + sex, div)
    has_cols(df[df$level == level, ])
  }

  # At top level, hbar, hspine and fluct should all have columns
  expect_that(div_has_cols(c("hspine", "hbar")), is_true())
  expect_that(div_has_cols(c("hspine", "hspine")), is_true())
  expect_that(div_has_cols(c("fluct")), is_true())

  # And vbar, vspine and tile should _not_ have columns
  expect_that(div_has_cols(c("hspine", "vbar")), is_false())
  expect_that(div_has_cols(c("hspine", "vspine")), is_false())

  # At the second level, columns should occur for hbar nested inside
  # hbars, hspines or vspines
  expect_that(div_has_cols(c("hbar", "hbar"), level = 2), is_true())
  expect_that(div_has_cols(c("hbar", "hspine"), level = 2), is_true())
  expect_that(div_has_cols(c("hbar", "vspine"), level = 2), is_true())

  # Not vbars
  expect_that(div_has_cols(c("hbar", "vbar"), level = 2), is_false())
})

test_that("vbar, vspine and fluct all have rows", {
  div_has_rows <- function(div, level = 1) {
    df <- prodcalc(happy, ~ happy + sex, div)
    has_rows(df[df$level == level, ])
  }

  # Only need mild testing because should just be rotation of columns
  expect_that(div_has_rows(c("hspine", "vbar")), is_true())
  expect_that(div_has_rows(c("hspine", "hbar")), is_false())

})

test_that("labelling levels identified corrected", {

  a <- prodcalc(happy, ~ finrela + degree, "fluct", na.rm = T)
  expect_that(find_col_level(a), equals(1))
  expect_that(find_row_level(a), equals(1))

  b <- prodcalc(happy, ~ finrela | degree, c("vbar", "hspine"), na.rm = T)
  expect_that(find_col_level(b), equals(1))
  expect_that(find_row_level(b), equals(2))

  c <- prodcalc(happy, ~ finrela | degree, c("vbar", "vspine"), na.rm = T)
  expect_that(find_col_level(c), equals(NA_real_))
  expect_that(find_row_level(c), equals(1))
})

### test-plotting.r

library(testthat)

context("Division algorithm")

test_that("2d areas are proportional to weights", {
  rand3x4 <- rand_array(3, 4)

  types <- list(
    c(hbar, hbar),
    c(hspine, hbar),
    c(hbar, vspine),
    c(vspine, hbar),
    c(vspine, vspine),
    c(fluct),
    c(hbar, tile)
  )

  for(type in types) {
    expect_that(calc_area(rand3x4, type), has_proportional_areas())
  }
})

test_that("3d areas are proportional to weights", {
  rand2x3x4 <- rand_array(2, 3, 4)

  types <- list(
    c(hbar, hbar, hbar),
    c(hbar, hbar, vspine),
    c(hbar, vspine, hbar),
    c(hbar, vspine, vspine),
    c(hbar, fluct),
    c(vspine, hbar, hbar),
    c(vspine, hbar, vspine),
    c(vspine, vspine, hbar),
    c(vspine, vspine, vspine),
    c(vspine, fluct),
    c(fluct, hbar, hbar),
    c(fluct, hbar, vspine)
  )

  for(type in types) {
    expect_that(calc_area(rand2x3x4, type), has_proportional_areas())
  }
})

test_that("4d areas are proportional to weights", {
  rand2x3x4x5 <- array(runif(2 * 3 * 4 * 5), dim = c(2, 3, 4, 5))

  types <- list(
    c(fluct, hbar, hbar),
    c(hbar, fluct, hbar),
    c(hbar, hbar, fluct),
    c(fluct, fluct),
    c(hbar, vspine, hbar, vspine),
    c(fluct, hbar, vspine)
  )

  for(type in types) {
    expect_that(calc_area(rand2x3x4x5, type), has_proportional_areas())
  }
})


test_that("missing values are handled correctly", {
  expect_that(add_area(prodcalc(happy, ~ age + year)),
    has_proportional_areas())

  expect_that(add_area(prodcalc(happy, ~ age + year, div = "fluct")),
    has_proportional_areas())


})

