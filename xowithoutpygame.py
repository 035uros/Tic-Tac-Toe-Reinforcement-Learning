# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 18:38:33 2022

@authors: Anđela and Uroš
"""

import numpy as np
import pickle as pkl

REDOVI = 3
KOLONE = 3

# класа State омогућава креирање табле, праћење и проверу резултата и победника, дели награде и проглашава крај игре
class State:
    def __init__(self, p1, p2):
        self.tabla = np.zeros((REDOVI, KOLONE)) #табла величине 3х3 је у старту попуњена нулама
        self.p1 = p1
        self.p2 = p2
        self.Kraj = False  # флег који нам означава крај игре када се постави на True
        self.hashTable = None
        self.simbolIgraca = 1 #играч p1 игра први
        
    def getHash(self):
        self.hashTable = str(self.tabla.reshape(REDOVI * KOLONE)) #јединствена вредност за тренутно стање на табли
        return self.hashTable

    def sudija(self):
        # проверавмо да ли постоји ред са три иста симбола
        for i in range(REDOVI):
            if sum(self.tabla[i, :]) == 3:
                self.Kraj = True
                return 1
            if sum(self.tabla[i, :]) == -3:
                self.Kraj = True
                return -1
        # проверавмо да ли постоји колона са три иста симбола
        for i in range(KOLONE):
            if sum(self.tabla[:, i]) == 3:
                self.Kraj = True
                return 1
            if sum(self.tabla[:, i]) == -3:
                self.Kraj = True
                return -1
        # проверавмо да ли постоји дијагонала са три иста симбола
        d_sum1 = sum([self.tabla[i, i] for i in range(KOLONE)]) #главна дијагонала
        d_sum2 = sum([self.tabla[i, KOLONE - i - 1] for i in range(KOLONE)]) #супротна дијагонала
        d_sum = max(abs(d_sum1), abs(d_sum2))
        if d_sum == 3:
            self.Kraj = True
            if d_sum1 == 3 or d_sum2 == 3:
                return 1
            else:
                return -1
            
            # уколико је збир 3 победник је Х а уколико је збир -3 победник је О (Х = 1, О = -1)
            # враћамо број 1 уколико је Х победник односно -1 уколико је О победник

        # игра се завршава нерешеним резултатом уколико ни један од услове изнад није испуњен а притом нам није остала ни једна слободна позиција
        if len(self.slobodnePozicije()) == 0:
            self.Kraj = True
            return 0
        # у случају да и даље има слободних позиција настављамо са играњем
        self.Kraj = False
        return None
    
    def slobodnePozicije(self):
        pozicije = [] #дефинишемо празану листу која ће садржати слободне позиције
        for i in range(REDOVI):
            for j in range(KOLONE):
                if self.tabla[i, j] == 0: # 0 означава да је позиција слободна
                    pozicije.append((i, j))  # уписујемо индексе слободних позиција у листу
        return pozicije
    
    def updateState(self, pozicija):
        self.tabla[pozicija] = self.simbolIgraca #уписујемо 1(Х) или -1(О) на дату позицију 
        
        # додељујемо супротном играчу потез мењајући simbolIgraca у 1 односно -1
        if self.simbolIgraca == 1:
            self.simbolIgraca = -1 # промена из Х у О
        else:
            self.simbolIgraca = 1 # промена из О у Х
            
    # метода се позива након завршетка партије
    def dodelaNagrade(self):
        rezultat = self.sudija()
        # Бекпропагација награде
        if rezultat == 1:
            self.p1.doprinosNagrade(1) # уколико је p1 победио дајемо му награду 1
            self.p2.doprinosNagrade(0) # уколико је p2 изгубио дајемо му награду 0
        elif rezultat == -1:
            self.p1.doprinosNagrade(0) # уколико је p1 изгубио дајемо му награду 0
            self.p2.doprinosNagrade(1) # уколико је p2 победио дајемо му награду 1
        else:
            self.p1.doprinosNagrade(0.5) # уколико је нерешено делимо награду на пола међу играчима
            self.p2.doprinosNagrade(0.5)
            
    # враћање табле на почетне вредности
    def reset(self):
        self.tabla = np.zeros((REDOVI, KOLONE))
        self.Kraj = False
        self.hashTable = None
        self.simbolIgraca = 1
        
    def trening(self, partije=1000):
        for i in range(partije):
            if i % 1000 == 0:
                print("Наши виртуелни играчи су одиграли {} партија".format(i))
            while not self.Kraj:
                # Потез првог играча
                pozicije = self.slobodnePozicije() # узимамо стање талбе, тј. слободне позиције
                p1_action = self.p1.chooseAction(pozicije, self.tabla, self.simbolIgraca) # бирамо потез
                self.updateState(p1_action) # одиграмо потез
                hashTable = self.getHash() # стање на табли је промењено па узумамо нову хеш вредност
                self.p1.addState(hashTable) # додајемо стање 

                rezultat = self.sudija()
                if rezultat is not None: # уколико је игра завршена додељујемо награде и ресетујемо игру
                    self.dodelaNagrade()
                    self.p1.reset()
                    self.p2.reset()
                    self.reset()
                    break
                else:
                    # Потез другог играча
                    pozicije = self.slobodnePozicije() # узимамо стање талбе, тј. слободне позиције
                    p2_action = self.p2.chooseAction(pozicije, self.tabla, self.simbolIgraca) # бирамо потез
                    self.updateState(p2_action) # одиграмо потез
                    hashTable = self.getHash() # стање на табли је промењено па узумамо нову хеш вредност
                    self.p2.addState(hashTable) # додајемо стање 

                    rezultat = self.sudija()
                    if rezultat is not None: # уколико је игра завршена додељујемо награде и ресетујемо игру
                        self.dodelaNagrade()
                        self.p1.reset()
                        self.p2.reset()
                        self.reset()
                        break
        print("Тренинг је готов!")
        self.p1.sacuvajPolitiku()
        self.p2.sacuvajPolitiku()
                    
    # играње против реалног играча са позиције Х
    def igraX(self):
        while not self.Kraj:
            # Рачунар је на потезу
            pozicije = self.slobodnePozicije() # узимамо стање талбе, тј. слободне позиције
            p1_action = self.p1.chooseAction(pozicije, self.tabla, self.simbolIgraca) # бирамо потез
            self.updateState(p1_action) # одиграмо потез
            self.prikaziTablu() # приказујемо таблу -------------------
            
            rezultat = self.sudija()
            if rezultat is not None:  # уколико је игра завршена додељујемо награде и ресетујемо игру
                if rezultat == 1:
                    print(self.p1.ime, "је победио!") # проглашавање рачунара за победника
                else:
                    print("Резултат је нерешен!") # проглашавање нерешеног резултата
                self.reset()
                break

            else:
                # Човек је на потезу
                pozicije = self.slobodnePozicije() # узимамо стање талбе, тј. слободне позиције
                p2_action = self.p2.chooseAction(pozicije) # бирамо потез
                self.updateState(p2_action) # одиграмо потез
                self.prikaziTablu() # приказујемо таблу -------------------
                
                rezultat = self.sudija()
                if rezultat is not None:
                    if rezultat == -1:
                        print(self.p2.ime, "је победио!") # проглашавање човека за победника
                    else:
                        print("Резултат је нерешен!") # проглашавање нерешеног резултата
                    self.reset()
                    break
                
    # играње против реалног играча са позиције O
    def igraO(self):
        while not self.Kraj:
            # Човек је на потезу
            pozicije = self.slobodnePozicije() # узимамо стање талбе, тј. слободне позиције
            p1_action = self.p1.chooseAction(pozicije) # бирамо потез
            self.updateState(p1_action) # одиграмо потез
            self.prikaziTablu() # приказујемо таблу -------------------
            
            rezultat = self.sudija()
            if rezultat is not None:
                if rezultat == 1:
                    print(self.p1.ime, "је победио!") # проглашавање човека за победника
                else:
                        print("Резултат је нерешен!") # проглашавање нерешеног резултата
                self.reset()
                break

            else:
                # Рачунар је на потезу 
                pozicije = self.slobodnePozicije() # узимамо стање талбе, тј. слободне позиције
                p2_action = self.p2.chooseAction(pozicije, self.tabla, self.simbolIgraca) # бирамо потез
                self.updateState(p2_action) # одиграмо потез
                self.prikaziTablu() # приказујемо таблу -------------------
                
                rezultat = self.sudija()
                if rezultat is not None:
                    if rezultat == -1:
                        print(self.p2.ime, "је победио!") # проглашавање рачунара за победника
                    else:
                        print("Резултат је нерешен!") # проглашавање нерешеног резултата
                    self.reset()
                    break
                
    def prikaziTablu(self):
        # p1 је играч Х док је p2 играч О
        for i in range(0, REDOVI):
            print('-------------')
            out = '| '
            for j in range(0, KOLONE):
                if self.tabla[i, j] == 1:
                    token = 'x'
                if self.tabla[i, j] == -1:
                    token = 'o'
                if self.tabla[i, j] == 0:
                    token = ' '
                out += token + ' | '
            print(out)
        print('-------------')
        
class Igrac:
    def __init__(self, ime, stopaIstrazivanja=0.3):
        self.ime = ime # назив играча
        self.states = []  # овде бележимо све одигране потезе
        self.stopaUcenja = 0.2 #learning rate
        self.stopaIstrazivanja = stopaIstrazivanja #exploration rate, овде подешавамо однос истраживања нових путања (насумичним потезима) и праћења досад научених путања, default вредност је 0,3 што је 30% односно у 70% случајева ће рачунар одиграти потез применом научених потеза
        self.decay_gamma = 0.9  # редуковање награде у односну на број потеза, повећањем корака смањујемо вредност укупне награде јер не желимо да подједнако вреднујемо победу у 3 потеза као победу у 5 потеза.
        self.states_value = {}  # state -> value, памтимо стања и вредности у речнику

    def getHash(self, tabla):
        hashTable = str(tabla.reshape(REDOVI * KOLONE)) #јединствена вредност за тренутно стање на табли
        return hashTable
    
    def chooseAction(self, pozicije, trenutna_tabla, simbol):
        if np.random.uniform(0, 1) <= self.stopaIstrazivanja: # генеришемо насумични број у интервалу од 0 до 1 и упоређујемо са стопом истраживања, на основу резултата бирамо да ли ћемо начинити насумични потез или не
            indeks = np.random.choice(len(pozicije)) # уколико смо одлучили да начинимо насумичан потез, бирамо насумични индекс
            action = pozicije[indeks] # бирамо позицију на коју ћемо да одиграмо потез
        else:
            value_max = -10000 #дефинишемо веома малу почетну максималну вредност која ће после прве итерације бити постављена на неку од вредности добијену игром
            for p in pozicije:
                nova_tabla = trenutna_tabla.copy() # копирамо тренутну таблу
                nova_tabla[p] = simbol  # уписујемо нови симбол на позицију
                novi_hashTable = self.getHash(nova_tabla) # генеришемо нову хеш вредност
                #if self.states_value.get(novi_hashTable) is None: #проверавамо да ли смо добили неку повољну вреност
                    #value = 0 # уколико нисмо 
                #else:
                    #self.states_value.get(novi_hashTable) # уколико јесмо, чувамо ту хеш вредност
                value = 0 if self.states_value.get(novi_hashTable) is None else self.states_value.get(novi_hashTable)
                if value >= value_max: # помоћу овог услова бирамо следећи потез са најбољом вероватноћом за добар потез
                    value_max = value # ажурирамо нову макс вреност
                    action = p # чувамо индекс акције
        return action # враћамо позицију на табли на коју желимо да одиграмо потез
    
   
     # додајемо нову хеш вредност
    def addState(self, state):
        self.states.append(state)
        
    # када се игра заврши, вршимо бекпропагацију и ажуирирамо вредности стања
    def doprinosNagrade(self, nagrada):
        for i in reversed(self.states): # окрећемо потезе тако да кренемо од последњег
            if self.states_value.get(i) is None: # проверавамо да ли постоји вредност за потез
                self.states_value[i] = 0 # уколико не посотји додељујемо нулу
            self.states_value[i] += self.stopaUcenja * (self.decay_gamma * nagrada - self.states_value[i]) # ажурирамо вредност стања помоћу додавања на тренутну вредност стања разлику производа награде и редукције награде и тренутне вредности помножене са стопом учења
            nagrada = self.states_value[i] #нова вредност награде
        

    # ресетујемо стања
    def reset(self):
        self.states = []

    #чување политике
    def sacuvajPolitiku(self):
        with open('politika_' + str(self.ime), 'wb') as fw: # otvaramo датотеку у којој ћемо чувати вредност атрибута објекта
            pkl.dump(self.states_value, fw) # уписујемо бинарно вредност потеза
            fw.close() # затварамо датотеку

    #читање политике
    def ucitajPolitiku(self, datoteka):
        fr = open(datoteka, 'rb')
        self.states_value = pkl.load(fr) # додељивање политике атрибуту објекта
        fr.close()
        
class Covek:
    def __init__(self, ime):
        self.ime = ime

    def chooseAction(self, pozicije):
        while True:
            row = int(input("Унеси ред:"))
            col = int(input("Унеси колону:"))
            action = (row, col)
            if action in pozicije:
                return action
if __name__ == "__main__":
    
    print("Опције: 1 - тренинг, 2 - Играч X, 3 - Играч O:")
    opcija = input()
    
    if(opcija == '1'):
        trening = input("Број партија за тренирање? оптимално од 1000 - 50000: ")
        p1 = Igrac("p1")
        p2 = Igrac("p2")

        st = State(p1, p2)
        print("Тренирамо...")
        st.trening(int(trening))
        
    elif(opcija == '3'):
        p1 = Igrac("Рачунар", stopaIstrazivanja=0)
        p1.ucitajPolitiku("politika_p1")
        
        p2 = Covek("Човек")
        st = State(p1, p2)
        st.igraX()
    else:
        p1 = Covek("Човек")
        
        p2 = Igrac("Рачунар", stopaIstrazivanja=0)
        p2.ucitajPolitiku("politika_p2")
        st = State(p1, p2)
        st.igraO()
