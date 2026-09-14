// Estado global
const state = {
    moradores: 4,
    tempo_banho: 10,
    pcs: 2,
    base_kwh: 180, // consumo médio fixo além de TI
    reducao_banho: false,
    reducao_pcs: false
};

// Listeners dos inputs do Quiz
document.getElementById('inp-banho').addEventListener('input', e => {
    document.getElementById('val-banho').innerText = e.target.value + " min";
    state.tempo_banho = parseInt(e.target.value);
});
document.getElementById('inp-pcs').addEventListener('input', e => {
    document.getElementById('val-pcs').innerText = e.target.value + " aparelhos";
    state.pcs = parseInt(e.target.value);
});
document.getElementById('inp-moradores').addEventListener('input', e => {
    state.moradores = parseInt(e.target.value);
});

// Navegação de Telas
function showScreen(screenId) {
    document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
    document.getElementById(screenId).classList.add('active');
}

// Lógica do Quiz
function nextStep(stepNum) {
    document.querySelectorAll('.quiz-step').forEach(s => s.classList.remove('active'));
    document.getElementById('step-' + stepNum).classList.add('active');
    document.getElementById('quiz-progress').style.width = (stepNum * 33.3) + "%";
}
function prevStep(stepNum) {
    nextStep(stepNum);
}

function finalizarQuiz() {
    showScreen('screen-loading');
    
    // Atualiza estado final
    state.moradores = parseInt(document.getElementById('inp-moradores').value);
    
    setTimeout(() => {
        showScreen('screen-dashboard');
        calcularESimular();
        gerarQRCode();
    }, 2000); // 2s de suspense
}

// Animação de números (Counter)
function animateValue(id, start, end, duration) {
    if (start === end) return;
    let range = end - start;
    let current = start;
    let increment = end > start ? 1 : -1;
    let stepTime = Math.abs(Math.floor(duration / range));
    if(stepTime < 10) stepTime = 10;
    
    const obj = document.getElementById(id);
    let timer = setInterval(function() {
        current += Math.ceil((end-start) * (stepTime/duration));
        
        if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
            current = end;
            clearInterval(timer);
        }
        obj.innerHTML = current.toLocaleString('pt-BR');
    }, stepTime);
}

// Lógica Matemática
function calcularESimular() {
    // 1. Água
    let tempoReal = state.tempo_banho;
    if (state.reducao_banho) tempoReal -= 2; // Menos 2 minutos
    if(tempoReal < 0) tempoReal = 0;
    
    const litros_banho_mes = tempoReal * 9 * state.moradores * 30;
    const consumo_outro_agua = state.moradores * 30 * 40;
    const consumo_agua_total = litros_banho_mes + consumo_outro_agua;

    // 2. Energia
    let horas_pcs = 8;
    if (state.reducao_pcs) horas_pcs = 4; // Desligando fora de uso cai pela metade

    const kwh_ti_mes = state.pcs * 0.150 * horas_pcs * 30;
    const kwh_total_mes = state.base_kwh + kwh_ti_mes;

    // 3. CO2
    const co2_energia_kg = kwh_total_mes * 0.085;
    const co2_agua_kg = consumo_agua_total * 0.0005;
    const co2_total_ano_kg = (co2_energia_kg + co2_agua_kg) * 12;

    const arvores_equivalentes = Math.round(co2_total_ano_kg / 15.0);

    // 4. Lógica de Redução (Simulador Ao vivo)
    // Calcula como seria SEM as reducoes vs COM reducoes para ver o extra
    const base_litros = (state.tempo_banho * 9 * state.moradores * 30) + consumo_outro_agua;
    const base_ti = state.pcs * 0.150 * 8 * 30;
    const base_kwh = state.base_kwh + base_ti;
    const base_co2_ano = ((base_kwh * 0.085) + (base_litros * 0.0005)) * 12;

    const co2_evitado = base_co2_ano - co2_total_ano_kg;
    const arvores_salvas_extras = Math.round(co2_evitado / 15.0);
    const economia_reais = (base_kwh - kwh_total_mes) * 0.75 * 12; // economia anual

    // 5. Atualiza UI com Counter Animation
    const prevCo2 = parseInt(document.getElementById('out-co2').innerText.replace(/\./g,'')) || 0;
    const prevAgua = parseInt(document.getElementById('out-agua').innerText.replace(/\./g,'')) || 0;
    const prevEnergia = parseInt(document.getElementById('out-energia').innerText.replace(/\./g,'')) || 0;
    
    animateValue('out-co2', prevCo2, Math.round(co2_total_ano_kg), 800);
    animateValue('out-agua', prevAgua, Math.round(consumo_agua_total), 800);
    animateValue('out-energia', prevEnergia, Math.round(kwh_total_mes), 800);

    // 6. Impacto Simulator Box
    document.getElementById('out-arvores-salvas').innerText = arvores_salvas_extras;
    document.getElementById('out-economia').innerText = economia_reais.toLocaleString('pt-BR', {minimumFractionDigits: 2});

    // 7. Visual Gêmeo Digital
    atualizarEcoVille(co2_total_ano_kg, arvores_equivalentes);
    
    // Salva global para PDF
    window.ecoData = { 
        co2: co2_total_ano_kg, 
        agua: consumo_agua_total, 
        energia: kwh_total_mes,
        arvores_eq: arvores_equivalentes,
        economia: economia_reais,
        arvores_salvas: arvores_salvas_extras
    };
}

function atualizarEcoVille(co2, arvores) {
    const rankBadge = document.getElementById('rank-badge');
    const ecoVille = document.getElementById('eco-ville-visual');
    const forestView = document.getElementById('forest-view');
    const body = document.body;

    ecoVille.classList.remove('polluted', 'clean');
    body.classList.remove('theme-polluted');

    if (co2 > 1000) {
        rankBadge.innerText = "🚨 Alerta Vermelho";
        rankBadge.style.backgroundColor = "#EF4444";
        ecoVille.classList.add('polluted');
        body.classList.add('theme-polluted');
        document.getElementById('eco-status').innerText = `Seu estilo de vida consome o oxigênio de ${arvores} árvores adultas. 🏭`;
    } else if (co2 > 500) {
        rankBadge.innerText = "⚖️ Consumidor Mediano";
        rankBadge.style.backgroundColor = "#F59E0B";
        document.getElementById('eco-status').innerText = `Você precisa de ${arvores} árvores para empatar. Pode melhorar! 🏙️`;
    } else {
        rankBadge.innerText = "🌟 Herói Verde";
        rankBadge.style.backgroundColor = "#10B981";
        ecoVille.classList.add('clean');
        document.getElementById('eco-status').innerText = `Sensacional! Seu impacto é baixo (${arvores} árvores). A natureza agradece! 🏞️`;
    }

    // Desenhar árvores com delay (Animação visual)
    forestView.innerHTML = '';
    const qtde = Math.min(arvores, 40); // cap para n quebrar tela
    for(let i=0; i<qtde; i++){
        setTimeout(() => {
            const tree = document.createElement('span');
            tree.innerText = co2 > 1000 ? "🍂" : "🌳";
            tree.style.animation = "slideIn 0.3s ease-out";
            forestView.appendChild(tree);
        }, i * 30);
    }
}

// Trigger do Simulator
function recalcularSimulacao() {
    state.reducao_banho = document.getElementById('toggle-banho').checked;
    state.reducao_pcs = document.getElementById('toggle-pcs').checked;
    calcularESimular();
}

// QRCode Generator
function gerarQRCode() {
    document.getElementById("qrcode-container").innerHTML = "";
    // O QRCode direciona para a URL atual (onde estiver hospedado, ex: github.io/Miladys)
    const url = window.location.href;
    new QRCode(document.getElementById("qrcode-container"), {
        text: url,
        width: 100,
        height: 100,
        colorDark : "#000000",
        colorLight : "#ffffff",
        correctLevel : QRCode.CorrectLevel.H
    });
}

// Relatório PDF
function gerarPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    doc.setFont("helvetica", "bold");
    doc.setTextColor(16, 185, 129); // Verde
    doc.setFontSize(22);
    doc.text("Relatório - Feira FECART (EcoTwin)", 20, 20);
    
    doc.setFont("helvetica", "normal");
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(14);
    doc.text("O Gêmeo Digital da sua Sustentabilidade", 20, 30);
    
    doc.autoTable({
        startY: 40,
        head: [['Métrica de Impacto', 'Resultado Pessoal']],
        body: [
            ['Pegada de Carbono', `${window.ecoData.co2.toFixed(1)} kg CO2e/ano`],
            ['Consumo de Água', `${window.ecoData.agua.toFixed(0)} Litros/mês`],
            ['Gasto de Energia', `${window.ecoData.energia.toFixed(0)} kWh/mês`],
            ['Árvores Necessárias p/ Compensar', `${window.ecoData.arvores_eq} árvores adultas`]
        ],
        headStyles: { fillColor: [16, 185, 129], textColor: 255 },
        alternateRowStyles: { fillColor: [241, 245, 249] }
    });
    
    doc.save("Meu_Impacto_EcoTwin.pdf");
}
