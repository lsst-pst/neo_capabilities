#foreach i (astro_lsst_01_1016 minion_1016 astro_lsst_01_1015 astro_lsst_01_1017)
#   foreach j (`ls orbits/pha_split`)
#      makeLSSTobs.py --orbitFile orbits/pha_split/$j --outDir pha_split_obs --obsFile $i"__"$j"__obs" --ephMode nbody ../db/$i"_sqlite.db" &
#      end
#   sleep 1.5h
#end

foreach i (astro-lsst-01_2013)
   foreach j (`ls orbits/pha_split`)
      python $SIMS_MOVINGOBJECTS_DIR/bin.src/makeLSSTobs.py --orbitFile orbits/pha_split/$j --outDir pha_split_obs --obsFile $i"__"$j"__obs" --ephMode nbody /ssd/lsst/opsimv4/rundb/$i".db" &
      end
   sleep 1.5h
end
