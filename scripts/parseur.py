
# le but de ce script est de parser les donnees csv en commandes sql INSERT,
# pour separer les differentes routes de l'attribut rout_I_count,
# une rangee est cree pour chaque route de la liste

#executer le scripte "python3 parseur.py *.csv (nom table) >> (nom table)_.sql"

import sys
fichier = open(sys.argv[1])
next(fichier)

for line in fichier:
	colones = line.rstrip("\n").split(";") 
	s = [colones[j] for j in [0,1,-1]]
	sub_s = s[:-1]
	step_lst = s[-1].split(",")
	inserer = f'INSERT INTO {sys.argv[2]} VALUES ('

	for elem in sub_s:
		inserer = inserer + elem + ','
	for n,step in enumerate(step_lst):

		temp = step.split(":")
		inserer_temp = inserer
		for i,e in enumerate(temp):
			inserer_temp += e  
			if i != len(temp)-1:
				inserer_temp += ','
		inserer_temp = inserer_temp 
		inserer_temp = inserer_temp + ');'
		print(inserer_temp)	
