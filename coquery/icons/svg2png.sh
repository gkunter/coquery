for i in small-n-flat/SVG/*.svg; do convert -density 300x300 -resize x96 -background none "$i" "small-n-flat/PNG/$(basename ${i%.*}).png" ; done
