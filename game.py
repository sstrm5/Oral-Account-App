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
    num_1 = random.randint(1, 9000)
    operation = random.choice(list(operators.keys()))
    if operation == "/":
        num_2 = random.randint(2, 1000)
        if num_1 % num_2 != 0:
            while num_2 % 5 != 0:
                num_2 += 1
            while num_1 % num_2 != 0:
                num_1 += 1

    elif operation == "*":
        num_2 = random.randint(2, 100)

    else:
        num_2 = random.randint(1, 9000)

    # Находим ответ на задачку
    answer = float(round(operators.get(operation)(num_1, num_2), 3))
    # print(f'What is {num_1} {operation} {num_2}')
    return num_1, operation, num_2, answer

# Проверка правильности ввденого ответа пользователем


def ask_question():
    answer = random_problem()
    try:
        guess = float(input('Enter you answer: '))
    except ValueError:
        guess = errorHandler(answer)
    return guess == answer

# Запускает игру, считает очки, оканчивает игру


def game():
    score = 0
    while True:
        if ask_question():
            score += 1
        else:
            break
    # print(f'======== Game Over ========\nYou score is {score}\nKeep going!')
