document.addEventListener('DOMContentLoaded', function() {
    // Elementos da interface
    const codigoInput = document.getElementById('codigo-cliente');
    const buscarBtn = document.getElementById('buscar-btn');
    const resultadoDiv = document.getElementById('resultado');
    const nomeSpan = document.getElementById('nome-cliente');
    const telefoneSpan = document.getElementById('telefone-atual');
    const novoTelefoneInput = document.getElementById('novo-telefone');
    const atualizarBtn = document.getElementById('atualizar-btn');
    const mensagemDiv = document.getElementById('mensagem');
    
    // Variável para armazenar o código do cliente atual
    let clienteAtualCodigo = '';
    
    // Função para buscar cliente
    buscarBtn.addEventListener('click', function() {
        const codigo = codigoInput.value.trim();
        
        if (!codigo) {
            mostrarMensagem('Por favor, digite o código do cliente.', 'erro');
            return;
        }
        
        // Limpar resultados anteriores
        resultadoDiv.classList.add('hidden');
        mensagemDiv.classList.add('hidden');
        
        // Mostrar indicador de carregamento
        mostrarMensagem('Buscando cliente...', 'info');
        
        // Fazer requisição para a API
        fetch('/api/buscar_cliente', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ codigo: codigo })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.erro || 'Erro ao buscar cliente');
                });
            }
            return response.json();
        })
        .then(data => {
            // Preencher os dados do cliente
            nomeSpan.textContent = data.nome;
            telefoneSpan.textContent = data.telefone || 'Não cadastrado';
            novoTelefoneInput.value = data.telefone || '';
            
            // Armazenar o código do cliente atual
            clienteAtualCodigo = data.codigo;
            
            // Mostrar a seção de resultado
            resultadoDiv.classList.remove('hidden');
            mensagemDiv.classList.add('hidden');
        })
        .catch(error => {
            mostrarMensagem(error.message, 'erro');
        });
    });
    
    // Função para atualizar telefone
    atualizarBtn.addEventListener('click', function() {
        const novoTelefone = novoTelefoneInput.value.trim();
        
        if (!clienteAtualCodigo) {
            mostrarMensagem('Nenhum cliente selecionado.', 'erro');
            return;
        }
        
        // Mostrar indicador de carregamento
        mostrarMensagem('Atualizando telefone...', 'info');
        
        // Fazer requisição para a API
        fetch('/api/atualizar_telefone', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                codigo: clienteAtualCodigo,
                telefone: novoTelefone
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.erro || 'Erro ao atualizar telefone');
                });
            }
            return response.json();
        })
        .then(data => {
            // Atualizar o telefone exibido
            telefoneSpan.textContent = novoTelefone || 'Não cadastrado';
            
            // Mostrar mensagem de sucesso
            mostrarMensagem('Telefone atualizado com sucesso!', 'sucesso');
        })
        .catch(error => {
            mostrarMensagem(error.message, 'erro');
        });
    });
    
    // Função para mostrar mensagens
    function mostrarMensagem(texto, tipo) {
        mensagemDiv.textContent = texto;
        mensagemDiv.className = 'visible';
        
        // Adicionar classe de estilo baseada no tipo
        if (tipo === 'erro') {
            mensagemDiv.classList.add('erro');
        } else if (tipo === 'sucesso') {
            mensagemDiv.classList.add('sucesso');
        } else {
            mensagemDiv.classList.remove('erro', 'sucesso');
        }
    }
    
    // Permitir busca ao pressionar Enter no campo de código
    codigoInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            buscarBtn.click();
        }
    });
    
    // Permitir atualização ao pressionar Enter no campo de novo telefone
    novoTelefoneInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            atualizarBtn.click();
        }
    });
});
