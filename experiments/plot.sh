#!/usr/bin/sh

gnuplot -e "title='Escalamiento'; inputfile='size.csv'; outputfile='escalamiento.pdf'; xLabel='Nivel de escalamiento'" plot.plot
gnuplot -e "title='Ruido por desenfoque'; inputfile='blur.csv'; outputfile='desenfoque.pdf'; xLabel='Tamaño de la matriz de difuminado'" plot.plot
gnuplot -e "title='Ruido sal y pimienta'; inputfile='noise.csv'; outputfile='ruido.pdf'; xLabel='Nivel de visibilidad'" plot.plot
gnuplot -e "title='Ruido por obstrucción'; inputfile='obstruction.csv'; outputfile='obstruccion.pdf'; xLabel='Nivel de obstrucción'" plot.plot
gnuplot -e "title='Iluminación'; inputfile='brightness.csv'; outputfile='iluminacion.pdf'; xLabel='Nivel de Iluminación'" plot.plot
gnuplot -e "title='Rotación'; inputfile='rotate.csv'; outputfile='rotacion.pdf'; xLabel='Ángulo de rotación'" plot.plot
