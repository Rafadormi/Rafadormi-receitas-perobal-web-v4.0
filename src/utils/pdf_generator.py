from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from datetime import datetime, timedelta
import os
import tempfile

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        # Caminho para o logo (assumindo que está na pasta static)
        self.logo_path = os.path.join(os.path.dirname(__file__), 
                                      os.pardir, 
                                      'static', 
                                      'perobal_logo.png') # Nome do arquivo do logo

    def setup_custom_styles(self):
        """Configurar estilos customizados"""
        self.normal_style = self.styles['Normal']
        self.normal_style.fontName = 'Helvetica'
        self.normal_style.fontSize = 10

        self.bold_style = ParagraphStyle(
            'BoldStyle',
            parent=self.normal_style,
            fontName='Helvetica-Bold'
        )

        self.header_title_style = ParagraphStyle(
            'HeaderTitleStyle',
            parent=self.bold_style,
            fontSize=14,
            alignment=TA_CENTER
        )

        self.header_subtitle_style = ParagraphStyle(
            'HeaderSubtitleStyle',
            parent=self.normal_style,
            fontSize=12,
            alignment=TA_CENTER
        )

        self.address_style = ParagraphStyle(
            'AddressStyle',
            parent=self.normal_style,
            fontSize=8,
            alignment=TA_CENTER
        )

        self.recipe_title_style = ParagraphStyle(
            'RecipeTitleStyle',
            parent=self.bold_style,
            fontSize=12,
            alignment=TA_CENTER,
            spaceAfter=10
        )

        self.patient_info_label_style = ParagraphStyle(
            'PatientInfoLabelStyle',
            parent=self.bold_style,
            fontSize=10,
            alignment=TA_LEFT
        )

        self.patient_info_value_style = ParagraphStyle(
            'PatientInfoValueStyle',
            parent=self.normal_style,
            fontSize=10,
            alignment=TA_LEFT
        )

        self.medication_list_style = ParagraphStyle(
            'MedicationListStyle',
            parent=self.normal_style,
            fontSize=10,
            alignment=TA_LEFT,
            leading=12 # Espaçamento entre linhas
        )

        self.medication_item_style = ParagraphStyle(
            'MedicationItemStyle',
            parent=self.bold_style,
            fontSize=10,
            alignment=TA_LEFT
        )

        self.medication_detail_style = ParagraphStyle(
            'MedicationDetailStyle',
            parent=self.normal_style,
            fontSize=9,
            alignment=TA_LEFT,
            leftIndent=15 # Indentação para posologia e instruções
        )

        self.observations_style = ParagraphStyle(
            'ObservationsStyle',
            parent=self.normal_style,
            fontSize=10,
            alignment=TA_LEFT,
            spaceBefore=10
        )

        self.footer_style = ParagraphStyle(
            'FooterStyle',
            parent=self.normal_style,
            fontSize=8,
            alignment=TA_CENTER,
            spaceBefore=20
        )

    def create_header(self, data_receita):
        """Criar cabeçalho oficial da receita com logo e informações"""
        elements = []

        # Logo
        try:
            logo = Image(self.logo_path, width=50*mm, height=15*mm) # Ajustar tamanho conforme necessário
        except Exception as e:
            print(f"Erro ao carregar logo: {e}")
            logo = Paragraph("LOGO AQUI", self.header_title_style)

        # Informações da prefeitura
        prefeitura_info = [
            Paragraph("PREFEITURA MUNICIPAL DE PEROBAL", self.header_title_style),
            Paragraph("Secretaria Municipal de Saúde", self.header_subtitle_style),
            Paragraph("Cidade de todos", self.address_style) # Adicionado do modelo
        ]

        # Data da receita no canto superior direito
        data_formatada = data_receita.strftime("%d/%m/%Y")
        perobal_date = Paragraph(f"Perobal, {data_formatada}", self.normal_style)

        # Tabela para organizar logo, informações e data
        header_table_data = [
            [logo, Paragraph("", self.normal_style), perobal_date], # Espaço em branco para alinhar
            [Paragraph("", self.normal_style), prefeitura_info[0], Paragraph("", self.normal_style)],
            [Paragraph("", self.normal_style), prefeitura_info[1], Paragraph("", self.normal_style)],
            [Paragraph("", self.normal_style), prefeitura_info[2], Paragraph("", self.normal_style)]
        ]

        header_table = Table(header_table_data, colWidths=[55*mm, 90*mm, 50*mm])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (0,-1), 'LEFT'),
            ('ALIGN', (1,0), (1,-1), 'CENTER'),
            ('ALIGN', (2,0), (2,0), 'RIGHT'),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 5*mm))
        elements.append(Paragraph("RECEITA MÉDICA", self.recipe_title_style))
        elements.append(Spacer(1, 5*mm))

        return elements

    def create_patient_info(self, paciente_info, data_receita):
        """Criar seção de informações do paciente em duas colunas"""
        patient_elements = []

        # Data de Nascimento formatada
        data_nasc_formatada = ""
        if paciente_info.get('data_nascimento'):
            try:
                data_nasc = datetime.strptime(paciente_info['data_nascimento'], '%Y-%m-%d')
                data_nasc_formatada = data_nasc.strftime("%d/%m/%Y")
            except:
                pass

        # Dados do paciente para a tabela
        data = [
            [Paragraph(f"<b>Paciente:</b> {paciente_info['nome']}", self.patient_info_label_style), 
             Paragraph(f"<b>Data de Nascimento:</b> {data_nasc_formatada}", self.patient_info_label_style)],
            [Paragraph(f"<b>CPF/RG:</b> {paciente_info.get('cpf_rg', '')}", self.patient_info_label_style), 
             Paragraph("", self.patient_info_label_style)] # Coluna vazia para alinhamento
        ]

        patient_table = Table(data, colWidths=[100*mm, 80*mm])
        patient_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ]))
        patient_elements.append(patient_table)
        patient_elements.append(Spacer(1, 10*mm))

        return patient_elements

    def create_medications_section(self, medicamentos_info):
        """Criar seção de medicamentos"""
        med_elements = []

        med_elements.append(Paragraph("<b>Medicamentos:</b>", self.patient_info_label_style))
        med_elements.append(Spacer(1, 2*mm))

        for i, med in enumerate(medicamentos_info, 1):
            # Nome do medicamento com concentração e apresentação
            med_name = med['denominacao']
            if med.get('concentracao') and med['concentracao'].strip():
                med_name += f" {med['concentracao']}"
            if med.get('apresentacao') and med['apresentacao'].strip():
                med_name += f" - {med['apresentacao']}"
            
            med_elements.append(Paragraph(f"{i}. {med_name}", self.medication_item_style))
            
            # Posologia (se não estiver vazia)
            if med.get('posologia') and med['posologia'].strip():
                med_elements.append(Paragraph(f"Posologia: {med['posologia']}", self.medication_detail_style))
            
            # Instruções (se não estiverem vazias)
            if med.get('instrucoes') and med['instrucoes'].strip():
                med_elements.append(Paragraph(f"Instruções: {med['instrucoes']}", self.medication_detail_style))
            
            med_elements.append(Spacer(1, 5*mm))
        
        return med_elements

    def create_observations_section(self, observacoes):
        """Criar seção de observações"""
        obs_elements = []
        
        if observacoes and observacoes.strip():
            obs_elements.append(Spacer(1, 10*mm))
            obs_elements.append(Paragraph("<b>Observações:</b>", self.patient_info_label_style))
            obs_elements.append(Paragraph(observacoes, self.observations_style))
        
        return obs_elements

    def create_signature_footer(self):
        """Criar rodapé com espaço para assinatura e informações de contato"""
        footer_elements = []
        
        footer_elements.append(Spacer(1, 40*mm)) # Espaço para assinatura
        footer_elements.append(Paragraph("______________________________________", self.normal_style))
        footer_elements.append(Paragraph("Assinatura do Médico", self.normal_style))
        footer_elements.append(Spacer(1, 5*mm))
        footer_elements.append(Paragraph("CRM:", self.normal_style))
        footer_elements.append(Spacer(1, 20*mm))

        # Rodapé com endereço
        address_footer = "Rua Jaracatiá, 1060 - Telefax (044)3625-1225 - CEP. 87538-000 - PEROBAL - PARANÁ"
        footer_elements.append(Paragraph(address_footer, self.footer_style))
        
        return footer_elements

    def generate_receita_pdf(self, paciente_info, medicamentos_info, data_receita, observacoes=""):
        """Gerar uma única receita em PDF"""
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_filename = temp_file.name
        temp_file.close()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            temp_filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        # Construir conteúdo
        story = []
        
        # Cabeçalho
        story.extend(self.create_header(data_receita))
        
        # Informações do paciente
        story.extend(self.create_patient_info(paciente_info, data_receita))
        
        # Medicamentos
        story.extend(self.create_medications_section(medicamentos_info))
        
        # Observações
        story.extend(self.create_observations_section(observacoes))
        
        # Rodapé
        story.extend(self.create_signature_footer())
        
        # Gerar PDF
        doc.build(story)
        
        return temp_filename
    
    def generate_receitas_multiplas(self, paciente_info, medicamentos_info, num_receitas, data_inicial, observacoes=""):
        """Gerar múltiplas receitas em um único PDF"""
        # Criar arquivo temporário
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        temp_filename = temp_file.name
        temp_file.close()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(
            temp_filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2*cm,
            bottomMargin=2*cm
        )
        
        story = []
        
        # Gerar cada receita
        for i in range(num_receitas):
            # Calcular data da receita (primeira = data_inicial, demais +30 dias)
            data_receita = data_inicial + timedelta(days=30 * i)
            
            # Cabeçalho
            story.extend(self.create_header(data_receita))
            
            # Informações do paciente
            story.extend(self.create_patient_info(paciente_info, data_receita))
            
            # Medicamentos
            story.extend(self.create_medications_section(medicamentos_info))
            
            # Observações
            story.extend(self.create_observations_section(observacoes))
            
            # Rodapé
            story.extend(self.create_signature_footer())
            
            # Quebra de página (exceto na última receita)
            if i < num_receitas - 1:
                story.append(PageBreak())
        
        # Gerar PDF
        doc.build(story)
        
        return temp_filename
    
    def get_filename_for_patient(self, paciente_nome, data_inicial, num_receitas):
        """Gerar nome do arquivo baseado no paciente e data"""
        # Limpar nome do paciente para usar no arquivo
        nome_limpo = "".join(c for c in paciente_nome if c.isalnum() or c in (' ', '-', '_')).rstrip()
        nome_limpo = nome_limpo.replace(' ', '_')
        
        # Formato da data
        data_str = data_inicial.strftime("%Y%m%d")
        
        # Nome do arquivo
        if num_receitas == 1:
            filename = f"receita_{nome_limpo}_{data_str}.pdf"
        else:
            filename = f"receitas_{nome_limpo}_{data_str}_{num_receitas}meses.pdf"
        
        return filename



