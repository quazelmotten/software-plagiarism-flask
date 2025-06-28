import pytest
import copy
import re
import os

def lensort(array):
    sorted_array = sorted(array,key = len) # sorts by descending length
    return sorted_array
### sort() и sorted() сортируют массив, однако sort() меняет исходный на отсортированный


def unique(array):
    mylist = list(set(array))
    return mylist
### функция set() - предназначена для множеств, а так как повторяющиеся элементы игнорируется в множествах -> 
### set() - игнорирует дубликаты и выводит только уникальные значения множества 


array = [1,2,1,3,2,5]
unique(array)

def my_enumerate(array):
    enumerated_array = []
    for i, x in zip(range(len(array)), array):
        enumerated_array.append((i, x))
    return enumerated_array

array = [ "a" , "b" , "c" ]
my_enumerate(array)


def word_frequency(filename):
    with open(filename, 'r') as file:
        text = file.read().lower() # строчный регистр
        words = text.split()
        word_counts = {}
        for word in words:
            if word in word_counts:
                word_counts[word] += 1
            else:
                word_counts[word] = 1
        return word_counts
    
word_counts = word_frequency("ivse.txt")  
print(word_counts)  # Вывод словаря


import time

def time_it(func):
  """Декоратор для измерения времени выполнения функции."""
  def wrapper(*args, **kwargs):
    start_time = time.time()
    result = func(*args, **kwargs)
    end_time = time.time()
    print(f"Время выполнения {func.__name__}: {end_time - start_time:.4f} секунд")
    return result
  return wrapper

#квадраты в цикле
@time_it
def square_for_loop(numbers):
    squares = []
    for number in numbers:
        squares.append(number * number)
    return squares

#квадраты в list comprehension
@time_it
def square_list_comprehension(numbers):
    squares = [number * number for number in numbers]
    return squares

#квадраты в map
@time_it
def square_map(numbers):
    squares = list(map(lambda x: x * x, numbers))
    return squares

# Тестирование функций
numbers = list(range(1000000))


print("Метод с использованием цикла for:")
square_for_loop(numbers)

print("\nМетод с использованием list comprehension:")
square_list_comprehension(numbers)

print("\nМетод с использованием map:")
square_map(numbers)