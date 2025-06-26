from flask import Blueprint, request, jsonify
from src.models.receitas_models import db, Paciente
from datetime import datetime
import csv
import io

pacientes_bp = Blueprint('pacientes', __name__)

@pacientes_bp.route('/pacientes', methods=['GET'])
def get_pacientes():
    """Listar todos os pacientes"""
    try:
        search = request.args.get('search', '')
        
        if search:
            pacientes = Paciente.query.filter(
                Paciente.nome_completo.ilike(f'%{search}%')
            ).order_by(Paciente.nome_completo).all()
        else:
            pacientes = Paciente.query.order_by(Paciente.nome_completo).all()
        
        return jsonify({
            'success': True,
            'data': [paciente.to_dict() for paciente in pacientes],
            'total': len(pacientes)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@pacientes_bp.route('/pacientes', methods=['POST'])
def create_paciente():
    """Criar novo paciente"""
    try:
        data = request.get_json()
        
        if not data.get('nome_completo'):
            return jsonify({'success': False, 'error': 'Nome é obrigatório'}), 400
        
        # Verificar se CPF já existe (se fornecido)
        if data.get('cpf'):
            existing = Paciente.query.filter_by(cpf=data['cpf']).first()
            if existing:
                return jsonify({'success': False, 'error': 'CPF já cadastrado'}), 400
        
        paciente = Paciente(
            nome_completo=data['nome_completo'],
            cpf=data.get('cpf'),
            data_nascimento=datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date() if data.get('data_nascimento') else None
        )
        
        db.session.add(paciente)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': paciente.to_dict(),
            'message': 'Paciente cadastrado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@pacientes_bp.route('/pacientes/<int:paciente_id>', methods=['PUT'])
def update_paciente(paciente_id):
    """Atualizar paciente"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        data = request.get_json()
        
        if not data.get('nome_completo'):
            return jsonify({'success': False, 'error': 'Nome é obrigatório'}), 400
        
        # Verificar se CPF já existe em outro paciente
        if data.get('cpf') and data['cpf'] != paciente.cpf:
            existing = Paciente.query.filter_by(cpf=data['cpf']).first()
            if existing:
                return jsonify({'success': False, 'error': 'CPF já cadastrado'}), 400
        
        paciente.nome_completo = data['nome_completo']
        paciente.cpf = data.get('cpf')
        paciente.data_nascimento = datetime.strptime(data['data_nascimento'], '%Y-%m-%d').date() if data.get('data_nascimento') else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': paciente.to_dict(),
            'message': 'Paciente atualizado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@pacientes_bp.route('/pacientes/<int:paciente_id>', methods=['DELETE'])
def delete_paciente(paciente_id):
    """Excluir paciente"""
    try:
        paciente = Paciente.query.get_or_404(paciente_id)
        
        # Verificar se tem receitas associadas
        if paciente.receitas:
            return jsonify({
                'success': False, 
                'error': 'Não é possível excluir paciente com receitas cadastradas'
            }), 400
        
        db.session.delete(paciente)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Paciente excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@pacientes_bp.route('/pacientes/export', methods=['GET'])
def export_pacientes_csv():
    """Exportar pacientes para CSV"""
    try:
        pacientes = Paciente.query.order_by(Paciente.nome_completo).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['Nome Completo', 'CPF', 'Data Nascimento'])
        
        # Dados
        for paciente in pacientes:
            writer.writerow([
                paciente.nome_completo,
                paciente.cpf or '',
                paciente.data_nascimento.strftime('%Y-%m-%d') if paciente.data_nascimento else ''
            ])
        
        csv_data = output.getvalue()
        output.close()
        
        return jsonify({
            'success': True,
            'data': csv_data,
            'filename': f'pacientes_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@pacientes_bp.route('/pacientes/import', methods=['POST'])
def import_pacientes_csv():
    """Importar pacientes de CSV"""
    try:
        data = request.get_json()
        csv_content = data.get('csv_content', '')
        
        if not csv_content:
            return jsonify({'success': False, 'error': 'Conteúdo CSV não fornecido'}), 400
        
        # Processar CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        imported = 0
        duplicated = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                nome = row.get('Nome Completo', '').strip()
                cpf = row.get('CPF', '').strip()
                data_nasc = row.get('Data Nascimento', '').strip()
                
                if not nome:
                    errors.append(f'Linha {row_num}: Nome é obrigatório')
                    continue
                
                # Verificar duplicata por CPF
                if cpf:
                    existing = Paciente.query.filter_by(cpf=cpf).first()
                    if existing:
                        duplicated += 1
                        continue
                
                # Processar data
                data_nascimento = None
                if data_nasc:
                    try:
                        data_nascimento = datetime.strptime(data_nasc, '%Y-%m-%d').date()
                    except ValueError:
                        errors.append(f'Linha {row_num}: Data inválida ({data_nasc})')
                        continue
                
                # Criar paciente
                paciente = Paciente(
                    nome_completo=nome,
                    cpf=cpf if cpf else None,
                    data_nascimento=data_nascimento
                )
                
                db.session.add(paciente)
                imported += 1
                
            except Exception as e:
                errors.append(f'Linha {row_num}: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Importação concluída: {imported} importados, {duplicated} duplicados ignorados',
            'imported': imported,
            'duplicated': duplicated,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

