import time
import os

# 1
def lensort(input_list):
    return sorted(input_list, key = lambda x: len(x))

# 2
def unique(x):
    return set(x)

# 3
def my_enumerate(input_list):
    num_list = [i for i in range(len(input_list))]
    return list(zip(num_list, input_list))

# 4
def words_frequency(file_name):
    
    cwd_path = os.getcwd()
    file_path = os.path.join(cwd_path, file_name)
    
    if not os.path.isfile(file_path):
        print(f'Файл {file_path} не существует')
        return
    
    with open(file_path, 'r') as f:
        f_data = f.read()
        
    f_list = f_data.split()
    counts = [f_list.count(x) for x in f_list]
    my_dict = dict(zip(f_list, counts))
    
    for key, value in my_dict.items():
        print(f'{key}:{value}')
        
# 5
def get_func_time(func):
    def wrapper(*args, **kwards):
        start_time = time.time()
        return_data = func(*args, **kwards)
        end_time = time.time()
        print(f'Время выполенения функции {func} составило: {end_time - start_time} секунд')
        return return_data
    return wrapper

@get_func_time
def for_list(input_list):
    output_list = []
    for x in input_list:
        output_list.append(x^2)
    return(output_list)

@get_func_time
def lc_list(input_list):
    return [x^2 for x in input_list]

@get_func_time
def map_list(input_list):
    return list(map(lambda x: x^2, input_list))
