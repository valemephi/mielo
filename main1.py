import os
import argparse
import pyzbar.pyzbar as zbar
#import zbar
import numpy as np
import cv2
import winsound 
import time as tm
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from PIL import Image, ImageDraw
from bs4 import BeautifulSoup
import requests
from pyzbar.pyzbar import decode
import sqlite3 as sq

#import Image



cap = cv2.VideoCapture(0)  #запуск видео камеры
countt = 0 #задаем счетчик записанных за сессию продуктов
code_list = []
while(True): 
    img = 'test1.png' #название снятого изображения записываем в переменную
    for m in range(1,4):
        tm.sleep(3) #устанавливаем частоту кадров
        ret, frame = cap.read() #Делаем снимок
        cv2.imwrite('test'+str(1)+'.png', frame) #сохраняем снимок
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    try:
        image = cv2.imread(img,0) 
        decoded = zbar.decode(image) #расшифровываем изображение штрихкода
        print(decoded) #выводим декодированные данные
        countt += 1 #увеличиваем счетчик продуктов на 1
        image = Image.open(img).convert('RGB')
        draw = ImageDraw.Draw(image)
        for barcode in decode(image):
            rect = barcode.rect #создаем рамку зеленого цвета по расшифрованным параметрам штрихкода для визуального представления результата определения штрихкода на изображении
            draw.rectangle(
                (
                    (rect.left, rect.top),
                    (rect.left + rect.width, rect.top + rect.height)
                ),
                outline='#8ffe09', width = 3
            )
            
        if len(decoded)==1: #если на снимке присутствует штрихкод, то длина списка будет 1, если штрихкод не обнаружен, то 0
            code_list.append(decoded)
            image.save('bounding_box_and_polygon'+str(countt)+'.png') #сохраняем изображение штрихкода с цветной рамкой вокруг штрихкода
            frequency = 1000 
            duration = 400 
            winsound.Beep(frequency, duration) #при успешном сканировании штрихкода выводим звуковой сигнал, который поможет понять пользователю, что штрихкод был успешно отсканирован
            for decoded in code_list:
                code_ = decoded
                code_ = str(code_).split(', ')[0][-14:-1] #из декодированной информации мы выделяем тринадцатизначный номер, содержащий информацию о стране, компании изготовителе, кодовом номере товара
                url = 'https://barcode-list.ru/barcode/RU/barcode-'+str(code_)+'/%D0%9F%D0%BE%D0%B8%D1%81%D0%BA.htm' # в переменную url сохраняем ссылку на продукт с определенным триндцатизначным номером
                response = requests.get(url) 
                print(response)

                bs = BeautifulSoup(response.text, 'lxml')
                print(bs)

                meta = bs.find_all('meta')
                for tag in meta:
                    if 'name' in tag.attrs.keys() and tag.attrs['name'].strip().lower() in ['description']:
                        # print ('NAME    :',tag.attrs['name'].lower())
                        try:
                          # print (tag.attrs['content'].split(':')[2].split(';')[0])
                            print (tag.attrs['content'].split(':')[2])
                        except:
                            print('Этого штрихкода нет в базе данных ;(')
    except:
        continue
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()




def cr_db():
    file_baza = 'baza.db'
    hiso = sq.connect(file_baza)
    cursor = hiso.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS baza_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            instructions TEXT NOT NULL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recipe_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            ingredient_name TEXT NOT NULL,
            mass_g INTEGER NOT NULL,
            FOREIGN KEY (recipe_id) REFERENCES baza_recipes (id)
        )
    ''')

    hiso.commit()
    return hiso

def DOP_recipe(hiso, name, instructions, ingredients):
    cursor = hiso.cursor()
    cursor.execute('''
        INSERT INTO baza_recipes (name, instructions) VALUES (?, ?)
    ''', (name, instructions))

    recipe_id = cursor.lastrowid

    for ingredient_name, mass in ingredients.items():
        cursor.execute('''
            INSERT INTO recipe_ingredients (recipe_id, ingredient_name, mass_g) VALUES (?, ?, ?)
        ''', (recipe_id, ingredient_name, mass))
    hiso.commit()

def find_recipes(hiso, av_ingr):
    select_recipes = '''
    SELECT r.id, r.name, r.instructions, ri.ingredient_name, ri.mass_g
    FROM baza_recipes r
    JOIN recipe_ingredients ri ON r.id = ri.recipe_id;
    '''
    cursor = hiso.cursor()
    cursor.execute(select_recipes)
    all_recipes = cursor.fetchall()
    av_recipes = {}

    for recipe in all_recipes:
        recipe_id, name, instructions, ingredient_name, mass_g = recipe
        if name not in av_recipes:
            av_recipes[name] = {
                "instructions": instructions,
                "ingredients": [],
                "missing": []
            }
        av_recipes[name]["ingredients"].append((ingredient_name, mass_g))
        if ingredient_name not in av_ingr or av_ingr[ingredient_name] < mass_g:
            av_recipes[name]["missing"].append((ingredient_name, mass_g))

    return av_recipes

def check_find_recipes(hiso):
    cursor = hiso.cursor()
    cursor.execute("SELECT COUNT(*) FROM baza_recipes")
    count = cursor.fetchone()[0]
    if count == 0:  # Если рецептов нет, добавим их
        DOP_recipe(hiso, 'Паста с помидорами', 'Сварите пасту и добавьте соус.', {
            'паста': 200,
            'помидоры': 100,
            'оливковое масло': 20
        })
        DOP_recipe(hiso, 'Салат Цезарь', 'Смешайте ингредиенты и подавайте.', {
            'сырный соус': 50,
            'курица': 100,
            'соус': 30,
            'пармезан': 20
        })
        DOP_recipe(hiso, 'Омлет', 'Смешайте ингредиенты и готовьте на сковороде.', {
            'молоко': 60,
            'яйца': 120
        })

def Building_our_kingdom():
    hiso = cr_db()
    check_find_recipes(hiso)

    av_ingr = {
        'паста': 200,
        'помидоры': 50,
        'оливковое масло': 20,
        'сырный соус': 50,
        'курица': 100,
        'соус': 30,
        'пармезан': 20,
        'баклажаны': 1000,
        'яйца': 110
    }

    av_recipes = find_recipes(hiso, av_ingr)
    print("\nМилорд вам доступны эти рецепты:")
    for name_i, r_det in av_recipes.items():
        if r_det["missing"]:
            print(f"Милорд, ресурсы на исходе! Для рецепта: {name_i} - Не хватает этого предмета: {[ing[0] for ing in r_det['missing']]}")
        else:
            print(f"Милорд, королевство процветает! Для рецепта: {name_i} - Все предметы в наличии.")

    hiso.close()

if __name__ == "__main__":
    Building_our_kingdom()

