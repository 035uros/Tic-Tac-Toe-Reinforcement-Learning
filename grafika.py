import pygame, sys
import numpy as np
import pickle as pkl
import time

# inicijalizovanje pygame
pygame.init()

# KONSTANTE
SIRINA = 600
VISINA = 600
SIRINA_LINIJE = 7
SQUARE_SIZE = 200
POLUPRECNIK_O = 60
DEBLJINA_O = 15
DEBLJINA_X = 20
SPACE = 55
REDOVI = 3
KOLONE = 3
#boje
CRNA = (77, 77, 77)
ZUTA = (255, 185, 0)
CRVENA = (255, 73, 91)
ROZA = (224, 127, 174)
LILA = (159, 125, 193)
PLAVA = (152, 182, 255)
ZELENA = (60, 179, 113)
BOJA_LINIJA = (128, 158, 179)
BOJAX = LILA
BOJAO = ZELENA
SIVA = BOJA_LINIJA

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
                self.horizPobeda(i, 1)
                self.Kraj = True
                return 1
            if sum(self.tabla[i, :]) == -3:
                self.horizPobeda(i, -1)
                self.Kraj = True
                return -1
        # проверавмо да ли постоји колона са три иста симбола
        for i in range(KOLONE):
            if sum(self.tabla[:, i]) == 3:
                self.vertikalnaPobeda(i, 1)
                self.Kraj = True
                return 1
            if sum(self.tabla[:, i]) == -3:
                self.vertikalnaPobeda(i, -1)
                self.Kraj = True
                return -1
        # проверавмо да ли постоји дијагонала са три иста симбола
        d_sum1 = sum([self.tabla[i, i] for i in range(KOLONE)]) #главна дијагонала
        d_sum2 = sum([self.tabla[i, KOLONE - i - 1] for i in range(KOLONE)]) #супротна дијагонала
##        d_sum = max(abs(d_sum1), abs(d_sum2))
        if d_sum1 == 3:
            self.kosaLinijaDole(1)
            self.Kraj = True
            return 1
        elif d_sum1 == -3:
            self.kosaLinijaDole(-1)
            self.Kraj = True
            return -1
        elif d_sum2 == 3:
            self.kosaLinijaGore(1)
            self.Kraj = True
            return 1
        elif d_sum2 == -3:
            self.kosaLinijaGore(-1)
            self.Kraj = True
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


    def prikaziTablu(self):
        ekran = pygame.display.set_mode((SIRINA, VISINA))
        ekran.fill(PLAVA)

        #1. horizontalna
        pygame.draw.line(ekran, BOJA_LINIJA, (20,200), (580,200), SIRINA_LINIJE)
        #2. horizontalna
        pygame.draw.line(ekran, BOJA_LINIJA, (20,400), (580,400), SIRINA_LINIJE)
        #1. vertikalna
        pygame.draw.line(ekran, BOJA_LINIJA, (200,20), (200,580), SIRINA_LINIJE)
        #2. vertikalna
        pygame.draw.line(ekran, BOJA_LINIJA, (400,20), (400,580), SIRINA_LINIJE)
        print(self.tabla)
        for row in range(REDOVI):
            for col in range(KOLONE):
                if self.tabla[row][col] == 1:
                    pygame.draw.line(ekran, BOJAX, (col*200+40,row*200+160), (col*200+160, row*200+40), DEBLJINA_X)
                    pygame.draw.line(ekran, BOJAX, (col*200+40,row*200+40), (col*200+160,row*200+160), DEBLJINA_X)
                elif self.tabla[row][col] == -1:
                    pygame.draw.circle(ekran, BOJAO, (int(col*200+100),int(row*200+100)), POLUPRECNIK_O, DEBLJINA_O)

        pygame.display.update()

    def vertikalnaPobeda(self, col, player):
        posX = col*200 + 100

        if player == 1:
            color = BOJAX
        elif player == -1:
            color = BOJAO
        pygame.draw.line(ekran, color, (posX, 15), (posX, VISINA - 15), 15)

    def horizPobeda(self, row, player):
        posY = row*200 + 100

        if player == 1:
            color = BOJAX
        elif player == -1:
            color = BOJAO
        pygame.draw.line(ekran, color, (15, posY), (SIRINA - 15, posY), 15)

    def kosaLinijaGore(self, player):
        if player == 1:
            color = BOJAX
        elif player == -1:
            color = BOJAO
        pygame.draw.line(ekran, color, (15, VISINA - 15), (SIRINA - 15, 15), 15)

    def kosaLinijaDole(self, player):
        if player == 1:
            color = BOJAX
        elif player == -1:
            color = BOJAO
        pygame.draw.line(ekran, color, (15, 15), (SIRINA - 15, VISINA - 15), 15)
    
     
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
            for event in pygame.event.get():

                if event.type == pygame.MOUSEBUTTONDOWN:
                    X = event.pos[0]
                    Y = event.pos[1]
                    
                    row = int(Y // 200)
                    col = int(X // 200)

                    action = (row, col)
                    if action in pozicije:
                        return action

class Ekran:
    def __init__(self, title, width = 600, height = 600, fill = PLAVA):
        self.title = title
        self.width = width
        self.height = height
        self.fill = fill
        self.current = False

    def makeCurrent(self):
        pygame.display.set_caption(self.title)
        self.current = True
        self.screen = pygame.display.set_mode((self.width, self.height))

    def endCurrent(self):
        self.current = False

    def checkUpdate(self):
        return self.current

    def screenUpdate(self):
        if(self.current):
            self.screen.fill(self.fill)

    def returnTitle(self):
        return self.screen
        

    def prviEkran(self):
        font1 = pygame.font.Font('freesansbold.ttf', 50)
        text = font1.render('CHOOSE YOUR LEVEL', True, CRNA)
        textRect = text.get_rect()
        textRect.center = (SIRINA // 2, 100)
        self.screen.blit(text, textRect)

    def drugiEkran(self):
        font1 = pygame.font.Font('freesansbold.ttf', 50)
        text = font1.render('CHOOSE YOUR PLAYER', True, CRNA)
        textRect = text.get_rect()
        textRect.center = (SIRINA // 2, 100)
        self.screen.blit(text, textRect)
        

class Button:
    def __init__(self, x, y, sx, sy, bcolor, fbcolor, font, fontsize, fcolor, text):
        self.x = x
        self.y = y
        self.sx = sx
        self.sy = sy
        self.bcolor = bcolor
        self.fbcolor = fbcolor
        self.font = font
        self.fontsize = fontsize
        self.fcolor = fcolor
        self.text = text
        self.current = False
        self.buttonf = pygame.font.SysFont(font, fontsize)

    def showButton(self, display):
        if(self.current):
            pygame.draw.rect(display, self.fbcolor, (self.x, self.y, self.sx, self.sy))
        else:
            pygame.draw.rect(display, self.bcolor, (self.x, self.y, self.sx, self.sy))

        textSurface = self.buttonf.render(self.text, False, self.fcolor)
        display.blit(textSurface, ((self.x + (self.sx/2) - (self.fontsize/2)*(len(self.text)/2) - 5, (self.y + (self.sy/2) - (self.fontsize/2) - 4))))

    def focusCheck(self, mousepos, mouseclick):
        if(mousepos[0] >= self.x and mousepos[0] <= self.x + self.sx and mousepos[1] >= self.y and mousepos[1] <= self.y + self.sy):
            self.current = True
            return mouseclick[0]
        else:
            self.current = False
            return False
        
if __name__ == "__main__":

    ekran = pygame.display.set_mode((SIRINA, VISINA))
    ekran.fill(PLAVA)
   # file = 'meow.wav'
   # sound = pygame.mixer.Sound(file) #Load the wav
   # sound.play() #Play it

    menuEkran = Ekran('IKS OKS')
    menuEkran1 = Ekran('IKS OKS')
    menuEkran2 = Ekran('IKS OKS')
    menuEkran3 = Ekran('IKS OKS')
    treningEkran = Ekran('Treniranje')

    trenutni = menuEkran.makeCurrent()

    done = False

    HardButton = Button(220, 220, 150, 50, ZELENA, CRVENA, 'arial', 30, CRNA, 'HARD')
    MediumButton = Button(220, 280, 150, 50, ZELENA, ZUTA, 'arial', 30, CRNA, 'MEDIUM')
    EasyButton = Button(220, 340, 150, 50, ZELENA, ROZA, 'arial', 30, CRNA, 'EASY')
    TrainButton = Button(220, 400, 150, 50, ZELENA, LILA, 'arial', 30, CRNA, 'TRAIN')
    IgracX = Button(100, 300, 150, 50, ZELENA, LILA, 'arial', 30, CRNA, 'PLAYER X')
    IgracO = Button(350, 300, 150, 50, ZELENA, LILA, 'arial', 30, CRNA, 'PLAYER O')

    while not done:
        menuEkran.screenUpdate()
        menuEkran1.screenUpdate()
        menuEkran2.screenUpdate()
        menuEkran3.screenUpdate()
        treningEkran.screenUpdate()
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if menuEkran.checkUpdate():
            menuEkran.prviEkran()
            Hard = HardButton.focusCheck(mouse_pos, mouse_click)
            HardButton.showButton(menuEkran.returnTitle())
            Medium = MediumButton.focusCheck(mouse_pos, mouse_click)
            MediumButton.showButton(menuEkran.returnTitle())
            Easy = EasyButton.focusCheck(mouse_pos, mouse_click)
            EasyButton.showButton(menuEkran.returnTitle())
            Train = TrainButton.focusCheck(mouse_pos, mouse_click)
            TrainButton.showButton(menuEkran.returnTitle())
            

            if Hard:
                trenutni = menuEkran1.makeCurrent()
                menuEkran.endCurrent()
            elif Medium:
                trenutni = menuEkran2.makeCurrent()
                menuEkran.endCurrent()
            elif Easy:
                trenutni = menuEkran3.makeCurrent()
                menuEkran.endCurrent()
            elif Train:
                trenutni = treningEkran.makeCurrent()
                menuEkran.endCurrent()

                
        elif menuEkran1.checkUpdate():
            menuEkran1.drugiEkran()
            button0 = IgracX.focusCheck(mouse_pos, mouse_click)
            IgracX.showButton(menuEkran1.returnTitle())
            button1 = IgracO.focusCheck(mouse_pos, mouse_click)
            IgracO.showButton(menuEkran1.returnTitle())

            if button0:
                p1 = Covek("Човек")
                p2 = Igrac("Рачунар", stopaIstrazivanja=0)
                p2.ucitajPolitiku("politika_p2_hard")
                st = State(p1, p2)
                st.prikaziTablu()
                st.igraO()
                pygame.display.update()
                time.sleep(5)
                done = True
            elif button1:
                p1 = Igrac("Рачунар", stopaIstrazivanja=0)
                p1.ucitajPolitiku("politika_p1_hard")
                p2 = Covek("Човек")
                st = State(p1, p2)
                st.prikaziTablu()
                st.igraX()
                pygame.display.update()
                time.sleep(5)
                done = True
                
        elif menuEkran2.checkUpdate():
            menuEkran2.drugiEkran()
            button0 = IgracX.focusCheck(mouse_pos, mouse_click)
            IgracX.showButton(menuEkran2.returnTitle())
            button1 = IgracO.focusCheck(mouse_pos, mouse_click)
            IgracO.showButton(menuEkran2.returnTitle())

            if button0:
                p1 = Covek("Човек")
                p2 = Igrac("Рачунар", stopaIstrazivanja=0)
                p2.ucitajPolitiku("politika_p2_medium")
                st = State(p1, p2)
                st.prikaziTablu()
                st.igraO()
                pygame.display.update()
                time.sleep(5)
                done = True
            elif button1:
                p1 = Igrac("Рачунар", stopaIstrazivanja=0)
                p1.ucitajPolitiku("politika_p1_medium")
                p2 = Covek("Човек")
                st = State(p1, p2)
                st.prikaziTablu()
                st.igraX()
                pygame.display.update()
                time.sleep(5)
                done = True

        elif menuEkran3.checkUpdate():
            menuEkran3.drugiEkran()
            button0 = IgracX.focusCheck(mouse_pos, mouse_click)
            IgracX.showButton(menuEkran3.returnTitle())
            button1 = IgracO.focusCheck(mouse_pos, mouse_click)
            IgracO.showButton(menuEkran3.returnTitle())

            if button0:
                p1 = Covek("Човек")
                p2 = Igrac("Рачунар", stopaIstrazivanja=0)
                p2.ucitajPolitiku("politika_p2_easy")
                st = State(p1, p2)
                st.prikaziTablu()
                st.igraO()
                pygame.display.update()
                time.sleep(5)
                done = True
            elif button1:
                p1 = Igrac("Рачунар", stopaIstrazivanja=0)
                p1.ucitajPolitiku("politika_p1_easy")
                p2 = Covek("Човек")
                st = State(p1, p2)
                st.prikaziTablu()
                st.igraX()
                pygame.display.update()
                time.sleep(5)
                done = True
                
        elif treningEkran.checkUpdate():
            treningEkran.drugiEkran()
            button0 = IgracX.focusCheck(mouse_pos, mouse_click)
            IgracX.showButton(treningEkran.returnTitle())
            button1 = IgracO.focusCheck(mouse_pos, mouse_click)
            IgracO.showButton(treningEkran.returnTitle())

            if button0:
                p1 = Covek("Човек")
                p2 = Igrac("Рачунар", stopaIstrazivanja=0)
                p2.ucitajPolitiku("politika_p2")
                st = State(p1, p2)
                st.prikaziTablu()
                st.igraO()
                pygame.display.update()
                time.sleep(5)
                done = True
            elif button1:
                p1 = Igrac("Рачунар", stopaIstrazivanja=0)
                p1.ucitajPolitiku("politika_p1")
                p2 = Covek("Човек")
                st = State(p1, p2)
                st.prikaziTablu()
                st.igraX()
                pygame.display.update()
                time.sleep(5)
                done = True

        for event in pygame.event.get():
            if(event.type == pygame.QUIT):
                done = True

        pygame.display.update()
    pygame.quit()
