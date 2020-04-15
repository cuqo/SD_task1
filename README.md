# SD_task1
En aquest apartat realitzarem un breu explicació de cada tros de codi (molt breument)
amb petites particularitats que pugui tenir cada segment.

Main
El segment principal s’encarrega de realitzar les crides al generador de matrius a partir de
la seves dimensions, es crida una vegada per cada matriu, posteriorment crida al
generador del vector “iterdata” (l’input per la funció map_reduce()) i realitza la crida a la
funció map_reduce(), finalment realitza l’escriptura per pantalla de les dades més
importants.

Generador de matrius
En aquesta funció es crea una matriu de les dimensions passades per paràmetre i amb
nombres definits amb un rang que està definit com a global, posteriorment es desa la
matriu completa al núvol (serialitzada) i es procedeix a realitzar la partició en files o
columnes i el conseqüent emmagatzemament al núvol de cada tros per separat i segons el
seu nom, també passat per paràmetre.

Generador de l’iterdata
En aquesta funció es realitza la repartició de feina entre cada Worker existent (el nombre
de workers estarà limitat entre 1 i el nombre total de chunks o 100 en el cas de matrius
grans). Aquesta funció genera un vector general en que cada posició serà un altre vector
que contindrà els identificadors de les files i columnes que ha de multiplicar cada Worker.

Funció map
Aquesta funció rep un vector en que cada posició és un altre vector fix de dues posicions
que pertanyen als dos identificadors (un per la fila de la matriu A i l’altre per la columna
de la matriu B) que es volen multiplicar i sumar posteriorment. Es realitza la descarrega
des del bucket del núvol, es realitza la suma vectorial i amb el valor obtingut, juntament
amb el numero de la fila i la columna que pertany s’envien a la funció reduce.


Funció Reduce
Aquesta funció rep els vectors en que cada posició és un altre vector amb el format (fila,
columna, valor) pertanyents a cada chunk i que envia cada worker, aquesta funció realitza
la inserció de cada element a la seva posició de la matriu i finalment emmagatzema la
matriu resultat sencera al núvol.
