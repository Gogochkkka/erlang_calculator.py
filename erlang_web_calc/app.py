# app.py
from flask import Flask, render_template, request, jsonify
from erlang_calculator import ErlangBCalculator
import math

app = Flask(__name__)
calc = ErlangBCalculator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        data = request.get_json()
        mode = data.get('mode')

        # ------------------------------------------------------------
        # 1. a, v -> E, m
        # ------------------------------------------------------------
        if mode == 'av_to_Em':
            a = float(data['a'])
            v = int(data['v'])
            E = calc.erlang_b(v, a)
            m = a * (1 - E)
            return jsonify({
                'success': True,
                'result': f'E = {E:.6f}, m = {m:.6f}',
                'details': {'E': E, 'm': m}
            })

        # ------------------------------------------------------------
        # 2. a, E -> v, m
        # ------------------------------------------------------------
        elif mode == 'aE_to_vm':
            a = float(data['a'])
            target_E = float(data['target_e'])
            v, E_act = calc.find_min_v(a, target_E)
            m = a * (1 - E_act)
            return jsonify({
                'success': True,
                'result': f'v = {v}, m = {m:.6f} (E = {E_act:.6f})',
                'details': {'v': v, 'm': m, 'E': E_act}
            })

        # ------------------------------------------------------------
        # 3. a, m -> v, E
        # ------------------------------------------------------------
        elif mode == 'am_to_vE':
            a = float(data['a'])
            target_m = float(data['target_m'])
            if target_m >= a:
                return jsonify({'success': False, 'error': 'm должно быть меньше a (m = a·(1-E) < a)'})
            # E = 1 - m/a
            target_E = 1.0 - target_m / a
            v, E_act = calc.find_min_v(a, target_E)
            m_act = a * (1 - E_act)
            return jsonify({
                'success': True,
                'result': f'v = {v}, E = {E_act:.6f} (m = {m_act:.6f})',
                'details': {'v': v, 'E': E_act, 'm': m_act}
            })

        # ------------------------------------------------------------
        # 4. v, m -> a, E
        # ------------------------------------------------------------
        elif mode == 'vm_to_aE':
            v = int(data['v'])
            target_m = float(data['target_m'])
            if target_m >= v:
                return jsonify({'success': False, 'error': 'm должно быть меньше v'})
            # Решаем уравнение m = a * (1 - E(v,a)) относительно a
            # используем бисекцию, т.к. m монотонно возрастает с a
            a_low = 0.0
            a_high = v * 10.0  # начальное предположение
            while True:
                try:
                    m_high = a_high * (1 - calc.erlang_b(v, a_high))
                    if m_high >= target_m:
                        break
                    a_high *= 2.0
                except:
                    a_high *= 2.0
                if a_high > 1e9:
                    return jsonify({'success': False, 'error': 'Не удалось найти решение'})
            for _ in range(200):
                a_mid = (a_low + a_high) / 2.0
                m_mid = a_mid * (1 - calc.erlang_b(v, a_mid))
                if abs(m_mid - target_m) < 1e-9:
                    break
                if m_mid < target_m:
                    a_low = a_mid
                else:
                    a_high = a_mid
            a_opt = (a_low + a_high) / 2.0
            E_opt = calc.erlang_b(v, a_opt)
            m_opt = a_opt * (1 - E_opt)
            return jsonify({
                'success': True,
                'result': f'a = {a_opt:.6f}, E = {E_opt:.6f} (m = {m_opt:.6f})',
                'details': {'a': a_opt, 'E': E_opt, 'm': m_opt}
            })

        # ------------------------------------------------------------
        # 5. v, E -> a, m
        # ------------------------------------------------------------
        elif mode == 'vE_to_am':
            v = int(data['v'])
            target_E = float(data['target_e'])
            a, E_act = calc.find_max_a(v, target_E)
            m = a * (1 - E_act)
            return jsonify({
                'success': True,
                'result': f'a = {a:.6f}, m = {m:.6f} (E = {E_act:.6f})',
                'details': {'a': a, 'm': m, 'E': E_act}
            })

        # ------------------------------------------------------------
        # 6. E, m -> a, v
        # ------------------------------------------------------------
        elif mode == 'Em_to_av':
            target_E = float(data['target_e'])
            target_m = float(data['target_m'])
            # a = m / (1 - E)
            a = target_m / (1.0 - target_E)
            v, E_act = calc.find_min_v(a, target_E)
            m_act = a * (1 - E_act)
            return jsonify({
                'success': True,
                'result': f'a = {a:.6f}, v = {v} (E = {E_act:.6f}, m = {m_act:.6f})',
                'details': {'a': a, 'v': v, 'E': E_act, 'm': m_act}
            })

        else:
            return jsonify({'success': False, 'error': 'Неизвестный режим'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)