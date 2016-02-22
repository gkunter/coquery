for i in small-n-flat/SVG/*.svg; do convert -resize x32 -background none "$i" "small-n-flat/PNG/$(basename ${i%.*}).png" ; done
