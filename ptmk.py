import sys
import datetime
import time
import sqlite3
import random
import calendar
from russian_names import RussianNames
from alive_progress import alive_bar

script, parameter = sys.argv[:2]

def getAge(str):
    day = str[:2] 
    month = str[2:4]
    year = str[4:]

    now = datetime.datetime.today()

    birthDate = datetime.datetime(int(year), int(month), int(day))

    age = int((now - birthDate).days / 365)

    return age

def getBirthDate():
    month = random.randint(1, 12)
    year = random.randint(1930, 2022)
    day = random.randint(1, calendar.monthrange(year, month)[1])
                
    month = '0' + str(month) if len(str(month)) == 1 else str(month)
    day = '0' + str(day) if len(str(day)) == 1 else str(day)

    birthDate = f"{day}{month}{str(year)}"

    return birthDate

def getSex(user):
    if user.get('patronymic').endswith('a') == True:
        sex = 'female'
    else:
        sex = 'male'
    
    return sex

def validName(user):
    return f"{user.get('surname')} {user.get('name')} {user.get('patronymic')}"

def pushManyToDb(users):
        with sqlite3.connect('ptmk.db') as db:
            cursor = db.cursor()

            cursor.executemany("INSERT INTO users(fio, birthDate, sex) VALUES(?, ?, ?)", (users))

def getUsers(usersCount, case):
    match case:
        case 'million':
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Генерация миллиона имен начата.")
            rn = RussianNames(count=usersCount, patronymic=True, transliterate=True, gender=0.5, output_type='dict')
            batch = []
            with alive_bar(len(rn)) as bar:
                for name in rn:
                    batch.append(name)
                    bar()
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Генерация имена звершена.")
            
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Преобразование данных для отправки.")
            users = []
            for user in batch:
                person = []

                # имя
                person.append(validName(user))
                ###

                # день рождения
                person.append(getBirthDate())
                ###

                # пол
                person.append(getSex(user))
                ###

                users.append(person)
                
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Отправка в базу.")
            pushManyToDb(users)
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Процесс завершен.\n")

        case 'hundred':
            users = []
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Генерация сотни имен и подготовка к отправке начаты.")
            while len(users) < usersCount:
                rn = RussianNames(count=10000, patronymic=True, transliterate=True, gender=1, output_type='dict')
                batch = []
                for name in rn:
                    batch.append(name)

                for user in batch:
                    if user.get('surname').startswith('F'):
                        person = []

                         # имя
                        person.append(validName(user))
                        ###

                        # день рождения
                        person.append(getBirthDate())
                        ###

                        # пол
                        person.append('male')
                        ###

                        users.append(person)


            delta = len(users) - usersCount
            if delta > 0:
                users = users[:-delta]

            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Отправка в базу.")
            pushManyToDb(users)
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Процесс звершен.\n")

match parameter:
    case '1':
        with sqlite3.connect('ptmk.db') as db:
            cursor = db.cursor()

            cursor.execute("""CREATE TABLE IF NOT EXISTS users(
                        fio VARCHAR(50),
                        birthDate VARCHAR(8),
                        sex VARCHAR(6)
            )""")

            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Таблица успешно создана, либо уже существует.")

    case '2':
        fio, birthDate, sex = sys.argv[2:]
        with sqlite3.connect('ptmk.db') as db:
            cursor = db.cursor()

            cursor.execute("INSERT INTO users VALUES(?, ?, ?)", [fio, birthDate, sex])
            print(f'[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Создание записи прошло успешно.')

    case '3':
        with sqlite3.connect('ptmk.db') as db:
            cursor = db.cursor()

            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Начинаю выборку по критерию: уникальные пол + ФИО, сортировка по ФИО.")
            cursor.execute("SELECT fio, birthDate, sex FROM users GROUP BY fio, birthDate")
            for value in cursor.fetchall():
                if value[2] == 'male':
                    sex = 'мужчина'
                else:
                    sex = 'женщина'
                print(f'ФИО: {value[0]} | Дата рождения: {value[1][:2]}.{value[1][2:4]}.{value[1][4:]} | Пол: {sex} | Полных лет: {getAge(value[1])}')

    case '4':
        getUsers(1000000, 'million')
        getUsers(100, 'hundred')

    case '5':
        with sqlite3.connect('ptmk.db') as db:
            cursor = db.cursor()

            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Начинаю выборку по критерию: пол мужской, ФИО начинается с F.")
            startTime = time.time()
            cursor.execute("SELECT fio FROM users WHERE fio LIKE 'F%' AND sex = ?", ['male'])
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Время исполнения запроса составило: {time.time() - startTime} секунд.")
            
            output = input(f"[?] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Напечатать выборку? (Y/N)\n")
            if output == 'Y' or output == 'y':
                print(f'[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Вывод всех записей:')
                iter = 1
                for value in cursor.fetchall():
                    print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | #{iter} | {value[0]}")
                    iter += 1

    case '6':
        print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Произвожу оптимизацию БД.")
        print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Разобью поле ФИО на три: фамилия, имя, отчество.")
        
        with sqlite3.connect('ptmk.db') as db:
            cursor = db.cursor()

            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Забираю данные из исходной таблицы.")
            cursor.execute("SELECT * FROM users")
            users = []
            for user in cursor.fetchall():
                person = []
                
                # имя
                for char in user[0]:
                    if char == ' ':
                        index = user[0].index(char)
                        surname = user[0][:index]

                        str = user[0][index + 1:]

                        for char in str:
                            if char == ' ':
                               index = str.index(char)
                               name = str[:index]
                               patronymic = str[index + 1:]
                               break
                        break
                
                person.append(surname)
                person.append(name)
                person.append(patronymic)
                ###

                # дата рождения
                person.append(user[1])
                ###

                # пол
                person.append(user[2])
                ###

                users.append(person)

            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Данные собраны.")
            
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Создаю новую таблицу.")
            cursor.execute("""CREATE TABLE IF NOT EXISTS users_modified(
                           surname VARCHAR(15),
                           name VARCHAR(15),
                           patronymic VARCHAR(20),
                           birthDate VARCHAR(8),
                           sex VARCHAR(6)
            )""")


            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Переношу данные в новую таблицу.")
            cursor.executemany("INSERT INTO users_modified(surname, name, patronymic, birthDate, sex) VALUES(?, ?, ?, ?, ?)", (users))
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Готово.")

    case '7':
        print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Осуществим запрос на новой таблице.")
        with sqlite3.connect('ptmk.db') as db:
            cursor = db.cursor()
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Начинаю выборку по критерию: пол мужской, ФИО начинается с F.")
            startTime = time.time()
            cursor.execute("SELECT surname FROM users_modified WHERE surname LIKE 'F%' AND sex = ?", ['male'])
            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Время исполнения запроса составило: {time.time() - startTime} секунд.")
            
            output = input(f"[?] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Напечатать выборку? (Y/N)\n")
            if output == 'Y' or output == 'y':
                print(f'[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Вывод всех записей:')
                iter = 1
                for value in cursor.fetchall():
                    print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | #{iter} | {value[0]}")
                    iter += 1

    case '8':
        answer = input(f"[?] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Создать или удалить индекс? (Y/N)\n")
        if answer == 'Y' or answer == 'y':

            print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Произвожу индексацию базы по полю ФИО.")
            with sqlite3.connect('ptmk.db') as db:
                cursor = db.cursor()

                cursor.execute("CREATE INDEX users_fio ON users (fio)")
        
        if answer == 'N' or answer == 'n':

            with sqlite3.connect('ptmk.db') as db:
                cursor = db.cursor()
                try:
                    cursor.execute("DROP INDEX users_fio")
                    print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Индекс удален.")

                except sqlite3.Error as e:
                    print(f"[x] {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec} | Ошибка. Индекс не был создан:", e)