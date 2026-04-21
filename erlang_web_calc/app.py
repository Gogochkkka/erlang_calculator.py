# app.py
from flask import Flask, render_template, request, jsonify
from erlang_calculator import ErlangBCalculator

app = Flask(__name__)
calc = ErlangBCalculator()


@app.route('/')
def index():
    """Главная страница с формой."""
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    """Обработка AJAX-запроса от клиента."""
    try:
        data = request.get_json()
        mode = data.get('mode')

        if mode == 'calc_e':
            v = int(data['v'])
            a = float(data['a'])
            E = calc.erlang_b(v, a)
            m = a * (1 - E)
            return jsonify({
                'success': True,
                'result': f'E = {E:.6f}, m = {m:.4f}',
                'details': {
                    'E': round(E, 6),
                    'm': round(m, 4)
                }
            })

        elif mode == 'find_v':
            a = float(data['a'])
            target_E = float(data['target_e'])
            v, E_act = calc.find_min_v(a, target_E)
            m = a * (1 - E_act)
            return jsonify({
                'success': True,
                'result': f'v = {v} (факт. E = {E_act:.6f}, m = {m:.4f})',
                'details': {
                    'v': v,
                    'E': round(E_act, 6),
                    'm': round(m, 4)
                }
            })

        elif mode == 'find_a':
            v = int(data['v'])
            target_E = float(data['target_e'])
            a, E_act = calc.find_max_a(v, target_E)
            m = a * (1 - E_act)
            return jsonify({
                'success': True,
                'result': f'a = {a:.4f} Эрл (факт. E = {E_act:.6f}, m = {m:.4f})',
                'details': {
                    'a': round(a, 4),
                    'E': round(E_act, 6),
                    'm': round(m, 4)
                }
            })
        else:
            return jsonify({'success': False, 'error': 'Неизвестный режим'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})


if __name__ == '__main__':
    # debug=True включает авто-перезагрузку при изменениях в коде
    app.run(debug=True, host='127.0.0.1', port=5000)