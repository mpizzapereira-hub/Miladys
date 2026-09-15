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
    calc_ar: 3,
    calc_delivery: 3,
    calc_voo: 1,
    calc_lavar: 4,
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

const inpEnergiaEl = document.getElementById('inp-energia');
if (inpEnergiaEl) {
    inpEnergiaEl.addEventListener('input', e => {
        document.getElementById('val-energia').innerText = e.target.value + " kWh";
    });
}

// Finaliza Quiz Inicial e Inicializa Todo o Dashboard
function finalizarQuiz() {
    state.moradores = parseInt(document.getElementById('inp-moradores').value) || 4;
    state.energia_kwh = parseInt(document.getElementById('inp-energia').value) || 220;
    
    showScreen('screen-loading');
    setTimeout(() => {
        showScreen('screen-dashboard');
        initDashboard();
        gerarQRCode();
    }, 1200);
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

    // Se abrir a aba do Carbon Twin, inicializa/redimensiona o Three.js
    if (tabId === 'tab-twin') {
        setTimeout(() => {
            initThreeFarm();
            onWindowResize();
        }, 100);
    }
}

// =============================================================================
// INICIALIZAÇÃO DO DASHBOARD E GRÁFICOS (CHART.JS)
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
    if (badge) {
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
    }

    // Gráficos Chart.js
    if (typeof Chart !== 'undefined') {
        Chart.defaults.color = '#E2E8F0';
        
        const donutCtx = document.getElementById('chart-donut');
        if (donutCtx && !chartDonut) {
            chartDonut = new Chart(donutCtx, {
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
        } else if (chartDonut) {
            chartDonut.data.datasets[0].data = [co2_energia, state.co2 * 0.35, state.co2 * 0.20];
            chartDonut.update();
        }

        const barCtx = document.getElementById('chart-bar');
        if (barCtx && !chartBar) {
            chartBar = new Chart(barCtx, {
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
        } else if (chartBar) {
            chartBar.data.datasets[0].data = [state.co2, meta_red];
            chartBar.update();
        }

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
        const mlCtx = document.getElementById('chart-ml');
        if (mlCtx && !chartML) {
            chartML = new Chart(mlCtx, {
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
                options: { responsive: true, maintainAspectRatio: false }
            });
            const iaAlert = document.getElementById('ia-alert');
            if (iaAlert) {
                iaAlert.innerHTML = `💡 <strong>Previsão de IA:</strong> A tendência aponta um consumo estabilizado em torno de <strong>${avg.toFixed(0)} kWh/mês</strong>. Mantenha aparelhos desligados fora do expediente.`;
            }
        }
    }

    // Inicializa Simulador de Plantio e Fazendinha 3D
    updPlantio();

    // Inicializa Calculadora Pessoal
    updCalc();

    // Inicializa Calculadora de Vazamentos
    const vazSlider = document.getElementById('vaz-int');
    if (vazSlider) updVazCalc(vazSlider.value);

    // Inicializa Three.js se o container estiver pronto
    setTimeout(initThreeFarm, 150);
}

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    if (!obj) return;
    if (start === end) {
        obj.innerHTML = end.toLocaleString('pt-BR');
        return;
    }
    let range = end - start;
    let current = start;
    let increment = end > start ? 1 : -1;
    let stepTime = Math.abs(Math.floor(duration / range));
    if (stepTime < 10) stepTime = 10;
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
    const bEl = document.getElementById('calc-banho');
    const cEl = document.getElementById('calc-carne');
    const lEl = document.getElementById('calc-lixo');
    const tEl = document.getElementById('calc-transp');
    const arEl = document.getElementById('calc-ar');
    const delEl = document.getElementById('calc-delivery');
    const vooEl = document.getElementById('calc-voo');
    const lavEl = document.getElementById('calc-lavar');

    if (bEl) state.calc_banho = parseInt(bEl.value);
    if (cEl) state.calc_carne = parseInt(cEl.value);
    if (lEl) state.calc_lixo = parseInt(lEl.value);
    if (tEl) state.calc_transp = parseInt(tEl.value);
    if (arEl) state.calc_ar = parseInt(arEl.value);
    if (delEl) state.calc_delivery = parseInt(delEl.value);
    if (vooEl) state.calc_voo = parseInt(vooEl.value);
    if (lavEl) state.calc_lavar = parseInt(lavEl.value);

    if (document.getElementById('v-banho')) document.getElementById('v-banho').innerText = state.calc_banho;
    if (document.getElementById('v-carne')) document.getElementById('v-carne').innerText = state.calc_carne;
    if (document.getElementById('v-lixo')) document.getElementById('v-lixo').innerText = state.calc_lixo;
    if (document.getElementById('v-transp')) document.getElementById('v-transp').innerText = state.calc_transp;
    if (document.getElementById('v-ar')) document.getElementById('v-ar').innerText = state.calc_ar;
    if (document.getElementById('v-delivery')) document.getElementById('v-delivery').innerText = state.calc_delivery;
    if (document.getElementById('v-voo')) document.getElementById('v-voo').innerText = state.calc_voo;
    if (document.getElementById('v-lavar')) document.getElementById('v-lavar').innerText = state.calc_lavar;

    // Médias Brasileiras
    renderDelta('d-banho', state.calc_banho, 12, 'min');
    renderDelta('d-carne', state.calc_carne, 3, 'dias');
    renderDelta('d-lixo', state.calc_lixo, 4, 'sacos');
    renderDelta('d-transp', state.calc_transp, 15, 'km');
    renderDelta('d-ar', state.calc_ar, 2, 'h');
    renderDelta('d-delivery', state.calc_delivery, 2, 'entregas');
    renderDelta('d-voo', state.calc_voo, 1, 'voos');
    renderDelta('d-lavar', state.calc_lavar, 3, 'ciclos');

    // --- Cálculo Dinâmico de Impacto Global ---
    // Valores base do quiz inicial
    const co2_energia = state.energia_kwh * 0.085 * 12;
    const co2_base_moradores = state.moradores * 160;

    // Modificadores de Hábitos (em kg CO2/ano) comparado à média
    const mod_banho = (state.calc_banho - 12) * 5;
    const mod_carne = (state.calc_carne - 3) * 45;
    const mod_lixo = (state.calc_lixo - 4) * 20;
    const mod_transp = (state.calc_transp - 15) * 12;
    const mod_ar = (state.calc_ar - 2) * 15;
    const mod_delivery = (state.calc_delivery - 2) * 15;
    const mod_voo = (state.calc_voo - 1) * 150;
    const mod_lavar = (state.calc_lavar - 3) * 5;

    state.co2 = co2_energia + co2_base_moradores + mod_banho + mod_carne + mod_lixo + mod_transp + mod_ar + mod_delivery + mod_voo + mod_lavar;
    if (state.co2 < 0) state.co2 = 0; // Prevenir negativo
    
    state.arvores = Math.round(state.co2 / 15);

    // Atualiza elementos globais e gráficos se já estiverem inicializados
    const outCo2 = document.getElementById('out-co2');
    if (outCo2 && outCo2.innerText !== "0") {
        outCo2.innerHTML = Math.round(state.co2).toLocaleString('pt-BR');
    }
    const outArvores = document.getElementById('out-arvores');
    if (outArvores && outArvores.innerText !== "0") {
        outArvores.innerHTML = state.arvores.toLocaleString('pt-BR');
    }

    const badge = document.getElementById('rank-badge');
    if (badge) {
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
    }

    if (typeof chartDonut !== 'undefined' && chartDonut) {
        chartDonut.data.datasets[0].data = [co2_energia, state.co2 * 0.35, state.co2 * 0.20];
        chartDonut.update();
    }
    if (typeof chartBar !== 'undefined' && chartBar) {
        const meta_red = state.co2 * 0.85;
        chartBar.data.datasets[0].data = [state.co2, meta_red];
        chartBar.update();
    }
    
    atualizarTwin();
    updPlantio(); // Refresh farm percentage as well
}

function renderDelta(id, val, media, unit) {
    const el = document.getElementById(id);
    if (!el) return;
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
// ABA 3: CARBON TWIN — SIMULADOR DE PLANTIO, 3D WEBGL & BIOMA FLORESTAL
// =============================================================================
function updPlantio() {
    const inpArea = document.getElementById('inp-area-plantio');
    if (inpArea) {
        state.area_plantio = parseInt(inpArea.value);
    }
    const valArea = document.getElementById('val-area-plantio');
    if (valArea) {
        valArea.innerText = state.area_plantio + " m²";
    }

    // 1 árvore adulta nativa requer cerca de 12 m²
    state.mudas_capacidade = Math.floor(state.area_plantio / 12);
    state.mudas_absorcao = state.mudas_capacidade * 15;
    const cobertura = state.co2 > 0 ? Math.min(100, Math.round((state.mudas_absorcao / state.co2) * 100)) : 100;

    if (document.getElementById('out-mudas-capacidade')) document.getElementById('out-mudas-capacidade').innerText = state.mudas_capacidade;
    if (document.getElementById('out-mudas-absorcao')) document.getElementById('out-mudas-absorcao').innerText = state.mudas_absorcao.toLocaleString('pt-BR');
    if (document.getElementById('out-mudas-cobertura')) document.getElementById('out-mudas-cobertura').innerText = cobertura + "%";

    // Evolução Dinâmica dos Módulos da Fazendinha
    const container = document.getElementById('farm-grid-elements');
    const badgeNivel = document.getElementById('farm-badge-nivel');
    if (container && badgeNivel) {
        container.innerHTML = '';

        let elementos = [];
        if (state.area_plantio >= 1200 || cobertura >= 70) {
            state.nivel_fazenda = "Nível 4: Oásis Regenerativo Sustentável (Ouro)";
            badgeNivel.innerText = state.nivel_fazenda;
            badgeNivel.style.background = "linear-gradient(135deg, #059669 0%, #10B981 100%)";
            elementos = [
                { emoji: "☀️", nome: "Energia Solar", desc: "Painéis Fotovoltaicos" },
                { emoji: "🌳", nome: "Mata Nativa", desc: "Dossel & Sombreamento" },
                { emoji: "🍎", nome: "Pomar Frutífero", desc: "Alimento Orgânico" },
                { emoji: "🐝", nome: "Apiário Ecológico", desc: "Polinização Ativa" },
                { emoji: "💧", nome: "Cisterna Pluvial", desc: "Reúso de Chuva" },
                { emoji: "🌽", nome: "Agrofloresta", desc: "Milho & Consórcios" },
                { emoji: "🐑", nome: "Pasto Rotativo", desc: "Zero Emissão" },
                { emoji: "🏡", nome: "Eco-Casa", desc: "Design Bioclimático" }
            ];
        } else if (state.area_plantio >= 600 || cobertura >= 40) {
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
        } else if (state.area_plantio >= 180) {
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
                { emoji: "🌾", nome: "Capim Cobertor", desc: "Proteção de Solo" },
                { emoji: "🚜", nome: "Preparo do Solo", desc: "Transição Verde" }
            ];
        }

        elementos.forEach((el, idx) => {
            const blk = document.createElement('div');
            blk.className = 'farm-block';
            blk.style.animationDelay = (idx * 50) + 'ms';
            blk.innerHTML = `
                <span class="farm-emoji">${el.emoji}</span>
                <div class="farm-name">${el.nome}</div>
                <div class="farm-desc">${el.desc}</div>
            `;
            container.appendChild(blk);
        });
    }

    // Atualiza árvores 3D no Three.js
    if (typeof render3DTrees === 'function') {
        render3DTrees();
    }
}

function atualizarTwin() {
    const view = document.getElementById('forest-view');
    const ecoVille = document.getElementById('eco-ville-visual');
    if (!view || !ecoVille) return;
    view.innerHTML = '';
    
    if (state.co2 > 1000) {
        ecoVille.classList.add('polluted');
        document.getElementById('eco-status').innerText = `Sua rotina requer ${state.arvores} árvores adultas para limpar seu impacto anual. 🏭`;
    } else {
        ecoVille.classList.add('clean');
        document.getElementById('eco-status').innerText = `Seu impacto é brando, compensado por ${state.arvores} árvores anuais. 🏞️`;
    }

    const qtde = state.arvores; // Usando a quantidade exata
    const tipos = [
        { icon: "🌲", nome: "Pinheiro" },
        { icon: "🌳", nome: "Ipê Amarelo" },
        { icon: "🌴", nome: "Palmeira" },
        { icon: "🌳", nome: "Jacarandá" }
    ];

    for(let i = 0; i < qtde; i++) {
        const item = tipos[i % tipos.length];
        const tile = document.createElement('div');
        tile.className = 'tree-3d-tile';
        tile.style.animationDelay = ((i % 50) * 15) + 'ms';
        tile.innerHTML = `
            <span class="tree-3d-icon">${state.co2 > 1000 ? "🍂" : item.icon}</span>
            <div class="tree-3d-tag">#${i + 1} - ${item.nome}</div>
            <div style="font-size:0.6rem; color:#A7F3D0; font-weight:700;">15kg/ano</div>
        `;
        view.appendChild(tile);
    }
}

// =============================================================================
// ENGINE THREE.JS: FAZENDINHA VIRTUAL 3D INTERATIVA (WEBGL)
// =============================================================================
let scene3D, camera3D, renderer3D, controls3D;
let islandGroup, treesGroup, windmillMesh, bladesMesh, solarMesh, cloudsGroup;
let isAutoRotating = true;
let threeInitialized = false;

function initThreeFarm() {
    const container = document.getElementById('farm-3d-canvas-container');
    if (!container || threeInitialized || typeof THREE === 'undefined') return;

    const width = container.clientWidth || 800;
    const height = container.clientHeight || 480;

    // Cena
    scene3D = new THREE.Scene();
    scene3D.fog = new THREE.FogExp2(0x06150f, 0.015);

    // Câmera Isométrica/Perspectiva
    camera3D = new THREE.PerspectiveCamera(38, width / height, 0.1, 1000);
    camera3D.position.set(26, 22, 26);

    // Renderer WebGL com Suporte a Sombras
    renderer3D = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer3D.setSize(width, height);
    renderer3D.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer3D.shadowMap.enabled = true;
    renderer3D.shadowMap.type = THREE.PCFSoftShadowMap;
    container.innerHTML = '';
    container.appendChild(renderer3D.domElement);

    // Controles Orbitais (Arrastar para girar em 360°)
    if (typeof THREE.OrbitControls !== 'undefined') {
        controls3D = new THREE.OrbitControls(camera3D, renderer3D.domElement);
        controls3D.enableDamping = true;
        controls3D.dampingFactor = 0.05;
        controls3D.maxPolarAngle = Math.PI / 2.15;
        controls3D.minDistance = 14;
        controls3D.maxDistance = 55;
        controls3D.autoRotate = isAutoRotating;
        controls3D.autoRotateSpeed = 1.0;
    }

    // Iluminação Realista (Luz Solar Direcional + Luz Ambiente Natural)
    const ambientLight = new THREE.AmbientLight(0xdcfce7, 0.85);
    scene3D.add(ambientLight);

    const hemiLight = new THREE.HemisphereLight(0xecfdf5, 0x14532d, 0.5);
    scene3D.add(hemiLight);

    const sunLight = new THREE.DirectionalLight(0xfffae0, 1.4);
    sunLight.position.set(22, 35, 18);
    sunLight.castShadow = true;
    sunLight.shadow.mapSize.width = 1024;
    sunLight.shadow.mapSize.height = 1024;
    sunLight.shadow.camera.near = 10;
    sunLight.shadow.camera.far = 80;
    sunLight.shadow.camera.left = -16;
    sunLight.shadow.camera.right = 16;
    sunLight.shadow.camera.top = 16;
    sunLight.shadow.camera.bottom = -16;
    sunLight.shadow.bias = -0.0005;
    scene3D.add(sunLight);

    // Grupo da Ilha Flutuante
    islandGroup = new THREE.Group();
    scene3D.add(islandGroup);

    // Plataforma Superior (Grama Verde Vibrante e Orgânica)
    const grassGeo = new THREE.BoxGeometry(17, 1.3, 17, 12, 1, 12);
    const posG = grassGeo.attributes.position;
    for (let i = 0; i < posG.count; i++) {
        if (posG.getY(i) > 0) {
            const px = posG.getX(i);
            const pz = posG.getZ(i);
            const distCenter = Math.hypot(px, pz);
            if (distCenter > 5) {
                posG.setY(i, posG.getY(i) + (Math.random() * 0.4));
            }
        }
    }
    grassGeo.computeVertexNormals();
    const grassMat = new THREE.MeshStandardMaterial({
        color: 0x16a34a,
        roughness: 0.85,
        metalness: 0.05,
        flatShading: true
    });
    const grassMesh = new THREE.Mesh(grassGeo, grassMat);
    grassMesh.position.y = 0;
    grassMesh.receiveShadow = true;
    grassMesh.castShadow = true;
    islandGroup.add(grassMesh);

    // Rocha de Sustentação Inferior (Solo Orgânico e Mineral)
    const dirtGeo = new THREE.CylinderGeometry(11.8, 2.5, 7, 12, 4);
    const posD = dirtGeo.attributes.position;
    for (let i = 0; i < posD.count; i++) {
        posD.setX(i, posD.getX(i) + (Math.random() - 0.5) * 1.5);
        posD.setZ(i, posD.getZ(i) + (Math.random() - 0.5) * 1.5);
    }
    dirtGeo.computeVertexNormals();
    const dirtMat = new THREE.MeshStandardMaterial({
        color: 0x3d2817,
        roughness: 1.0,
        flatShading: true
    });
    const dirtMesh = new THREE.Mesh(dirtGeo, dirtMat);
    dirtMesh.position.y = -4.1;
    dirtMesh.castShadow = true;
    dirtMesh.receiveShadow = true;
    islandGroup.add(dirtMesh);

    // Caminho da Fazenda / Solo Cultivado
    const pathGeo = new THREE.BoxGeometry(3.5, 0.05, 11);
    const pathMat = new THREE.MeshStandardMaterial({ color: 0x5a4128, roughness: 0.9 });
    const pathMesh = new THREE.Mesh(pathGeo, pathMat);
    pathMesh.position.set(-2.5, 0.66, 0);
    pathMesh.receiveShadow = true;
    islandGroup.add(pathMesh);

    // Lago / Espelho d'água Sustentável
    const pondGeo = new THREE.CylinderGeometry(2.4, 2.4, 0.08, 16);
    const pondMat = new THREE.MeshStandardMaterial({
        color: 0x0284c7,
        roughness: 0.15,
        metalness: 0.35,
        transparent: true,
        opacity: 0.9
    });
    const pondMesh = new THREE.Mesh(pondGeo, pondMat);
    pondMesh.position.set(4.5, 0.66, 4.5);
    islandGroup.add(pondMesh);

    // Eco-Casa Bioclimática
    const houseGroup = new THREE.Group();
    const houseBase = new THREE.Mesh(
        new THREE.BoxGeometry(3, 2.2, 3),
        new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.6 })
    );
    houseBase.position.y = 1.1 + 0.65;
    houseBase.castShadow = true;
    houseBase.receiveShadow = true;
    houseGroup.add(houseBase);

    // Telhado Terracota
    const roofGeo = new THREE.ConeGeometry(2.8, 1.6, 4);
    const roofMat = new THREE.MeshStandardMaterial({ color: 0x991b1b, roughness: 0.5 });
    const roofMesh = new THREE.Mesh(roofGeo, roofMat);
    roofMesh.position.y = 2.2 + 0.8 + 0.65;
    roofMesh.rotation.y = Math.PI / 4;
    roofMesh.castShadow = true;
    houseGroup.add(roofMesh);

    // Chaminé Ecológica
    const chimney = new THREE.Mesh(
        new THREE.BoxGeometry(0.5, 1.2, 0.5),
        new THREE.MeshStandardMaterial({ color: 0x475569 })
    );
    chimney.position.set(0.8, 3.2, 0.4);
    chimney.castShadow = true;
    houseGroup.add(chimney);

    houseGroup.position.set(-4.5, 0, -4.5);
    islandGroup.add(houseGroup);

    // Turbina Eólica com Hélices Giratórias
    const windGroup = new THREE.Group();
    const pole = new THREE.Mesh(
        new THREE.CylinderGeometry(0.18, 0.35, 6, 8),
        new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.4 })
    );
    pole.position.y = 3.6;
    pole.castShadow = true;
    windGroup.add(pole);

    const hub = new THREE.Mesh(
        new THREE.SphereGeometry(0.35, 8, 8),
        new THREE.MeshStandardMaterial({ color: 0x0f172a })
    );
    hub.position.set(0, 6.6, 0.3);
    windGroup.add(hub);

    bladesMesh = new THREE.Group();
    for (let b = 0; b < 3; b++) {
        const blade = new THREE.Mesh(
            new THREE.BoxGeometry(0.2, 2.4, 0.05),
            new THREE.MeshStandardMaterial({ color: 0x38bdf8 })
        );
        blade.position.y = 1.2;
        const bPivot = new THREE.Group();
        bPivot.rotation.z = (b * Math.PI * 2) / 3;
        bPivot.add(blade);
        bladesMesh.add(bPivot);
    }
    bladesMesh.position.set(0, 6.6, 0.35);
    windGroup.add(bladesMesh);
    windGroup.position.set(5, 0, -5);
    islandGroup.add(windGroup);
    windmillMesh = windGroup;

    // Painéis Solares
    solarMesh = new THREE.Group();
    for (let s = 0; s < 2; s++) {
        const panel = new THREE.Mesh(
            new THREE.BoxGeometry(1.6, 0.1, 1.2),
            new THREE.MeshStandardMaterial({ color: 0x1e3a8a, metalness: 0.8, roughness: 0.2 })
        );
        panel.rotation.x = -Math.PI / 6;
        panel.position.set(-4.5 + (s * 1.8), 0.9, 3.5);
        panel.castShadow = true;
        solarMesh.add(panel);
    }
    islandGroup.add(solarMesh);

    // Grupo de Árvores 3D Geradas Proceduralmente
    treesGroup = new THREE.Group();
    islandGroup.add(treesGroup);

    // Nuvens Flutuantes Baixas
    cloudsGroup = new THREE.Group();
    for (let c = 0; c < 4; c++) {
        const cloud = create3DCloud();
        cloud.position.set(
            (Math.random() - 0.5) * 32,
            12 + Math.random() * 4,
            (Math.random() - 0.5) * 32
        );
        cloudsGroup.add(cloud);
    }
    scene3D.add(cloudsGroup);

    threeInitialized = true;

    // Loop de Animação 60fps
    animateThree();

    // Renderiza as árvores 3D iniciais
    render3DTrees();

    // Listener de Redimensionamento Responsivo
    window.addEventListener('resize', onWindowResize);
}

function create3DCloud() {
    const group = new THREE.Group();
    const mat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.9, transparent: true, opacity: 0.85 });
    for (let i = 0; i < 5; i++) {
        const sphere = new THREE.Mesh(new THREE.SphereGeometry(1.2 + Math.random() * 0.8, 7, 7), mat);
        sphere.position.set((i - 2) * 1.0, (Math.random() - 0.5) * 0.4, (Math.random() - 0.5) * 0.8);
        group.add(sphere);
    }
    return group;
}

// Criação de Árvore 3D Mais Realista, Complexa e Texturizada
function createProcedural3DTree(scale = 1, type = 'pine') {
    const tree = new THREE.Group();

    // Tronco de Madeira Detalhado
    const trunkGeo = new THREE.CylinderGeometry(0.18 * scale, 0.28 * scale, 1.4 * scale, 8);
    const posT = trunkGeo.attributes.position;
    for(let i = 0; i < posT.count; i++) {
        if (posT.getY(i) > 0) continue;
        posT.setX(i, posT.getX(i) + (Math.random() - 0.5) * 0.05);
        posT.setZ(i, posT.getZ(i) + (Math.random() - 0.5) * 0.05);
    }
    trunkGeo.computeVertexNormals();
    
    const trunkMat = new THREE.MeshStandardMaterial({ 
        color: 0x4a3018, 
        roughness: 0.95,
        flatShading: true 
    });
    const trunk = new THREE.Mesh(trunkGeo, trunkMat);
    trunk.position.y = 0.7 * scale;
    trunk.castShadow = true;
    trunk.receiveShadow = true;
    tree.add(trunk);

    if (type === 'pine') {
        // Pinheiro em 4 Níveis Orgânicos
        const colorsPine = [0x0f5132, 0x146c43, 0x198754, 0x22c55e];
        for (let i = 0; i < 4; i++) {
            const coneGeo = new THREE.ConeGeometry((1.2 - (i * 0.25)) * scale, 1.4 * scale, 9);
            const posC = coneGeo.attributes.position;
            for(let j = 0; j < posC.count; j++) {
                if (posC.getY(j) > 0.5) continue;
                posC.setX(j, posC.getX(j) + (Math.random() - 0.5) * 0.15);
                posC.setZ(j, posC.getZ(j) + (Math.random() - 0.5) * 0.15);
            }
            coneGeo.computeVertexNormals();

            const coneMat = new THREE.MeshStandardMaterial({ 
                color: colorsPine[i], 
                roughness: 0.8,
                flatShading: true
            });
            const cone = new THREE.Mesh(coneGeo, coneMat);
            cone.position.y = (1.4 + (i * 0.6)) * scale;
            cone.castShadow = true;
            cone.receiveShadow = true;
            tree.add(cone);
        }
    } else {
        // Árvore de Folhas Largas Multi-Copas
        const leavesGroup = new THREE.Group();
        const leafMat = new THREE.MeshStandardMaterial({ 
            color: 0x22c55e, 
            roughness: 0.7,
            flatShading: true
        });
        
        const blobs = [
            { y: 1.8, s: 1.2 },
            { y: 2.2, s: 1.0, x: 0.5, z: 0.3 },
            { y: 2.1, s: 0.9, x: -0.5, z: -0.2 },
            { y: 2.3, s: 0.95, x: -0.2, z: 0.5 },
            { y: 1.9, s: 0.85, x: 0.4, z: -0.6 }
        ];

        blobs.forEach(b => {
            const crownGeo = new THREE.DodecahedronGeometry(b.s * scale, 1);
            const pos = crownGeo.attributes.position;
            for(let j=0; j<pos.count; j++){
                pos.setX(j, pos.getX(j) * (1 + (Math.random()*0.2)));
                pos.setY(j, pos.getY(j) * (1 + (Math.random()*0.2)));
                pos.setZ(j, pos.getZ(j) * (1 + (Math.random()*0.2)));
            }
            crownGeo.computeVertexNormals();

            const crown = new THREE.Mesh(crownGeo, leafMat);
            crown.position.set((b.x||0)*scale, b.y*scale, (b.z||0)*scale);
            crown.castShadow = true;
            crown.receiveShadow = true;
            leavesGroup.add(crown);
        });
        tree.add(leavesGroup);

        // Frutos Ocasionais
        if (Math.random() > 0.4) {
            for (let f = 0; f < 8; f++) {
                const fruit = new THREE.Mesh(
                    new THREE.SphereGeometry(0.12 * scale, 6, 6),
                    new THREE.MeshStandardMaterial({ color: 0xe11d48, roughness: 0.3, metalness: 0.1 })
                );
                const angle = Math.random() * Math.PI * 2;
                const r = 0.7 * scale + Math.random() * 0.4;
                fruit.position.set(
                    Math.cos(angle) * r,
                    (1.7 + Math.random() * 0.8) * scale,
                    Math.sin(angle) * r
                );
                fruit.castShadow = true;
                tree.add(fruit);
            }
        }
    }

    return tree;
}

function render3DTrees() {
    if (!treesGroup) return;

    // A quantidade de árvores 3D é EXATAMENTE a quantidade de mudas_capacidade salvas.
    const targetCount = state.mudas_capacidade;
    const maxTrees = 150; // Limite de segurança para WebGL no navegador
    const count = Math.min(targetCount, maxTrees);

    const currentCount = treesGroup.children.length;

    // Adiciona novas árvores caso o slider aumente
    if (currentCount < count) {
        const treesToAdd = count - currentCount;
        for (let i = 0; i < treesToAdd; i++) {
            let x, z, inHouse, inWindmill, inPond, inPath;
            let attempts = 0;
            do {
                x = (Math.random() - 0.5) * 15; 
                z = (Math.random() - 0.5) * 15; 
                inHouse = Math.hypot(x - (-4.5), z - (-4.5)) < 3.5;
                inWindmill = Math.hypot(x - 5, z - (-5)) < 2.5;
                inPond = Math.hypot(x - 4.5, z - 4.5) < 3.0;
                inPath = Math.abs(x - (-2.5)) < 2.0 && Math.abs(z) < 5.5;
                attempts++;
            } while ((inHouse || inWindmill || inPond || inPath) && attempts < 50);

            const type = Math.random() > 0.4 ? 'pine' : 'oak';
            const s = 0.65 + Math.random() * 0.5; // Escala variável para realismo
            
            const tree = createProcedural3DTree(s, type);
            tree.position.set(x, 0.65, z);
            tree.scale.set(0.01, 0.01, 0.01);
            tree.rotation.y = Math.random() * Math.PI * 2;
            
            treesGroup.add(tree);

            // Animação de brotamento suave
            setTimeout(() => {
                let p = 0;
                const growTimer = setInterval(() => {
                    p += 0.08;
                    if (p >= 1) {
                        tree.scale.set(1, 1, 1);
                        clearInterval(growTimer);
                    } else {
                        tree.scale.set(p, p, p);
                    }
                }, 16);
            }, i * (800 / treesToAdd)); // Brotamento progressivo
        }
    } 
    // Remove árvores caso o slider diminua
    else if (currentCount > count) {
        const treesToRemove = currentCount - count;
        for (let i = 0; i < treesToRemove; i++) {
            const tree = treesGroup.children[treesGroup.children.length - 1];
            treesGroup.remove(tree);
        }
    }
}

function animateThree() {
    requestAnimationFrame(animateThree);

    const time = Date.now() * 0.001;

    // Rotação suave das pás da turbina eólica
    if (bladesMesh) {
        bladesMesh.rotation.z += 0.035;
    }

    // Nuvens orbitando suavemente
    if (cloudsGroup) {
        cloudsGroup.rotation.y += 0.0012;
    }

    // Brisa balançando sutilmente as copas das árvores 3D
    if (treesGroup) {
        treesGroup.children.forEach((tree, idx) => {
            tree.rotation.z = Math.sin(time * 2 + idx) * 0.025;
            tree.rotation.x = Math.cos(time * 1.5 + idx) * 0.015;
        });
    }

    if (controls3D) {
        controls3D.update();
    }

    if (renderer3D && scene3D && camera3D) {
        renderer3D.render(scene3D, camera3D);
    }
}

function reset3DCamera() {
    if (camera3D && controls3D) {
        camera3D.position.set(26, 22, 26);
        controls3D.target.set(0, 0, 0);
        controls3D.update();
    }
}

function toggle3DAutoRotate() {
    isAutoRotating = !isAutoRotating;
    if (controls3D) controls3D.autoRotate = isAutoRotating;
    const btn = document.getElementById('btn-toggle-spin');
    if (btn) {
        btn.innerHTML = `<i class="fas fa-sync-alt"></i> Giro 360°: ${isAutoRotating ? 'ON' : 'OFF'}`;
    }
}

function onWindowResize() {
    const container = document.getElementById('farm-3d-canvas-container');
    if (!container || !camera3D || !renderer3D) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    if (w > 0 && h > 0) {
        camera3D.aspect = w / h;
        camera3D.updateProjectionMatrix();
        renderer3D.setSize(w, h);
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
    const text = btnMsg || (chatInput ? chatInput.value.trim() : '');
    if(!text) return;
    
    const win = document.getElementById('chat-window');
    if (win) {
        win.innerHTML += `<div class="chat-message user">${text}</div>`;
        if (!btnMsg && chatInput) chatInput.value = '';
        win.scrollTop = win.scrollHeight;

        setTimeout(() => {
            let resp = "";
            const txt = text.toLowerCase();
            
            // Variedade de Respostas baseadas em contexto
            const respostasEnergia = [
                `Você sabia que consome em média **${state.energia_kwh} kWh/mês**? Se reduzirmos apenas 15%, sua pegada cairá significativamente. Tente aproveitar mais a luz do sol!`,
                `Sua meta atual foca em reduzir **${state.energia_kwh} kWh**. Tirar eletrônicos do modo stand-by já ajuda muito. Que tal começar por aí?`,
                `Em termos de energia, se mantiver os aparelhos desligados fora de uso, sua projeção de IA mostra que podemos estabilizar seu consumo e economizar R$ ${(state.energia_kwh * 0.15 * 0.75).toFixed(2)} por mês!`
            ];
            
            const respostasFazenda = [
                `Uau, sua fazendinha está no nível: **${state.nivel_fazenda}**! Com ${state.area_plantio} m² e ${state.mudas_capacidade} árvores, você absorve ${state.mudas_absorcao} kg de CO₂/ano. Tente interagir girando a maquete!`,
                `A Fazendinha é o seu "Gêmeo Digital" ambiental. No momento ela suporta ${state.mudas_capacidade} árvores. Gire a câmera 3D para ver os detalhes da natureza crescendo!`,
                `Através da sua área de plantio (${state.area_plantio} m²), você desbloqueia módulos sustentáveis. Explore o painel da fazenda e veja como a natureza te recompensa visualmente!`
            ];
            
            const respostasBanho = [
                `Seu banho diário reportado é de **${state.calc_banho} minutos**. Reduzir 2 minutos já poupa milhares de litros por ano!`,
                `Atenção à água! Com seus banhos de ${state.calc_banho} min, estamos falando de muita energia no chuveiro. Desligar a água ao se ensaboar já faz a diferença.`,
                `Água e energia andam juntas. Se formos diminuir os ${state.calc_banho} min de banho, estaremos ajudando na conta de luz e na conservação hídrica também.`
            ];

            const respostasVazamento = [
                `Vazamentos são silenciosos! Lembre-se que registrar vazamentos na nossa aba ajuda a auditar quanto de água tratada você está perdendo.`,
                `Um pequeno filete de água escapando na privada desperdiça milhares de litros. Fique atento e use a ferramenta "Registro de Vazamentos"!`
            ];

            const respostasDefault = [
                `Interessante... Como copiloto EcoTwin, posso ajudar com cálculos de CO₂, energia, dicas sobre a Fazenda 3D, banhos ou até sobre seus vazamentos. O que prefere explorar?`,
                `Excelente ponto. Lembre-se que você pode gerar seu Laudo PDF oficial com todos os resultados ou testar seu nível de conhecimento no Quiz 10 perguntas!`,
                `Sua pegada total é de ${state.co2.toFixed(1)} kg CO₂e. Posso te ajudar a entender melhor esse número se quiser perguntar sobre 'energia', 'banho', ou 'fazendinha'.`
            ];

            function getRandom(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

            if (txt.includes('energia') || txt.includes('luz') || txt.includes('kwh')) {
                resp = getRandom(respostasEnergia);
            } else if (txt.includes('fazendinha') || txt.includes('3d') || txt.includes('plantio') || txt.includes('arvore') || txt.includes('árvore')) {
                resp = getRandom(respostasFazenda);
            } else if (txt.includes('banho') || txt.includes('água') || txt.includes('agua')) {
                resp = getRandom(respostasBanho);
            } else if (txt.includes('vazamento') || txt.includes('torneira') || txt.includes('desperdício')) {
                resp = getRandom(respostasVazamento);
            } else {
                resp = getRandom(respostasDefault);
            }
            
            win.innerHTML += `<div class="chat-message assistant"><strong>🤖 Aero:</strong> ${resp}</div>`;
            win.scrollTop = win.scrollHeight;
        }, 600);
    }
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

    for (let i = 1; i <= 10; i++) {
        const chave = "qz" + i;
        const marcada = document.querySelector(`input[name="${chave}"]:checked`);
        const fbEl = document.getElementById("fb-" + chave);

        if (!marcada) {
            if (fbEl) {
                fbEl.className = "quiz-feedback incorrect";
                fbEl.innerHTML = "⚠️ Por favor, selecione Mito ou Verdade nesta questão.";
            }
            continue;
        }

        const acertou = (marcada.value === gabaritoQuiz[chave].correta);
        if (acertou) {
            acertos++;
            if (fbEl) {
                fbEl.className = "quiz-feedback correct";
                fbEl.innerHTML = `✅ <strong>Correto!</strong> ${gabaritoQuiz[chave].exp}`;
            }
        } else {
            if (fbEl) {
                fbEl.className = "quiz-feedback incorrect";
                fbEl.innerHTML = `❌ <strong>Incorreto!</strong> ${gabaritoQuiz[chave].exp}`;
            }
        }
    }

    state.quiz_score = acertos;

    // Atualiza Barra de Placar
    const placarEl = document.getElementById('quiz-placar-atual');
    const progTxt = document.getElementById('quiz-progresso-txt');
    if (placarEl) placarEl.innerText = `${acertos} / 10 Acertos`;
    if (progTxt) progTxt.innerText = `${acertos * 10}% de Conhecimento Ecológico`;

    // Exibe Caixa de Resultado Final
    const resBox = document.getElementById('quiz-result-box');
    const titEl = document.getElementById('quiz-final-titulo');
    const descEl = document.getElementById('quiz-final-desc');
    if (resBox && titEl && descEl) {
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
    }

    // Efeito Visual de Comemoração / Balões
    if (typeof confetti === 'function' && acertos >= 5) {
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
function updVazCalc(val) {
    document.getElementById('vaz-int-val').innerText = val;
    const dia = val * 25; // 25 litros por dia por ponto de severidade
    const mes = dia * 30;
    const hora = dia / 24;
    
    document.getElementById('vaz-hora').innerText = `~${Math.round(hora)} L`;
    document.getElementById('vaz-dia').innerText = `${dia} L`;
    document.getElementById('vaz-mes').innerText = `${mes.toLocaleString('pt-BR')} L`;
    
    document.getElementById('vaz-didatico').innerText = `${mes.toLocaleString('pt-BR')} litros/mês`;
    
    // Um banho de 5 min consome aprox 45 litros (chuveiro normal)
    const banhos = Math.floor(mes / 45);
    document.getElementById('vaz-didatico-banhos').innerText = banhos;
}

function registrarVazamento() {
    const local = document.getElementById('vaz-local').value;
    const int = document.getElementById('vaz-int').value;
    const dia = int * 25;
    const perda = dia * 30; // Litros por mes
    const custo = (perda * 0.018).toFixed(2);

    state.vazamentos.push({
        local: local,
        intensidade: int,
        perda: perda,
        custo: custo
    });

    const lista = document.getElementById('vaz-lista');
    if (lista) {
        lista.innerHTML += `
            <div class="vaz-item">
                🔴 <strong>${local}</strong> — Intensidade ${int}/10<br>
                Desperdício: <strong>${perda.toLocaleString('pt-BR')} L/mês</strong> (~R$ ${custo}/mês)
            </div>
        `;
    }
}

// =============================================================================
// ABA 8: RELATÓRIO PDF CONSOLIDADO (JSPDF + AUTOTABLE)
// =============================================================================
function gerarQRCode() {
    const box = document.getElementById("qrcode-container");
    if (!box || typeof QRCode === 'undefined') return;
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
    if (typeof window.jspdf === 'undefined') {
        alert("Carregando motor de PDF, aguarde um segundo...");
        return;
    }
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF('p', 'pt', 'letter');

    // Cabeçalho Principal
    doc.setFont("helvetica", "bold");
    doc.setTextColor(6, 95, 70);
    doc.setFontSize(20);
    doc.text("Laudo Técnico de Inteligência Ambiental - EcoTwin", 40, 45);

    doc.setFont("helvetica", "normal");
    doc.setTextColor(75, 85, 99);
    doc.setFontSize(10);
    doc.text("Documento Técnico Consolidado de Pegada Ecológica, Hábitos, 3D Farm e Auditoria", 40, 62);

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
