import sys
import locale
from flask import Flask, jsonify, Response, request
from flask_cors import CORS
import psycopg2
import json
import bcrypt
import secrets
from functools import wraps
from db_connection import get_db_connection

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

app = Flask(__name__)
CORS(app)

app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False


def generate_token():
    return secrets.token_hex(16)

def check_login(email, password):
    conn = get_db_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute("SELECT id, name, email , password FROM users WHERE email = %s;", (email,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user and bcrypt.checkpw(password.encode('utf-8'), user[3].encode('utf-8')):
        return {'id': user[0], 'name': user[1], 'email': user[2]}
    return None

def verify_token(token):
    conn = get_db_connection()
    if conn is None:
        return None
    cur = conn.cursor()
    cur.execute("SELECT user_id FROM sessions WHERE token = %s;", (token,))
    session = cur.fetchone()
    cur.close()
    conn.close()
    return session[0] if session else None

@app.route('/api/login', methods=['POST'])  
def login():
    data = request.get_json()    
    email = data.get('email')
    password = data.get('password')
    print(f"Tentativa de login: email={email}")
    
    if not email or not password:
        print("Email ou senha não fornecidos")
        return Response(json.dumps({"error": "Email e senha são obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400

    user = check_login(email, password)
    if user:
        token = generate_token()
        print(f"Usuário autenticado: {user['id']}, token gerado: {token}")
        conn = get_db_connection()
        if conn is None:
            print("Falha na conexão com o banco")
            return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO sessions (user_id, token) VALUES (%s, %s);", (user['id'], token))
            conn.commit()
            print(f"Sessão criada para user_id {user['id']} com token {token}")
            return Response(json.dumps({"message": "Login bem-sucedido", "user": user, "token": token}, ensure_ascii=False), mimetype='application/json'), 200
        except Exception as e:
            conn.rollback()
            print(f"Erro ao criar sessão: {e}")
            return Response(json.dumps({"error": "Erro ao criar sessão"}, ensure_ascii=False), mimetype='application/json'), 500
        finally:
            cur.close()
            conn.close()
    print("Email ou senha inválidos")
    return Response(json.dumps({"error": "Email ou senha inválidos"}, ensure_ascii=False), mimetype='application/json'), 401

#PROTEGER OS ENDPOINTS
def require_login(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return Response(json.dumps({"error": "Autenticação requerida"}, ensure_ascii=False), mimetype='application/json'), 401
        user_id = verify_token(token)
        if not user_id:
            return Response(json.dumps({"error": "Token inválido"}, ensure_ascii=False), mimetype='application/json'), 401
        return f(*args, **kwargs)
    return decorated
    
 
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password') 
    if not all ([name, email, password]):
        return Response(json.dumps({"error": "Nome, email e senha são obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s) RETURNING id;",
            (name, email, hashed_password.decode('utf-8'))
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        print(f"Usuário registrado: {user_id}")
        return Response(json.dumps({"message": "Usuário registrado com sucesso", "id": user_id}, ensure_ascii=False), mimetype='application/json'), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return Response(json.dumps({"error": "Email já registrado"}, ensure_ascii=False), mimetype='application/json'), 409
    except Exception as e:
        conn.rollback()
        print(f"Erro ao registrar usuário: {e}")
        return Response(json.dumps({"error": "Erro ao registrar usuário"}, ensure_ascii=False), mimetype='application/json'), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/users', methods=['GET'])
@require_login
def get_users():
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Falha na conexão com o banco"}), 500
    cur = conn.cursor()
    cur.execute("SELECT id, name, email FROM users;")
    users = cur.fetchall()
    print(f"Dados brutos do banco (users): {users}")
    cur.close()
    conn.close()
    result = [{'id': u[0], 'name': u[1], 'email': u[2]} for u in users]
    # fazer serialização manualmente pra evitar escape de letras (ã, á, â)
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')

@app.route('/api/gains/<int:user_id>', methods=['GET'])
@require_login
def get_gains(user_id):
    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    cur.execute("SELECT id, description, amount, source, date FROM gains WHERE user_id = %s;", (user_id,))
    gains = cur.fetchall()
    print(f"Dados brutos do banco (gains): {gains}")
    cur.close()
    conn.close()
    if not gains:
        print("Nenhum ganho encontrado para o user_id fornecido.")
        return Response(json.dumps([], ensure_ascii=False), mimetype='application/json')
    try:
        result = [{
            'id': g[0],
            'description': g[1],
            'amount': float(g[2]),
            'source': g[3],
            'date': str(g[4])
            } for g in gains]
        print(f"Dados formatados para JSON (gains): {result}")
        return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')
    except IndexError as e:
        print(f"Erro ao formatar dados: {e}")
        return jsonify({"error": "Erro ao processar os dados do banco"}), 500
    
@app.route('/api/expenses/<int:user_id>', methods=['GET'])
@require_login
def get_expenses(user_id):
    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    cur.execute("SELECT id, user_id, description, category_id, amount, date FROM expenses WHERE user_id = %s;", (user_id,))
    expenses = cur.fetchall()
    print(f"Dados brutos do banco (expenses): {expenses}")
    cur.close()
    conn.close()
    if not expenses:
        print("Nenhuma despesa encontrada para o user_id fornecido.")
        return Response(json.dumps([], ensure_ascii=False), mimetype='application/json')
    try:
        result = [{
            'id': e[0],
            'user_id': e[1],
            'description': e[2],
            'category_id': e[3],  # category_id é a 4ª coluna (índice 3)
            'amount': float(e[4]),  # amount é a 5ª coluna (índice 4)
            'date': str(e[5])  # date é a 6ª coluna (índice 5)
        } for e in expenses]
        print(f"Dados formatados para JSON (expenses): {result}")
        return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')
    except IndexError as e:
        print(f"Erro ao formatar dados: {e}")
        return Response(json.dumps({"error": "Erro ao processar os dados do banco"}, ensure_ascii=False), mimetype='application/json'), 500
    
@app.route('/api/gains', methods=['POST'])
@require_login
def add_gain():
    data = request.get_json()
    user_id = data.get('user_id')
    description = data.get('description')
    amount = data.get('amount')
    source = data.get('source')
    date = data.get('date')

    if not all([user_id, description, amount, source, date]):
        return Response(json.dumps({"error": "Faltam campos obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400

    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO gains (user_id, description, amount, source, date) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (user_id, description, amount, source, date)
        )
        gain_id = cur.fetchone()[0]
        conn.commit()
        print(f"Ganho adicionado: {gain_id}")
        return Response(json.dumps({"message": "Ganho adicionado com sucesso", "id": gain_id}, ensure_ascii=False), mimetype='application/json'), 201
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar ganho: {e}")
        return Response(json.dumps({"error": "Erro ao adicionar ganho"}, ensure_ascii=False), mimetype='application/json'), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/expenses', methods=['POST'])
@require_login
def add_expense():
    data = request.get_json()
    user_id = data.get('user_id')
    description = data.get('description')
    amount = data.get('amount')
    date = data.get('date')
    category_id = data.get('category_id')

    if not all([user_id, description, amount, date, category_id]):
        return Response(json.dumps({"error": "Faltam campos obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400

    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO expenses (user_id, category_id, amount, description, date) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
            (user_id, category_id, amount, description, date)
        )
        expense_id = cur.fetchone()[0]
        conn.commit()
        print(f"Despesa adicionada: {expense_id}")
        return Response(json.dumps({"message": "Despesa adicionada com sucesso", "id": expense_id}, ensure_ascii=False), mimetype='application/json'), 201
    except Exception as e:
        conn.rollback()
        print(f"Erro ao adicionar despesa: {e}")
        return Response(json.dumps({"error": "Erro ao adicionar despesa"}, ensure_ascii=False), mimetype='application/json'), 500
    finally:
        cur.close()
        conn.close()
        
@app.route('/api/gains/<int:gain_id>', methods=['PUT'])
@require_login
def update_gain(gain_id):
    data = request.get_json()
    description = data.get('description')
    amount = data.get('amount')
    source = data.get('source')
    date = data.get('date')

    if not all([description, amount, source, date]):
        return Response(json.dumps({"error": "Faltam campos obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400

    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE gains SET description = %s, amount = %s, source = %s, date = %s WHERE id = %s;",
            (description, amount, source, date, gain_id)
        )
        conn.commit()
        print(f"Ganho atualizado: {gain_id}")
        return Response(json.dumps({"message": "Ganho atualizado com sucesso"}, ensure_ascii=False), mimetype='application/json'), 200
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar ganho: {e}")
        return Response(json.dumps({"error": "Erro ao atualizar ganho"}, ensure_ascii=False), mimetype='application/json'), 500
    finally:
        cur.close()
        conn.close()
        
@app.route('/api/gains/<int:gain_id>', methods=['DELETE'])
@require_login
def delete_gain(gain_id):
    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM gains WHERE id = %s;", (gain_id,))
        conn.commit()
        print(f"Ganho deletado: {gain_id}")
        return Response(json.dumps({"message": "Ganho deletado com sucesso"}, ensure_ascii=False), mimetype='application/json'), 200
    except Exception as e:
        conn.rollback()
        print(f"Erro ao deletar ganho: {e}")
        return Response(json.dumps({"error": "Erro ao deletar ganho"}, ensure_ascii=False), mimetype='application/json'), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
@require_login
def update_expense(expense_id):
    data = request.get_json()
    description = data.get('description')
    amount = data.get('amount')
    date = data.get('date')
    category_id = data.get('category_id')

    if not all([description, amount, date, category_id]):
        return Response(json.dumps({"error": "Faltam campos obrigatórios"}, ensure_ascii=False), mimetype='application/json'), 400

    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    try:
        cur.execute(
            "UPDATE expenses SET description = %s, amount = %s, date = %s, category_id = %s WHERE id = %s;",
            (description, amount, date, category_id, expense_id)
        )
        conn.commit()
        print(f"Despesa atualizada: {expense_id}")
        return Response(json.dumps({"message": "Despesa atualizada com sucesso"}, ensure_ascii=False), mimetype='application/json'), 200
    except Exception as e:
        conn.rollback()
        print(f"Erro ao atualizar despesa: {e}")
        return Response(json.dumps({"error": "Erro ao atualizar despesa"}, ensure_ascii=False), mimetype='application/json'), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
@require_login
def delete_expense(expense_id):
    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM expenses WHERE id = %s;", (expense_id,))
        conn.commit()
        print(f"Despesa deletada: {expense_id}")
        return Response(json.dumps({"message": "Despesa deletada com sucesso"}, ensure_ascii=False), mimetype='application/json'), 200
    except Exception as e:
        conn.rollback()
        print(f"Erro ao deletar despesa: {e}")
        return Response(json.dumps({"error": "Erro ao deletar despesa"}, ensure_ascii=False), mimetype='application/json'), 500
    finally:
        cur.close()
        conn.close()

@app.route('/api/categories', methods=['GET'])
@require_login
def get_categories():
    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM categories;")
    categories = cur.fetchall()
    print(f"Dados brutos do banco (categories): {categories}")
    cur.close()
    conn.close()
    result = [{'id': c[0], 'name': c[1]} for c in categories]
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')
 
@app.route('/api/financial-score/<int:user_id>', methods=['GET'])
@require_login
def get_financial_score(user_id):
    conn = get_db_connection()
    if conn is None:
        return Response(json.dumps({"error": "Falha na conexão com o banco"}, ensure_ascii=False), mimetype='application/json'), 500
    cur = conn.cursor()
    # total dos ganhos
    cur.execute("SELECT SUM(amount) FROM gains WHERE user_id = %s;", (user_id,))
    total_gains = cur.fetchone()[0] or 0
    # total das despesas
    cur.execute("SELECT SUM(amount) FROM expenses WHERE user_id = %s;", (user_id,))
    total_expenses = cur.fetchone()[0] or 0
    cur.close()
    conn.close()
    saldo = float(total_gains) - float(total_expenses)
    score = 100 - (float(total_expenses) / float(total_gains) * 100) if total_gains > 0 else 0
    result = {
        'saldo': saldo,
        'score': max(0, min(100, score))  # score entre 0 e 100 (mediante mudanças)
    }
    # gains = [g for g in gains_data if str['user_id'] == user_id]
    # expenses = [e for e in expenses_data if str(e['user_id']) == user_id]
    # total_gains = sum(g['amount'] for g in gains)
    # total_expenses = sum(e['amount'] for e in expenses)
    # saldo = total_gains - total_expenses
    # score = (saldo / total_gains * 100) if total_gains > 0 else 0
    # return jsonify({'score': score, 'saldo': saldo})
    print(f"Financial score para user_id {user_id}: {result}")
    return Response(json.dumps(result, ensure_ascii=False), mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True, port=5000)