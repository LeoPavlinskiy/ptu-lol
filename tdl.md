# Технический дизайн-лист (TDL): Алгоритм подбора параметров верхней панели крыла

## Общая структура проекта

```
wing-panel-design/
├── main.py                 # Главный файл запуска
├── aircraft_data.py        # Класс для хранения данных о самолёте
├── material.py             # Класс для свойств материала
├── geometry.py             # Расчёт геометрии крыла и сечений
├── loads.py                # Расчёт нагрузок и изгибающих моментов
├── panel.py                # Класс панели с параметрами
├── stringer.py             # Класс стрингера с геометрией
├── stability.py            # Расчёт критических напряжений
├── reduction.py            # Методы редуцирования обшивки
├── strength.py             # Расчёт напряжений и проверка прочности
├── optimization.py         # Подбор параметров панели (опционально)
├── output.py               # Вывод результатов
├── utils.py                # Вспомогательные функции
├── data/
│   ├── deep-research-1-result.md  # Параметры самолёта
│   ├── deep-research-2-result.md  # Свойства материала В95
│   ├── deep-research-3-result.md  # Методы расчёта устойчивости
│   ├── deep-research-4-result.md  # Методы редуцирования
│   └── bot-stuff/                 # Данные от бота
├── requirements.txt        # Зависимости Python
└── README.md              # Документация
```

---

## Этап 1: Подготовка и настройка окружения

### Задача 1.1: Создание структуры проекта
**Приоритет:** Высокий  
**Статус:** Завершено

**Шаги:**
1. Создать директорию `wing-panel-design/`
2. Создать поддиректорию `data/`
3. Создать поддиректорию `data/bot-stuff/`
4. Скопировать файлы deep-research в `data/`
5. Скопировать файлы из `bot-stuff/` в `data/bot-stuff/`
6. Создать пустые файлы для всех модулей согласно архитектуре
7. Создать `requirements.txt` с зависимостями:
   - numpy >= 1.21.0
   - scipy >= 1.7.0
   - matplotlib >= 3.4.0
   - pandas >= 1.3.0 (опционально)

**Критерии готовности:**
- Все директории созданы
- Все файлы созданы
- requirements.txt заполнен

---

### Задача 1.2: Извлечение данных из эпюр бота
**Приоритет:** Высокий  
**Статус:** Завершено

**Шаги:**
1. Открыть файл `data/bot-stuff/photo_2025-12-04 17.57.59.jpeg`
2. Определить масштаб графика (ось X - размах крыла, ось Y - изгибающий момент)
3. Определить значения изгибающих моментов для сечений:
   - z = 0.2L (где L = 17.16 м - полуразмах)
   - z = 0.4L
   - z = 0.6L
   - z = 0.8L
4. Открыть файл `data/bot-stuff/photo_2025-12-04 17.58.00.jpeg`
5. Определить значения поперечных сил для тех же сечений (если доступно)
6. Записать значения в файл `data/bot-moments.txt` в формате:
   ```
   # Изгибающие моменты из бота Чедрика (Н·м)
   # Сечение z/L | z (м) | M (Н·м)
   0.2 | 3.432 | <значение>
   0.4 | 6.864 | <значение>
   0.6 | 10.296 | <значение>
   0.8 | 13.728 | <значение>
   ```
7. Записать перегрузки в файл `data/bot-overloads.txt`:
   ```
   # Расчётные перегрузки
   ny_max = 3.75
   ny_min = -1.5
   safety_factor = 1.5
   ```

**Критерии готовности:**
- Все значения извлечены и записаны
- Формат данных стандартизирован
- Значения проверены на разумность

---

## Этап 2: Реализация базовых классов данных

### Задача 2.1: Класс Aircraft (aircraft_data.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задача 1.1

**Шаги:**

1. **Создать класс Aircraft:**
   ```python
   class Aircraft:
       def __init__(self):
           # Параметры из deep-research-1-result.md
           self.name = "Boeing 737-800"
           self.class_type = "пассажирский, магистральный, узкофюзеляжный"
           self.mtow = 79016  # кг
           self.normal_takeoff_mass = 70000  # кг (для расчётов)
           
           # Геометрия крыла
           self.wing_span = 34.32  # м
           self.wing_area = 124.6  # м²
           self.aspect_ratio = 9.45
           self.sweep_le = 28.5  # градусы (по передней кромке)
           self.incidence_angle = 3.0  # градусы
           self.dihedral = 6.0  # градусы
           self.airfoil_type = "Boeing 737 midspan airfoil"
           
           # Хорды
           self.root_chord = 6.65  # м
           self.tip_chord = 1.25  # м
           self.taper_ratio = 0.19
           
           # Конструктивно-силовая схема
           self.spar_count = 2
           self.spar_positions_root = {
               'front': 0.15,  # доля хорды
               'rear': 0.60
           }
           self.spar_positions_tip = {
               'front': 0.20,
               'rear': 0.74
           }
           self.structure_type = "лонжеронно-стрингерный кессонный"
           
           # Высота кессона (интерполяция)
           self.box_height_root = 0.5  # м
           self.box_height_mid = 0.35  # м
           self.box_height_tip = 0.2  # м
   ```

2. **Добавить методы:**
   - `get_chord(z_relative)` - хорда в сечении z/L
   - `get_box_height(z_relative)` - высота кессона в сечении
   - `get_spar_positions(z_relative)` - положение лонжеронов (интерполяция)
   - `get_box_width(z_relative)` - ширина кессона (расстояние между лонжеронами)

3. **Реализовать интерполяцию:**
   - Линейная интерполяция между корнем (z=0), серединой (z=0.5L) и законцовкой (z=L)
   - Формулы для трапециевидного крыла

4. **Добавить валидацию:**
   - Проверка диапазона z_relative (0 <= z_relative <= 1)
   - Проверка физической разумности значений

**Критерии готовности:**
- Класс создан и протестирован
- Все методы работают корректно
- Интерполяция даёт разумные значения
- Добавлены docstrings для всех методов

---

### Задача 2.2: Класс Material (material.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задача 1.1

**Шаги:**

1. **Создать класс Material:**
   ```python
   class Material:
       def __init__(self, material_type='B95T1', product_type='sheet'):
           # Параметры из deep-research-2-result.md
           if material_type == 'B95T1' and product_type == 'sheet':
               # Лист
               self.ultimate_strength = 520e6  # Па (σв)
               self.yield_strength = 440e6  # Па (σ0.2)
               self.proportional_limit = 0.8 * self.yield_strength  # Па (σпц)
           elif material_type == 'B95T1' and product_type == 'profile':
               # Профиль
               self.ultimate_strength = 520e6  # Па
               self.yield_strength = 450e6  # Па
               self.proportional_limit = 0.8 * self.yield_strength  # Па
           
           # Общие свойства
           self.young_modulus = 74e9  # Па (E)
           self.shear_modulus = 26e9  # Па (G)
           self.poisson_ratio = 0.32  # μ
           self.density = 2850  # кг/м³
           
           # Допускаемые напряжения
           self.allowable_tension = 350e6  # Па
           self.allowable_compression = 300e6  # Па
           self.allowable_shear = 180e6  # Па
           
           # Коэффициенты запаса
           self.safety_factor_ultimate = 1.5
           self.safety_factor_yield = 1.15
   ```

2. **Добавить методы:**
   - `get_allowable_stress(load_type)` - допускаемое напряжение по типу нагрузки
   - `check_strength(stress, load_type)` - проверка прочности
   - `get_reduced_modulus(stress)` - редуцированный модуль (если нужно)

3. **Добавить валидацию:**
   - Проверка типа материала
   - Проверка типа продукции

**Критерии готовности:**
- Класс создан
- Все свойства соответствуют данным из deep-research-2-result.md
- Методы работают корректно
- Добавлены docstrings

---

### Задача 2.3: Класс Panel (panel.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задачи 2.1, 2.2

**Шаги:**

1. **Создать класс Panel:**
   ```python
   class Panel:
       def __init__(self, z_relative, aircraft, material):
           self.z_relative = z_relative  # Положение сечения (0.2, 0.4, 0.6, 0.8)
           self.aircraft = aircraft
           self.material = material
           
           # Геометрия панели
           self.skin_thickness = None  # м (подбирается)
           self.stringer_spacing = None  # м (шаг стрингеров)
           self.stringer_count = None  # количество стрингеров
           self.panel_width = None  # м (ширина панели между лонжеронами)
           
           # Стрингеры
           self.stringers = []  # список объектов Stringer
           
           # Эффективные параметры (после редуцирования)
           self.effective_skin_width = None
           self.reduced_area = None
           self.reduced_inertia = None
   ```

2. **Добавить методы:**
   - `calculate_panel_width()` - ширина панели между лонжеронами
   - `calculate_effective_area()` - эффективная площадь с учётом редуцирования
   - `calculate_effective_inertia()` - эффективный момент инерции
   - `add_stringer(stringer)` - добавление стрингера

**Критерии готовности:**
- Класс создан
- Методы реализованы
- Добавлены docstrings

---

### Задача 2.4: Класс Stringer (stringer.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задача 2.2

**Шаги:**

1. **Создать класс Stringer:**
   ```python
   class Stringer:
       def __init__(self, stringer_type='Z'):
           self.type = stringer_type  # 'Z', 'C', 'T', 'L'
           
           # Геометрические параметры (в метрах)
           self.web_height = None  # высота стенки
           self.flange_width = None  # ширина полки
           self.web_thickness = None  # толщина стенки
           self.flange_thickness = None  # толщина полки
           self.radius = None  # радиус закругления
           
           # Расчётные параметры
           self.area = None  # площадь поперечного сечения
           self.inertia = None  # момент инерции относительно собственной оси
           self.effective_area = None  # приведённая площадь с обшивкой
   ```

2. **Добавить методы:**
   - `calculate_area()` - расчёт площади поперечного сечения
   - `calculate_inertia()` - расчёт момента инерции
   - `calculate_effective_area(skin_thickness, effective_width)` - приведённая площадь с обшивкой
   - `set_geometry_from_typical()` - установка типовых размеров для Boeing 737-800

3. **Реализовать расчёты для разных типов:**
   - Z-образный стрингер
   - Швеллерный (C-образный)
   - Тавровый
   - Уголковый

**Критерии готовности:**
- Класс создан
- Методы расчёта реализованы для всех типов
- Добавлены docstrings

---

## Этап 3: Реализация модуля геометрии

### Задача 3.1: Функции расчёта геометрии крыла (geometry.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задача 2.1

**Шаги:**

1. **Создать функцию расчёта хорды:**
   ```python
   def calculate_chord(z_relative, root_chord, tip_chord, span):
       """
       Расчёт хорды в сечении z_relative
       Линейная интерполяция для трапециевидного крыла
       """
       z_absolute = z_relative * span / 2  # расстояние от корня
       chord = root_chord - (root_chord - tip_chord) * z_relative
       return chord
   ```

2. **Создать функцию расчёта высоты кессона:**
   ```python
   def calculate_box_height(z_relative, aircraft):
       """
       Интерполяция высоты кессона между корнем, серединой и законцовкой
       """
       if z_relative <= 0.5:
           # Интерполяция между корнем и серединой
           h = aircraft.box_height_root - (aircraft.box_height_root - aircraft.box_height_mid) * (z_relative / 0.5)
       else:
           # Интерполяция между серединой и законцовкой
           h = aircraft.box_height_mid - (aircraft.box_height_mid - aircraft.box_height_tip) * ((z_relative - 0.5) / 0.5)
       return h
   ```

3. **Создать функцию расчёта положения лонжеронов:**
   ```python
   def calculate_spar_positions(z_relative, aircraft):
       """
       Интерполяция положения лонжеронов
       """
       front_spar = (aircraft.spar_positions_root['front'] + 
                    (aircraft.spar_positions_tip['front'] - aircraft.spar_positions_root['front']) * z_relative)
       rear_spar = (aircraft.spar_positions_root['rear'] + 
                   (aircraft.spar_positions_tip['rear'] - aircraft.spar_positions_root['rear']) * z_relative)
       return {'front': front_spar, 'rear': rear_spar}
   ```

4. **Создать функцию расчёта ширины кессона:**
   ```python
   def calculate_box_width(z_relative, aircraft):
       """
       Ширина кессона = расстояние между лонжеронами
       """
       chord = calculate_chord(z_relative, aircraft.root_chord, aircraft.tip_chord, aircraft.wing_span)
       spar_pos = calculate_spar_positions(z_relative, aircraft)
       width = (spar_pos['rear'] - spar_pos['front']) * chord
       return width
   ```

5. **Создать функцию расчёта площади полок лонжеронов:**
   ```python
   def calculate_spar_flange_area(z_relative, aircraft, material):
       """
       Оценочный расчёт площади полок лонжеронов
       (упрощённая модель для начальных расчётов)
       """
       # Можно использовать типовые значения или упрощённую модель
       # Для детального расчёта нужны дополнительные данные
       pass
   ```

**Критерии готовности:**
- Все функции реализованы
- Интерполяция работает корректно
- Добавлены unit-тесты
- Добавлены docstrings с формулами

---

## Этап 4: Реализация модуля нагрузок

### Задача 4.1: Загрузка данных от бота (loads.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задача 1.2

**Шаги:**

1. **Создать функцию загрузки изгибающих моментов:**
   ```python
   def load_moments_from_bot(filepath='data/bot-moments.txt'):
       """
       Загрузка изгибающих моментов из файла
       """
       moments = {}
       with open(filepath, 'r') as f:
           for line in f:
               if line.startswith('#') or not line.strip():
                   continue
               parts = line.split('|')
               z_rel = float(parts[0].strip())
               z_abs = float(parts[1].strip())
               M = float(parts[2].strip())
               moments[z_rel] = {'z': z_abs, 'M': M}
       return moments
   ```

2. **Создать функцию загрузки перегрузок:**
   ```python
   def load_overloads_from_bot(filepath='data/bot-overloads.txt'):
       """
       Загрузка перегрузок из файла
       """
       overloads = {}
       with open(filepath, 'r') as f:
           for line in f:
               if line.startswith('#') or not line.strip():
                   continue
               if '=' in line:
                   key, value = line.split('=')
                   overloads[key.strip()] = float(value.strip())
       return overloads
   ```

3. **Создать функцию получения момента для сечения:**
   ```python
   def get_moment_at_section(z_relative, moments_dict):
       """
       Получение изгибающего момента для заданного сечения
       """
       if z_relative in moments_dict:
           return moments_dict[z_relative]['M']
       else:
           # Интерполяция между ближайшими значениями
           sorted_keys = sorted(moments_dict.keys())
           # ... логика интерполяции
           pass
   ```

**Критерии готовности:**
- Функции загрузки работают
- Данные корректно парсятся
- Добавлена обработка ошибок
- Добавлены docstrings

---

### Задача 4.2: Расчёт напряжений от изгибающего момента (loads.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задачи 2.1, 2.2, 2.3, 4.1

**Шаги:**

1. **Создать функцию расчёта напряжений:**
   ```python
   def calculate_bending_stress(M, I_eff, y_max, area_eff=None):
       """
       Расчёт нормальных напряжений от изгибающего момента
       
       σ = M * y / I
       
       где:
       M - изгибающий момент
       I_eff - эффективный момент инерции сечения
       y_max - расстояние от нейтральной оси до крайнего волокна
       """
       stress = M * y_max / I_eff
       return stress
   ```

2. **Создать функцию определения нейтральной оси:**
   ```python
   def calculate_neutral_axis(panel, stringers):
       """
       Определение положения нейтральной оси составного сечения
       (обшивка + стрингеры)
       """
       # Суммирование статических моментов
       # Расчёт координаты центра тяжести
       pass
   ```

**Критерии готовности:**
- Формулы реализованы корректно
- Учитывается эффективная площадь и момент инерции
- Добавлены docstrings с формулами

---

## Этап 5: Реализация модуля устойчивости

### Задача 5.1: Местная потеря устойчивости обшивки (stability.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задачи 2.2, 2.3

**Шаги:**

1. **Создать функцию расчёта критического напряжения обшивки:**
   ```python
   def local_skin_buckling(skin_thickness, stringer_spacing, material, 
                          boundary_condition='hinged'):
       """
       Расчёт критического напряжения местной потери устойчивости обшивки
       
       σ_cr = k_σ * (π² * E) / (12 * (1 - ν²)) * (t / b_p)²
       
       Из deep-research-3-result.md, раздел 1
       """
       E = material.young_modulus
       nu = material.poisson_ratio
       
       # Коэффициент устойчивости в зависимости от граничных условий
       k_sigma = {
           'hinged': 4.0,      # оба края шарнирно опёрты
           'clamped': 6.97,    # оба края защемлены
           'mixed': 5.0        # один защемлён, другой шарнирно
       }[boundary_condition]
       
       b_p = stringer_spacing  # ширина поля обшивки
       t = skin_thickness
       
       sigma_cr = (k_sigma * np.pi**2 * E / 
                  (12 * (1 - nu**2)) * (t / b_p)**2)
       
       return sigma_cr
   ```

2. **Добавить валидацию:**
   - Проверка граничных условий
   - Проверка физической разумности результата

**Критерии готовности:**
- Формула реализована согласно deep-research-3-result.md
- Все коэффициенты соответствуют данным
- Добавлены docstrings с ссылкой на источник

---

### Задача 5.2: Местная потеря устойчивости стрингера (stability.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задачи 2.2, 2.4

**Шаги:**

1. **Создать функцию расчёта критического напряжения элемента стрингера:**
   ```python
   def local_stringer_buckling(element_width, element_thickness, material,
                              element_type='web'):
       """
       Расчёт критического напряжения местной потери устойчивости элемента стрингера
       
       σ_cr = k_σ,i * (π² * E) / (12 * (1 - ν²)) * (t_i / b_i)²
       
       Из deep-research-3-result.md, раздел 2
       """
       E = material.young_modulus
       nu = material.poisson_ratio
       
       # Коэффициенты устойчивости для разных элементов
       k_sigma = {
           'web_clamped': 6.97,      # стенка между полками (оба края защемлены)
           'flange_internal': 4.0,   # внутренний пояс (оба края опёрты)
           'flange_free': 0.43,      # свободный вынос полки (консоль)
           'flange_Z': 0.425         # пояс Z-стрингера
       }
       
       # Определение коэффициента в зависимости от типа элемента
       if element_type == 'web':
           k = k_sigma['web_clamped']
       elif element_type == 'flange_internal':
           k = k_sigma['flange_internal']
       elif element_type == 'flange_free':
           k = k_sigma['flange_free']
       else:
           k = k_sigma['flange_Z']
       
       sigma_cr = (k * np.pi**2 * E / 
                  (12 * (1 - nu**2)) * (element_thickness / element_width)**2)
       
       return sigma_cr
   ```

2. **Создать функцию проверки всех элементов стрингера:**
   ```python
   def check_stringer_local_buckling(stringer, material, stress):
       """
       Проверка местной устойчивости всех элементов стрингера
       """
       results = {}
       
       # Проверка стенки
       if stringer.web_height and stringer.web_thickness:
           sigma_cr_web = local_stringer_buckling(
               stringer.web_height, stringer.web_thickness, material, 'web'
           )
           results['web'] = {
               'sigma_cr': sigma_cr_web,
               'safe': stress < sigma_cr_web
           }
       
       # Проверка полок
       # ... аналогично для каждого элемента
       
       return results
   ```

**Критерии готовности:**
- Формулы реализованы для всех типов элементов
- Коэффициенты соответствуют данным из deep-research-3-result.md
- Добавлены docstrings

---

### Задача 5.3: Общая потеря устойчивости панели (stability.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задачи 2.3, 5.1, 5.2

**Шаги:**

1. **Создать функцию расчёта критического напряжения общей устойчивости:**
   ```python
   def general_panel_buckling(panel, stringers, material, panel_length, 
                              boundary_condition='hinged'):
       """
       Расчёт критического напряжения общей потери устойчивости панели
       
       Использует формулу Эйлера:
       N_cr = (π² * E_red * I_eff) / (μ * L)²
       σ_cr = N_cr / A_eff
       
       Из deep-research-3-result.md, раздел 3
       """
       # Коэффициент приведённой длины
       mu = {
           'hinged': 1.0,      # оба конца шарнирно опёрты
           'clamped': 0.5,     # оба конца защемлены
           'mixed': 0.7,       # один защемлён, другой шарнирно
           'cantilever': 2.0   # консоль
       }[boundary_condition]
       
       # Эффективные параметры (уже рассчитаны с учётом редуцирования)
       A_eff = panel.reduced_area
       I_eff = panel.reduced_inertia
       E_red = material.young_modulus  # или редуцированный модуль
       
       # Эффективная гибкость
       r_eff = np.sqrt(I_eff / A_eff)
       lambda_eff = (mu * panel_length) / r_eff
       
       # Критическое напряжение
       sigma_cr = (np.pi**2 * E_red) / (lambda_eff**2)
       
       return sigma_cr
   ```

2. **Добавить валидацию:**
   - Проверка эффективных параметров
   - Проверка граничных условий

**Критерии готовности:**
- Формула Эйлера реализована
- Учитываются эффективные параметры
- Добавлены docstrings

---

## Этап 6: Реализация модуля редуцирования

### Задача 6.1: Эффективная ширина обшивки (reduction.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задачи 2.2, 2.3, 5.1

**Шаги:**

1. **Создать функцию расчёта эффективной ширины (формула Винтера):**
   ```python
   def effective_width(skin_width, sigma_cr, sigma_edge, material, method='winter'):
       """
       Расчёт эффективной ширины обшивки при закритическом деформировании
       
       Метод Винтера (из deep-research-4-result.md, раздел 1.3):
       λ_p = sqrt(f_y / σ_cr)
       ρ = (1 - 0.22/λ_p) / λ_p  при λ_p > 0.673
       b_eff = ρ * b
       """
       if method == 'winter':
           # Параметр тонкостенности
           lambda_p = np.sqrt(material.yield_strength / sigma_cr)
           
           if lambda_p <= 0.673:
               # Пластинка работает полностью
               rho = 1.0
           else:
               # Редуцирование
               rho = (1 - 0.22 / lambda_p) / lambda_p
           
           b_eff = rho * skin_width
           
       elif method == 'karman':
           # Формула фон Кармана (упругая область)
           if sigma_edge <= sigma_cr:
               b_eff = skin_width
           else:
               b_eff = skin_width * np.sqrt(sigma_cr / sigma_edge)
       
       return b_eff, rho
   ```

2. **Добавить валидацию:**
   - Проверка метода
   - Проверка физической разумности

**Критерии готовности:**
- Оба метода реализованы
- Формулы соответствуют deep-research-4-result.md
- Добавлены docstrings

---

### Задача 6.2: Редуцированный модуль упругости (reduction.py)
**Приоритет:** Средний  
**Статус:** Завершено  
**Зависимости:** Задачи 2.2, 2.3, 2.4

**Шаги:**

1. **Создать функцию расчёта редуцированного модуля:**
   ```python
   def reduced_modulus(panel, stringers, material, stress_level):
       """
       Расчёт редуцированного модуля упругости
       
       E_red = (E * A_s + E_t * A_skin_eff) / (A_s + A_skin_eff)
       
       Из deep-research-4-result.md, раздел 3
       """
       E = material.young_modulus
       
       # Площадь стрингеров
       A_s = sum(s.area for s in stringers)
       
       # Эффективная площадь обшивки
       A_skin_eff = panel.skin_thickness * panel.effective_skin_width
       
       # Касательный модуль (упрощённо, для алюминия до 0.6-0.7 f_y можно E_t ≈ E)
       if stress_level < 0.6 * material.yield_strength:
           E_t = E
       else:
           # Упрощённая модель для пластической области
           E_t = E * (1 - (stress_level - 0.6 * material.yield_strength) / 
                     (0.4 * material.yield_strength))
       
       # Редуцированный модуль
       E_red = (E * A_s + E_t * A_skin_eff) / (A_s + A_skin_eff)
       
       return E_red
   ```

**Критерии готовности:**
- Формула реализована
- Учитывается касательный модуль
- Добавлены docstrings

---

### Задача 6.3: Итерационный расчёт с редуцированием (reduction.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задачи 6.1, 6.2, 5.1, 5.3

**Шаги:**

1. **Создать функцию итерационного расчёта:**
   ```python
   def iterative_reduction(panel, stringers, material, moment, 
                          panel_length, max_iterations=10, tolerance=0.02):
       """
       Итерационный расчёт с учётом редуцирования обшивки
       
       Алгоритм из deep-research-4-result.md, раздел 4:
       1. Начальное приближение (без редукции)
       2. Расчёт критического напряжения обшивки
       3. Проверка и редуцирование
       4. Пересчёт эффективных параметров
       5. Повторение до сходимости
       """
       # Начальное приближение
       b_eff_prev = panel.stringer_spacing  # полная ширина
       E_red_prev = material.young_modulus
       
       for iteration in range(max_iterations):
           # Расчёт критического напряжения обшивки
           sigma_cr_skin = local_skin_buckling(
               panel.skin_thickness, panel.stringer_spacing, material
           )
           
           # Расчёт действующего напряжения
           # (упрощённо, нужен полный расчёт напряжений)
           sigma_edge = moment / (panel.reduced_inertia / 
                                 (panel.box_height / 2))
           
           # Редуцирование обшивки
           if sigma_edge > sigma_cr_skin:
               b_eff, rho = effective_width(
                   panel.stringer_spacing, sigma_cr_skin, sigma_edge, material
               )
           else:
               b_eff = panel.stringer_spacing
               rho = 1.0
           
           # Пересчёт эффективных параметров
           panel.effective_skin_width = b_eff
           panel.reduced_area = calculate_effective_area(panel, stringers)
           panel.reduced_inertia = calculate_effective_inertia(panel, stringers)
           
           # Редуцированный модуль
           E_red = reduced_modulus(panel, stringers, material, sigma_edge)
           
           # Проверка сходимости
           if abs(b_eff - b_eff_prev) / b_eff_prev < tolerance:
               break
           
           b_eff_prev = b_eff
           E_red_prev = E_red
       
       return panel, stringers, iteration
   ```

2. **Добавить функции расчёта эффективных параметров:**
   - `calculate_effective_area()` - эффективная площадь
   - `calculate_effective_inertia()` - эффективный момент инерции

3. **Добавить критерии сходимости:**
   - По эффективной ширине
   - По критическому напряжению
   - По рабочим напряжениям

**Критерии готовности:**
- Итерационный алгоритм реализован
- Критерии сходимости работают
- Алгоритм соответствует deep-research-4-result.md
- Добавлены docstrings

---

## Этап 7: Реализация модуля прочности

### Задача 7.1: Расчёт напряжений в панели (strength.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Задачи 2.3, 4.2, 6.3

**Шаги:**

1. **Создать функцию расчёта напряжений:**
   ```python
   def calculate_stresses(panel, stringers, moment, material):
       """
       Расчёт напряжений в панели с учётом редуцирования
       """
       # Эффективные параметры (уже рассчитаны с учётом редуцирования)
       I_eff = panel.reduced_inertia
       A_eff = panel.reduced_area
       
       # Расстояние до крайнего волокна
       y_max = panel.box_height / 2
       
       # Напряжения от изгибающего момента
       sigma_bending = moment * y_max / I_eff
       
       # Распределение напряжений по элементам
       stresses = {
           'skin': sigma_bending,
           'stringers': sigma_bending,
           'max': sigma_bending
       }
       
       return stresses
   ```

2. **Добавить функцию проверки прочности:**
   ```python
   def check_strength(stress, material, load_type='compression'):
       """
       Проверка прочности по пределу пропорциональности
       """
       sigma_pc = material.proportional_limit
       
       # Проверка
       is_safe = stress < sigma_pc
       safety_margin = sigma_pc / stress if stress > 0 else float('inf')
       
       return {
           'safe': is_safe,
           'safety_margin': safety_margin,
           'stress': stress,
           'limit': sigma_pc
       }
   ```

**Критерии готовности:**
- Расчёт напряжений реализован
- Проверка прочности работает
- Учитывается редуцирование
- Добавлены docstrings

---

## Этап 8: Реализация главного модуля

### Задача 8.1: Главный файл запуска (main.py)
**Приоритет:** Высокий  
**Статус:** Завершено  
**Зависимости:** Все предыдущие задачи

**Шаги:**

1. **Создать структуру main.py:**
   ```python
   import numpy as np
   from aircraft_data import Aircraft
   from material import Material
   from panel import Panel
   from stringer import Stringer
   from geometry import *
   from loads import *
   from stability import *
   from reduction import *
   from strength import *
   from output import *
   
   def main():
       # Инициализация
       aircraft = Aircraft()
       material = Material('B95T1', 'sheet')
       
       # Расчётные сечения
       sections = [0.2, 0.4, 0.6, 0.8]
       
       # Загрузка данных от бота
       moments = load_moments_from_bot()
       overloads = load_overloads_from_bot()
       
       results = {}
       
       # Расчёт для каждого сечения
       for z_rel in sections:
           print(f"\n=== Расчёт сечения z/L = {z_rel} ===")
           
           # Создание панели
           panel = Panel(z_rel, aircraft, material)
           
           # Расчёт геометрии
           panel.panel_width = calculate_box_width(z_rel, aircraft)
           panel.box_height = calculate_box_height(z_rel, aircraft)
           
           # Получение изгибающего момента
           M = get_moment_at_section(z_rel, moments)
           
           # Предварительный подбор параметров панели
           # (толщина обшивки, стрингеры и т.д.)
           # ...
           
           # Итерационный расчёт с редуцированием
           panel, stringers, iterations = iterative_reduction(
               panel, stringers, material, M, panel_length=...
           )
           
           # Расчёт напряжений
           stresses = calculate_stresses(panel, stringers, M, material)
           
           # Проверка прочности
           strength_check = check_strength(stresses['max'], material)
           
           # Сохранение результатов
           results[z_rel] = {
               'panel': panel,
               'stresses': stresses,
               'strength': strength_check,
               'iterations': iterations
           }
       
       # Вывод результатов
       output_results(results, output_file='results.md')
       
   if __name__ == '__main__':
       main()
   ```

2. **Добавить обработку ошибок:**
   - Валидация входных данных
   - Обработка исключений
   - Логирование

**Критерии готовности:**
- Главный файл работает
- Все модули интегрированы
- Результаты выводятся корректно

---

## Этап 9: Реализация модуля вывода

### Задача 9.1: Форматированный вывод результатов (output.py)
**Приоритет:** Средний  
**Статус:** Завершено  
**Зависимости:** Задача 8.1

**Шаги:**

1. **Создать функцию вывода в консоль:**
   ```python
   def print_results(results):
       """
       Вывод результатов в консоль
       """
       for z_rel, data in results.items():
           print(f"\n{'='*60}")
           print(f"Сечение z/L = {z_rel}")
           print(f"{'='*60}")
           print(f"Изгибающий момент: {data['moment']:.2e} Н·м")
           print(f"Толщина обшивки: {data['panel'].skin_thickness*1000:.2f} мм")
           print(f"Эффективная ширина обшивки: {data['panel'].effective_skin_width*1000:.2f} мм")
           print(f"Напряжение: {data['stresses']['max']/1e6:.2f} МПа")
           print(f"Предел пропорциональности: {data['strength']['limit']/1e6:.2f} МПа")
           print(f"Запас прочности: {data['strength']['safety_margin']:.2f}")
   ```

2. **Создать функцию вывода в файл:**
   ```python
   def output_results(results, output_file='results.md'):
       """
       Вывод результатов в markdown файл
       """
       with open(output_file, 'w', encoding='utf-8') as f:
           f.write("# Результаты расчёта верхней панели крыла\n\n")
           f.write(f"Самолёт: Boeing 737-800\n")
           f.write(f"Материал: В95-Т1\n\n")
           
           for z_rel, data in results.items():
               f.write(f"## Сечение z/L = {z_rel}\n\n")
               # ... детальный вывод
   ```

**Критерии готовности:**
- Вывод в консоль работает
- Вывод в файл работает
- Форматирование читаемое

---

## Этап 10: Тестирование и валидация

### Задача 10.1: Unit-тесты для базовых классов
**Приоритет:** Средний  
**Статус:** Завершено

**Шаги:**

1. Создать файл `tests/test_aircraft.py`
2. Написать тесты для класса Aircraft:
   - Проверка интерполяции хорды
   - Проверка интерполяции высоты кессона
   - Проверка граничных значений

3. Создать файл `tests/test_material.py`
4. Написать тесты для класса Material:
   - Проверка свойств материала
   - Проверка допускаемых напряжений

5. Создать файл `tests/test_geometry.py`
6. Написать тесты для функций геометрии:
   - Проверка расчёта хорды
   - Проверка расчёта ширины кессона

**Критерии готовности:**
- Все тесты проходят
- Покрытие кода > 80%

---

### Задача 10.2: Проверка на известных примерах
**Приоритет:** Высокий  
**Статус:** Не начато

**Шаги:**

1. Найти примеры из книги Вольмира (примеры 9.3, 9.4)
2. Воспроизвести расчёты в программе
3. Сравнить результаты
4. При необходимости скорректировать алгоритм

**Критерии готовности:**
- Результаты совпадают с примерами
- Разница < 5%

---

### Задача 10.3: Проверка физической корректности
**Приоритет:** Высокий  
**Статус:** Завершено

**Шаги:**

1. Проверка размерностей всех формул
2. Проверка знаков напряжений (сжатие отрицательное)
3. Проверка граничных случаев:
   - Очень тонкая обшивка
   - Очень толстая обшивка
   - Нулевой момент
4. Проверка монотонности результатов

**Критерии готовности:**
- Все проверки пройдены
- Нет физически некорректных результатов

---

## Этап 11: Документация

### Задача 11.1: Комментарии в коде
**Приоритет:** Средний  
**Статус:** Завершено

**Шаги:**

1. Добавить docstrings для всех классов и функций
2. Добавить комментарии к сложным формулам
3. Добавить ссылки на источники (deep-research файлы, Вольмир)

**Критерии готовности:**
- Все функции документированы
- Формулы имеют ссылки на источники

---

### Задача 11.2: README.md
**Приоритет:** Средний  
**Статус:** Завершено

**Шаги:**

1. Создать README.md с описанием:
   - Назначение программы
   - Установка и запуск
   - Структура проекта
   - Примеры использования
   - Описание алгоритма

**Критерии готовности:**
- README полный и понятный
- Есть примеры использования

---

## Приоритизация задач

### Критический путь (необходимо для базовой функциональности):
1. Задача 1.1 - Создание структуры проекта
2. Задача 1.2 - Извлечение данных из эпюр
3. Задача 2.1 - Класс Aircraft
4. Задача 2.2 - Класс Material
5. Задача 2.3 - Класс Panel
6. Задача 2.4 - Класс Stringer
7. Задача 3.1 - Функции геометрии
8. Задача 4.1 - Загрузка данных от бота
9. Задача 5.1 - Местная устойчивость обшивки
10. Задача 6.1 - Эффективная ширина
11. Задача 6.3 - Итерационный расчёт
12. Задача 7.1 - Расчёт напряжений
13. Задача 8.1 - Главный файл

### Важные задачи (улучшают качество):
- Задача 5.2 - Местная устойчивость стрингера
- Задача 5.3 - Общая устойчивость
- Задача 6.2 - Редуцированный модуль
- Задача 9.1 - Вывод результатов
- Задача 10.2 - Проверка на примерах

### Опциональные задачи:
- Задача 10.1 - Unit-тесты
- Задача 11.1 - Документация
- Задача 11.2 - README

---

## Оценка времени (примерная)

- Этап 1 (Подготовка): 2-4 часа
- Этап 2 (Базовые классы): 8-12 часов
- Этап 3 (Геометрия): 4-6 часов
- Этап 4 (Нагрузки): 4-6 часов
- Этап 5 (Устойчивость): 8-12 часов
- Этап 6 (Редуцирование): 8-12 часов
- Этап 7 (Прочность): 4-6 часов
- Этап 8 (Главный модуль): 6-8 часов
- Этап 9 (Вывод): 2-4 часа
- Этап 10 (Тестирование): 8-12 часов
- Этап 11 (Документация): 4-6 часов

**Итого:** 60-90 часов работы

---

## Зависимости между задачами

```
1.1 → 2.1, 2.2, 2.3, 2.4
1.2 → 4.1
2.1 → 3.1, 2.3
2.2 → 2.3, 2.4, 5.1, 5.2, 6.1, 6.2
2.3 → 3.1, 5.1, 6.1, 6.3, 7.1
2.4 → 5.2, 6.2, 6.3
3.1 → 8.1
4.1 → 4.2, 8.1
5.1 → 6.1, 6.3
5.2 → 6.3
5.3 → 6.3
6.1 → 6.3
6.2 → 6.3
6.3 → 7.1
7.1 → 8.1
8.1 → 9.1, 10.2
```

---

## Критерии завершения проекта

1. ✅ Все модули реализованы и работают
2. ✅ Алгоритм работает для всех четырёх сечений (0.2, 0.4, 0.6, 0.8)
3. ✅ Учитывается редуцирование обшивки
4. ✅ Рассчитываются все требуемые параметры
5. ✅ Результаты физически корректны
6. ✅ Код структурирован и документирован
7. ✅ Результаты выводятся в читаемом формате

