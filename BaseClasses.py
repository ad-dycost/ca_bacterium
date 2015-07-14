#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
#
# импорт необходимых модулей
from random import choice, gauss, randrange
import copy

# Класс, определяющий состояние клетки
class Cell():
	def __init__(self, sustenance):
		# вероятность клетки, быть занятой при инициализации
		self.arr_for_rand = 0, 0, 0, 0, 0, 0, 0, 0, 0, 1
		self.status = choice(self.arr_for_rand)
		# питательность клетки
		self.sustenance = sustenance


# Класс, определяющий состояние бактерий
class Bacterium():
	def __init__(self, appetite_mean, Time_life, e_bact_0):
		self.Energy = e_bact_0
		if Time_life > 0:
			self.Time_life = randrange(0, Time_life, 1)
		else:
			self.Time_life = 0
		self.appetite = gauss(appetite_mean, 0.02)



# класс, определяющий состояние поля
class Area():
	def __doc__(self):
		'''Основным элементом класса является аттрибут self.arraycell,
		 являющийся двумерным массивом с координатами элементов,
		 соответствыющимим координатам клеток.
		Каждой клетке соответствует экземпляр класса Cell.
		Если в клетке находится бактерия, то у экземпляра Cell имеется
		 аттрибут bact, являющийся экземпляром класса Bacterium'''

	def __init__(self, size_area, E_bact_tact, E_bact_step, E_bact_0, E_bact_max, E_bact_eat, E_env_0, E_bact_born, E_tresh_born, N_life, N_lag):
		self.size_area = size_area
		self.expense_energy_tact = E_bact_tact
		self.expense_energy_step = E_bact_step
		self.threshold_energy_limit = E_bact_max
		self.start_energy_bact = E_bact_0
		self.expense_appetite_mean = E_bact_eat
		self.expense_energy_born = E_bact_born
		self.threshold_energy_born = E_tresh_born
		self.N_life = N_life
		self.N_lag = N_lag
		self.list_bacterium = []
		# Список координат окружения клетки (возможных переходов)
		self.transition = ['-1,1','0,1','1,1','1,0','1,-1','0,-1','-1,-1','-1,0']
		# все состояния клеток будут писаться в массив
		self.arraycell = []
		for i in xrange(size_area):
			self.arraycell.append([])
			for j in xrange(size_area):
				self.arraycell[i].append([])
				self.cell = Cell(E_env_0)
				if self.cell.status == 1:
					self.cell.bact = Bacterium(self.expense_appetite_mean, self.N_life, self.start_energy_bact)
					self.list_bacterium.append([i,j])
				del self.cell.arr_for_rand
				self.arraycell[i][j] = self.cell
	
	# пересчет координаты, если она вдруг вышла за пределы массива
	def coord_env(self,coord):
		if coord >= self.size_area - 1:
			return 0
		elif coord < 0:
			return self.size_area - 1
		else:
			return coord

	# пересчитываем ближайшее окружение клеток
	def calc_environment(self,coord_cell):
		res = []
		for coord in self.transition:
			# расчет координат клеток окружения
			coord_1 = self.coord_env(coord_cell[0] + int(coord.split(',')[0]))
			coord_2 = self.coord_env(coord_cell[1] + int(coord.split(',')[1]))
			# проверка клеток на занятость
			if self.arraycell[coord_1][coord_2].status == 0:
				res.append([coord_1, coord_2])
		return res

	# запуск смены состояния
	def run(self, logfile):
		f = open(logfile,'a')
		# кормим бактерий
		self.eat()
		self.expense()
		self.death()
		self.go()
		self.reproduction()
		f.write(str(len(self.list_bacterium) / float(self.size_area) ** 2))
		f.write('\t')
		f.write(str(self.mud() / float(self.size_area) ** 2))
		f.write('\t')
		f.write(str(self.fatness()))
		f.write('\t')
		f.write(str(self.age()))
		f.write('\n')
		
	# питание бактерий
	def eat(self):
		for i in self.list_bacterium:
			# аппетит бактерии
			appetite = self.arraycell[i[0]][i[1]].bact.appetite
			# питательность клетки
			sustenance = self.arraycell[i[0]][i[1]].sustenance
			# энергия
			Energy = self.arraycell[i[0]][i[1]].bact.Energy
			if Energy < self.threshold_energy_limit:
				if sustenance < appetite:
					self.arraycell[i[0]][i[1]].bact.Energy = sustenance + Energy
					self.arraycell[i[0]][i[1]].sustenance = 0
				else:
					self.arraycell[i[0]][i[1]].bact.Energy = appetite + Energy
					self.arraycell[i[0]][i[1]].sustenance = sustenance - appetite
	
	# расход на жизнедеятельность
	def expense(self):
		for i in self.list_bacterium:
			# уменьшаем энергию бактерий
			self.arraycell[i[0]][i[1]].bact.Energy = self.arraycell[i[0]][i[1]].bact.Energy - self.expense_energy_tact
			# старим бактерию
			self.arraycell[i[0]][i[1]].bact.Time_life = self.arraycell[i[0]][i[1]].bact.Time_life + 1

	# смерть организмов
	def death(self):
		for i in self.list_bacterium:
			if self.arraycell[i[0]][i[1]].bact.Energy <= 0 or self.arraycell[i[0]][i[1]].bact.Time_life > self.N_life:
				self.arraycell[i[0]][i[1]].status = 0
				self.list_bacterium.remove(i)

	# передвижение
	def go(self):
		list_bacterium_old = copy.deepcopy(self.list_bacterium)
		for i in list_bacterium_old:
			if self.arraycell[i[0]][i[1]].bact.Energy > self.expense_energy_step:
				free_coord = self.calc_environment([i[0],i[1]])
				if len(free_coord) != 0:
					if len(free_coord) == 1:
						next_coord = free_coord[0]
					elif len(free_coord) > 1:
						next_coord = choice(free_coord)
					# добавление новой позиции бактерии
					self.arraycell[next_coord[0]][next_coord[1]].status = 1
					self.list_bacterium.append(next_coord)
					self.arraycell[next_coord[0]][next_coord[1]].bact = self.arraycell[i[0]][i[1]].bact
					# расход энергии на передвижение
					self.arraycell[next_coord[0]][next_coord[1]].bact.Energy = self.arraycell[next_coord[0]][next_coord[1]].bact.Energy - self.expense_energy_step
					# удаление предыдущей позиции бактерии
					self.arraycell[i[0]][i[1]].status = 0
					self.list_bacterium.remove(i)
					delattr(self.arraycell[i[0]][i[1]], "bact")
	
	# размножение бактерий
	def reproduction(self):
		list_bacterium_old = copy.deepcopy(self.list_bacterium)
		for i in list_bacterium_old:
			if self.arraycell[i[0]][i[1]].bact.Time_life >= self.N_lag and self.arraycell[i[0]][i[1]].bact.Energy >= self.threshold_energy_born:
				free_coord = self.calc_environment([i[0],i[1]])
				if len(free_coord) != 0:
					if len(free_coord) == 1:
						next_coord = free_coord[0]
					elif len(free_coord) > 1:
						next_coord = choice(free_coord)
					# добавление новой позиции бактерии
					self.arraycell[next_coord[0]][next_coord[1]].status = 1
					self.list_bacterium.append(next_coord)
					self.arraycell[next_coord[0]][next_coord[1]].bact = Bacterium(self.expense_appetite_mean, 0, self.start_energy_bact)
					# расход энергии на размножение
					self.arraycell[i[0]][i[1]].bact.Energy = self.arraycell[i[0]][i[1]].bact.Energy - self.start_energy_bact - self.expense_energy_born
	
	# расчет остатка неживой органики в среде
	def mud(self):
		res = 0
		# суммируем питательность по всем клеткам
		for i in xrange(self.size_area):
			for j in xrange(self.size_area):
				res = res + self.arraycell[i][j].sustenance
		return res

	# расчет упитанности бактерий
	def fatness(self):
		res = 0
		# суммируем энергию всех бактерий
		for i in self.list_bacterium:
			res = res + self.arraycell[i[0]][i[1]].bact.Energy
		try:
			return res / len(self.list_bacterium)
		except:
			return 0

	# расчет среднего возраста бактерий
	def age(self):
		res = 0
		# суммируем энергию всех бактерий
		for i in self.list_bacterium:
			res = res + self.arraycell[i[0]][i[1]].bact.Time_life
		try:
			return res / len(self.list_bacterium)
		except:
			return 0

