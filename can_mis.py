import math
import sys
import time
import os.path


class NodParcurgere:
    def __init__(self, info, parinte, cost=0, h=0):
        self.info = info
        self.parinte = parinte
        self.g = cost
        self.h = h
        self.f = self.g + self.h

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self):
        l = self.obtineDrum()
        for nod in l:
            print(str(nod))

        return len(l)

    @staticmethod
    def print_detalii(nod, gr=None, fisier=None):
        if nod.info[4] == gr.malInitial:
            B0 = "B"
            B1 = ""
        else:
            B0 = ""
            B1 = "B"

        if gr is None:
            print(str(nod), file=fisier)
        else:
            str_val = gr.malInitialStr.upper() + ": " + str(nod.info[0]) + "c " + str(nod.info[1]) + "m " + \
                      str(nod.info[2]) + "f |" + B0 + "   " + B1 + "| " + gr.malFinalStr.upper() + ": " + \
                      str(gr.N - nod.info[0]) + "c " + str(gr.N - nod.info[1]) + "m " + str(nod.info[3] - nod.info[2]) \
                      + "f"
            print(str_val, file=fisier)

    def afisareSolutie(self, gr=None, fisier=None):
        l = self.obtineDrum()

        print("=" * 100, file=fisier)
        for i, nod in enumerate(l):
            if nod.parinte is not None:
                if nod.parinte.info[4] == gr.malInitial:
                    mal_plecare = gr.malInitialStr
                    mal_sosire = gr.malFinalStr
                else:
                    mal_plecare = gr.malFinalStr
                    mal_sosire = gr.malInitialStr
                can_b = abs(nod.info[0] - nod.parinte.info[0])
                mis_b = abs(nod.info[1] - nod.parinte.info[1])
                fan_b = abs(nod.info[2] - nod.parinte.info[2])

                if nod.info[3] != nod.parinte.info[3]:
                    ritual = True
                    if fan_b > 0:
                        fan_b -= 1
                else:
                    ritual = False

                print("--- Barca se deplaseaza de la malul de %s la malul de %s cu " % (mal_plecare, mal_sosire),
                      end="", file=fisier)
                if can_b > 0:
                    print("%d canibal" % can_b, end="", file=fisier)
                    if can_b > 1:
                        print("i", end="", file=fisier)
                    if mis_b + fan_b == 0:
                        print(" ---", file=fisier)
                    elif mis_b == 0 or fan_b == 0:
                        print(" si ", end="", file=fisier)
                    else:
                        print(", ", end="", file=fisier)

                if mis_b > 0:
                    print("%d misionar" % mis_b, end="", file=fisier)
                    if mis_b > 1:
                        print("i", end="", file=fisier)
                    if fan_b == 0:
                        print(" ---", file=fisier)
                    else:
                        print(" si ", end="", file=fisier)

                if fan_b > 0:
                    print("%d fantom" % fan_b, end="", file=fisier)
                    if fan_b > 1:
                        print("e", end="", file=fisier)
                    else:
                        print("a", end="", file=fisier)
                    print(" ---", file=fisier)

                if ritual:
                    print("--- Misionarii au organizat un ritual si au eliminat o fantoma pe malul de %s ---"
                          % mal_plecare, file=fisier)
            print("Stare %d: " % (i + 1), end="", file=fisier)
            self.print_detalii(nod, gr, fisier=fisier)

        return len(l)

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if (infoNodNou == nodDrum.info):
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info) + "\n"
        return (sir)

    def __str__(self):
        sir = str(self.info)
        return sir


# noinspection PyUnreachableCode
class Graph:
    N = None
    M = None
    NF = None
    malInitial = None
    malFinal = None
    malInitialStr = None
    malFinalStr = None

    def __init__(self, fisier):
        self.error = False
        linii = fisier.read().splitlines()

        perechi = [linie.split("=") for linie in linii]

        try:
            for pereche in perechi:
                if pereche[0].lower() == "n":
                    Graph.N = int(pereche[1])

                if pereche[0].lower() == "m":
                    Graph.M = int(pereche[1])

                if pereche[0].lower() == "nf":
                    Graph.NF = int(pereche[1])

                if pereche[0].lower() == "malinitial":
                    Graph.malInitial = 0
                    mal = pereche[1].lower()
                    if Graph.malFinalStr is None or mal != Graph.malFinalStr:
                        Graph.malInitialStr = mal
                    else:
                        print("Fisierul %s contine date invalide!", file=sys.stderr)
                        self.error = True
                        return

                if pereche[0].lower() == "malfinal":
                    Graph.malFinal = 1
                    mal = pereche[1].lower()
                    if Graph.malInitialStr is None or mal != Graph.malInitialStr:
                        Graph.malFinalStr = mal
                    else:
                        print("Fisierul %s contine date invalide!", file=sys.stderr)
                        self.error = True
                        return
        except ValueError:
            print("Fisierul %s contine date invalide!" % fisier.name, file=sys.stderr)
            self.error = True
            return

        # retine datele de pe malul initial + numarul total de fantome + malul pe care se afla barca acum
        # (can, mis, fan, total_fantome, mal_barca)
        self.start = (Graph.N, Graph.N, Graph.NF, Graph.NF, Graph.malInitial)
        self.scopuri = [(0, 0, x, x, Graph.malFinal) for x in range(Graph.NF + 1)]

    def calculeaza_h(self, infoNod, tip_euristica):
        if tip_euristica == "euristica admisibila 1":
            oameniMalInitial = infoNod[0] + infoNod[1]
            oameniMalFinal = 2 * Graph.N - oameniMalInitial
            fanMalInitial = infoNod[2]
            fanMalFinal = infoNod[3] - infoNod[2]

            return oameniMalInitial - math.floor(fanMalInitial / 2) - (oameniMalFinal - fanMalFinal)
        """
        presupunem ca cel jumatate din fantomele de pe malul initial vor pleca pe malul final,
        toti oamenii de pe malul initial trebuie sa ajunga pe malul final, iar toate fantomele
        de pe malul final trebuie sa ajunga pe cel initial si vor scadea din costul celor care
        le transporta inapoi
        """

        if tip_euristica == "euristica admisibila 2":
            oameniMalInitial = infoNod[0] + infoNod[1]
            locuri = Graph.M
            drum_suplimentar = 1 if infoNod[4] == Graph.malInitial else 0
            deplasari = 2 * (math.floor(oameniMalInitial / (locuri - 1)) - 1) + 1 + drum_suplimentar
            deplasari = math.floor(deplasari / 2)
            locuri = math.floor(locuri / 2)
            return deplasari * min(locuri, oameniMalInitial)
        """
        consideram ca barca pleaca mereu doar cu jumatate din locuri ocupate,
        iar barca se poate intoarce singura, deci injumatatim numarul de deplasari
        considerate si costul pentru fiecare deplasare este limitat de jumatate din
        numarul locuri sau de cati oameni mai sunt pe malul initial, daca acestia sunt
        mai putini
        
        10 oameni
        3 locuri
        --> +3
        <-- -1
        
        barca e pe malul initial:
            +3 -->
            -1 <--
            +3 -->
            -1 <--
            +3 -->
            -1 <--
            +3 -->
            -1 <--
            +2 -->
            ------
            10
        daca barca e pe malul final, trebuie sa mai scadem -1
        pentru a aduce barca pe malul initial
        
        observam ca se formeaza niste grupari de forma:
        | +nr_locuri
        | -1
        deci putem calcula cate astfel de grupari se obtin prin impartirea:
        math.floor(nr_oameni / (nr_locuri - 1))  (ne intereseaza doar catul)
        ultima grupare nu este completa, deoarece contine doar drumul catre malul final,
        deci o scadem => math.floor(nr_oameni / (nr_locuri - 1)) - 1
        fiecare grupare reprezinta doua deplasari => 2 * (math.floor(nr_oameni / (nr_locuri - 1)) - 1)
        acum mai trebuie sa adugam ultima deplasare (catre malul final),
        deoarece am eliminat ultima grupare => 2 * (math.floor(nr_oameni / (nr_locuri - 1)) - 1) + 1
        si pentru cazul in care barca este pe malul final trebuie sa mai adaugam 1 => 
        2 * (math.floor(nr_oameni / (nr_locuri - 1)) - 1) + 1 + drum_suplimentar
        """

        if tip_euristica == "euristica inadmisibila":
            oameniMalInitial = infoNod[0] + infoNod[1]
            oameniTotal = 2 * Graph.N
            locuri = Graph.M
            drum_suplimentar = 1 if infoNod[4] == Graph.malInitial else 0
            deplasari = 2 * (math.floor(oameniMalInitial / (locuri - 1)) - 1) + 1 + drum_suplimentar

            return (deplasari + 10) * oameniTotal * locuri ** locuri
        """
        Calculam numarul de deplasari si adunam 10, ca sa avem mereu mai multe decat necesare.
        Inmultim cu numarul total de oameni, ca si cum i-am deplasa pe toti in acelasi timp.
        Apoi mai inmultim si cu locuri^locuri pentru a creste si mai mai mult costul estimat.
        """

        if infoNod in self.scopuri:
            return 0
        return 1
        """
        aceasta euristica banala este folosita doar in cazul in
        care nu a fost selectata o euristica valida
        """

    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        def conditie(can, mis, fan):
            return (mis == 0 and can == 0) or (mis + can >= fan and (mis == 0 or mis >= can))

        def adaugaSuccesori(lista_succesori, can_mal, mis_mal, fan_mal, fan_total, can_veniti, mis_veniti, mal):
            global totalNoduri
            misBarcaMax = min(Graph.M, mis_mal)

            for misBarca in range(misBarcaMax + 1):
                canBarcaMax = min(Graph.M, can_mal) if misBarca == 0 else min(Graph.M - misBarca,
                                                                              can_mal, misBarca)

                for canBarca in range(canBarcaMax + 1):
                    if canBarca + misBarca == 0 or (
                            fan_total > 0 and canBarca == can_veniti and misBarca == mis_veniti):
                        continue

                    if misBarca == 0:
                        fanBarca = min(Graph.M - canBarca, fan_mal)
                    else:
                        fanBarca = 0

                    canMalNou = can_mal - canBarca
                    misMalNou = mis_mal - misBarca
                    fanMalNou = fan_mal - fanBarca

                    canMalOpusNou = Graph.N - canMalNou
                    misMalOpusNou = Graph.N - misMalNou
                    fanMalOpusNou = fan_total - fanMalNou

                    if not (conditie(canBarca, misBarca, fanBarca) and
                            conditie(canMalNou, misMalNou, fanMalNou) and
                            conditie(canMalOpusNou, misMalOpusNou, fanMalOpusNou)):
                        continue

                    ritual = 0
                    if canMalNou == 0 and misMalNou > 0 and fanMalNou > 0:
                        fanMalNou -= 1
                        ritual = 1

                    if malCurent == Graph.malInitial:
                        infoNod = (canMalNou, misMalNou, fanMalNou, fan_total - ritual, Graph.malFinal)
                    else:
                        infoNod = (canMalOpusNou, misMalOpusNou, fanMalOpusNou, fan_total - ritual, Graph.malInitial)

                    if not nodCurent.contineInDrum(infoNod):
                        costSuccesor = canBarca + misBarca - fanBarca
                        h = self.calculeaza_h(infoNod, tip_euristica)
                        lista_succesori.append(NodParcurgere(info=infoNod, parinte=nodCurent,
                                                             cost=nodCurent.g + costSuccesor, h=h))
                        totalNoduri += 1

        listaSuccesori = []

        info = nodCurent.info

        fanTotal = info[3]

        canMalInitial = info[0]
        misMalInitial = info[1]
        fanMalInitial = info[2]

        canMalOpus = Graph.N - info[0]
        misMalOpus = Graph.N - info[1]
        fanMalOpus = fanTotal - info[2]

        malCurent = info[4]

        if nodCurent.parinte is None:
            canVeniti = 0
            misVeniti = 0
        else:
            infoParinte = nodCurent.parinte.info
            canVeniti = abs(info[0] - infoParinte[0])
            misVeniti = abs(info[1] - infoParinte[1])

        if malCurent == Graph.malInitial:
            adaugaSuccesori(listaSuccesori, canMalInitial, misMalInitial, fanMalInitial, fanTotal,
                            canVeniti, misVeniti, malCurent)
        else:
            adaugaSuccesori(listaSuccesori, canMalOpus, misMalOpus, fanMalOpus, fanTotal,
                            canVeniti, misVeniti, malCurent)

        return listaSuccesori

    def testeaza_scop(self, nodCurent):
        return nodCurent.info in self.scopuri


def breadth_first(gr, nrSolutiiCautate=1, fisier=None, timeout=60.0, tip_euristica="euristica banala"):
    # euristica este doar pentru a putea generaliza functia de cautare
    global totalNoduri
    tstart = time.time()

    c = [NodParcurgere(gr.start, None)]
    nr_sol_cautate = nrSolutiiCautate
    while len(c) > 0:

        if time.time() > tstart + timeout:
            print("TIMEOUT", file=fisier)
            break

        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            ldrum = nodCurent.afisareSolutie(gr, fisier=fisier)
            print("Lungime drum: %d" % ldrum, file=fisier)
            print("Numar de noduri generate: %d" % totalNoduri, file=fisier)
            print("Cost solutie: %d" % nodCurent.g, file=fisier)
            print("Timp: %d milisecunde" % round((time.time() - tstart) * 1000), file=fisier)
            # input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                print("Au fost gasite %d solutii." % nr_sol_cautate, file=fisier)
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        c.extend(lSuccesori)

    print("Au fost gasite %d solutii." % (nr_sol_cautate - nrSolutiiCautate), file=fisier)


def depth_first(gr, nrSolutiiCautate=1, fisier=None, timeout=60.0, tip_euristica="euristica banala"):
    # euristica este doar pentru a putea generaliza functia de cautare
    def df(nod_curent, graph, nr_sol_cautate, timp_limita, tstart):
        global totalNoduri
        if time.time() > timp_limita:
            return nr_sol_cautate

        if nr_sol_cautate == 0:
            return nr_sol_cautate

        if graph.testeaza_scop(nod_curent):
            ldrum = nod_curent.afisareSolutie(graph, fisier=fisier)
            print("Lungime drum: %d" % ldrum, file=fisier)
            print("Numar de noduri generate: %d" % totalNoduri, file=fisier)
            print("Cost solutie: %d" % nod_curent.g, file=fisier)
            print("Timp: %d milisecunde" % round((time.time() - tstart) * 1000), file=fisier)
            # input()
            nr_sol_cautate -= 1
            if nr_sol_cautate == 0:
                return nr_sol_cautate

        lSuccesori = graph.genereazaSuccesori(nod_curent)
        for s in lSuccesori:
            if nr_sol_cautate != 0:
                nr_sol_cautate = df(s, graph, nr_sol_cautate, timp_limita, tstart)
        return nr_sol_cautate

    tstart = time.time()
    nr_sol = df(NodParcurgere(gr.start, None), gr, nrSolutiiCautate, tstart + timeout, tstart)

    if time.time() > tstart + timeout:
        print("TIMEOUT", file=fisier)

    print("Au fost gasite %d solutii." % (nrSolutiiCautate - nr_sol), file=fisier)


def depth_first_iterativ(gr, nrSolutiiCautate=1, fisier=None, timeout=60.0, tip_euristica="euristica banala",
                         adancime_max=100):
    # euristica este doar pentru a putea generaliza functia de cautare
    def dfi(nod_curent, adancime, graph, nr_sol_cautate, timp_limita, tstart):
        global totalNoduri
        if time.time() > timp_limita:
            return nr_sol_cautate

        if nr_sol_cautate == 0:
            return nr_sol_cautate

        if adancime == 1 and graph.testeaza_scop(nod_curent):
            ldrum = nod_curent.afisareSolutie(graph, fisier=fisier)
            print("Lungime drum: %d" % ldrum, file=fisier)
            print("Numar de noduri generate: %d" % totalNoduri, file=fisier)
            print("Cost solutie: %d" % nod_curent.g, file=fisier)
            print("Timp: %d milisecunde" % round((time.time() - tstart) * 1000), file=fisier)
            # input()
            nr_sol_cautate -= 1
            if nr_sol_cautate == 0:
                return nr_sol_cautate

        if adancime > 1:
            lSuccesori = graph.genereazaSuccesori(nod_curent)
            for s in lSuccesori:
                if nr_sol_cautate != 0:
                    nr_sol_cautate = dfi(s, adancime - 1, graph, nr_sol_cautate, timp_limita, tstart)
        return nr_sol_cautate

    i = 0
    nr_sol = 0
    tstart = time.time()
    while i <= adancime_max and time.time() < tstart + timeout:
        nr_sol_cautatea = nrSolutiiCautate
        nrSolutiiCautate = dfi(NodParcurgere(gr.start, None), i, gr, nrSolutiiCautate, tstart + timeout, tstart)
        nr_sol += nr_sol_cautatea - nrSolutiiCautate
        i += 1

    if time.time() > tstart + timeout:
        print("TIMEOUT", file=fisier)
    print("Au fost gasite %d solutii." % nr_sol, file=fisier)


def uniform_cost(gr, nrSolutiiCautate=1, fisier=None, timeout=60.0, tip_euristica="euristica banala"):
    # euristica este doar pentru a putea generaliza functia de cautare
    global totalNoduri
    tstart = time.time()
    c = [NodParcurgere(gr.start, None, cost=0)]
    nr_sol_cautate = nrSolutiiCautate
    while len(c) > 0:

        if time.time() > tstart + timeout:
            print("TIMEOUT", file=fisier)
            break

        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            ldrum = nodCurent.afisareSolutie(gr, fisier=fisier)
            print("Lungime drum: %d" % ldrum, file=fisier)
            print("Numar de noduri generate: %d" % totalNoduri, file=fisier)
            print("Cost solutie: %d" % nodCurent.g, file=fisier)
            print("Timp: %d milisecunde" % round((time.time() - tstart) * 1000), file=fisier)
            # input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                print("Au fost gasite %d solutii." % nr_sol_cautate, file=fisier)
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent)

        for s in lSuccesori:
            i = 0
            while i < len(c):
                if c[i].f >= s.g:
                    break
                i += 1
            c.insert(i, s)
    print("Au fost gasite %d solutii." % (nr_sol_cautate - nrSolutiiCautate), file=fisier)


def a_star(gr, nrSolutiiCautate=1, fisier=None, timeout=60.0, tip_euristica="euristica banala"):
    global totalNoduri
    tstart = time.time()

    c = [NodParcurgere(gr.start, None, cost=0, h=gr.calculeaza_h(gr.start, tip_euristica))]
    nr_sol_cautate = nrSolutiiCautate
    while len(c) > 0:

        if time.time() > tstart + timeout:
            print("TIMEOUT", file=fisier)
            break

        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            ldrum = nodCurent.afisareSolutie(gr, fisier=fisier)
            print("Lungime drum: %d" % ldrum, file=fisier)
            print("Numar de noduri generate: %d" % totalNoduri, file=fisier)
            print("Cost solutie: %d" % nodCurent.g, file=fisier)
            print("Timp: %d milisecunde" % round((time.time() - tstart)*1000), file=fisier)
            # input()
            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                print("Au fost gasite %d solutii." % nr_sol_cautate, file=fisier)
                return
        lSuccesori = gr.genereazaSuccesori(nodCurent, tip_euristica)

        for s in lSuccesori:
            i = 0
            while i < len(c):
                if c[i].f >= s.f:
                    break
                i += 1
            c.insert(i, s)
    print("Au fost gasite %d solutii." % (nr_sol_cautate - nrSolutiiCautate), file=fisier)


def cautare_solutii(functie_cautare, gr, nrSolutiiCautate=1, cale_fisier=None, timeout=60.0,
                    tip_euristica="euristica banala"):
    global totalNoduri
    if cale_fisier is not None:
        f = open(cale_fisier, "w")
    else:
        f = sys.stdout

    totalNoduri = 0
    tinitial = time.time()
    functie_cautare(gr=gr, nrSolutiiCautate=nrSolutiiCautate, fisier=f, timeout=timeout, tip_euristica=tip_euristica)
    tfinal = time.time()
    print("Timp total: %d milisecunde" % round((tfinal - tinitial) * 1000), file=f)

    if cale_fisier is not None:
        f.close()


def main():
    if len(sys.argv) < 4:
        print("Utilizare: %s f_in1 [f_in2 ... f_inN] nr_solutii timeout", file=sys.stderr)
        sys.exit(1)

    fisiere_input = [arg for i, arg in enumerate(sys.argv) if 0 < i < len(sys.argv) - 2]

    try:
        N = int(sys.argv[-2])  # numarul de solutii cautate
    except ValueError:
        print("Numarul de solutii cautate trebuie sa fie natural pozitiv!", file=sys.stderr)
        sys.exit(1)
    if N <= 0:
        print("Numarul de solutii cautate trebuie sa fie natural pozitiv!", file=sys.stderr)
        sys.exit(1)

    try:
        timeout = float(sys.argv[-1])  # timpul de asteptare
    except ValueError:
        print("Timpul de asteptare trebuie sa fie un numar rational pozitiv!", file=sys.stderr)
        sys.exit(1)
    if timeout <= 0:
        print("Timpul de asteptare trebuie sa fie un numar rational pozitiv!", file=sys.stderr)
        sys.exit(1)

    for cale in fisiere_input:
        if not os.path.isfile(cale):
            print("%s nu este un fisier!" % cale, file=sys.stderr)
            continue

        f = open(cale)
        gr_can_mis = Graph(f)
        f.close()

        if gr_can_mis.error:
            continue

        cautare_solutii(functie_cautare=breadth_first, gr=gr_can_mis, nrSolutiiCautate=N,
                        cale_fisier=(cale + ".bfs.out"), timeout=timeout)
        cautare_solutii(functie_cautare=depth_first, gr=gr_can_mis, nrSolutiiCautate=N,
                        cale_fisier=(cale + ".dfs.out"), timeout=timeout)
        cautare_solutii(functie_cautare=depth_first_iterativ, gr=gr_can_mis, nrSolutiiCautate=N,
                        cale_fisier=(cale + ".dfi.out"), timeout=timeout)
        cautare_solutii(functie_cautare=uniform_cost, gr=gr_can_mis, nrSolutiiCautate=N,
                        cale_fisier=(cale + ".ucs.out"), timeout=timeout)
        cautare_solutii(functie_cautare=a_star, gr=gr_can_mis, nrSolutiiCautate=N,
                        cale_fisier=(cale + ".a_star_ad1.out"), timeout=timeout,
                        tip_euristica="euristica admisibila 1")
        cautare_solutii(functie_cautare=a_star, gr=gr_can_mis, nrSolutiiCautate=N,
                        cale_fisier=(cale + ".a_star_ad2.out"), timeout=timeout,
                        tip_euristica="euristica admisibila 2")
        cautare_solutii(functie_cautare=a_star, gr=gr_can_mis, nrSolutiiCautate=N,
                        cale_fisier=(cale + ".a_star_inad.out"), timeout=timeout,
                        tip_euristica="euristica inadmisibila")


totalNoduri = 0

if __name__ == "__main__":
    main()
