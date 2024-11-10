"""
    Skript pro zapis hodnot frekvence, rozsahu akcelerometru a rozsahu
    gyroskopu do hlavicky souboru s namerenymi daty z akcelerometru a
    gyroskopu.

    Tento skript projde vsechny soubory v aktualnim adresari, ktere jsou ve
    tvaru:

            3_1_2024-09-08_10-11-07_fre_833_acc_4_gyr_250.txt

    Tedy, znakem "_" oddelene:

            cislo, cislo, datum, cas, "fre", cislo, "acc", cislo, "gyr", cislo

    Na zacatek souboru je potom pripsano:

            frequency = 833
            acc_range = 4
            gyr_range = 250

    a vysledny soubor je ulozen s koncovkou ".ag":

            3_1_2024-09-08_10-11-07_fre_833_acc_4_gyr_250.ag

    Pouziti: skript zkopirujte do adresare, kde jsou soubory, a napiste
      
            python3 addfag.py

    Milan Petrik (petrikm@tf.czu.cz) 10.11.2024
"""

from pathlib import Path

pathlist = Path('.').rglob('*.txt')
for path in pathlist:
    frequency = None
    acc_range = None
    gyr_range = None
    filename = str(path)
    words = filename[:-4].split('_')
    for i in range(len(words)):
        if words[i] == 'fre':
            frequency = words[i + 1]
        elif words[i] == 'acc':
            acc_range = words[i + 1]
        elif words[i] == 'gyr':
            gyr_range = words[i + 1]
    ag_filename = filename[:-4] + '.ag'
    with open(filename) as f, open(ag_filename, 'w') as agf:
        if frequency != None:
            agf.write('frequency = ' + frequency + "\n")
        if acc_range != None:
            agf.write('acc_range = ' + acc_range + "\n")
        if gyr_range != None:
            agf.write('gyr_range = ' + gyr_range + "\n")
        for line in f:
            agf.write(line)
