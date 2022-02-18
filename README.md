# Tic-Tac-Toe-Reinforcement-Learning
Tic Tac Toe Reinforcement Learning

# Завршни пројекат за предмет Основи машинског учења, Јануар 2022. Факултет инжењерских наука, универзитет у Крагујевцу.

Популарна игра "Икс-Окс" је реализована у програмском језику Python помоћу методе учења подстицајем.
Потребно је преузети све датотеке односно XOgame.py, пропратне политике и meow.wav фајл, сместити их у један фолдер и покренути. Уколико нешто није у реду проверите вашу PyGame инсталацију.
Уколико желимо да тренирамо можемо додати следћу линију у мејн функцију: ` st.trening(int(trening))` где је trening број партија за тренирање. Алтернативно, можемо користити и датотеку xowithoutpygame.py и покренути одређени број тренинга из конзоле. Обратити пажњу на то да је излаз тренинга увек назван politika_p1 и politika_p2 за првог и другог играча респективно, док су већ истрениране политике фиксне и већ назване са суфиксима _hard, _medium, _easy. Кликом на Train дугме у PyGame-у можете одиграти партију са свеже истренираном политиком!

У даљем тексту ће бити објашњени кључни делови кода и семантика иза њих.

  Класа State - у осови има задатак да омогући играње игре. У њој се чувају подаци о стању табле и њене   методе проверавју регуларност и резултат игре. Омогућава тренирање виртуелног играча.
  
  Класа Играч и Човек - декларише виртуелног и људског играча, респективно.
  
  Метода која нам даје уникатну вредност тренутног стања на табли:
 ``` def getHash(self):
    self.hashTable = str(self.tabla.reshape(REDOVI * KOLONE))
    return self.hashTable
 ```
  
 
 Метода за доделу награде, награђује играче у односу на постигнути резултат.
```def dodelaNagrade(self):
        rezultat = self.sudija()
        if rezultat == 1:
            self.p1.doprinosNagrade(1) # уколико је p1 победио дајемо му награду 1
            self.p2.doprinosNagrade(0) # уколико је p2 изгубио дајемо му награду 0
        elif rezultat == -1:
            self.p1.doprinosNagrade(0) # уколико је p1 изгубио дајемо му награду 0
            self.p2.doprinosNagrade(1) # уколико је p2 победио дајемо му награду 1
        else:
            self.p1.doprinosNagrade(0.5) # уколико је нерешено делимо награду на пола међу играчима
            self.p2.doprinosNagrade(0.5)
```
            
Битне променљиве класе Играч:<br/>  stopaUcenja - стопа учења је параметар подешавања у алгоритму оптимизације који одређујевеличину корака при свакој итерацији док се креће ка минималној функцији губитка.  stopaIstrazivanja - exploration rate, овде подешавамо однос истраживања нових путања (насумичним потезима) и праћења досад научених путања, default вредност је 0,3 што је 30% односно у 70% случајева ће рачунар одиграти потез применом научених потеза.
<br/> decoy_gamma - редуковање награде у односну на број потеза, повећањем корака смањујемо вредност укупне награде јер не желимо да подједнако вреднујемо победу у 3 потеза као победу у 5 потеза.
      
## Kада се игра заврши, вршимо бекпропагацију и ажуирирамо вредности стања
    def doprinosNagrade(self, nagrada):
        for i in reversed(self.states): # окрећемо потезе тако да кренемо од последњег
            if self.states_value.get(i) is None: # проверавамо да ли постоји вредност за потез
                self.states_value[i] = 0 # уколико не посотји додељујемо нулу
            self.states_value[i] += self.stopaUcenja * (self.decay_gamma * nagrada - self.states_value[i]) # ажурирамо вредност стања помоћу додавања на тренутну вредност стања разлику производа награде и редукције награде и тренутне вредности помножене са стопом учења
            nagrada = self.states_value[i] #нова вредност награде

## Реализовање игрице 'Икс-Окс' помоћу библиотеке PyGame:

Класа Ekran приказује одговарајуће екране за одговарајуће акције корисника. Први екран који се приказује је главни мени, док се други екран приказује тек након што корисник одабере једну од опција из главног менија.
Класа Button служи за прављење тастера који мењају боју када пређемо курсором преко њих.

Док играмо игру, једну од главних улога игра функција `prikaziTablu(self)` која исцртава таблу и облике X и O на местима која су попуњена, односно, која су већ одабрали рачунар или људски играч. Та функција се налази у класи State заједно са још неким функцијама задужним за исцртавање линија преко X или O облика уколико дође до победе.
```
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
```
Коначно, исцртавање облика на жељено место које бира људски играч се реализује преко класе Covek. Када људски играч кликне на одређено празно поље, то се региструје помоћу функције `chooseAction(self, pozicije)` тако што се ново стање уноси у матрицу стања табле, након чега се изглед табле ажурира да би се исцртао облик.
```
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
```
