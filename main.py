#! /usr/bin/env python
# -*- mode: python; coding: utf-8 -*-
#
# импорт необходимых модулей
#import numpy

from time import time
import BaseClasses


time_0 = time()

# Файл, куда будут записываться результаты
logfile = "1.txt"

# Ввод констант
size_area = 50
E_bact_born = 0.01
E_tresh_born = 0.4
E_bact_max = 1
E_bact_tact = 0.004
E_bact_step = 0.01
E_bact_eat = 0.02
E_env_0 = 2.
N_life = 100.
N_lag = 10.


# Инициализация поля клеточного автомата
StateArea = BaseClasses.Area(size_area, E_bact_tact, E_bact_step, E_bact_max, E_bact_eat, E_env_0, E_bact_born, E_tresh_born, N_life, N_lag)


# Очищаем предыдущие результаты
f = open(logfile,'w')
f.write("")
f.close()

# инициализация цикла жизни
for i in xrange(400):
	StateArea.run(logfile)
