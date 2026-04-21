#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Калькулятор характеристик пропускной способности моносервисных узлов доступа
Модель Эрланга (Erlang B) с потерями.

Версия: 3.0 (финальная, учебная)
"""

import math
import sys
from datetime import datetime


class ErlangBCalculator:
    """Класс для расчётов по модели Эрланга B."""

    @staticmethod
    def erlang_b(v: int, a: float) -> float:
        """Вычисляет вероятность блокировки по формуле Эрланга B."""
        if v < 0 or a < 0:
            raise ValueError("Число каналов и нагрузка не могут быть отрицательными.")
        if v == 0:
            return 1.0
        # Рекурсивный алгоритм: E(r) = a * E(r-1) / (r + a * E(r-1))
        E = 1.0
        for r in range(1, v + 1):
            E = (a * E) / (r + a * E)
        return E

    @staticmethod
    def find_min_v(a: float, target_loss: float, max_v: int = 100000) -> tuple:
        """Находит минимальное v, при котором E(v, a) <= target_loss."""
        if a < 0:
            raise ValueError("Нагрузка a должна быть >= 0.")
        if not (0.0 < target_loss < 1.0):
            raise ValueError("Допустимая вероятность блокировки должна быть в (0, 1).")
        if a == 0.0:
            return 1, 0.0  # При нулевой нагрузке достаточно 1 канала (потери 0)

        for v in range(1, max_v + 1):
            E = ErlangBCalculator.erlang_b(v, a)
            if E <= target_loss:
                return v, E
        raise RuntimeError(f"Не удалось найти v <= {max_v}.")

    @staticmethod
    def find_max_a(v: int, target_loss: float, tol: float = 1e-12, max_iter: int = 200) -> tuple:
        """Находит максимальную нагрузку a, при которой E(v, a) <= target_loss."""
        if v <= 0:
            raise ValueError("Число каналов v должно быть положительным.")
        if not (0.0 < target_loss < 1.0):
            raise ValueError("Допустимая вероятность блокировки должна быть в (0, 1).")

        # Определяем верхнюю границу отрезка для метода бисекции
        a_high = 1.0
        while ErlangBCalculator.erlang_b(v, a_high) <= target_loss:
            a_high *= 2.0
            if a_high > 1e15:
                break
        a_low = 0.0

        for _ in range(max_iter):
            a_mid = (a_low + a_high) / 2.0
            E_mid = ErlangBCalculator.erlang_b(v, a_mid)
            if abs(E_mid - target_loss) < tol:
                break
            if E_mid < target_loss:
                a_low = a_mid
            else:
                a_high = a_mid
        return (a_low + a_high) / 2.0, ErlangBCalculator.erlang_b(v, (a_low + a_high) / 2.0)


def safe_input_float(prompt: str, min_val: float = None, max_val: float = None) -> float:
    """Безопасный ввод числа с плавающей точкой с проверкой диапазона."""
    while True:
        try:
            val = float(input(prompt).strip())
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"Значение должно быть в диапазоне [{min_val}, {max_val}]. Повторите ввод.")
                continue
            return val
        except ValueError:
            print("Ошибка ввода. Пожалуйста, введите число.")


def safe_input_int(prompt: str, min_val: int = None, max_val: int = None) -> int:
    """Безопасный ввод целого числа с проверкой диапазона."""
    while True:
        try:
            val = int(input(prompt).strip())
            if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
                print(f"Значение должно быть в диапазоне [{min_val}, {max_val}]. Повторите ввод.")
                continue
            return val
        except ValueError:
            print("Ошибка ввода. Пожалуйста, введите целое число.")


def save_to_file(text: str, filename: str = "erlang_results.txt"):
    """Добавляет запись в файл с отметкой времени."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"[{timestamp}]\n{text}\n{'-' * 50}\n")
    print(f"Результат сохранён в файл '{filename}'.")


def main():
    print("=" * 50)
    print("   КАЛЬКУЛЯТОР МОДЕЛИ ЭРЛАНГА (ERLANG B)")
    print("=" * 50)

    calc = ErlangBCalculator()

    while True:
        print("\n--- Меню ---")
        print("1. Вычислить Вероятность блокировки (E) по v и a")
        print("2. Найти Число каналов (v) по a и допустимой E")
        print("3. Найти Нагрузку (a) по v и допустимой E")
        print("0. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            v = safe_input_int("Введите число каналов v: ", min_val=0)
            a = safe_input_float("Введите нагрузку a (Эрл): ", min_val=0.0)
            E = calc.erlang_b(v, a)
            m = a * (1 - E)
            res = (f"Прямой расчёт:\n"
                   f"v = {v}, a = {a:.4f} Эрл\n"
                   f"Вероятность блокировки E = {E:.6f}\n"
                   f"Среднее число занятых каналов m = {m:.4f}")
            print("\n" + res)
            if input("Сохранить результат в файл? (y/n): ").strip().lower() == 'y':
                save_to_file(res)

        elif choice == '2':
            a = safe_input_float("Введите нагрузку a (Эрл): ", min_val=0.0)
            target_E = safe_input_float("Введите допустимую вероятность блокировки E: ", min_val=0.0, max_val=1.0)
            if target_E <= 0.0 or target_E >= 1.0:
                print("Ошибка: допустимая вероятность блокировки должна быть строго между 0 и 1.")
                continue
            try:
                v, E_act = calc.find_min_v(a, target_E)
                m = a * (1 - E_act)
                res = (f"Обратная задача (поиск v):\n"
                       f"Заданная нагрузка a = {a:.4f} Эрл\n"
                       f"Допустимая вероятность блокировки <= {target_E:.6f}\n"
                       f"Минимальное число каналов v = {v}\n"
                       f"Фактическая вероятность блокировки E = {E_act:.6f}\n"
                       f"Среднее число занятых каналов m = {m:.4f}")
                print("\n" + res)
                if input("Сохранить результат в файл? (y/n): ").strip().lower() == 'y':
                    save_to_file(res)
            except RuntimeError as e:
                print(f"\nОшибка: {e}")

        elif choice == '3':
            v = safe_input_int("Введите число каналов v: ", min_val=1)
            target_E = safe_input_float("Введите допустимую вероятность блокировки E: ", min_val=0.0, max_val=1.0)
            if target_E <= 0.0 or target_E >= 1.0:
                print("Ошибка: допустимая вероятность блокировки должна быть строго между 0 и 1.")
                continue
            a, E_act = calc.find_max_a(v, target_E)
            m = a * (1 - E_act)
            res = (f"Обратная задача (поиск a):\n"
                   f"Число каналов v = {v}\n"
                   f"Допустимая вероятность блокировки <= {target_E:.6f}\n"
                   f"Максимальная нагрузка a = {a:.4f} Эрл\n"
                   f"Фактическая вероятность блокировки E = {E_act:.6f}\n"
                   f"Среднее число занятых каналов m = {m:.4f}")
            print("\n" + res)
            if input("Сохранить результат в файл? (y/n): ").strip().lower() == 'y':
                save_to_file(res)

        elif choice == '0':
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, выберите пункт меню от 0 до 3.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nРабота калькулятора завершена.")
        sys.exit(0)