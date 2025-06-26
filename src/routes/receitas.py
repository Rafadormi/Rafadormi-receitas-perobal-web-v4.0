from flask import Blueprint, request, jsonify, send_file
from src.models.receitas_models import db, Receita, ReceitaMedicamento, Paciente, Medicamento
from src.utils.pdf_generator import PDFGenerator
from datetime import datetime
import os
import tempfile

receitas_bp = Blueprint('receitas', __name__)

@receitas_bp.route('/receitas', methods=['GET'])
def get_receitas():
    """Listar todas as receitas"""
    try:
        receitas = Receita.query.order_by(Receita.created_at.desc()).all()
        
        return jsonify({
            'success': True,
            'data': [receita.to_dict() for receita in receitas],
            'total': len(receitas)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@receitas_bp.route('/receitas', methods=['POST'])
def create_receita():
    """Criar nova receita"""
    try:
        data = request.get_json()
        
        # Validações
        if not data.get('paciente_id'):
            return jsonify({'success': False, 'error': 'Paciente é obrigatório'}), 400
        
        if not data.get('medicamentos') or len(data['medicamentos']) == 0:
            return jsonify({'success': False, 'error': 'Pelo menos um medicamento é obrigatório'}), 400
        
        # Verificar se paciente existe
        paciente = Paciente.query.get(data['paciente_id'])
        if not paciente:
            return jsonify({'success': False, 'error': 'Paciente não encontrado'}), 404
        
        # Processar data inicial
        data_inicial = datetime.strptime(data['data_inicial'], '%Y-%m-%d').date()
        
        # Criar receita
        receita = Receita(
            paciente_id=data['paciente_id'],
            data_inicial=data_inicial,
            num_receitas=data.get('num_receitas', 1),
            observacoes=data.get('observacoes', '')
        )
        
        db.session.add(receita)
        db.session.flush()  # Para obter o ID da receita
        
        # Adicionar medicamentos
        for med_data in data['medicamentos']:
            # Verificar se medicamento existe
            medicamento = Medicamento.query.get(med_data['medicamento_id'])
            if not medicamento:
                return jsonify({'success': False, 'error': f'Medicamento ID {med_data["medicamento_id"]} não encontrado'}), 404
            
            receita_medicamento = ReceitaMedicamento(
                receita_id=receita.id,
                medicamento_id=med_data['medicamento_id'],
                posologia=med_data.get('posologia', ''),
                instrucoes=med_data.get('instrucoes', '')
            )
            
            db.session.add(receita_medicamento)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'data': receita.to_dict(),
            'message': 'Receita criada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@receitas_bp.route('/receitas/<int:receita_id>/pdf', methods=['GET'])
def generate_receita_pdf(receita_id):
    """Gerar PDF da receita"""
    try:
        receita = Receita.query.get_or_404(receita_id)
        
        # Preparar dados do paciente
        paciente_info = {
            'nome': receita.paciente.nome_completo,
            'data_nascimento': receita.paciente.data_nascimento.isoformat() if receita.paciente.data_nascimento else None,
            'cpf_rg': receita.paciente.cpf
        }
        
        # Preparar dados dos medicamentos
        medicamentos_info = []
        for receita_med in receita.medicamentos:
            med_info = {
                'denominacao': receita_med.medicamento.denominacao_generica,
                'concentracao': receita_med.medicamento.concentracao,
                'apresentacao': receita_med.medicamento.apresentacao,
                'posologia': receita_med.posologia,
                'instrucoes': receita_med.instrucoes
            }
            medicamentos_info.append(med_info)
        
        # Gerar PDF
        pdf_generator = PDFGenerator()
        
        if receita.num_receitas == 1:
            # Receita única
            pdf_file = pdf_generator.generate_receita_pdf(
                paciente_info,
                medicamentos_info,
                receita.data_inicial,
                receita.observacoes
            )
        else:
            # Múltiplas receitas
            pdf_file = pdf_generator.generate_receitas_multiplas(
                paciente_info,
                medicamentos_info,
                receita.num_receitas,
                receita.data_inicial,
                receita.observacoes
            )
        
        # Nome do arquivo
        filename = pdf_generator.get_filename_for_patient(
            receita.paciente.nome_completo,
            receita.data_inicial,
            receita.num_receitas
        )
        
        return send_file(
            pdf_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@receitas_bp.route('/receitas/generate', methods=['POST'])
def generate_receita_direct():
    """Gerar receita diretamente sem salvar no banco"""
    try:
        data = request.get_json()
        
        # Validações
        if not data.get('paciente_id'):
            return jsonify({'success': False, 'error': 'Paciente é obrigatório'}), 400
        
        if not data.get('medicamentos') or len(data['medicamentos']) == 0:
            return jsonify({'success': False, 'error': 'Pelo menos um medicamento é obrigatório'}), 400
        
        # Buscar dados do paciente
        paciente = Paciente.query.get(data['paciente_id'])
        if not paciente:
            return jsonify({'success': False, 'error': 'Paciente não encontrado'}), 404
        
        # Preparar dados do paciente
        paciente_info = {
            'nome': paciente.nome_completo,
            'data_nascimento': paciente.data_nascimento.isoformat() if paciente.data_nascimento else None,
            'cpf_rg': paciente.cpf
        }
        
        # Preparar dados dos medicamentos
        medicamentos_info = []
        for med_data in data['medicamentos']:
            medicamento = Medicamento.query.get(med_data['medicamento_id'])
            if not medicamento:
                return jsonify({'success': False, 'error': f'Medicamento ID {med_data["medicamento_id"]} não encontrado'}), 404
            
            med_info = {
                'denominacao': medicamento.denominacao_generica,
                'concentracao': medicamento.concentracao,
                'apresentacao': medicamento.apresentacao,
                'posologia': med_data.get('posologia', ''),
                'instrucoes': med_data.get('instrucoes', '')
            }
            medicamentos_info.append(med_info)
        
        # Processar data inicial
        data_inicial = datetime.strptime(data['data_inicial'], '%Y-%m-%d').date()
        num_receitas = data.get('num_receitas', 1)
        observacoes = data.get('observacoes', '')
        
        # Gerar PDF
        pdf_generator = PDFGenerator()
        
        if num_receitas == 1:
            # Receita única
            pdf_file = pdf_generator.generate_receita_pdf(
                paciente_info,
                medicamentos_info,
                data_inicial,
                observacoes
            )
        else:
            # Múltiplas receitas
            pdf_file = pdf_generator.generate_receitas_multiplas(
                paciente_info,
                medicamentos_info,
                num_receitas,
                data_inicial,
                observacoes
            )
        
        # Nome do arquivo
        filename = pdf_generator.get_filename_for_patient(
            paciente.nome_completo,
            data_inicial,
            num_receitas
        )
        
        return send_file(
            pdf_file,
            as_attachment=True,
            download_name=filename,
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@receitas_bp.route('/receitas/<int:receita_id>', methods=['DELETE'])
def delete_receita(receita_id):
    """Excluir receita"""
    try:
        receita = Receita.query.get_or_404(receita_id)
        
        db.session.delete(receita)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Receita excluída com sucesso'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

