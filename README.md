# Tic-Tac-Toe-Reinforcement-Learning
Tic Tac Toe Reinforcement Learning

# Завршни пројекат за предмет Основи машинског учења, Јануар 2022. Факултет инжењерских наука, универзитет у Крагујевцу.

Популарна игра "Икс-Окс" је реализована у програмском језику Python помоћу методе учења подстицајем.
Потребно је преузети све датотеке односно xo.py и пропратне политике, сместити их у један фолдер и покренути. Уколико нешто није у реду проверите вашу PyGame инсталацију.
Уколико желимо да тренирамо можемо додати следћу линију у мејн функцију:` st.trening(int(trening))` где је trening број партија за тренирање. Алтернативно, можемо користити и датотеку xowithoutpygame.py и покренути одређени број тренинга из конзоле. Обратити пажњу на то да је излаз тренинга увек назван politika_p1 и politika_p2 за првог и другог играча респективно, док су већ истрениране политике фиксне и већ назване са суфиксима _hard, _medium, _easy.

У даљем тексту ће бити објањени кључни делови кода и семантика иза њих.

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
```
            
Битне променљиве класе Играч:  stopaUcenja - стопа учења је параметар подешавања у алгоритму оптимизације који одређујевеличину корака при свакој итерацији док се креће ка минималној функцији губитка.  stopaIstrazivanja - exploration rate, овде подешавамо однос истраживања нових путања (насумичним потезима) и праћења досад научених путања, default вредност је 0,3 што је 30% односно у 70% случајева ће рачунар одиграти потез применом научених потеза.
  decoy_gamma - редуковање награде у односну на број потеза, повећањем корака смањујемо вредност укупне награде јер не желимо да подједнако вреднујемо победу у 3 потеза као победу у 5 потеза.
      
# Kада се игра заврши, вршимо бекпропагацију и ажуирирамо вредности стања
    def doprinosNagrade(self, nagrada):
        for i in reversed(self.states): # окрећемо потезе тако да кренемо од последњег
            if self.states_value.get(i) is None: # проверавамо да ли постоји вредност за потез
                self.states_value[i] = 0 # уколико не посотји додељујемо нулу
            self.states_value[i] += self.stopaUcenja * (self.decay_gamma * nagrada - self.states_value[i]) # ажурирамо вредност стања помоћу додавања на тренутну вредност стања разлику производа награде и редукције награде и тренутне вредности помножене са стопом учења
            nagrada = self.states_value[i] #нова вредност награде
