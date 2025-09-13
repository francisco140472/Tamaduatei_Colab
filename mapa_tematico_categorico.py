import geopandas as gpd
import folium
from folium import LayerControl
from pyproj import Transformer
import os
import sys
import pyodbc
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import mpld3

def conectar_sql_server(server, database, username, password):
    try:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'
        conn = pyodbc.connect(conn_str)
        print(f"✅ Conectado ao SQL Server: {server}/{database}")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao SQL Server: {e}")
        return None

def normalizar_quadra(valor):
    if pd.isna(valor):
        return None
    valor_str = str(valor).strip()
    valor_limpo = valor_str.replace('-', '')
    return valor_limpo

def classificar_categoria(row):
    if row['TOTAL_EXE'] > 0:
        return 'EXECUTADOS'
    elif row['TOTAL_PROG'] > 0:
        return 'PROGRAMADOS'
    elif row['TOTAL_PEND'] > 0:
        return 'PENDENTES'
    else:
        return 'S/ MATRÍCULAS'

def criar_mapa_tematico_categorico():
    SERVER = "200.98.80.97"
    DATABASE = "CENSO_RIBERAO_PRETO"
    USERNAME = "sa"
    PASSWORD = "SantoAndre2021"
    TABELA_SQL = "vwRESUMEN_ESTADO_QUADRAS"
    CAMPO_SHAPEFILE = "quadra"
    CAMPO_SQL = "GSAN_SETQUA"
    caminho_quadras = r"C:\Projetos\0206_Proj_Ribeirao_Preto\HYGOR\CORRECAO_DANILO\RP_QUADRAS_SIRGAS2000_20240229_R4.shp"
    caminho_setores = r"C:\Projetos\0206_Proj_Ribeirao_Preto\HYGOR\CORRECAO_DANILO\SETORES ABASTECIMENTO_sigras_2000.shp"

    print("🎨 Criando mapa temático categórico...")
    if not os.path.exists(caminho_quadras):
        print(f"❌ Arquivo de quadras não encontrado: {caminho_quadras}")
        return None
    if not os.path.exists(caminho_setores):
        print(f"❌ Arquivo de setores não encontrado: {caminho_setores}")
        return None
    conn = conectar_sql_server(SERVER, DATABASE, USERNAME, PASSWORD)
    if not conn:
        print("❌ Não foi possível conectar ao SQL Server")
        return None
    try:
        gdf_quadras = gpd.read_file(caminho_quadras)
        gdf_setores = gpd.read_file(caminho_setores)
        if CAMPO_SHAPEFILE not in gdf_quadras.columns:
            print(f"❌ Campo '{CAMPO_SHAPEFILE}' não encontrado no shapefile")
            print(f"📋 Campos disponíveis: {list(gdf_quadras.columns)}")
            return None
    except Exception as e:
        print(f"❌ Erro ao carregar shapefiles: {e}")
        return None
    try:
        query = f"SELECT * FROM {TABELA_SQL}"
        df_sql = pd.read_sql(query, conn)
        colunas_tematicas = ['TOTAL_PEND', 'TOTAL_PROG', 'TOTAL_EXE']
        for col in colunas_tematicas:
            if col not in df_sql.columns:
                print(f"❌ Coluna '{col}' não encontrada no SQL!")
                return None
        df_sql['GSAN_SETQUA_normalizado'] = df_sql['GSAN_SETQUA'].apply(normalizar_quadra)
        gdf_quadras['quadra_normalizado'] = gdf_quadras['quadra'].apply(normalizar_quadra)
        gdf_joined = gdf_quadras.merge(
            df_sql,
            left_on='quadra_normalizado',
            right_on='GSAN_SETQUA_normalizado',
            how='left'
        )
        # Preencher NaN com 0 para classificação
        for col in colunas_tematicas:
            gdf_joined[col] = gdf_joined[col].fillna(0)
        gdf_joined['CATEGORIA'] = gdf_joined.apply(classificar_categoria, axis=1)
        conn.close()
    except Exception as e:
        print(f"❌ Erro no JOIN: {e}")
        return None
    # CRS
    try:
        gdf_joined = gdf_joined.set_crs(epsg=31983, allow_override=True)
        gdf_joined = gdf_joined.to_crs(epsg=4326)
        gdf_setores = gdf_setores.set_crs(epsg=31983, allow_override=True)
        gdf_setores = gdf_setores.to_crs(epsg=4326)
    except Exception as e:
        print(f"❌ Erro no CRS: {e}")
        return None
    # Centro
    try:
        bounds = gdf_joined.geometry.total_bounds  # [minx, miny, maxx, maxy]
        centro_x = (bounds[0] + bounds[2]) / 2
        centro_y = (bounds[1] + bounds[3]) / 2
        map_center = [centro_y, centro_x]
    except Exception:
        map_center = [-21.1767, -47.8208]
    # Cores
    cores = {
        'EXECUTADOS': '#00FF00',      # Verde
        'PROGRAMADOS': '#FFD700',     # Amarelo forte (dourado)
        'PENDENTES': '#FFD699',       # Bege/Laranja claro
        'S/ MATRÍCULAS': '#BDBDBD'    # Cinza
    }
    # Contagem
    totais = gdf_joined['CATEGORIA'].value_counts().to_dict()
    # Mapa base padrão
    m = folium.Map(location=map_center, zoom_start=14, tiles='cartodb positron', name='Mapa Claro')

    # Camada Satélite ESRI
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satélite (Esri)',
        overlay=False,
        control=True
    ).add_to(m)

    # Camada Satélite Google
    folium.TileLayer(
        tiles='http://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Satélite (Google)',
        overlay=False,
        control=True
    ).add_to(m)

    # Camada Híbrido Google (satélite + labels)
    folium.TileLayer(
        tiles='http://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google',
        name='Híbrido (Google)',
        overlay=False,
        control=True
    ).add_to(m)

    # Camada das quadras
    quadras_fg = folium.FeatureGroup(name="Quadras", show=True)
    quadras_fg.add_child(folium.GeoJson(
        gdf_joined,
        name="Quadras",
        tooltip=folium.features.GeoJsonTooltip(
            fields=[CAMPO_SHAPEFILE, 'CATEGORIA', 'TOTAL_EXE', 'TOTAL_PROG', 'TOTAL_PEND'],
            aliases=['Quadra', 'Categoria', 'Executados', 'Programados', 'Pendentes'],
            sticky=True
        ),
        style_function=lambda feature: {
            'fillColor': cores.get(feature['properties']['CATEGORIA'], '#FFFFFF'),
            'color': '#000000',
            'weight': 1,
            'fillOpacity': 0.7,
        }
    ))
    quadras_fg.add_to(m)
    # Camada dos setores
    setores_fg = folium.FeatureGroup(name="Setores de Abastecimento", show=True)
    setores_fg.add_child(folium.GeoJson(
        gdf_setores,
        name="Setores de Abastecimento",
        style_function=lambda feature: {
            'fillColor': 'none',
            'color': 'blue',
            'weight': 2,
            'dashArray': '5, 5'
        }
    ))
    setores_fg.add_to(m)
    # Rótulos dos setores
    nome_col_setor = None
    for col in gdf_setores.columns:
        if col.strip().lower() == 'nome':
            nome_col_setor = col
            break
    if nome_col_setor:
        rotulos_setores = folium.FeatureGroup(name='Rótulos dos Setores', show=True)
        for idx, row in gdf_setores.iterrows():
            try:
                centro = row.geometry.centroid
                nome_setor = str(row[nome_col_setor])
                rotulos_setores.add_child(
                    folium.map.Marker(
                        [centro.y, centro.x],
                        icon=folium.DivIcon(
                            html=f'<div style="font-size:10px; font-weight: bold; color:#1a237e; padding:0px 3px;">{nome_setor}</div>',
                            icon_size=(75, 13),
                            icon_anchor=(37, 6)
                        )
                    )
                )
            except Exception:
                continue
        rotulos_setores.add_to(m)
    # Rótulos das quadras (FeatureGroup)
    rotulos_quadras = folium.FeatureGroup(name='Rótulos das Quadras', show=False)
    for idx, row in gdf_joined.iterrows():
        try:
            centro = row.geometry.centroid
            numero_quadra = str(row[CAMPO_SHAPEFILE])
            rotulos_quadras.add_child(
                folium.map.Marker(
                    [centro.y, centro.x],
                    icon=folium.DivIcon(
                        html=f'<div style="font-size:9px; font-weight: bold; color:#263238; padding:0px 2px;">{numero_quadra}</div>',
                        icon_size=(30, 10),
                        icon_anchor=(15, 5)
                    )
                )
            )
        except Exception:
            continue
    rotulos_quadras.add_to(m)
    # Cabeçalho moderno com botões personalizados
    cabecalho_html = f'''
    <div style="position: fixed; top: 0; left: 0; width: 100vw; height: 54px; background: linear-gradient(90deg, #1976d2 60%, #64b5f6 100%); color: #fff; z-index:9999; display: flex; align-items: center; box-shadow: 0 2px 8px #8883; font-family: 'Segoe UI', Arial, sans-serif;">
        <div style="font-size: 22px; font-weight: bold; margin-left: 32px; letter-spacing: 1px;">Ribeirão Preto</div>
        <div style="font-size: 15px; font-weight: 400; margin-left: 24px; opacity: 0.85;">Mapa Temático - Situação das Quadras</div>
        <div style="margin-left: auto; display: flex; gap: 12px; align-items: center;">
            <button onclick="window.print()" title="Exportar Mapa" style="background:#fff; color:#1976d2; border:none; border-radius:6px; padding:6px 14px; font-weight:bold; font-size:14px; box-shadow:1px 1px 6px #1976d233; cursor:pointer; transition:background 0.2s; margin-right:2px;">🖨️ Exportar</button>
            <button onclick="abrirPopupTotais()" title="Ver Gráfico Totais" style="background:#fff; color:#1976d2; border:none; border-radius:6px; padding:6px 14px; font-weight:bold; font-size:14px; box-shadow:1px 1px 6px #1976d233; cursor:pointer; transition:background 0.2s;">📊 Totais</button>
            <button onclick="alert('Ajuda: Este é um mapa temático interativo. Use os controles para explorar.');" title="Ajuda" style="background:#fff; color:#1976d2; border:none; border-radius:6px; padding:6px 14px; font-weight:bold; font-size:14px; box-shadow:1px 1px 6px #1976d233; cursor:pointer; transition:background 0.2s; margin-right: 24px;">❓ Ajuda</button>
        </div>
        <div style="margin-right: 12px; font-size: 13px; font-weight: 400; opacity: 0.8;">{pd.Timestamp.today().strftime('%d/%m/%Y')}</div>
    </div>
    <div style="height:54px;"></div> <!-- Espaço para não sobrepor o mapa -->
    '''
    m.get_root().html.add_child(folium.Element(cabecalho_html))

    # Painel de totais moderno (acima da legenda, canto inferior esquerdo)
    painel_html = f'''
    <div id="painel-totais" style="position: fixed; bottom: 182px; left: 40px; min-width: 340px; max-width: 420px; background: #e3f2fd; border:2px solid #1976d2; z-index:9999; font-size:15px; padding: 14px 18px 12px 18px; border-radius: 16px; box-shadow: 2px 4px 16px #8883; font-family: 'Segoe UI', Arial, sans-serif;">
        <div style="font-weight:bold; font-size:16px; margin-bottom:8px; text-align:center; letter-spacing:1px; color:#1976d2;">Totais por Categoria</div>
        <table style="width:100%; text-align:left; font-size:14px;">
            <tr><td>Executados:</td><td style='text-align:right; font-weight:bold; color:#388e3c;'>{totais.get('EXECUTADOS',0)}</td></tr>
            <tr><td>Programados:</td><td style='text-align:right; font-weight:bold; color:#fbc02d;'>{totais.get('PROGRAMADOS',0)}</td></tr>
            <tr><td>Pendentes:</td><td style='text-align:right; font-weight:bold; color:#f57c00;'>{totais.get('PENDENTES',0)}</td></tr>
            <tr><td>S/ Matrículas:</td><td style='text-align:right; font-weight:bold; color:#616161;'>{totais.get('S/ MATRÍCULAS',0)}</td></tr>
        </table>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(painel_html))

    # Legenda customizada moderna (mantida no canto inferior esquerdo, logo abaixo do painel de totais)
    legenda_html = f'''
    <div style="position: fixed; bottom: 80px; left: 40px; min-width: 340px; max-width: 420px; height: 90px;
                background: rgba(255,255,255,0.98); border:2px solid #1976d2; z-index:9999; font-size:14px; padding: 14px 18px 12px 18px; border-radius: 18px; box-shadow: 2px 4px 16px #8883; font-family: 'Segoe UI', Arial, sans-serif;">
        <div style="font-weight:bold; font-size:17px; margin-bottom:8px; text-align:center; letter-spacing:1px; color:#1976d2; background: #e3f2fd; border-radius: 8px; padding: 2px 0 2px 0;">Legenda - Situação das Quadras</div>
        <table style="width:100%; text-align:center; font-weight:bold; border-collapse:collapse;">
            <tr>
                <td style="background-color:{cores['EXECUTADOS']}; border:1.5px solid #1976d2; padding:5px 10px; border-radius:8px; color:#222;">EXECUTADOS<br><span style='font-weight:normal; font-size:13px;'>{totais.get('EXECUTADOS',0)}</span></td>
                <td style="background-color:{cores['PROGRAMADOS']}; border:1.5px solid #1976d2; padding:5px 10px; border-radius:8px; color:#222;">PROGRAMADOS<br><span style='font-weight:normal; font-size:13px;'>{totais.get('PROGRAMADOS',0)}</span></td>
                <td style="background-color:{cores['PENDENTES']}; border:1.5px solid #1976d2; padding:5px 10px; border-radius:8px; color:#222;">PENDENTES<br><span style='font-weight:normal; font-size:13px;'>{totais.get('PENDENTES',0)}</span></td>
                <td style="background-color:{cores['S/ MATRÍCULAS']}; border:1.5px solid #1976d2; padding:5px 10px; border-radius:8px; color:#222;">S/ MATRÍCULAS<br><span style='font-weight:normal; font-size:13px;'>{totais.get('S/ MATRÍCULAS',0)}</span></td>
            </tr>
        </table>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legenda_html))

    # LayerControl no final
    LayerControl(collapsed=False).add_to(m)

    # Adicionar plugin leaflet-easyPrint para exportar imagem
    easyprint_js = 'https://rawcdn.githack.com/rowanwins/leaflet-easyPrint/2.1.9/dist/bundle.js'
    easyprint_css = ''
    m.get_root().header.add_child(folium.Element(f'<script src="{easyprint_js}"></script>'))
    # Botão de exportação
    export_script = '''
    <script>
    function addEasyPrint(){
      if(typeof L.easyPrint !== 'undefined'){
        var printer = L.easyPrint({
          title: 'Exportar Mapa',
          position: 'topleft',
          sizeModes: ['Current'],
          exportOnly: true,
          hideControlContainer: false,
          filename: 'mapa_tematico'
        }).addTo(window._map_);
      } else {
        setTimeout(addEasyPrint, 500);
      }
    }
    addEasyPrint();
    </script>
    '''
    m.get_root().html.add_child(folium.Element(export_script))

    # Gráfico de pizza moderno com rótulos fora das fatias
    categorias = list(totais.keys())
    valores = [totais[c] for c in categorias]
    nomes_abrev = {
        'EXECUTADOS': 'EXEC',
        'PROGRAMADOS': 'PROG',
        'PENDENTES': 'PEND',
        'S/ MATRÍCULAS': 'S/ MAT'
    }
    labels_abrev = [nomes_abrev.get(c, c) for c in categorias]
    cores_pizza = ['#66bb6a', '#ffd600', '#ffb74d', '#bdbdbd']
    fig, ax = plt.subplots(figsize=(7,5))
    wedges, _texts = ax.pie(
        valores,
        labels=None,
        colors=cores_pizza,
        startangle=90,
        wedgeprops={'edgecolor': 'white', 'linewidth': 2}
    )
    # Adicionar valores absolutos e percentuais fora das fatias, bem afastados, ao final da linha de ligação
    total = sum(valores)
    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        x = np.cos(np.deg2rad(ang))
        y = np.sin(np.deg2rad(ang))
        percent = 100.*valores[i]/total
        label = f'{valores[i]}\n{percent:.1f}%'
        ha = 'left' if x > 0 else 'right'
        ax.annotate(label,
                    xy=(x, y),
                    xytext=(2.5*x, 2.5*y + 0.25*i),  # bem mais afastado
                    ha=ha, va='center',
                    fontsize=15, fontweight='bold', color='#222',
                    arrowprops=dict(arrowstyle='-', color=cores_pizza[i], lw=2, connectionstyle='arc3,rad=0.25'))
    # Legenda fora do gráfico
    ax.legend(wedges, labels_abrev, title='Categoria', loc='center left', bbox_to_anchor=(1, 0.5), fontsize=13, title_fontsize=14)
    plt.tight_layout()
    fig.savefig('grafico_totais.png', bbox_inches='tight')
    plt.close(fig)

    # Adicionar popup/modal customizado para mostrar o gráfico
    popup_html = '''
    <div id="popup-totais" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.45); z-index:99999; justify-content:center; align-items:center;">
      <div style="background:#fff; border-radius:16px; box-shadow:0 4px 24px #0005; padding:24px 24px 12px 24px; max-width:520px; margin:auto; position:relative; top:10vh;">
        <button onclick=\"document.getElementById('popup-totais').style.display='none';\" style="position:absolute; top:8px; right:12px; background:#1976d2; color:#fff; border:none; border-radius:6px; font-size:18px; font-weight:bold; width:32px; height:32px; cursor:pointer;">&times;</button>
        <div style="text-align:center; font-size:18px; font-weight:bold; color:#1976d2; margin-bottom:10px;">Totais por Categoria</div>
        <img src='grafico_totais.png' alt='Gráfico Totais' style='max-width:440px; width:100%; border-radius:10px; box-shadow:0 2px 8px #8883;'>
      </div>
    </div>
    <script>
      function abrirPopupTotais(){
        document.getElementById('popup-totais').style.display = 'flex';
      }
    </script>
    '''
    m.get_root().html.add_child(folium.Element(popup_html))

    nome_arquivo = "mapa_tematico_categorico.html"
    m.save(nome_arquivo)
    print(f"\n✅ Mapa temático categórico salvo como: {nome_arquivo}")
    print(f"\nTotais por categoria:")
    for cat, val in totais.items():
        print(f"   {cat}: {val}")
    return m

if __name__ == "__main__":
    criar_mapa_tematico_categorico() 