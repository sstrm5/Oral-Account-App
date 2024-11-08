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
        1, 9000) if operation != "*" else random.randint(2, 343)
    if operation == "/":
        num_2 = random.randint(2, 1000)
        if num_1 % num_2 != 0:
            while num_2 % 5 != 0:
                num_2 += 1
            while num_1 % num_2 != 0:
                num_1 += 1

    elif operation == "*":
        num_2 = random.randint(2, 100)
        num_1, num_2 = random.sample([num_1, num_2], 2)

    else:
        num_2 = random.randint(1, 9000)

    # Находим ответ на задачку
    res = round(operators.get(operation)(num_1, num_2), 3)
    answer = str(int(res) if res == int(res) else res)
    # print(f'What is {num_1} {operation} {num_2}')
    return num_1, operation, num_2, answer
