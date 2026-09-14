// =============================================================================
// ESTADO GLOBAL DO ECOTWIN WEB
// =============================================================================
const state = {
    moradores: 4,
    energia_kwh: 220,
    co2: 0,
    arvores: 0,
    area_plantio: 120,
    mudas_capacidade: 10,
    mudas_absorcao: 150,
    nivel_fazenda: "Oásis Agroecológico (Nível 3)",
    calc_banho: 15,
    calc_carne: 4,
    calc_lixo: 5,
    calc_transp: 20,
    quiz_score: 0,
    vazamentos: []
};

// Navegação de Telas Principais (Welcome -> Quiz Inicial -> Loading -> Dashboard)
function showScreen(id) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(id).classList.add('active');
}

function nextStep(stepNum) {
    document.querySelectorAll('.quiz-step').forEach(s => s.classList.remove('active'));
    document.getElementById('step-' + stepNum).classList.add('active');
    document.getElementById('quiz-progress').style.width = (stepNum * 50) + "%";
}
function prevStep(stepNum) { nextStep(stepNum); }

document.getElementById('inp-energia').addEventListener('input', e => {
    document.getElementById('val-energia').innerText = e.target.value + " kWh";
});

// Finaliza Quiz Inicial e Inicializa Todo o Dashboard
function finalizarQuiz() {
    state.moradores = parseInt(document.getElementById('inp-moradores').value);
    state.energia_kwh = parseInt(document.getElementById('inp-energia').value);
    
    showScreen('screen-loading');
    setTimeout(() => {
        showScreen('screen-dashboard');
        initDashboard();
        gerarQRCode();
    }, 1400);
}

// Navegação das 8 Abas
function openTab(tabId) {
    document.querySelectorAll('.tab-link').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    const targetContent = document.getElementById(tabId);
    if(targetContent) targetContent.classList.add('active');

    const btn = document.querySelector(`.tab-link[onclick*="${tabId}"]`);
    if(btn) btn.classList.add('active');

    if(!document.getElementById('screen-dashboard').classList.contains('active')) {
        showScreen('screen-dashboard');
        initDashboard();
        gerarQRCode();
    }

    if(tabId === 'tab-diag' && chartDonut) chartDonut.update();
    if(tabId === 'tab-diag' && chartBar) chartBar.update();
    if(tabId === 'tab-ia' && chartML) chartML.update();
}

// =============================================================================
// INICIALIZAÇÃO DO DASHBOARD E GRÁFICOS
// =============================================================================
let chartDonut, chartBar, chartML;

function initDashboard() {
    const co2_energia = state.energia_kwh * 0.085 * 12;
    state.co2 = co2_energia + (state.moradores * 160);
    state.arvores = Math.round(state.co2 / 15);
    const meta_red = state.co2 * 0.85;

    // Atualiza Caixas de Métricas da Aba 1
    animateValue('out-co2', 0, Math.round(state.co2), 900);
    animateValue('out-energia-total', 0, state.energia_kwh, 900);
    animateValue('out-arvores', 0, state.arvores, 900);

    // Rank Badge
    const badge = document.getElementById('rank-badge');
    if (state.co2 > 1000) { 
        badge.innerText = "🚨 Alerta Vermelho"; 
        badge.style.backgroundColor = "#EF4444"; 
    } else if (state.co2 > 500) { 
        badge.innerText = "⚖️ Consumidor Mediano"; 
        badge.style.backgroundColor = "#F59E0B"; 
    } else { 
        badge.innerText = "🌟 Herói Verde"; 
        badge.style.backgroundColor = "#10B981"; 
    }

    // Gráficos Chart.js
    Chart.defaults.color = '#E2E8F0';
    
    if(!chartDonut) {
        chartDonut = new Chart(document.getElementById('chart-donut'), {
            type: 'doughnut',
            data: { 
                labels: ["Eletricidade Geral", "Transporte & Rotina", "Resíduos & Gás"], 
                datasets: [{ 
                    data: [co2_energia, state.co2 * 0.35, state.co2 * 0.20], 
                    backgroundColor: ['#10B981', '#3B82F6', '#F59E0B'], 
                    borderWidth: 0 
                }] 
            },
            options: { responsive: true, plugins: { legend: { position: 'bottom' } } }
        });
    } else {
        chartDonut.data.datasets[0].data = [co2_energia, state.co2 * 0.35, state.co2 * 0.20];
        chartDonut.update();
    }

    if(!chartBar) {
        chartBar = new Chart(document.getElementById('chart-bar'), {
            type: 'bar',
            data: { 
                labels: ["Cenário Atual", "Meta (-15%)"], 
                datasets: [{ 
                    label: 'Pegada CO₂e/ano', 
                    data: [state.co2, meta_red], 
                    backgroundColor: ['#EF4444', '#10B981'] 
                }] 
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
    } else {
        chartBar.data.datasets[0].data = [state.co2, meta_red];
        chartBar.update();
    }

    // Tab 3: Inicializa Simulador de Plantio e Fazendinha 3D
    updPlantio();

    // Tab 4: Modelo de IA (Projeção Linear)
    const hist = [
        state.energia_kwh * 0.90, 
        state.energia_kwh * 0.94, 
        state.energia_kwh * 1.04, 
        state.energia_kwh * 0.97, 
        state.energia_kwh * 1.03, 
        state.energia_kwh * 1.00
    ];
    const avg = hist.reduce((a,b)=>a+b)/6;
    if(!chartML) {
        chartML = new Chart(document.getElementById('chart-ml'), {
            type: 'line',
            data: {
                labels: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul (IA)", "Ago (IA)", "Set (IA)"],
                datasets: [
                    { 
                        label: 'Histórico Real', 
                        data: hist.concat([null, null, null]), 
                        borderColor: '#10B981', 
                        backgroundColor: '#10B981', 
                        tension: 0.15 
                    },
                    { 
                        label: 'Projeção Inteligente (IA)', 
                        data: [null, null, null, null, null, state.energia_kwh, avg*1.01, avg*1.02, avg*1.03], 
                        borderColor: '#3B82F6', 
                        backgroundColor: '#3B82F6', 
                        borderDash: [5, 5], 
                        tension: 0.15 
                    }
                ]
            },
            options: { responsive: true }
        });
        document.getElementById('ia-alert').innerHTML = `💡 <strong>Previsão de IA:</strong> A tendência aponta um consumo estabilizado em torno de <strong>${avg.toFixed(0)} kWh/mês</strong>. Mantenha aparelhos desligados em horários de pico.`;
    }

    // Tab 2: Inicializa Calculadora Pessoal
    updCalc();
}

function animateValue(id, start, end, duration) {
    if (start === end) return;
    let range = end - start;
    let current = start;
    let increment = end > start ? 1 : -1;
    let stepTime = Math.abs(Math.floor(duration / range));
    if (stepTime < 10) stepTime = 10;
    const obj = document.getElementById(id);
    let timer = setInterval(function() {
        current += increment * Math.ceil(Math.abs(range) / (duration / stepTime));
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        obj.innerHTML = current.toLocaleString('pt-BR');
    }, stepTime);
}

// =============================================================================
// ABA 2: CALCULADORA DE IMPACTO PESSOAL
// =============================================================================
function updCalc() {
    state.calc_banho = parseInt(document.getElementById('calc-banho').value);
    state.calc_carne = parseInt(document.getElementById('calc-carne').value);
    state.calc_lixo = parseInt(document.getElementById('calc-lixo').value);
    state.calc_transp = parseInt(document.getElementById('calc-transp').value);

    document.getElementById('v-banho').innerText = state.calc_banho;
    document.getElementById('v-carne').innerText = state.calc_carne;
    document.getElementById('v-lixo').innerText = state.calc_lixo;
    document.getElementById('v-transp').innerText = state.calc_transp;

    // Médias Brasileiras
    renderDelta('d-banho', state.calc_banho, 12, 'min');
    renderDelta('d-carne', state.calc_carne, 3, 'dias');
    renderDelta('d-lixo', state.calc_lixo, 4, 'sacos');
    renderDelta('d-transp', state.calc_transp, 15, 'km');
}

function renderDelta(id, val, media, unit) {
    const el = document.getElementById(id);
    const diff = val - media;
    if (diff > 0) {
        el.innerHTML = `<span class="delta-bad">▲ +${diff} ${unit} vs Média BR (${media} ${unit})</span>`;
    } else if (diff < 0) {
        el.innerHTML = `<span class="delta-good">▼ ${diff} ${unit} vs Média BR (${media} ${unit})</span>`;
    } else {
        el.innerHTML = `<span style="color:#94A3B8;">= Exatamente na Média BR</span>`;
    }
}

// =============================================================================
// ABA 3: CARBON TWIN, SIMULADOR DE PLANTIO & FAZENDINHA 3D
// =============================================================================
function updPlantio() {
    const area = parseInt(document.getElementById('inp-area-plantio').value);
    state.area_plantio = area;
    document.getElementById('val-area-plantio').innerText = area + " m²";

    // 1 árvore adulta nativa precisa de ~12m²
    state.mudas_capacidade = Math.floor(area / 12);
    state.mudas_absorcao = state.mudas_capacidade * 15;
    const cobertura = state.co2 > 0 ? Math.min(100, Math.round((state.mudas_absorcao / state.co2) * 100)) : 100;

    document.getElementById('out-mudas-capacidade').innerText = state.mudas_capacidade;
    document.getElementById('out-mudas-absorcao').innerText = state.mudas_absorcao.toLocaleString('pt-BR');
    document.getElementById('out-mudas-cobertura').innerText = cobertura + "%";

    // Evolução Dinâmica da Fazendinha 3D
    const container = document.getElementById('farm-grid-elements');
    const badgeNivel = document.getElementById('farm-badge-nivel');
    container.innerHTML = '';

    let elementos = [];
    if (area >= 1200 || cobertura >= 70) {
        state.nivel_fazenda = "Nível 4: Oásis Regenerativo Sustentável (Ouro)";
        badgeNivel.innerText = state.nivel_fazenda;
        badgeNivel.style.background = "linear-gradient(135deg, #059669 0%, #10B981 100%)";
        elementos = [
            { emoji: "☀️", nome: "Energia Solar", desc: "Painéis Fotovoltaicos" },
            { emoji: "🌳", nome: "Mata Nativa", desc: "Dossel e Sombra" },
            { emoji: "🍎", nome: "Pomar Frutífero", desc: "Alimento Orgânico" },
            { emoji: "🐝", nome: "Apiário de Abelhas", desc: "Polinização Ativa" },
            { emoji: "💧", nome: "Cisterna Pluvial", desc: "Reúso de Chuva" },
            { emoji: "🌽", nome: "Agrofloresta", desc: "Milho & Consórcios" },
            { emoji: "🐑", nome: "Pasto Rotativo", desc: "Zero Carbono" },
            { emoji: "🏡", nome: "Eco-Casa", desc: "Design Bioclimático" }
        ];
    } else if (area >= 600 || cobertura >= 40) {
        state.nivel_fazenda = "Nível 3: Fazenda Agroecológica em Transição (Prata)";
        badgeNivel.innerText = state.nivel_fazenda;
        badgeNivel.style.background = "linear-gradient(135deg, #2563EB 0%, #3B82F6 100%)";
        elementos = [
            { emoji: "🌳", nome: "Árvores Nativas", desc: "Absorção Contínua" },
            { emoji: "🍊", nome: "Citros & Frutas", desc: "Pomar Jovem" },
            { emoji: "🥕", nome: "Horta Familiar", desc: "Cultivo Local" },
            { emoji: "🐔", nome: "Aves Livres", desc: "Manejo Ecológico" },
            { emoji: "💧", nome: "Poço Sustentável", desc: "Água Eficiente" },
            { emoji: "🌾", nome: "Solo Protegido", desc: "Cobertura Verde" }
        ];
    } else if (area >= 180) {
        state.nivel_fazenda = "Nível 2: Sítio em Desenvolvimento Verde (Bronze)";
        badgeNivel.innerText = state.nivel_fazenda;
        badgeNivel.style.background = "linear-gradient(135deg, #D97706 0%, #F59E0B 100%)";
        elementos = [
            { emoji: "🌱", nome: "Mudas em Crescimento", desc: "Início do Plantio" },
            { emoji: "🌾", nome: "Solo em Recuperação", desc: "Adubação Verde" },
            { emoji: "🍎", nome: "Árvores Iniciais", desc: "Raízes Fortes" },
            { emoji: "💧", nome: "Irrigação Gota", desc: "Zero Desperdício" }
        ];
    } else {
        state.nivel_fazenda = "Nível 1: Solo Inicial em Recuperação";
        badgeNivel.innerText = state.nivel_fazenda;
        badgeNivel.style.background = "linear-gradient(135deg, #4B5563 0%, #6B7280 100%)";
        elementos = [
            { emoji: "🌱", nome: "Primeiros Brotos", desc: "Mudas Pioneiras" },
            { emoji: "🌾", nome: "Capim Cobertor", desc: "Proteção contra Erosão" },
            { emoji: "🚜", nome: "Preparo do Solo", desc: "Transição Ecológica" }
        ];
    }

    elementos.forEach((el, idx) => {
        const blk = document.createElement('div');
        blk.className = 'farm-block';
        blk.style.animationDelay = (idx * 60) + 'ms';
        blk.innerHTML = `
            <span class="farm-emoji">${el.emoji}</span>
            <div class="farm-name">${el.nome}</div>
            <div class="farm-desc">${el.desc}</div>
        `;
        container.appendChild(blk);
    });

    // Floresta Visual Geral
    atualizarTwin();
}

function atualizarTwin() {
    const view = document.getElementById('forest-view');
    const ecoVille = document.getElementById('eco-ville-visual');
    if (!view || !ecoVille) return;
    view.innerHTML = '';
    
    if (state.co2 > 1000) {
        ecoVille.classList.add('polluted');
        document.getElementById('eco-status').innerText = `Sua rotina requer ${state.arvores} árvores adultas para limpar seu impacto. 🏭`;
    } else {
        ecoVille.classList.add('clean');
        document.getElementById('eco-status').innerText = `Seu impacto é brando, compensado por ${state.arvores} árvores anuais. 🏞️`;
    }

    const qtde = Math.min(state.arvores, 100);
    for(let i = 0; i < qtde; i++){
        setTimeout(() => {
            const tree = document.createElement('span');
            tree.innerText = state.co2 > 1000 ? "🍂" : "🌳";
            tree.style.animation = "slideIn 0.25s ease-out";
            view.appendChild(tree);
        }, i * 15);
    }
}

// =============================================================================
// ABA 5: CHAT AERO INTERATIVO
// =============================================================================
const chatInput = document.getElementById('chat-input');
if (chatInput) {
    chatInput.addEventListener('keypress', e => { if(e.key === 'Enter') sendChat(); });
}

function sendChat(btnMsg) {
    const text = btnMsg || chatInput.value.trim();
    if(!text) return;
    
    const win = document.getElementById('chat-window');
    win.innerHTML += `<div class="chat-message user">${text}</div>`;
    if (!btnMsg) chatInput.value = '';
    win.scrollTop = win.scrollHeight;

    setTimeout(() => {
        let resp = "";
        const txt = text.toLowerCase();
        if(txt.includes('energia')) {
            resp = `Você consome **${state.energia_kwh} kWh/mês**. Se desligar aparelhos em standby e limitar ar-condicionado, sua meta de 15% economiza cerca de R$ ${(state.energia_kwh * 0.15 * 0.75).toFixed(2)} todo mês!`;
        } else if(txt.includes('fazendinha') || txt.includes('3d') || txt.includes('plantio')) {
            resp = `Sua fazendinha 3D está no **${state.nivel_fazenda}**! Com seus ${state.area_plantio} m² de solo simulado, você abriga ${state.mudas_capacidade} árvores, absorvendo ${state.mudas_absorcao} kg de CO₂/ano.`;
        } else if(txt.includes('banho') || txt.includes('água')) {
            resp = `Seu banho diário informado é de **${state.calc_banho} minutos**. Reduzir 2 minutinhos economiza mais de 540 litros de água tratada por mês por pessoa!`;
        } else {
            resp = "Como copiloto Aero, recomendo testar o Quiz de 10 perguntas e emitir seu laudo PDF oficial para a feira!";
        }
        
        win.innerHTML += `<div class="chat-message assistant"><strong>🤖 Aero:</strong> ${resp}</div>`;
        win.scrollTop = win.scrollHeight;
    }, 500);
}

// =============================================================================
// ABA 6: QUIZ DE 10 PERGUNTAS MITO OU VERDADE COM GAMIFICAÇÃO & BALÕES
// =============================================================================
const gabaritoQuiz = {
    qz1: { correta: "mito", exp: "Mito! Aparelhos em stand-by respondem por até 10% a 12% da conta residencial." },
    qz2: { correta: "verdade", exp: "Verdade! Ruminantes emitem grandes volumes de gás metano (CH₄)." },
    qz3: { correta: "verdade", exp: "Verdade! Um banho de 15 minutos supera facilmente 130 litros de água." },
    qz4: { correta: "mito", exp: "Mito! Sacolas plásticas levam de 100 a 400 anos para se fragmentar." },
    qz5: { correta: "mito", exp: "Mito! Módulos solares continuam gerando eletricidade através de radiação difusa." },
    qz6: { correta: "verdade", exp: "Verdade! Lâmpadas LED convertem luz diretamente, poupando até 80% de energia." },
    qz7: { correta: "verdade", exp: "Verdade! 1 kg de caco de vidro limpo produz exatamente 1 kg de vidro novo para sempre." },
    qz8: { correta: "verdade", exp: "Verdade! O ciclo completo do algodão e do jeans demanda cerca de 10.000 litros de água." },
    qz9: { correta: "mito", exp: "Mito! Carregadores na tomada possuem consumo fantasma por indução contínua." },
    qz10: { correta: "verdade", exp: "Verdade! Mais de 80% dos plásticos nos oceanos chegam trazidos dos continentes." }
};

function verificarQuiz10() {
    let acertos = 0;
    let todasRespondidas = true;

    for (let i = 1; i <= 10; i++) {
        const chave = "qz" + i;
        const marcada = document.querySelector(`input[name="${chave}"]:checked`);
        const fbEl = document.getElementById("fb-" + chave);

        if (!marcada) {
            todasRespondidas = false;
            fbEl.className = "quiz-feedback incorrect";
            fbEl.innerHTML = "⚠️ Por favor, selecione Mito ou Verdade nesta questão.";
            continue;
        }

        const acertou = (marcada.value === gabaritoQuiz[chave].correta);
        if (acertou) {
            acertos++;
            fbEl.className = "quiz-feedback correct";
            fbEl.innerHTML = `✅ <strong>Correto!</strong> ${gabaritoQuiz[chave].exp}`;
        } else {
            fbEl.className = "quiz-feedback incorrect";
            fbEl.innerHTML = `❌ <strong>Incorreto!</strong> ${gabaritoQuiz[chave].exp}`;
        }
    }

    state.quiz_score = acertos;

    // Atualiza Barra de Placar
    document.getElementById('quiz-placar-atual').innerText = `${acertos} / 10 Acertos`;
    document.getElementById('quiz-progresso-txt').innerText = `${acertos * 10}% de Conhecimento Ecológico`;

    // Exibe Caixa de Resultado Final
    const resBox = document.getElementById('quiz-result-box');
    const titEl = document.getElementById('quiz-final-titulo');
    const descEl = document.getElementById('quiz-final-desc');
    resBox.style.display = 'block';

    let rank = "";
    if (acertos === 10) {
        rank = "🏆 Mestre Supremo da Sustentabilidade (Gabaritou!)";
    } else if (acertos >= 8) {
        rank = "🌟 Guardião Ecológico de Elite";
    } else if (acertos >= 5) {
        rank = "🌿 Cidadão Consciente em Ação";
    } else {
        rank = "🌱 Aprendiz do Meio Ambiente";
    }

    titEl.innerText = `Seu Resultado: ${acertos} / 10 Acertos`;
    descEl.innerHTML = `Título Conquistado: <strong>${rank}</strong>.<br>Os detalhes técnicos e gabarito foram atualizados acima e salvos no Laudo PDF!`;

    // Efeito Visual de Comemoração / Balões
    if (acertos >= 5) {
        confetti({
            particleCount: 160,
            spread: 100,
            origin: { y: 0.6 }
        });
    }
}

// =============================================================================
// ABA 7: VAZAMENTOS
// =============================================================================
function registrarVazamento() {
    const local = document.getElementById('vaz-local').value;
    const int = document.getElementById('vaz-int').value;
    const perda = int * 25 * 30; // Litros por mes
    const custo = (perda * 0.018).toFixed(2);

    state.vazamentos.push({
        local: local,
        intensidade: int,
        perda: perda,
        custo: custo
    });

    const lista = document.getElementById('vaz-lista');
    lista.innerHTML += `
        <div class="vaz-item">
            🔴 <strong>${local}</strong> — Intensidade ${int}/10<br>
            Desperdício: <strong>${perda.toLocaleString('pt-BR')} L/mês</strong> (~R$ ${custo}/mês)
        </div>
    `;
}

// =============================================================================
// ABA 8: RELATÓRIO PDF CONSOLIDADO (JSPDF + AUTOTABLE)
// =============================================================================
function gerarQRCode() {
    const box = document.getElementById("qrcode-container");
    if (!box) return;
    box.innerHTML = "";
    new QRCode(box, {
        text: window.location.href,
        width: 120,
        height: 120,
        colorDark : "#000",
        colorLight : "#fff",
        correctLevel : QRCode.CorrectLevel.H
    });
}

function gerarPDFConsolidado() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'pt', 'letter');

    // Cabeçalho Principal
    doc.setFont("helvetica", "bold");
    doc.setTextColor(6, 95, 70); // Verde Escuro
    doc.setFontSize(20);
    doc.text("Laudo Técnico de Inteligência Ambiental - EcoTwin", 40, 45);

    doc.setFont("helvetica", "normal");
    doc.setTextColor(75, 85, 99);
    doc.setFontSize(10);
    doc.text("Documento Técnico Consolidado de Pegada Ecológica, Hábitos, 3D Farm e Auditoria", 40, 62);

    // Linha Divisória
    doc.setDrawColor(5, 150, 105);
    doc.setLineWidth(1.5);
    doc.line(40, 72, 572, 72);

    let startYPos = 90;

    // 1. Tabela: Diagnóstico Geral
    doc.autoTable({
        startY: startYPos,
        margin: { left: 40, right: 40 },
        head: [['1. Diagnóstico Geral da Instalação', 'Valor Registrado']],
        body: [
            ['Ocupantes da Instalação', `${state.moradores} pessoas`],
            ['Consumo Mensal de Energia Elétrica', `${state.energia_kwh} kWh/mês`],
            ['Pegada de Carbono Total Estimada', `${state.co2.toFixed(1)} kg CO2e/ano`],
            ['Meta Voluntária de Redução', '15% de redução programada'],
            ['Árvores Adultas p/ Neutralização Bruta', `${state.arvores} árvores adultas/ano`]
        ],
        headStyles: { fillColor: [5, 150, 105], textColor: 255, fontStyle: 'bold' },
        alternateRowStyles: { fillColor: [240, 253, 244] },
        styles: { fontSize: 8.5, cellPadding: 3.5 }
    });

    startYPos = doc.lastAutoTable.finalY + 12;

    // 2. Tabela: Hábitos Individuais e Comparativo Média BR
    const deltaB = state.calc_banho - 12;
    const deltaT = state.calc_transp - 15;
    const deltaC = state.calc_carne - 3;
    const deltaL = state.calc_lixo - 4;

    doc.autoTable({
        startY: startYPos,
        margin: { left: 40, right: 40 },
        head: [['2. Hábitos e Consumo Individual', 'Parâmetro', 'Comparativo vs Média BR']],
        body: [
            ['Duração Média de Banho', `${state.calc_banho} min/dia`, `${deltaB >= 0 ? '+' : ''}${deltaB} min (Média BR: 12 min)`],
            ['Deslocamento com Veículo Fóssil', `${state.calc_transp} km/dia`, `${deltaT >= 0 ? '+' : ''}${deltaT} km (Média BR: 15 km)`],
            ['Consumo de Carne Vermelha', `${state.calc_carne} dias/semana`, `${deltaC >= 0 ? '+' : ''}${deltaC} dias (Média BR: 3 dias)`],
            ['Descarte de Resíduos Sólidos', `${state.calc_lixo} sacos 50L/sem`, `${deltaL >= 0 ? '+' : ''}${deltaL} sacos (Média BR: 4 sacos)`]
        ],
        headStyles: { fillColor: [16, 185, 129], textColor: 255, fontStyle: 'bold' },
        alternateRowStyles: { fillColor: [240, 253, 244] },
        styles: { fontSize: 8.5, cellPadding: 3.5 }
    });

    startYPos = doc.lastAutoTable.finalY + 12;

    // 3. Tabela: Carbon Twin & Fazendinha 3D
    doc.autoTable({
        startY: startYPos,
        margin: { left: 40, right: 40 },
        head: [['3. Gêmeo Digital & Fazendinha EcoTwin 3D', 'Status / Métricas']],
        body: [
            ['Área de Solo Simulada para Plantio', `${state.area_plantio} m²`],
            ['Capacidade de Árvores Nativas na Área', `${state.mudas_capacidade} mudas viáveis`],
            ['Absorção Anual Estimada do Plantio', `${state.mudas_absorcao.toFixed(1)} kg CO2/ano`],
            ['Nível Alcançado na Fazendinha 3D', `${state.nivel_fazenda}`]
        ],
        headStyles: { fillColor: [4, 120, 87], textColor: 255, fontStyle: 'bold' },
        alternateRowStyles: { fillColor: [240, 253, 244] },
        styles: { fontSize: 8.5, cellPadding: 3.5 }
    });

    startYPos = doc.lastAutoTable.finalY + 12;

    // 4. Tabela: Quiz Gamificado (10 Perguntas)
    doc.autoTable({
        startY: startYPos,
        margin: { left: 40, right: 40 },
        head: [['4. Avaliação Gamificada de Conhecimento Ecológico', 'Pontuação']],
        body: [
            ['Desafio de 10 Perguntas Mito ou Verdade', `${state.quiz_score} acertos de 10 (${state.quiz_score * 10}%)`],
            ['Classificação de Perfil', state.quiz_score === 10 ? 'Mestre Supremo' : (state.quiz_score >= 8 ? 'Guardião de Elite' : (state.quiz_score >= 5 ? 'Cidadão Consciente' : 'Aprendiz Verde'))]
        ],
        headStyles: { fillColor: [6, 95, 70], textColor: 255, fontStyle: 'bold' },
        alternateRowStyles: { fillColor: [240, 253, 244] },
        styles: { fontSize: 8.5, cellPadding: 3.5 }
    });

    startYPos = doc.lastAutoTable.finalY + 12;

    // 5. Tabela: Auditoria de Vazamentos Hídricos
    const bodyVaz = state.vazamentos.length > 0 
        ? state.vazamentos.map(v => [v.local, `Severidade ${v.intensidade}/10`, `${v.perda.toLocaleString('pt-BR')} L/mês`, `~R$ ${v.custo}/mês`])
        : [['Inspeção Geral de Tubulações', 'Normal', '0 L/mês', 'R$ 0,00 (Nenhum vazamento detectado)']];

    doc.autoTable({
        startY: startYPos,
        margin: { left: 40, right: 40 },
        head: [['5. Auditoria de Vazamentos Hídricos', 'Severidade', 'Perda Estimada', 'Custo Estimado']],
        body: bodyVaz,
        headStyles: { fillColor: [31, 41, 55], textColor: 255, fontStyle: 'bold' },
        alternateRowStyles: { fillColor: state.vazamentos.length > 0 ? [254, 242, 242] : [240, 253, 244] },
        styles: { fontSize: 8.5, cellPadding: 3.5 }
    });

    // Rodapé
    doc.setFont("helvetica", "italic");
    doc.setFontSize(8);
    doc.setTextColor(156, 163, 175);
    doc.text("Emitido pelo EcoTwin - Inteligência Artificial & Sustentabilidade Urbana | FECART 2026", 40, doc.lastAutoTable.finalY + 20);

    doc.save("Laudo_Tecnico_Consolidado_EcoTwin.pdf");
}
