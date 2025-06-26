from flask import Blueprint, request, jsonify
from src.models.receitas_models import db, Medicamento
import csv
import io
from datetime import datetime

medicamentos_bp = Blueprint('medicamentos', __name__)

@medicamentos_bp.route('/medicamentos', methods=['GET'])
def get_medicamentos():
    """Listar todos os medicamentos"""
    try:
        search = request.args.get('search', '')
        
        if search:
            medicamentos = Medicamento.query.filter(
                Medicamento.denominacao_generica.ilike(f'%{search}%')
            ).order_by(Medicamento.denominacao_generica).all()
        else:
            medicamentos = Medicamento.query.order_by(Medicamento.denominacao_generica).all()
        
        return jsonify({
            'success': True,
            'data': [medicamento.to_dict() for medicamento in medicamentos],
            'total': len(medicamentos)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@medicamentos_bp.route('/medicamentos', methods=['POST'])
def create_medicamento():
    """Criar novo medicamento"""
    try:
        data = request.get_json()
        
        if not data.get('denominacao_generica'):
            return jsonify({'success': False, 'error': 'Denominação genérica é obrigatória'}), 400
        
        medicamento = Medicamento(
            denominacao_generica=data['denominacao_generica'],
            concentracao=data.get('concentracao'),
            apresentacao=data.get('apresentacao')
        )
        
        db.session.add(medicamento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': medicamento.to_dict(),
            'message': 'Medicamento cadastrado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@medicamentos_bp.route('/medicamentos/<int:medicamento_id>', methods=['PUT'])
def update_medicamento(medicamento_id):
    """Atualizar medicamento"""
    try:
        medicamento = Medicamento.query.get_or_404(medicamento_id)
        data = request.get_json()
        
        if not data.get('denominacao_generica'):
            return jsonify({'success': False, 'error': 'Denominação genérica é obrigatória'}), 400
        
        medicamento.denominacao_generica = data['denominacao_generica']
        medicamento.concentracao = data.get('concentracao')
        medicamento.apresentacao = data.get('apresentacao')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': medicamento.to_dict(),
            'message': 'Medicamento atualizado com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@medicamentos_bp.route('/medicamentos/<int:medicamento_id>', methods=['DELETE'])
def delete_medicamento(medicamento_id):
    """Excluir medicamento"""
    try:
        medicamento = Medicamento.query.get_or_404(medicamento_id)
        
        db.session.delete(medicamento)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Medicamento excluído com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@medicamentos_bp.route('/medicamentos/export', methods=['GET'])
def export_medicamentos_csv():
    """Exportar medicamentos para CSV"""
    try:
        medicamentos = Medicamento.query.order_by(Medicamento.denominacao_generica).all()
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Cabeçalho
        writer.writerow(['Denominação Genérica', 'Concentração', 'Apresentação'])
        
        # Dados
        for medicamento in medicamentos:
            writer.writerow([
                medicamento.denominacao_generica,
                medicamento.concentracao or '',
                medicamento.apresentacao or ''
            ])
        
        csv_data = output.getvalue()
        output.close()
        
        return jsonify({
            'success': True,
            'data': csv_data,
            'filename': f'medicamentos_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@medicamentos_bp.route('/medicamentos/import', methods=['POST'])
def import_medicamentos_csv():
    """Importar medicamentos de CSV"""
    try:
        data = request.get_json()
        csv_content = data.get('csv_content', '')
        
        if not csv_content:
            return jsonify({'success': False, 'error': 'Conteúdo CSV não fornecido'}), 400
        
        # Processar CSV
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        imported = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):
            try:
                denominacao = row.get('Denominação Genérica', '').strip()
                concentracao = row.get('Concentração', '').strip()
                apresentacao = row.get('Apresentação', '').strip()
                
                if not denominacao:
                    errors.append(f'Linha {row_num}: Denominação genérica é obrigatória')
                    continue
                
                # Criar medicamento
                medicamento = Medicamento(
                    denominacao_generica=denominacao,
                    concentracao=concentracao if concentracao else None,
                    apresentacao=apresentacao if apresentacao else None
                )
                
                db.session.add(medicamento)
                imported += 1
                
            except Exception as e:
                errors.append(f'Linha {row_num}: {str(e)}')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Importação concluída: {imported} medicamentos importados',
            'imported': imported,
            'errors': errors
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@medicamentos_bp.route('/medicamentos/seed', methods=['POST'])
def seed_medicamentos():
    """Popular banco com medicamentos de teste"""
    try:
        # Verificar se já existem medicamentos
        if Medicamento.query.count() > 0:
            return jsonify({
                'success': False,
                'error': 'Banco já possui medicamentos cadastrados'
            }), 400
        
        medicamentos_teste = [
            {'denominacao_generica': 'Sertralina', 'concentracao': '50 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Clonazepam', 'concentracao': '2 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Omeprazol', 'concentracao': '20 mg', 'apresentacao': 'Cápsulas'},
            {'denominacao_generica': 'Fluoxetina', 'concentracao': '20 mg', 'apresentacao': 'Cápsulas'},
            {'denominacao_generica': 'Diazepam', 'concentracao': '5 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Losartana', 'concentracao': '50 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Metformina', 'concentracao': '850 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Sinvastatina', 'concentracao': '20 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Atenolol', 'concentracao': '25 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Captopril', 'concentracao': '25 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Hidroclorotiazida', 'concentracao': '25 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Paracetamol', 'concentracao': '500 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Ibuprofeno', 'concentracao': '600 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Dipirona', 'concentracao': '500 mg', 'apresentacao': 'Comprimidos'},
            {'denominacao_generica': 'Amoxicilina', 'concentracao': '500 mg', 'apresentacao': 'Cápsulas'}
        ]
        
        for med_data in medicamentos_teste:
            medicamento = Medicamento(**med_data)
            db.session.add(medicamento)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'{len(medicamentos_teste)} medicamentos de teste adicionados com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

