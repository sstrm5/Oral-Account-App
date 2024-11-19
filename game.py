import random
import operator


def errorHandler(problem_answer):
    switch = False
    validated_guess = 0.0
    while switch == False:
        try:
            validated_guess = float(input('Please enter a valid answer: '))
            if type(validated_guess) is float:
                switch = True
                break
        except ValueError:
            pass
    return validated_guess

# Рандомит 2 числа и операцию между ними


def random_problem():
    operators = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
    }

    # Выбираем на рандом первое, второе числа и операцию между ними
    operation = random.choice(list(operators.keys()))
    num_1 = random.randint(
        1, 400) if operation != "*" else random.randint(2, 20)
    if operation == "/":
        num_1 = random.randint(1, 1000)
        num_2 = random.randint(2, 20)
        if num_1 % num_2 != 0:
            while num_1 % num_2 != 0:
                num_1 += 1

    elif operation == "*":
        num_2 = random.randint(2, 20)
        num_1, num_2 = random.sample([num_1, num_2], 2)

    else:
        num_2 = random.randint(1, 600)

    # Находим ответ на задачку
    res = round(operators.get(operation)(num_1, num_2), 3)
    answer = str(int(res) if res == int(res) else res)
    # print(f'What is {num_1} {operation} {num_2}')
    return num_1, operation, num_2, answer


def random_color():
    red = random.randint(50, 230)
    green = random.randint(50, 100)
    blue = random.randint(50, 230)
    return f'rgb({red}, {green}, {blue})'
