// Estado Global
const state = {
    moradores: 4,
    energia_kwh: 220,
    co2: 0,
    arvores: 0
};

// Navegação de Telas Principais
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

// Finaliza Quiz -> Carrega Dashboard
function finalizarQuiz() {
    state.moradores = parseInt(document.getElementById('inp-moradores').value);
    state.energia_kwh = parseInt(document.getElementById('inp-energia').value);
    
    showScreen('screen-loading');
    setTimeout(() => {
        showScreen('screen-dashboard');
        initDashboard();
        gerarQRCode();
    }, 1500);
}

// Navegação das 8 Abas
function openTab(tabId) {
    document.querySelectorAll('.tab-link').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
    
    event.currentTarget.classList.add('active');
    document.getElementById(tabId).classList.add('active');

    // Força re-render dos graficos pra nao bugar tamanho
    if(tabId === 'tab-diag' && chartDonut) chartDonut.update();
    if(tabId === 'tab-diag' && chartBar) chartBar.update();
    if(tabId === 'tab-ia' && chartML) chartML.update();
}

// ==========================================
// INICIALIZAÇÃO DO DASHBOARD
// ==========================================
let chartDonut, chartBar, chartML;

function initDashboard() {
    // 1. Diagnóstico Básico
    const co2_energia = state.energia_kwh * 0.085 * 12;
    state.co2 = co2_energia + (state.moradores * 150); // Estimativa rapida baseada em hab
    state.arvores = Math.round(state.co2 / 15);
    const meta_red = state.co2 * 0.9;

    // Atualiza Caixas
    animateValue('out-co2', 0, Math.round(state.co2), 1000);
    animateValue('out-energia-total', 0, state.energia_kwh, 1000);
    animateValue('out-arvores', 0, state.arvores, 1000);

    // Rank Badge
    const badge = document.getElementById('rank-badge');
    if (state.co2 > 1000) { badge.innerText = "🚨 Alerta Vermelho"; badge.style.backgroundColor = "#EF4444"; }
    else if (state.co2 > 500) { badge.innerText = "⚖️ Consumidor Mediano"; badge.style.backgroundColor = "#F59E0B"; }
    else { badge.innerText = "🌟 Herói Verde"; badge.style.backgroundColor = "#10B981"; }

    // Gráficos Chart.js
    Chart.defaults.color = '#E2E8F0';
    
    if(!chartDonut) {
        chartDonut = new Chart(document.getElementById('chart-donut'), {
            type: 'doughnut',
            data: { labels: ["Energia", "Transporte (Est.)", "Lixo/Água"], datasets: [{ data: [co2_energia, state.co2*0.3, state.co2*0.2], backgroundColor: ['#10B981', '#3B82F6', '#F59E0B'], borderWidth: 0 }] },
            options: { responsive: true }
        });
    }

    if(!chartBar) {
        chartBar = new Chart(document.getElementById('chart-bar'), {
            type: 'bar',
            data: { labels: ["Atual", "Meta (-10%)"], datasets: [{ label: 'Pegada CO2', data: [state.co2, meta_red], backgroundColor: ['#EF4444', '#10B981'] }] },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });
    }

    // Tab Carbon Twin
    atualizarTwin();

    // Tab IA (Projeção Linear Simples)
    const hist = [state.energia_kwh*0.9, state.energia_kwh*0.95, state.energia_kwh*1.05, state.energia_kwh*0.98, state.energia_kwh*1.02, state.energia_kwh];
    const avg = hist.reduce((a,b)=>a+b)/6;
    if(!chartML) {
        chartML = new Chart(document.getElementById('chart-ml'), {
            type: 'line',
            data: {
                labels: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul (IA)", "Ago (IA)"],
                datasets: [
                    { label: 'Histórico', data: hist.concat([null, null]), borderColor: '#10B981', tension: 0.1 },
                    { label: 'Projeção', data: [null, null, null, null, null, state.energia_kwh, avg*1.01, avg*1.02], borderColor: '#3B82F6', borderDash: [5, 5], tension: 0.1 }
                ]
            }
        });
        document.getElementById('ia-alert').innerHTML = `💡 A tendência aponta que seu consumo médio se estabilizará perto de <strong>${avg.toFixed(0)} kWh</strong>.`;
    }

    // Inicializa Calculadora Pessoal
    updCalc();
}

// Função para animação de numeros
function animateValue(id, start, end, duration) {
    if (start === end) return;
    let range = end - start;
    let current = start;
    let increment = end > start ? 1 : -1;
    let stepTime = Math.abs(Math.floor(duration / range));
    const obj = document.getElementById(id);
    let timer = setInterval(function() {
        current += increment;
        if (current == end) { clearInterval(timer); }
        obj.innerHTML = current.toLocaleString('pt-BR');
    }, stepTime);
}

// ==========================================
// ABA 2: CALCULADORA PESSOAL
// ==========================================
function updCalc() {
    const banho = parseInt(document.getElementById('calc-banho').value);
    const carne = parseInt(document.getElementById('calc-carne').value);
    const lixo = parseInt(document.getElementById('calc-lixo').value);
    const transp = parseInt(document.getElementById('calc-transp').value);

    document.getElementById('v-banho').innerText = banho;
    document.getElementById('v-carne').innerText = carne;
    document.getElementById('v-lixo').innerText = lixo;
    document.getElementById('v-transp').innerText = transp;

    // Médias Brasileiras
    const mBanho = 12, mCarne = 3, mLixo = 4, mTransp = 15;

    renderDelta('d-banho', banho, mBanho, 'min');
    renderDelta('d-carne', carne, mCarne, 'dias');
    renderDelta('d-lixo', lixo, mLixo, 'sacos');
    renderDelta('d-transp', transp, mTransp, 'km');
}

function renderDelta(id, val, media, unit) {
    const el = document.getElementById(id);
    const diff = val - media;
    if (diff > 0) {
        el.innerHTML = `<span class="delta-bad">▲ +${diff} ${unit} vs Média BR</span>`;
    } else if (diff < 0) {
        el.innerHTML = `<span class="delta-good">▼ ${diff} ${unit} vs Média BR</span>`;
    } else {
        el.innerHTML = `<span style="color:#94A3B8;">= Na Média BR</span>`;
    }
}

// ==========================================
// ABA 3: CARBON TWIN
// ==========================================
function atualizarTwin() {
    const view = document.getElementById('forest-view');
    const ecoVille = document.getElementById('eco-ville-visual');
    view.innerHTML = '';
    
    if (state.co2 > 1000) {
        ecoVille.classList.add('polluted');
        document.getElementById('eco-status').innerText = `Seu estilo de vida exige o oxigênio de ${state.arvores} árvores adultas. 🏭`;
    } else {
        ecoVille.classList.add('clean');
        document.getElementById('eco-status').innerText = `Seu impacto exige ${state.arvores} árvores anuais. 🏞️`;
    }

    const qtde = Math.min(state.arvores, 100);
    for(let i=0; i<qtde; i++){
        setTimeout(() => {
            const tree = document.createElement('span');
            tree.innerText = state.co2 > 1000 ? "🍂" : "🌳";
            tree.style.animation = "slideIn 0.3s ease-out";
            view.appendChild(tree);
        }, i * 20);
    }
}

// ==========================================
// ABA 5: CHAT AERO
// ==========================================
const chatInput = document.getElementById('chat-input');
chatInput.addEventListener('keypress', e => { if(e.key === 'Enter') sendChat(); });

function sendChat(btnMsg) {
    const text = btnMsg || chatInput.value.trim();
    if(!text) return;
    
    const win = document.getElementById('chat-window');
    win.innerHTML += `<div class="chat-message user">${text}</div>`;
    chatInput.value = '';
    win.scrollTop = win.scrollHeight;

    setTimeout(() => {
        let resp = "";
        const txt = text.toLowerCase();
        if(txt.includes('energia')) resp = `Você informou gastar ${state.energia_kwh} kWh/mês. Apague luzes ociosas e desative aparelhos em standby para reduzir esse valor!`;
        else if(txt.includes('twin')) resp = `O Carbon Twin calcula que suas atividades requerem ${state.arvores} árvores/ano só para filtrar o seu ar.`;
        else if(txt.includes('banho') || txt.includes('água')) resp = `Reduzir 2 minutinhos do seu banho poupa centenas de litros e corta sua conta!`;
        else resp = "Como copiloto Aero, minha dica é que pequenas mudanças de hábito já criam grande impacto no Gêmeo Digital.";
        
        win.innerHTML += `<div class="chat-message assistant"><strong>🤖 Aero:</strong> ${resp}</div>`;
        win.scrollTop = win.scrollHeight;
    }, 600);
}

// ==========================================
// ABA 6: QUIZ E GAMIFICAÇÃO
// ==========================================
function verificarQuiz() {
    const q1 = document.querySelector('input[name="qz1"]:checked');
    const q2 = document.querySelector('input[name="qz2"]:checked');
    const resDiv = document.getElementById('quiz-result');

    if(!q1 || !q2) {
        resDiv.innerHTML = '<span class="delta-bad">Responda as duas perguntas primeiro!</span>';
        return;
    }

    if(q1.value === 'mito' && q2.value === 'verdade') {
        resDiv.innerHTML = '<span class="delta-good">🎉 Parabéns! Você acertou tudo! (Standby consome muita energia sim, e vacas emitem metano).</span>';
        // Efeito Balões / Confete
        confetti({ particleCount: 150, spread: 80, origin: { y: 0.6 } });
    } else {
        resDiv.innerHTML = '<span class="delta-bad">❌ Ops! Alguma resposta está errada. (Dica: Standby consome energia). Tente novamente!</span>';
    }
}

// ==========================================
// ABA 7: VAZAMENTOS
// ==========================================
function registrarVazamento() {
    const local = document.getElementById('vaz-local').value;
    const int = document.getElementById('vaz-int').value;
    const perda = int * 15 * 30; // ex ficticio L/mes

    const lista = document.getElementById('vaz-lista');
    lista.innerHTML += `<div class="vaz-item">🔴 ${local} - Nível ${int} (Perda: <strong>${perda} Litros/mês</strong>)</div>`;
}

// ==========================================
// ABA 8: RELATÓRIO PDF & QR CODE
// ==========================================
function gerarQRCode() {
    const box = document.getElementById("qrcode-container");
    box.innerHTML = "";
    new QRCode(box, {
        text: window.location.href, width: 120, height: 120,
        colorDark : "#000", colorLight : "#fff", correctLevel : QRCode.CorrectLevel.H
    });
}

function gerarPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    doc.setFont("helvetica", "bold");
    doc.setTextColor(16, 185, 129);
    doc.setFontSize(22);
    doc.text("Relatório Ambiental - EcoTwin", 20, 20);
    
    doc.setFont("helvetica", "normal");
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(14);
    doc.text("Consolidado dos 8 Módulos de Sustentabilidade", 20, 30);
    
    doc.autoTable({
        startY: 40,
        head: [['Métrica', 'Seu Resultado']],
        body: [
            ['Moradores Informados', `${state.moradores} Pessoas`],
            ['Energia Declarada', `${state.energia_kwh} kWh/mês`],
            ['Pegada de Carbono (Est.)', `${state.co2.toFixed(1)} kg CO2e/ano`],
            ['Gêmeo Digital (Carbon Twin)', `${state.arvores} Árvores necessárias`]
        ],
        headStyles: { fillColor: [16, 185, 129] }
    });
    
    doc.save("Laudo_EcoTwin_Feira.pdf");
}
