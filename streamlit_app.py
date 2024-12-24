import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

# Configuración de la página con tema personalizado
st.set_page_config(
    page_title="Calculadora de Costos de Tokens",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Aplicar estilos CSS personalizados
st.markdown("""
    <style>
        .main {
            padding: 2rem;
        }
        .stTitle {
            color: #1E88E5;
            font-size: 2.5rem !important;
        }
        .metric-card {
            background-color: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .st-emotion-cache-1wivap2 {
            background-color: #ffffff;
            border-radius: 0.5rem;
            padding: 1rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
    </style>
""", unsafe_allow_html=True)

# Constantes
TOKENS_PER_SECOND = 50
USD_TO_EUR = 0.91
PROVIDER_RATES = {
    "AWS": {"compute": 0.526, "storage": 2.15, "network": 4.20, "color": "rgb(255, 153, 0)"},
    "Google Cloud": {"compute": 0.49, "storage": 1.88, "network": 4.00, "color": "rgb(66, 133, 244)"},
    "Azure": {"compute": 0.52, "storage": 1.70, "network": 3.80, "color": "rgb(0, 164, 239)"}
}

def calculate_costs(tokens, provider_rates):
    """
    Calcula los costos para todos los proveedores.
    """
    results = {}
    total_seconds = tokens / TOKENS_PER_SECOND
    total_hours = total_seconds / 3600
    
    for provider, rates in provider_rates.items():
        compute_rate_eur = rates["compute"] * USD_TO_EUR
        compute_cost = total_hours * compute_rate_eur
        total_cost = compute_cost + rates["storage"] + rates["network"]
        
        results[provider] = {
            "total_cost": total_cost,
            "compute_cost": compute_cost,
            "storage_cost": rates["storage"],
            "network_cost": rates["network"],
            "color": rates["color"]
        }
    
    return results, total_hours

def create_cost_breakdown_chart(results):
    """
    Crea un gráfico de barras apiladas para el desglose de costos.
    """
    providers = list(results.keys())
    compute_costs = [results[p]["compute_cost"] for p in providers]
    storage_costs = [results[p]["storage_cost"] for p in providers]
    network_costs = [results[p]["network_cost"] for p in providers]
    colors = [results[p]["color"] for p in providers]

    fig = go.Figure()
    
    # Agregar barras para cada tipo de costo con colores RGB válidos
    fig.add_trace(go.Bar(name='Cómputo', x=providers, y=compute_costs, marker_color=colors))
    fig.add_trace(go.Bar(name='Almacenamiento', x=providers, y=storage_costs, 
                        marker_color=['rgba(255, 153, 0, 0.7)', 'rgba(66, 133, 244, 0.7)', 'rgba(0, 164, 239, 0.7)']))
    fig.add_trace(go.Bar(name='Red', x=providers, y=network_costs, 
                        marker_color=['rgba(255, 153, 0, 0.4)', 'rgba(66, 133, 244, 0.4)', 'rgba(0, 164, 239, 0.4)']))

    fig.update_layout(
        barmode='stack',
        title='Desglose de Costos por Proveedor',
        yaxis_title='Costo (EUR)',
        plot_bgcolor='white',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

# Título principal y descripción
st.title("💰 Calculadora de Costos de Tokens en la Nube")
st.markdown("""
    Esta calculadora te ayuda a estimar y comparar los costos de procesamiento de tokens
    en los principales proveedores de servicios en la nube. Incluye costos de cómputo,
    almacenamiento y red.
""")

# Sidebar con configuración
with st.sidebar:
    st.header("⚙️ Configuración")
    
    # Entrada de tokens con formato de número más amigable
    tokens_input = st.text_input(
        "Número de tokens:",
        value="200000000",
        help="Ingresa el número de tokens a procesar (se admiten notaciones como 1M, 1B)",
    )
    
    # Convertir entrada de texto a número
    try:
        # Manejar sufijos K, M, B
        tokens_input = tokens_input.upper().replace(',', '')
        if 'K' in tokens_input:
            tokens = float(tokens_input.replace('K', '')) * 1000
        elif 'M' in tokens_input:
            tokens = float(tokens_input.replace('M', '')) * 1000000
        elif 'B' in tokens_input:
            tokens = float(tokens_input.replace('B', '')) * 1000000000
        else:
            tokens = float(tokens_input)
    except ValueError:
        st.error("Por favor, ingresa un número válido")
        tokens = 200000000

    st.markdown("---")
    st.markdown("#### 📊 Información del Proyecto")
    project_name = st.text_input("Nombre del Proyecto", "Mi Proyecto")
    st.markdown("#### 💾 Configuración de Recursos")
    st.slider("Tokens por segundo", 10, 100, TOKENS_PER_SECOND, 5, 
              help="Velocidad de procesamiento estimada")

# Cálculo de costos
results, total_hours = calculate_costs(tokens, PROVIDER_RATES)

# Mostrar resultados principales
st.header("📊 Resumen de Costos")

# Métricas principales en tarjetas
col1, col2, col3 = st.columns(3)
for col, (provider, data) in zip([col1, col2, col3], results.items()):
    with col:
        st.markdown(f"""
            <div class="metric-card">
                <h3 style="color: {data['color']}">{provider}</h3>
                <h2>{data['total_cost']:.2f} €</h2>
            </div>
        """, unsafe_allow_html=True)

# Información de tiempo
st.markdown("### ⏱️ Tiempo Estimado de Procesamiento")
days = total_hours / 24
if days >= 1:
    st.info(f"⏳ Tiempo total: {days:.1f} días ({total_hours:.1f} horas)")
else:
    st.info(f"⏳ Tiempo total: {total_hours:.1f} horas")

# Gráfico de desglose de costos
st.plotly_chart(create_cost_breakdown_chart(results), use_container_width=True)

# Detalles de los cálculos
with st.expander("📑 Ver detalles de los cálculos"):
    st.markdown("### 🔢 Desglose detallado por proveedor")
    
    for provider, data in results.items():
        st.markdown(f"""
            #### {provider}
            - **Costo de cómputo:** {data['compute_cost']:.2f} €
            - **Costo de almacenamiento:** {data['storage_cost']:.2f} €
            - **Costo de red:** {data['network_cost']:.2f} €
            - **Costo total:** {data['total_cost']:.2f} €
        """)

# Botón para exportar resultados
if st.button("📤 Exportar Resultados"):
    # Crear reporte
    report = f"""
    Reporte de Costos - {project_name}
    Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Tokens procesados: {tokens:,.0f}
    Tiempo estimado: {total_hours:.2f} horas
    
    Resultados por proveedor:
    """
    for provider, data in results.items():
        report += f"\n{provider}:\n"
        report += f"- Costo total: {data['total_cost']:.2f} €\n"
        report += f"- Cómputo: {data['compute_cost']:.2f} €\n"
        report += f"- Almacenamiento: {data['storage_cost']:.2f} €\n"
        report += f"- Red: {data['network_cost']:.2f} €\n"
    
    st.download_button(
        label="Descargar Reporte",
        data=report,
        file_name=f"reporte_costos_{datetime.now().strftime('%Y%m%d')}.txt",
        mime="text/plain"
    )

# Footer con información adicional
st.markdown("---")
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📱 Conecta conmigo")
    st.markdown("[Victor Lopez Rapado](https://www.linkedin.com/in/victorlopezrapado/)")
with col2:
    st.markdown("### ℹ️ Notas")
    st.markdown("""
        - Los precios son aproximados y pueden variar según la región
        - Actualizado: Diciembre 2024
        - Basado en precios estándar de cada proveedor
    """)