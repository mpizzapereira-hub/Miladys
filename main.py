st.markdown("""
    <style>
    /* Fundo Tecnológico e Futurista */
    .stApp {
        background: radial-gradient(circle at 50% -20%, #e8f5e9, #f4f9f5 70%);
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Sidebar Estilo Cyber */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1b4332 0%, #0d2318 100%);
        color: #ffffff;
        box-shadow: 4px 0px 15px rgba(27, 67, 50, 0.3);
    }
    
    /* Textos gerais da Sidebar em branco */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
    }

    /* CORREÇÃO DOS NÚMEROS/CAMPOS DE ENTRADA DA SIDEBAR */
    [data-testid="stSidebar"] input {
        color: #1b4332 !important;
        background-color: #ffffff !important;
        font-weight: bold !important;
    }
    
    /* Botões com Efeito Neon Cyber */
    .stButton>button {
        background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%);
        color: #e8f5e9 !important;
        border-radius: 10px;
        border: 1px solid #52b788;
        padding: 0.6rem 1.2rem;
        font-weight: bold;
        letter-spacing: 0.5px;
        box-shadow: 0 4px 12px rgba(45, 106, 79, 0.25);
        transition: all 0.3s ease-in-out;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #40916c 0%, #2d6a4f 100%);
        box-shadow: 0 0 15px rgba(82, 183, 136, 0.6);
        border-color: #74c69d;
        transform: translateY(-2px);
    }
    
    /* Cabeçalhos Estilizados */
    h1, h2, h3 {
        color: #1b4332 !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
    }
    
    /* Metrics Futuristas */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border-radius: 12px;
        padding: 12px;
        border: 1px solid rgba(82, 183, 136, 0.3);
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    [data-testid="stMetricValue"] {
        color: #2d6a4f !important;
        font-weight: 800;
    }
    
    /* Navegação por Tabs Cibernética */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(232, 245, 233, 0.6);
        border-radius: 10px 10px 0px 0px;
        color: #1b4332;
        font-weight: 700;
        border: 1px solid rgba(82, 183, 136, 0.2);
        backdrop-filter: blur(5px);
        padding: 8px 16px;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%) !important;
        color: #ffffff !important;
        border-bottom: 3px solid #52b788 !important;
        box-shadow: 0 4px 10px rgba(45, 106, 79, 0.3);
    }
    
    /* Cards com Efeito Glassmorphism */
    .info-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(12px);
        padding: 20px;
        border-radius: 14px;
        border-left: 6px solid #2d6a4f;
        border-top: 1px solid rgba(82, 183, 136, 0.3);
        border-right: 1px solid rgba(82, 183, 136, 0.3);
        border-bottom: 1px solid rgba(82, 183, 136, 0.3);
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
        margin-bottom: 15px;
    }
    .badge-card {
        background: rgba(255, 255, 255, 0.85);
        backdrop-filter: blur(8px);
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #b7e4c7;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        text-align: center;
        margin-bottom: 10px;
    }

    /* Mascot Aero Flutuante no Canto Inferior Direito */
    .aero-widget {
        position: fixed;
        bottom: 20px;
        right: 25px;
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 12px;
        animation: floatAnimation 3s ease-in-out infinite;
    }
    .aero-speech-bubble {
        background: #ffffff;
        color: #1b4332;
        padding: 10px 16px;
        border-radius: 16px 16px 2px 16px;
        font-weight: bold;
        font-size: 13px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.12);
        border: 2px solid #52b788;
        white-space: nowrap;
    }
    .aero-avatar {
        width: 60px;
        height: 60px;
        background: linear-gradient(135deg, #2d6a4f 0%, #1b4332 100%);
        border: 2px solid #52b788;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 30px;
        box-shadow: 0 0 15px rgba(82, 183, 136, 0.6);
        cursor: pointer;
    }
    
    @keyframes floatAnimation {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
        100% { transform: translateY(0px); }
    }
    </style>

    <!-- HTML do Aero Flutuante -->
    <div class="aero-widget">
        <div class="aero-speech-bubble">👋 Olá, Terra!</div>
        <div class="aero-avatar">🤖</div>
    </div>
""", unsafe_allow_html=True)