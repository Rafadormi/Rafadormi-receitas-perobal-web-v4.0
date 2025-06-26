// Configuração da API
const API_BASE = 'http://localhost:5001/api';

// Estado global da aplicação
let pacientes = [];
let medicamentos = [];
let medicamentosSelecionados = [];
let pacienteSelecionado = null;

// Inicialização da aplicação
document.addEventListener('DOMContentLoaded', function() {
    // Definir data inicial como hoje
    document.getElementById('dataInicialReceita').value = new Date().toISOString().split('T')[0];
    
    // Carregar dados iniciais
    carregarPacientes();
    carregarMedicamentos();
    atualizarEstatisticas();
});

// Funções de navegação
function showTab(tabName) {
    // Remover classe active de todas as abas
    document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Ativar aba selecionada
    event.target.classList.add('active');
    document.getElementById(tabName).classList.add('active');
    
    // Recarregar dados se necessário
    if (tabName === 'pacientes') {
        carregarPacientes();
    } else if (tabName === 'medicamentos') {
        carregarMedicamentos();
    } else if (tabName === 'receitas') {
        carregarPacientesSelect();
        carregarMedicamentosSelect();
    } else if (tabName === 'backup') {
        atualizarEstatisticas();
    }
}

// Funções de utilidade
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;
    
    // Inserir no início do conteúdo ativo
    const activeTab = document.querySelector('.tab-content.active');
    activeTab.insertBefore(alertDiv, activeTab.firstChild);
    
    // Remover após 5 segundos
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatCPF(cpf) {
    return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4');
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR');
}

// === FUNÇÕES DE PACIENTES ===

async function carregarPacientes() {
    try {
        const response = await fetch(`${API_BASE}/pacientes`);
        const data = await response.json();
        
        if (data.success) {
            pacientes = data.data;
            renderizarPacientes(pacientes);
            document.getElementById('totalPacientes').textContent = pacientes.length;
        } else {
            showAlert('Erro ao carregar pacientes: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao carregar pacientes', 'danger');
        console.error('Erro:', error);
    }
}

function renderizarPacientes(pacientesList) {
    const container = document.getElementById('listaPacientes');
    
    if (pacientesList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>Nenhum paciente encontrado</h3>
                <p>Cadastre o primeiro paciente para começar</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = pacientesList.map(paciente => `
        <div class="patient-item" onclick="selecionarPaciente(${paciente.id})">
            <div class="patient-name">${paciente.nome_completo}</div>
            <div class="patient-info">
                ${paciente.cpf ? `CPF: ${formatCPF(paciente.cpf)}` : ''}
                ${paciente.data_nascimento ? ` | Nascimento: ${formatDate(paciente.data_nascimento)}` : ''}
            </div>
            <div style="margin-top: 10px;">
                <button class="btn btn-warning" onclick="event.stopPropagation(); editarPaciente(${paciente.id})" style="margin-right: 10px;">Editar</button>
                <button class="btn btn-danger" onclick="event.stopPropagation(); excluirPaciente(${paciente.id})">Excluir</button>
            </div>
        </div>
    `).join('');
}

function selecionarPaciente(id) {
    pacienteSelecionado = pacientes.find(p => p.id === id);
    
    // Remover seleção anterior
    document.querySelectorAll('.patient-item').forEach(item => item.classList.remove('selected'));
    
    // Adicionar seleção atual
    event.target.closest('.patient-item').classList.add('selected');
}

async function cadastrarPaciente() {
    const nome = document.getElementById('nomePaciente').value.trim();
    const cpf = document.getElementById('cpfPaciente').value.trim();
    const dataNascimento = document.getElementById('dataNascimento').value;
    
    if (!nome) {
        showAlert('Nome é obrigatório', 'danger');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/pacientes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                nome_completo: nome,
                cpf: cpf || null,
                data_nascimento: dataNascimento || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Paciente cadastrado com sucesso!', 'success');
            
            // Limpar formulário
            document.getElementById('nomePaciente').value = '';
            document.getElementById('cpfPaciente').value = '';
            document.getElementById('dataNascimento').value = '';
            
            // Recarregar lista
            carregarPacientes();
        } else {
            showAlert('Erro ao cadastrar paciente: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao cadastrar paciente', 'danger');
        console.error('Erro:', error);
    }
}

async function excluirPaciente(id) {
    if (!confirm('Tem certeza que deseja excluir este paciente?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/pacientes/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Paciente excluído com sucesso!', 'success');
            carregarPacientes();
        } else {
            showAlert('Erro ao excluir paciente: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao excluir paciente', 'danger');
        console.error('Erro:', error);
    }
}

function buscarPacientes() {
    const termo = document.getElementById('searchPaciente').value.toLowerCase();
    const pacientesFiltrados = pacientes.filter(paciente => 
        paciente.nome_completo.toLowerCase().includes(termo)
    );
    renderizarPacientes(pacientesFiltrados);
}

async function exportarPacientesCSV() {
    try {
        const response = await fetch(`${API_BASE}/pacientes/export`);
        const data = await response.json();
        
        if (data.success) {
            const blob = new Blob([data.data], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            a.click();
            window.URL.revokeObjectURL(url);
            
            showAlert('Arquivo CSV exportado com sucesso!', 'success');
        } else {
            showAlert('Erro ao exportar CSV: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao exportar CSV', 'danger');
        console.error('Erro:', error);
    }
}

async function importarPacientesCSV(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = async function(e) {
        try {
            const response = await fetch(`${API_BASE}/pacientes/import`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    csv_content: e.target.result
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert(data.message, 'success');
                carregarPacientes();
            } else {
                showAlert('Erro ao importar CSV: ' + data.error, 'danger');
            }
        } catch (error) {
            showAlert('Erro de conexão ao importar CSV', 'danger');
            console.error('Erro:', error);
        }
    };
    reader.readAsText(file);
    
    // Limpar input
    event.target.value = '';
}

// === FUNÇÕES DE MEDICAMENTOS ===

async function carregarMedicamentos() {
    try {
        const response = await fetch(`${API_BASE}/medicamentos`);
        const data = await response.json();
        
        if (data.success) {
            medicamentos = data.data;
            renderizarMedicamentos(medicamentos);
            document.getElementById('totalMedicamentos').textContent = medicamentos.length;
        } else {
            showAlert('Erro ao carregar medicamentos: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao carregar medicamentos', 'danger');
        console.error('Erro:', error);
    }
}

function renderizarMedicamentos(medicamentosList) {
    const container = document.getElementById('listaMedicamentos');
    
    if (medicamentosList.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <h3>Nenhum medicamento encontrado</h3>
                <p>Cadastre medicamentos para facilitar a criação de receitas</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = medicamentosList.map(medicamento => `
        <div class="patient-item">
            <div class="patient-name">${medicamento.denominacao_generica}</div>
            <div class="patient-info">
                ${medicamento.concentracao ? `Concentração: ${medicamento.concentracao}` : ''}
                ${medicamento.apresentacao ? ` | Apresentação: ${medicamento.apresentacao}` : ''}
            </div>
            <div style="margin-top: 10px;">
                <button class="btn btn-warning" onclick="editarMedicamento(${medicamento.id})" style="margin-right: 10px;">Editar</button>
                <button class="btn btn-danger" onclick="excluirMedicamento(${medicamento.id})">Excluir</button>
            </div>
        </div>
    `).join('');
}

async function cadastrarMedicamento() {
    const denominacao = document.getElementById('denominacaoMedicamento').value.trim();
    const concentracao = document.getElementById('concentracaoMedicamento').value.trim();
    const apresentacao = document.getElementById('apresentacaoMedicamento').value.trim();
    
    if (!denominacao) {
        showAlert('Denominação genérica é obrigatória', 'danger');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/medicamentos`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                denominacao_generica: denominacao,
                concentracao: concentracao || null,
                apresentacao: apresentacao || null
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Medicamento cadastrado com sucesso!', 'success');
            
            // Limpar formulário
            document.getElementById('denominacaoMedicamento').value = '';
            document.getElementById('concentracaoMedicamento').value = '';
            document.getElementById('apresentacaoMedicamento').value = '';
            
            // Recarregar lista
            carregarMedicamentos();
        } else {
            showAlert('Erro ao cadastrar medicamento: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao cadastrar medicamento', 'danger');
        console.error('Erro:', error);
    }
}

async function excluirMedicamento(id) {
    if (!confirm('Tem certeza que deseja excluir este medicamento?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/medicamentos/${id}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert('Medicamento excluído com sucesso!', 'success');
            carregarMedicamentos();
        } else {
            showAlert('Erro ao excluir medicamento: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao excluir medicamento', 'danger');
        console.error('Erro:', error);
    }
}

function buscarMedicamentos() {
    const termo = document.getElementById('searchMedicamento').value.toLowerCase();
    const medicamentosFiltrados = medicamentos.filter(medicamento => 
        medicamento.denominacao_generica.toLowerCase().includes(termo)
    );
    renderizarMedicamentos(medicamentosFiltrados);
}

async function exportarMedicamentosCSV() {
    try {
        const response = await fetch(`${API_BASE}/medicamentos/export`);
        const data = await response.json();
        
        if (data.success) {
            const blob = new Blob([data.data], { type: 'text/csv' });
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            a.click();
            window.URL.revokeObjectURL(url);
            
            showAlert('Arquivo CSV exportado com sucesso!', 'success');
        } else {
            showAlert('Erro ao exportar CSV: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao exportar CSV', 'danger');
        console.error('Erro:', error);
    }
}

async function importarMedicamentosCSV(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = async function(e) {
        try {
            const response = await fetch(`${API_BASE}/medicamentos/import`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    csv_content: e.target.result
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                showAlert(data.message, 'success');
                carregarMedicamentos();
            } else {
                showAlert('Erro ao importar CSV: ' + data.error, 'danger');
            }
        } catch (error) {
            showAlert('Erro de conexão ao importar CSV', 'danger');
            console.error('Erro:', error);
        }
    };
    reader.readAsText(file);
    
    // Limpar input
    event.target.value = '';
}

async function popularMedicamentosTeste() {
    if (!confirm('Isso irá adicionar medicamentos de teste ao banco. Continuar?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/medicamentos/seed`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showAlert(data.message, 'success');
            carregarMedicamentos();
        } else {
            showAlert('Erro ao popular medicamentos: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao popular medicamentos', 'danger');
        console.error('Erro:', error);
    }
}

// === FUNÇÕES DE RECEITAS ===

async function carregarPacientesSelect() {
    const select = document.getElementById('pacienteReceita');
    select.innerHTML = '<option value="">Selecione um paciente</option>';
    
    pacientes.forEach(paciente => {
        const option = document.createElement('option');
        option.value = paciente.id;
        option.textContent = paciente.nome_completo;
        select.appendChild(option);
    });
}

async function carregarMedicamentosSelect() {
    const select = document.getElementById('medicamentoSelect');
    select.innerHTML = '<option value="">Selecione um medicamento</option>';
    
    medicamentos.forEach(medicamento => {
        const option = document.createElement('option');
        option.value = medicamento.id;
        
        let texto = medicamento.denominacao_generica;
        if (medicamento.concentracao) texto += ` ${medicamento.concentracao}`;
        if (medicamento.apresentacao) texto += ` - ${medicamento.apresentacao}`;
        
        option.textContent = texto;
        select.appendChild(option);
    });
}

function adicionarMedicamento() {
    const medicamentoId = document.getElementById('medicamentoSelect').value;
    const posologia = document.getElementById('posologiaSelect').value;
    const instrucoes = document.getElementById('instrucoesInput').value.trim();
    
    if (!medicamentoId) {
        showAlert('Selecione um medicamento', 'danger');
        return;
    }
    
    const medicamento = medicamentos.find(m => m.id == medicamentoId);
    if (!medicamento) {
        showAlert('Medicamento não encontrado', 'danger');
        return;
    }
    
    // Verificar se já foi adicionado
    if (medicamentosSelecionados.find(m => m.medicamento_id == medicamentoId)) {
        showAlert('Medicamento já foi adicionado', 'danger');
        return;
    }
    
    medicamentosSelecionados.push({
        medicamento_id: medicamentoId,
        medicamento: medicamento,
        posologia: posologia,
        instrucoes: instrucoes
    });
    
    renderizarMedicamentosSelecionados();
    
    // Limpar campos
    document.getElementById('medicamentoSelect').value = '';
    document.getElementById('posologiaSelect').value = '';
    document.getElementById('instrucoesInput').value = '';
}

function renderizarMedicamentosSelecionados() {
    const container = document.getElementById('listaMedicamentosReceita');
    
    if (medicamentosSelecionados.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>Nenhum medicamento adicionado</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = medicamentosSelecionados.map((item, index) => {
        let nome = item.medicamento.denominacao_generica;
        if (item.medicamento.concentracao) nome += ` ${item.medicamento.concentracao}`;
        if (item.medicamento.apresentacao) nome += ` - ${item.medicamento.apresentacao}`;
        
        return `
            <div class="medication-selected">
                <div class="medication-name">${nome}</div>
                <div class="medication-details">
                    ${item.posologia ? `Posologia: ${item.posologia}` : ''}
                    ${item.instrucoes ? ` | Instruções: ${item.instrucoes}` : ''}
                </div>
                <button class="btn btn-danger" onclick="removerMedicamento(${index})" style="margin-top: 10px;">Remover</button>
            </div>
        `;
    }).join('');
}

function removerMedicamento(index) {
    medicamentosSelecionados.splice(index, 1);
    renderizarMedicamentosSelecionados();
}

function limparMedicamentos() {
    medicamentosSelecionados = [];
    renderizarMedicamentosSelecionados();
}

async function gerarReceitaPDF() {
    const pacienteId = document.getElementById('pacienteReceita').value;
    const dataInicial = document.getElementById('dataInicialReceita').value;
    const numReceitas = document.getElementById('numReceitas').value;
    const observacoes = document.getElementById('observacoesReceita').value.trim();
    
    if (!pacienteId) {
        showAlert('Selecione um paciente', 'danger');
        return;
    }
    
    if (!dataInicial) {
        showAlert('Informe a data inicial', 'danger');
        return;
    }
    
    if (medicamentosSelecionados.length === 0) {
        showAlert('Adicione pelo menos um medicamento', 'danger');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/receitas/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                paciente_id: parseInt(pacienteId),
                data_inicial: dataInicial,
                num_receitas: parseInt(numReceitas),
                observacoes: observacoes,
                medicamentos: medicamentosSelecionados.map(item => ({
                    medicamento_id: item.medicamento_id,
                    posologia: item.posologia,
                    instrucoes: item.instrucoes
                }))
            })
        });
        
        if (response.ok) {
            // Baixar o PDF
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `receita_${new Date().getTime()}.pdf`;
            a.click();
            window.URL.revokeObjectURL(url);
            
            showAlert('Receita gerada com sucesso!', 'success');
            
            // Abrir para impressão
            const printWindow = window.open(url);
            printWindow.onload = function() {
                printWindow.print();
            };
            
        } else {
            const data = await response.json();
            showAlert('Erro ao gerar receita: ' + data.error, 'danger');
        }
    } catch (error) {
        showAlert('Erro de conexão ao gerar receita', 'danger');
        console.error('Erro:', error);
    }
}

// === FUNÇÕES DE BACKUP ===

async function atualizarEstatisticas() {
    try {
        const [pacientesResp, medicamentosResp] = await Promise.all([
            fetch(`${API_BASE}/pacientes`),
            fetch(`${API_BASE}/medicamentos`)
        ]);
        
        const pacientesData = await pacientesResp.json();
        const medicamentosData = await medicamentosResp.json();
        
        const estatisticas = document.getElementById('estatisticasGerais');
        estatisticas.innerHTML = `
            <p><strong>Pacientes cadastrados:</strong> ${pacientesData.success ? pacientesData.total : 0}</p>
            <p><strong>Medicamentos cadastrados:</strong> ${medicamentosData.success ? medicamentosData.total : 0}</p>
            <p><strong>Sistema:</strong> ReceitasPerobal v3.0</p>
            <p><strong>Última atualização:</strong> ${new Date().toLocaleString('pt-BR')}</p>
        `;
    } catch (error) {
        document.getElementById('estatisticasGerais').innerHTML = '<p>Erro ao carregar estatísticas</p>';
        console.error('Erro:', error);
    }
}

async function exportarTodosDados() {
    try {
        showAlert('Exportando dados...', 'info');
        
        // Exportar pacientes e medicamentos
        await exportarPacientesCSV();
        await exportarMedicamentosCSV();
        
        showAlert('Todos os dados foram exportados!', 'success');
    } catch (error) {
        showAlert('Erro ao exportar dados', 'danger');
        console.error('Erro:', error);
    }
}

