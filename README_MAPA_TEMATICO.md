# 🎨 Mapa Temático - Ribeirão Preto

Este projeto cria um **mapa temático interativo** que combina dados geográficos (shapefiles) com informações do banco de dados SQL Server, mostrando a distribuição espacial de diferentes métricas.

## 📊 Dados Temáticos

O mapa utiliza as seguintes colunas do SQL Server:
- **`total_ped`** - Total de pedidos
- **`total_prog`** - Total programado  
- **`total_exe`** - Total executado

## 🎯 Funcionalidades

### 🌈 Visualização Temática
- **Escala de cores**: Azul (valores baixos) → Vermelho (valores altos)
- **Múltiplas camadas**: Uma camada para cada coluna temática
- **Controle de camadas**: Ative/desative diferentes visualizações

### 🔍 Interatividade
- **Tooltips informativos**: Mostra valores ao passar o mouse
- **Zoom e navegação**: Explore diferentes áreas da cidade
- **Filtros visuais**: Veja apenas quadras com dados

### 📈 Estatísticas
- **Resumo estatístico**: Min, max, média, total para cada métrica
- **Percentual de cobertura**: Quantas quadras têm dados
- **Informações detalhadas**: Painel com estatísticas gerais

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
python instalar_dependencias.py
```

### 2. Executar o Mapa
```bash
python mapa_tematico.py
```

### 3. Abrir o Resultado
O arquivo `mapa_tematico.html` será gerado e pode ser aberto em qualquer navegador.

## 📁 Arquivos Necessários

### Shapefiles
- **Quadras**: `RP_QUADRAS_SIRGAS2000_20240229_R4.shp`
- **Setores**: `SETORES ABASTECIMENTO_sigras_2000.shp`

### Banco de Dados
- **Servidor**: 200.98.80.97
- **Database**: CENSO_RIBERAO_PRETO
- **Tabela**: vwRESUMEN_ESTADO_QUADRAS
- **Campos de JOIN**: `quadra` (shapefile) ↔ `gsan_setqua` (SQL)

## 🎨 Como Usar o Mapa

### Controles de Camada
1. **Mapa Temático - total_ped**: Mostra distribuição de pedidos
2. **Mapa Temático - total_prog**: Mostra distribuição programada
3. **Mapa Temático - total_exe**: Mostra distribuição executada
4. **Setores de Abastecimento**: Limites dos setores (linhas azuis)

### Interpretação das Cores
- **🔵 Azul escuro**: Valores baixos
- **🟡 Amarelo**: Valores médios  
- **🔴 Vermelho**: Valores altos
- **⚪ Cinza**: Quadras sem dados

### Tooltips
Ao passar o mouse sobre uma quadra, você verá:
- Número da quadra
- Valores das métricas temáticas
- Outras informações disponíveis

## 📊 Exemplo de Saída

```
🎨 Criando mapa temático com dados SQL...
📁 Diretório atual: C:\Projetos_Temp\colab

🔗 Conectando ao SQL Server...
✅ Conectado ao SQL Server: 200.98.80.97/CENSO_RIBERAO_PRETO

📁 Carregando shapefiles...
✓ Quadras carregadas: 1234 registros
✓ Setores carregados: 15 registros

🔗 Fazendo JOIN com dados SQL...
✅ Dados SQL carregados: 567 registros
✅ Colunas temáticas encontradas: ['total_ped', 'total_prog', 'total_exe']

📊 total_ped:
   Min: 0
   Max: 150
   Média: 45.23
   Total: 25645
   Quadras com dados: 567

✅ JOIN realizado: 1234 registros
🔗 Quadras com dados temáticos: 567

🗺️ Criando mapa temático...
🎨 Criando mapa temático para: total_ped
   ✅ Mapa temático criado para total_ped
   📊 Valores: 0 - 150
   🎨 Quadras com dados: 567

✅ Mapa temático salvo como: mapa_tematico.html

📊 RESUMO FINAL:
   🏘️ Total de quadras: 1234
   🔗 Quadras com dados temáticos: 567 (45.9%)
   🎨 Mapas temáticos criados: 3
   🏭 Total de setores: 15
```

## 🔧 Configurações

### Personalizar Cores
Edite a linha com `colors=` no código para mudar a paleta de cores:

```python
colors=['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffcc', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
```

### Adicionar Novas Métricas
Adicione novas colunas na lista `colunas_tematicas`:

```python
colunas_tematicas = ['total_ped', 'total_prog', 'total_exe', 'nova_metrica']
```

### Mudar Estilo dos Setores
Modifique a função `style_function` para os setores:

```python
style_function=lambda feature: {
    'fillColor': 'none',
    'color': 'blue',  # Cor da linha
    'weight': 2,      # Espessura
    'dashArray': '5, 5'  # Padrão tracejado
}
```

## 🐛 Solução de Problemas

### Erro de Conexão SQL
- Verifique se o servidor está acessível
- Confirme credenciais de acesso
- Teste a conexão manualmente

### Shapefiles Não Encontrados
- Verifique os caminhos dos arquivos
- Confirme se os arquivos existem
- Use caminhos absolutos se necessário

### Dependências Faltando
```bash
pip install geopandas folium pyproj pyodbc pandas numpy branca shapely fiona
```

### Performance Lenta
- O mapa pode ficar lento com muitas quadras
- Considere filtrar dados antes da visualização
- Use zoom para focar em áreas específicas

## 📞 Suporte

Para dúvidas ou problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme se os arquivos de entrada existem
3. Teste a conexão com o banco de dados
4. Verifique os logs de erro no console

---

**🎉 Divirta-se explorando os dados temáticos de Ribeirão Preto!** 