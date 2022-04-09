import numpy as np
import random
import operator
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
import math
from scipy.spatial import distance


#El gen es la ciudad
class Ciudad:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def Dis_Euc(self, ciudad):
        currentCity = (self.x, self.y)
        neighbourCity = (ciudad.x, ciudad.y)
        return distance.euclidean(currentCity, neighbourCity)

    def __repr__(self):
        return "(" + str(self.x) + "," + str(self.y) + ")"


#El cromosoma es la Ruta
class Ruta:
    def __init__(self, route):
        self.route = route
        self.Dis_Euc = 0
        self.fitness = 0.0

        
    def Distancia(self):
        if self.Dis_Euc == 0:
            camino = 0
            for i in range(0, len(self.route)):
                x = self.route[i]
                y = None
                if i + 1 < len(self.route):
                    y = self.route[i + 1]
                else:
                    y = self.route[0]
                camino += x.Dis_Euc(y)

            self.Dis_Euc = camino
        return self.Dis_Euc

    #nos importa la menor distancia
    def Fitness(self):
        if self.fitness == 0:
            self.fitness = self.Distancia()
        return self.fitness

#crea una ruta aleatoria 
def Crear_Rut(ciudades):
    route = random.sample(ciudades, len(ciudades))
    return route

#inicia la poblacion de rutas posibles  de las ciudades 
def iniciarPoblacion(popSize, ciudades):
    population = []
    for i in range(0, popSize):
        population.append(Crear_Rut(ciudades))
    global firstEverRoute
    firstEverRoute = population[popSize - 1]
    return population

#Realiza un rankin para obtener las distancias de rutas  de forma ascendente 
def Ranking(population):
    Fresult = {}
    for i in range(0, len(population)):
        Fresult[i] = Ruta(population[i]).Fitness()
    return sorted(Fresult.items(), key=operator.itemgetter(1), reverse=False)

#Seleccionamos a los padres por elitismo y probabilidad
#la funcion retorna los IDs de las padres(rutas)
def seleccion(popRanked, eliteSize):
    Sresult = []
    #definimos la ruleta
    df = pd.DataFrame(np.array(popRanked), columns=["Idx", "Fitness"])
    df['cum_sum'] = df.Fitness.cumsum()
    df['cum_perc'] = 100 * df.cum_sum / df.Fitness.sum()
    
    #Por elitismo se escoge las rutas mas optimas
    for i in range(0, eliteSize):
        Sresult.append(popRanked[i][0])
    
    #Elegimos por probabilidad los  posibles padres
    for i in range(0, len(popRanked) - eliteSize):
        pick = 100 * random.random()
        for i in range(0, len(popRanked)):
            if pick <= df.iat[i, 3]:
                Sresult.append(popRanked[i][0])
                break
    return Sresult


def getCandidatosPadres(population, Sresult):        
    padres = []
    for i in range(0, len(Sresult)):
        index = Sresult[i]
        padres.append(population[index])
    return padres


def Crusando(Padre1, Padre2):         
    Hijo = []
    HijoP1 = []
    HijoP2 = []
    A = int(random.random() * len(Padre1))
    B = int(random.random() * len(Padre1))
    ini = min(A, B)
    fin = max(A, B)
    for i in range(ini, fin):
        HijoP1.append(Padre1[i])
    HijoP2 = [item for item in Padre2 if item not in HijoP1]
    Hijo = HijoP1 + HijoP2
    return Hijo


def Crusando_Poblacion(matingpool, eliteSize):     ################################################################################
    Hijos = []
    length = len(matingpool) - eliteSize
    pool = random.sample(matingpool, len(matingpool))
    for i in range(0, eliteSize):
        Hijos.append(matingpool[i])
    for i in range(0, length):
        Hijo = Crusando(pool[i], pool[len(matingpool) - i - 1])
        Hijos.append(Hijo)
    return Hijos


def mutar(individual, mutationRate):
    for aux1 in range(len(individual)):
        if (random.random() < mutationRate):
            aux2 = int(random.random() * len(individual))
            c1 = individual[aux1]
            c2 = individual[aux2]
            individual[aux1] = c2
            individual[aux2] = c1
    return individual


def mutarPoblacion(population, mutationRate):
    mutatedPop = []
    for ind in range(0, len(population)):
        mutatedInd = mutar(population[ind], mutationRate)
        mutatedPop.append(mutatedInd)
    return mutatedPop


def NextG(currentGen, TamE, mutationRate):
    popRanked = Ranking(currentGen)
    Sresult = seleccion(popRanked, TamE)
    matingpool = getCandidatosPadres(currentGen, Sresult)
    Hijos = Crusando_Poblacion(matingpool, TamE)
    NextG = mutarPoblacion(Hijos, mutationRate)
    return NextG


def GA(population, popSize, TamE, mutationRate, generations):
    pop = iniciarPoblacion(popSize,population)
    print("Initial distance: " + str(Ranking(pop)[0][1]))

    progress = []
    promedio = []

    rankingRoutes = Ranking(pop)
    print(rankingRoutes)

    progress.append(rankingRoutes[0][1])
    promedio.append(sum(j for i, j in rankingRoutes)/len(rankingRoutes))

    print(progress)
    print(promedio)

    for i in range(0, generations):
        pop = NextG(pop, TamE, mutationRate)
        rankingRoutes = Ranking(pop)
        progress.append(rankingRoutes[0][1])
        promedio.append(sum(j for i, j in rankingRoutes)/len(rankingRoutes))


    print("Final distance: " + str(Ranking(pop)[0][1]))
    bestRouteIndex = Ranking(pop)[0][0]
    bestRoute = pop[bestRouteIndex]


    plt.plot(progress)
    plt.ylabel('Distance')
    plt.xlabel('Generation')
    plt.show()

    plt.plot(promedio)
    plt.ylabel('Promedio')
    plt.xlabel('Generation')
    plt.show()

    return bestRoute



########################################## main ################################################################


ciudades= []

lenCiudades = 25

#Generamos un numero de ciudades con sus coordenadas aleatorias
for i in range(0,lenCiudades):
    ciudades.append(Ciudad(x=int(random.random() * 200), y=int(random.random() * 200)))


poblacion = 10
elitismo = 6
mutacion = 0.01
generaciones = 50

GA(ciudades , poblacion, elitismo,mutacion , generaciones)














