set terminal pdf enhanced

set title title
set output outputfile
set datafile separator ","

set style data histogram
set style histogram cluster gap 1

set xlabel xLabel
set ylabel "Detecciones"

set style fill solid border rgb "black"
set auto x
set yrange [0:20]

plot inputfile using 2:xtic(1) title "Verdadero" linecolor rgb "#0B610B", \
'' using 3:xtic(1) title "Falso" linecolor rgb "#B40404", \
'' using 4:xtic(1) title "Error" linecolor rgb "#424242"
