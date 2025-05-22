import sys
import os
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file
import shutil
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))  # DON'T CHANGE THIS !!!

app = Flask(__name__)

# Caminho para o arquivo Excel original
EXCEL_ORIGINAL = '/home/ubuntu/upload/BASE CONTATO AVONA.xlsx'

# Diretório para armazenar as versões atualizadas
DATA_DIR = '/home/ubuntu/cliente_app/data'
os.makedirs(DATA_DIR, exist_ok=True)

# Caminho para o arquivo Excel atualizado
EXCEL_ATUAL = os.path.join(DATA_DIR, 'BASE CONTATO AVONA_atualizado.xlsx')

# Inicializa o arquivo atualizado copiando o original se não existir
if not os.path.exists(EXCEL_ATUAL):
    shutil.copy2(EXCEL_ORIGINAL, EXCEL_ATUAL)

def carregar_dados():
    """Carrega os dados do arquivo Excel atualizado"""
    try:
        return pd.read_excel(EXCEL_ATUAL)
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        # Se houver erro, tenta recriar o arquivo a partir do original
        shutil.copy2(EXCEL_ORIGINAL, EXCEL_ATUAL)
        return pd.read_excel(EXCEL_ATUAL)

@app.route('/')
def index():
    """Rota principal que renderiza a página inicial"""
    return render_template('index.html')

@app.route('/api/buscar_cliente', methods=['POST'])
def buscar_cliente():
    """API para buscar cliente pelo código"""
    try:
        codigo = request.json.get('codigo', '')
        
        # Validação básica
        if not codigo:
            return jsonify({'erro': 'Código do cliente é obrigatório'}), 400
        
        # Tenta converter para float para compatibilidade com o formato da planilha
        try:
            codigo_float = float(codigo)
        except ValueError:
            return jsonify({'erro': 'Código do cliente inválido'}), 400
        
        # Carrega os dados
        df = carregar_dados()
        
        # Busca o cliente pelo código
        cliente = df[df['CODCLI'] == codigo_float]
        
        if cliente.empty:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        # Retorna os dados do cliente
        cliente_data = {
            'codigo': str(cliente['CODCLI'].values[0]),
            'nome': str(cliente['RAZAO_SOCIAL'].values[0]),
            'telefone': str(cliente['CONTATO'].values[0]) if not pd.isna(cliente['CONTATO'].values[0]) else ''
        }
        
        return jsonify(cliente_data)
    
    except Exception as e:
        print(f"Erro ao buscar cliente: {e}")
        return jsonify({'erro': 'Erro ao buscar cliente'}), 500

@app.route('/api/atualizar_telefone', methods=['POST'])
def atualizar_telefone():
    """API para atualizar o telefone do cliente"""
    try:
        dados = request.json
        codigo = dados.get('codigo', '')
        novo_telefone = dados.get('telefone', '')
        
        # Validação básica
        if not codigo:
            return jsonify({'erro': 'Código do cliente é obrigatório'}), 400
        
        # Tenta converter para float para compatibilidade com o formato da planilha
        try:
            codigo_float = float(codigo)
        except ValueError:
            return jsonify({'erro': 'Código do cliente inválido'}), 400
        
        # Carrega os dados
        df = carregar_dados()
        
        # Verifica se o cliente existe
        cliente = df[df['CODCLI'] == codigo_float]
        if cliente.empty:
            return jsonify({'erro': 'Cliente não encontrado'}), 404
        
        # Atualiza o telefone
        df.loc[df['CODCLI'] == codigo_float, 'CONTATO'] = novo_telefone
        
        # Salva o arquivo atualizado
        df.to_excel(EXCEL_ATUAL, index=False)
        
        # Cria uma cópia com timestamp para histórico
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(DATA_DIR, f'BASE CONTATO AVONA_backup_{timestamp}.xlsx')
        df.to_excel(backup_file, index=False)
        
        return jsonify({'sucesso': True, 'mensagem': 'Telefone atualizado com sucesso'})
    
    except Exception as e:
        print(f"Erro ao atualizar telefone: {e}")
        return jsonify({'erro': 'Erro ao atualizar telefone'}), 500

@app.route('/download')
def download_excel():
    """Rota para download do arquivo Excel atualizado"""
    try:
        return send_file(EXCEL_ATUAL, as_attachment=True, download_name='BASE CONTATO AVONA_atualizado.xlsx')
    except Exception as e:
        print(f"Erro ao fazer download: {e}")
        return jsonify({'erro': 'Erro ao fazer download do arquivo'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
