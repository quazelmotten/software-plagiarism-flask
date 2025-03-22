# 1 задача

def lensort(list_to_sort: list)->list:
    return sorted(list_to_sort, key=lambda x: len(x))

# 2 задача

def unique(unique: list)->list:
    return list(set(unique))

# 3 задача

def my_enumerate(list_of_smth: list)->list:
    nums = range(len(list_of_smth))
    return list(zip(nums, list_of_smth))

# 4 задача

def words_frequency(path: str)->dict:
    bow_dict = {}
    with open(path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            words = map(lambda x: x.lower(), line.split())
            for word in words:
                if word in bow_dict.keys():
                    bow_dict[word] += 1
                else:
                    bow_dict[word] = 1

    return bow_dict

# 5 задача

import time
from functools import wraps

def execution_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        print(f"Функция {func.__name__} время выполнения {execution_time}")
        return result
    return wrapper

@execution_time
def for_list(numbers: list)->list:
    square_list = []
    for num in numbers:
        square_list.append(num**2)
        
    return square_list
        
@execution_time
def lc_list(numbers: list)->list:
    return [num**2 for num in numbers]

@execution_time
def map_list(numbers: list)->list:
    return list(map(lambda num: num**2, numbers))

