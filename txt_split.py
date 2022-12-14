import random
import shutil
import os
from math import ceil
from tqdm import tqdm
import time

def get_list_shuffle(path_file: str) -> list:
    list_file = []
    with open(path_file, 'r') as file:
        for item in file:
            collating = item.replace('\n', '').split('/')
            list_file.append(collating)
            random.shuffle(list_file)
    return list_file


def sort_category(root: str, list_file: list, quanity: int, dir_name: list) -> None:
    row_cnt = len(list_file)
    quanity_file = ceil(row_cnt/quanity)
    if os.path.exists(f'{root}'):
        shutil.rmtree(f'{root}')
    j = 0
    for dir in dir_name:
        os.makedirs(f'{root}/{dir}')
        file_number = i = pointer_i = 0
        while file_number < quanity_file:
            with open(f'{root}/{dir}/{dir}{file_number}.txt', 'a') as file:
                while i < row_cnt and i < quanity + pointer_i:
                    file.write(list_file[i][j] + '\n')
                    i += 1
                pointer_i = i
            file_number += 1
        j += 1


def main():

    path_file = input('Перетащите сюда файл ~ ').replace(' ', '')
    list_file = get_list_shuffle(path_file)

    SET_QUANITY = int(input('Количество строк ~ '))

    dirName = ['ip', 'port', 'login', 'pass']

    print('\n')
    for i in tqdm(range(100)):
        time.sleep(.01)

    sort_category(
        root='output',
        list_file=list_file,
        quanity=SET_QUANITY,
        dir_name=dirName
    )


if __name__ == "__main__":
    main()
