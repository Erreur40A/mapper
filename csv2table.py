import sys
#executer le scripte "python3 csv2table.py *.csv (nom table) >> (nom table)_data.sql"

#on ouvre le fichier donner en 1er argument de la ligne de commande
fichier=open(sys.argv[1], "r")
#on saute une ligne
next(fichier)

for ligne in fichier:
    #on supprime tout les '\n' et on sépare chaque la ligne en fonction de ';'
    colone=ligne.rstrip("\n").split(";")
    n=len(colone)

    """
    le 2eme argument en ligne de commande correspond au nom de la table ou
    l'on veut inserer les differentes valeurs
    """

    inserer="INSERT INTO " + sys.argv[2] + " VALUES ("

    for i in range(0, n):
        if(colone[i].find("'")==-1):
            inserer = inserer + "'" + colone[i] + "'"
        else:
            lst=colone[i].split("'")
            colone[i]=lst[0] + "''" + lst[1]
            inserer = inserer + "'" + colone[i] + "'"

        if i!=n-1:
            inserer=inserer + ","

    inserer=inserer + ");"

    print(inserer)
