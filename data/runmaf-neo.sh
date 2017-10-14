foreach i (astro_lsst_01_1016 astro_lsst_01_1015 astro_lsst_01_1017)
   foreach j (`ls orbits/neo_split`)
      movingObjects.py --opsimRun $i --orbitFile orbits/neo_5k --obsFile neo_split_obs/$i"__"$j"__obs" --opsimDb db/$i"_sqlite.db" --outDir neo_split_res/$i --hMin 11 --hMax 28 --hStep 0.5 --albedo 0.13 --hMark 22 --nYearsMax 12 --metadata $j &
      end
   sleep 1.5h
end

foreach i (minion_1016)
   foreach j (`ls orbits/neo_split`)
      movingObjects.py --opsimRun $i --orbitFile orbits/neo_5k --obsFile neo_split_obs/$i"__"$j"__obs" --opsimDb db/$i"_sqlite.db" --outDir neo_split_res/$i --hMin 11 --hMax 28 --hStep 0.5 --albedo 0.13 --hMark 22 --nYearsMax 10 --metadata $j &
      end
   sleep 1.5h
end 
