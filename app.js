// Elementos do DOM - Inputs
const inpMoradores = document.getElementById('inp-moradores');
const inpBanho = document.getElementById('inp-banho');
const inpEnergia = document.getElementById('inp-energia');
const inpPcs = document.getElementById('inp-pcs');
const inpHoras = document.getElementById('inp-horas');
const inpMeta = document.getElementById('inp-meta');

const valHoras = document.getElementById('val-horas');
const valMeta = document.getElementById('val-meta');

// Charts (Chart.js)
let donutChart, barChart, mlChart, clusterChart;

// Inicialização
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initCharts();
    calcularTudo();

    // Event Listeners nos inputs
    [inpMoradores, inpBanho, inpEnergia, inpPcs, inpHoras, inpMeta].forEach(el => {
        el.addEventListener('input', () => {
            // Atualiza labels visuais dos sliders
            valHoras.innerText = inpHoras.value;
            valMeta.innerText = inpMeta.value;
            calcularTudo();
        });
    });

    // Evento Chat Flutuante
    document.getElementById('btn-aero-float').addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelector('.tab-btn[data-target="tab-chat"]').click();
    });
});

// Lógica de Tabs
function initTabs() {
    const btns = document.querySelectorAll('.tab-btn');
    const contents = document.querySelectorAll('.tab-content');

    btns.forEach(btn => {
        btn.addEventListener('click', () => {
            btns.forEach(b => b.classList.remove('active'));
            contents.forEach(c => c.classList.remove('active'));
            
            btn.classList.add('active');
            document.getElementById(btn.getAttribute('data-target')).classList.add('active');
        });
    });
}

// Inicializa gráficos vazios
function initCharts() {
    // Config global Chart.js
    Chart.defaults.color = '#E2E8F0';
    
    const ctxDonut = document.getElementById('chart-donut').getContext('2d');
    donutChart = new Chart(ctxDonut, {
        type: 'doughnut',
        data: { labels: ["Eletricidade Geral", "Equipamentos TI", "Uso Hídrico"], datasets: [{ data: [0,0,0], backgroundColor: ['#10B981', '#3B82F6', '#06B6D4'], borderWidth: 0 }] },
        options: { responsive: true, plugins: { legend: { position: 'bottom' } }, cutout: '50%' }
    });

    const ctxBar = document.getElementById('chart-bar').getContext('2d');
    barChart = new Chart(ctxBar, {
        type: 'bar',
        data: { labels: ["Cenário Atual", "Com Meta de Redução"], datasets: [{ label: 'Emissão (kg CO₂e/ano)', data: [0,0], backgroundColor: ['#EF4444', '#10B981'] }] },
        options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } }
    });

    const ctxML = document.getElementById('chart-ml').getContext('2d');
    mlChart = new Chart(ctxML, {
        type: 'line',
        data: {
            labels: ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul (IA)", "Ago (IA)", "Set (IA)"],
            datasets: [
                { label: 'Histórico Real', data: [], borderColor: '#10B981', tension: 0.1, fill: false },
                { label: 'Projeção IA', data: [], borderColor: '#3B82F6', borderDash: [5, 5], tension: 0.1, fill: false }
            ]
        },
        options: { responsive: true }
    });

    const ctxCluster = document.getElementById('chart-cluster').getContext('2d');
    clusterChart = new Chart(ctxCluster, {
        type: 'scatter',
        data: { datasets: [] }, // preenchido na lógica
        options: {
            responsive: true,
            scales: { x: { title: { display: true, text: 'Energia (kWh)' } }, y: { title: { display: true, text: 'Água (L)' } } }
        }
    });
}

// Objeto global para armazenar dados para o PDF
window.ecoData = {};

function calcularTudo() {
    const moradores = parseInt(inpMoradores.value);
    const tempo_banho = parseInt(inpBanho.value);
    const energia_kwh = parseFloat(inpEnergia.value);
    const num_pcs = parseInt(inpPcs.value);
    const horas_pcs = parseInt(inpHoras.value);
    const meta_reducao_pct = parseInt(inpMeta.value);

    // Cálculos
    const litros_banho_mes = tempo_banho * 9 * moradores * 30;
    const consumo_outro_agua = moradores * 30 * 40;
    const consumo_agua_total = litros_banho_mes + consumo_outro_agua;

    const kwh_ti_mes = num_pcs * 0.150 * horas_pcs * 30;
    const kwh_total_mes = energia_kwh + kwh_ti_mes;

    const co2_energia_kg = kwh_total_mes * 0.085;
    const co2_agua_kg = consumo_agua_total * 0.0005;
    const co2_total_mes_kg = co2_energia_kg + co2_agua_kg;
    const co2_total_ano_kg = co2_total_mes_kg * 12;

    const co2_evitado_ano_kg = co2_total_ano_kg * (meta_reducao_pct / 100.0);
    
    const arvores_equivalentes = Math.round(co2_total_ano_kg / 15.0);
    const arvores_salvas = Math.round(co2_evitado_ano_kg / 15.0);
    
    const economia_fin_mes = (kwh_total_mes * (meta_reducao_pct / 100.0)) * 0.75;
    const economia_fin_ano = economia_fin_mes * 12;

    // Salvar no global
    window.ecoData = {
        moradores, kwh_total_mes, co2_total_ano_kg, meta_reducao_pct, co2_evitado_ano_kg, arvores_salvas, economia_fin_ano, energia_kwh, kwh_ti_mes, num_pcs
    };

    // Atualizar HTML
    document.getElementById('out-energia-total').innerText = kwh_total_mes.toLocaleString('pt-BR', {maximumFractionDigits: 0});
    document.getElementById('out-pegada').innerText = co2_total_ano_kg.toLocaleString('pt-BR', {maximumFractionDigits: 0});
    document.getElementById('out-arvores').innerText = arvores_salvas;
    document.getElementById('out-economia-fin').innerText = `R$ ${economia_fin_mes.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

    document.getElementById('txt-pegada').innerText = co2_total_ano_kg.toFixed(1);
    document.getElementById('txt-economia-ano').innerText = `R$ ${economia_fin_ano.toLocaleString('pt-BR', {minimumFractionDigits: 2, maximumFractionDigits: 2})}`;

    document.getElementById('txt-emissao-anual').innerText = co2_total_ano_kg.toFixed(0);
    document.getElementById('txt-arvores-eq').innerText = arvores_equivalentes;
    
    // Desenhar grid de árvores (máximo 60)
    const arvores_exibidas = Math.min(arvores_equivalentes, 60);
    document.getElementById('forest-container').innerText = "🌳 ".repeat(arvores_exibidas);

    // Atualizar Gráficos
    donutChart.data.datasets[0].data = [energia_kwh, kwh_ti_mes, (consumo_agua_total * 0.005)];
    donutChart.update();

    barChart.data.datasets[0].data = [co2_total_ano_kg, co2_total_ano_kg - co2_evitado_ano_kg];
    barChart.update();

    simularIA(kwh_total_mes);
}

// Simulação de IA (Regressão, Isolation Forest, KMeans) baseada na lógica original
function simularIA(kwh_total) {
    // 1. Regressão (Tendência)
    const hist = [kwh_total*0.88, kwh_total*0.92, kwh_total*1.04, kwh_total*0.98, kwh_total*1.05, kwh_total];
    const media = hist.reduce((a,b)=>a+b)/hist.length;
    // Previsão simulada suave
    const proj = [kwh_total, media * 1.02, media * 1.03, media * 1.04];
    
    mlChart.data.datasets[0].data = [hist[0], hist[1], hist[2], hist[3], hist[4], hist[5], null, null, null];
    mlChart.data.datasets[1].data = [null, null, null, null, null, proj[0], proj[1], proj[2], proj[3]];
    mlChart.update();

    document.getElementById('alert-ia-previsao').innerHTML = `💡 <strong>Interpretação da IA:</strong> O modelo prevê uma tendência de consumo médio de <strong>${media.toFixed(0)} kWh</strong> para os próximos 3 meses. Mantenha os computadores fora do modo standby para estabilizar a projeção.`;

    // 2. Anomalia
    const alertAnomalia = document.getElementById('alert-anomalia');
    // Simulando que se a meta for muito frouxa ou uso muito alto, dá anomalia
    if (kwh_total > 5000) {
        alertAnomalia.className = 'alert alert-warning';
        alertAnomalia.innerHTML = '⚠️ <strong>Alerta do EcoTwin:</strong> O modelo identificou um pico atípico no consumo projetado em relação à média esperada.';
    } else {
        alertAnomalia.className = 'alert alert-success';
        alertAnomalia.innerHTML = '✅ <strong>Status Normal:</strong> Consumo estabilizado sem picos anômalos detectados.';
    }

    // 3. Cluster KMeans Simulado
    const ptColor = ['#10B981', '#F59E0B', '#EF4444'];
    const datasets = [];
    for(let i=0; i<3; i++) {
        let pts = [];
        for(let j=0; j<10; j++){
            pts.push({x: Math.random()*1500 + 100 + (i*500), y: Math.random()*2000 + 100 + (i*500)});
        }
        datasets.push({
            label: `Perfil ${i+1}`,
            data: pts,
            backgroundColor: ptColor[i]
        });
    }
    clusterChart.data.datasets = datasets;
    clusterChart.update();
}

// CHATBOT AERO
const chatWindow = document.getElementById('chat-window');
const chatInput = document.getElementById('chat-input');

chatInput.addEventListener('keypress', function (e) {
    if (e.key === 'Enter') sendChat();
});

function sendChat(msgText = null) {
    const text = msgText || chatInput.value.trim();
    if (!text) return;
    
    // Appending User Message
    chatWindow.innerHTML += `<div class="chat-message user">${text}</div>`;
    chatInput.value = '';
    chatWindow.scrollTop = chatWindow.scrollHeight;

    // Simulate thinking delay
    setTimeout(() => {
        let resp = "";
        const lowerText = text.toLowerCase();
        
        if (lowerText.includes("gastando") || lowerText.includes("onde")) {
            resp = `📊 <strong>Análise do Aero:</strong> Com base nos seus dados, o gasto principal está na energia predial (<strong>${window.ecoData.energia_kwh} kWh/mês</strong>) e nos computadores de TI (<strong>${window.ecoData.kwh_ti_mes.toFixed(0)} kWh/mês</strong>).`;
        } else if (lowerText.includes("água") || lowerText.includes("banho")) {
            resp = `🚿 <strong>Dica do Aero:</strong> Reduzir 2 minutos no banho das ${window.ecoData.moradores} pessoas poupará cerca de <strong>${window.ecoData.moradores * 2 * 9 * 30} Litros de água por mês</strong>!`;
        } else {
            resp = `🌱 <strong>Dica do Aero:</strong> Para alcançar a meta de ${window.ecoData.meta_reducao_pct}% e economizar R$ ${(window.ecoData.economia_fin_ano / 12).toFixed(2)}/mês, priorize desligar os ${window.ecoData.num_pcs} computadores ao final do expediente.`;
        }

        chatWindow.innerHTML += `<div class="chat-message assistant"><strong>🤖 Aero:</strong> ${resp}</div>`;
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }, 600);
}

// Diagnóstico Inteligente
function calcularDiagnostico() {
    let q1 = parseInt(document.querySelector('input[name="q1"]:checked').value);
    let q2 = parseInt(document.querySelector('input[name="q2"]:checked').value);
    let q3 = parseInt(document.querySelector('input[name="q3"]:checked').value);
    let q4 = parseInt(document.querySelector('input[name="q4"]:checked').value);

    // Considerando "não sei" como 0 na soma
    let pts = (q1<0?0:q1) + (q2<0?0:q2) + (q3<0?0:q3) + (q4<0?0:q4);
    
    const div = document.getElementById('resultado-diagnostico');
    if(pts >= 30) {
        div.innerHTML = `<div class="alert alert-success"><h3>Pontuação: ${pts} / 40</h3>🌟 <strong>Excelente Desempenho Operacional!</strong> Seus hábitos estão altamente alinhados com a eficiência ambiental.</div>`;
    } else {
        div.innerHTML = `<div class="alert alert-warning"><h3>Pontuação: ${pts} / 40</h3>⚠️ <strong>Atenção:</strong> Identificamos margem de otimização no controle dos equipamentos.</div>`;
    }
}

// Vazamentos
document.getElementById('vaz-gotas').addEventListener('input', (e) => {
    const gotas = e.target.value;
    document.getElementById('vaz-gotas-val').innerText = gotas;
    const perda_litros = gotas * 30 * 30;
    document.getElementById('vaz-resultado').innerHTML = `Perda Estimada: <strong>${perda_litros} Litros / mês</strong> (Impacto orçamentário: R$ ${(perda_litros * 0.012).toFixed(2)}/mês)`;
});

function registrarVazamento() {
    const local = document.getElementById('vaz-local').value;
    const gotas = document.getElementById('vaz-gotas').value;
    const perda_litros = gotas * 30 * 30;
    
    document.getElementById('vaz-historico').innerHTML += `<div class="alert alert-warning" style="padding: 10px;">🔴 Registrado: ${local} - Perda: ${perda_litros} L/mês</div>`;
}

// Relatório PDF
function gerarPDF() {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    
    doc.setFont("helvetica", "bold");
    doc.setTextColor(6, 95, 70); // Verde escuro
    doc.setFontSize(18);
    doc.text("Relatório de Impacto Ambiental - EcoTwin", 20, 20);
    
    doc.setFont("helvetica", "normal");
    doc.setTextColor(0, 0, 0);
    doc.setFontSize(12);
    doc.text("Plataforma de Monitoramento & Inteligência Ambiental", 20, 30);
    
    doc.autoTable({
        startY: 40,
        head: [['Indicador Ambiental', 'Valor Medido / Estimado']],
        body: [
            ['Ocupantes da Instalação', String(window.ecoData.moradores)],
            ['Consumo Total de Energia', `${window.ecoData.kwh_total_mes.toFixed(0)} kWh/mês`],
            ['Pegada de Carbono Anual', `${window.ecoData.co2_total_ano_kg.toFixed(1)} kg CO2e/ano`],
            ['Meta de Redução Definida', `${window.ecoData.meta_reducao_pct}%`],
            ['Emissões Evitadas (Meta)', `${window.ecoData.co2_evitado_ano_kg.toFixed(1)} kg CO2e/ano`],
            ['Equivalência em Árvores Preservadas', `${window.ecoData.arvores_salvas} Árvores/ano`],
            ['Economia Financeira Estimada', `R$ ${window.ecoData.economia_fin_ano.toFixed(2)}/ano`]
        ],
        headStyles: { fillColor: [5, 150, 105], textColor: 255 },
        alternateRowStyles: { fillColor: [240, 253, 244] }
    });
    
    doc.save("Relatorio_Tecnico_EcoTwin.pdf");
}
