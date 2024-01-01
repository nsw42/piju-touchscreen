#! /bin/bash
# Make a dark version of each light icon

for inf in *light*; do
  outf=${inf/light/dark}
  convert $inf -channel RGB -negate +level 10% $outf
done
