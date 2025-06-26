import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, request, jsonify
from flask_cors import CORS
from src.models.receitas_models import db
from src.routes.pacientes import pacientes_bp
from src.routes.medicamentos import medicamentos_bp
from src.routes.receitas import receitas_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints
app.register_blueprint(pacientes_bp, url_prefix='/api')
app.register_blueprint(medicamentos_bp, url_prefix='/api')
app.register_blueprint(receitas_bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'receitas.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Printar o caminho absoluto do banco de dados
print('Banco de dados em uso:', os.path.abspath(os.path.join(os.path.dirname(__file__), 'database', 'receitas.db')))

# Criar tabelas
with app.app_context():
    db.create_all()

@app.route('/api/shutdown', methods=['POST'])
def shutdown():
    """Endpoint para encerrar o servidor de forma controlada"""
    try:
        # Função para encerrar o servidor Flask
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            # Para versões mais recentes do Werkzeug
            import signal
            import threading
            def shutdown_server():
                import time
                time.sleep(1)  # Aguarda um pouco antes de encerrar
                os.kill(os.getpid(), signal.SIGTERM)
            
            threading.Thread(target=shutdown_server).start()
            return jsonify({'message': 'Sistema sendo encerrado...'}), 200
        else:
            func()
            return jsonify({'message': 'Sistema encerrado com sucesso!'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
            return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
