#! /bin/bash
# Make a dark version of each light icon

for inf in *light*; do
  outf=${inf/light/dark}
  # aiming for about RGB 200,200,200 for the body of the icon
  convert $inf -channel RGB -negate +level 20% $outf
done
