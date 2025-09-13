# 🎨 Mapas Temáticos - Ribeirão Preto

Este projeto oferece **3 versões diferentes** de mapas temáticos que combinam dados geográficos (shapefiles) com informações do banco SQL Server, mostrando a distribuição espacial das métricas `total_ped`, `total_prog` e `total_exe`.

## 📊 Dados Temáticos

O mapa utiliza as seguintes colunas do SQL Server:
- **`total_ped`** - Total de pedidos
- **`total_prog`** - Total programado  
- **`total_exe`** - Total executado

## 🗺️ Versões Disponíveis

### 1. 🎨 Mapa Temático Básico
**Arquivo**: `mapa_tematico.py` → `mapa_tematico.html`

**Características**:
- Múltiplas camadas separadas (uma para cada coluna)
- Escala de cores azul → vermelho
- Tooltips informativos
- Controle de camadas
- Estatísticas detalhadas

### 2. 🏷️ Mapa Temático com Labels
**Arquivo**: `mapa_tematico_com_labels.py` → `mapa_tematico_com_labels.html`

**Características**:
- **Labels mínimos** nas quadras mostrando valores
- Mapa temático baseado em `total_prog` (padrão)
- Menu de totais detalhado
- Labels pequenos e discretos
- Foco em uma coluna principal

### 3. 🎛️ Mapa Temático Interativo
**Arquivo**: `mapa_tematico_interativo.py` → `mapa_tematico_interativo.html`

**Características**:
- **Múltiplas camadas** com labels para cada coluna
- Controle completo de camadas
- Labels separados por coluna
- Menu de totais e instruções
- Máxima flexibilidade

## 🚀 Como Executar

### 1. Instalar Dependências
```bash
python instalar_dependencias.py
```

### 2. Escolher e Executar um Mapa

#### Opção A: Mapa Básico
```bash
python mapa_tematico.py
```

#### Opção B: Mapa com Labels
```bash
python mapa_tematico_com_labels.py
```

#### Opção C: Mapa Interativo
```bash
python mapa_tematico_interativo.py
```

### 3. Abrir o Resultado
O arquivo HTML correspondente será gerado e pode ser aberto em qualquer navegador.

## 🎯 Recomendações por Uso

### 📱 Para Visualização Rápida
**Use**: Mapa Temático Básico
- Carregamento mais rápido
- Visualização clara das diferenças
- Ideal para apresentações

### 🏷️ Para Identificação de Valores
**Use**: Mapa Temático com Labels
- Labels mostram valores diretamente
- Foco em uma métrica específica
- Ideal para análise detalhada

### 🎛️ Para Análise Completa
**Use**: Mapa Temático Interativo
- Controle total sobre camadas
- Comparação entre métricas
- Ideal para análise técnica

## 🎨 Como Usar os Mapas

### Controles de Camada (Canto Superior Direito)
- **Mapa Temático - total_ped**: Distribuição de pedidos
- **Mapa Temático - total_prog**: Distribuição programada
- **Mapa Temático - total_exe**: Distribuição executada
- **Labels - [coluna]**: Labels numéricos nas quadras
- **Setores de Abastecimento**: Limites dos setores

### Interpretação das Cores
- **🔵 Azul escuro**: Valores baixos
- **🟡 Amarelo**: Valores médios  
- **🔴 Vermelho**: Valores altos
- **⚪ Cinza**: Quadras sem dados

### Labels nas Quadras
- **Números pequenos**: Valores da métrica selecionada
- **Fundo branco**: Para melhor legibilidade
- **Tooltip**: Mostra detalhes ao passar o mouse

## 📊 Menu de Totais

Cada mapa inclui um painel informativo com:

### 📈 Estatísticas por Métrica
- **Total**: Soma de todos os valores
- **Média**: Valor médio por quadra
- **Min/Max**: Valores mínimo e máximo
- **Quadras**: Número de quadras com dados

### 📋 Resumo Geral
- Total de quadras no sistema
- Percentual de quadras com dados
- Número de setores
- Coordenadas do centro
- Tabela SQL utilizada

## 🔧 Personalização

### Mudar Coluna Principal (Mapa com Labels)
Edite a linha no código:
```python
coluna_principal = 'total_ped'  # ou 'total_prog' ou 'total_exe'
```

### Ajustar Tamanho dos Labels
Modifique o CSS no código:
```python
html=f'<div style="font-size: 10px; ...">'  # Aumentar tamanho
```

### Mudar Paleta de Cores
Edite a lista de cores:
```python
colors=['#313695', '#4575b4', '#74add1', ...]
```

## 📁 Arquivos Necessários

### Shapefiles
- **Quadras**: `RP_QUADRAS_SIRGAS2000_20240229_R4.shp`
- **Setores**: `SETORES ABASTECIMENTO_sigras_2000.shp`

### Banco de Dados
- **Servidor**: 200.98.80.97
- **Database**: CENSO_RIBERAO_PRETO
- **Tabela**: vwRESUMEN_ESTADO_QUADRAS
- **Campos de JOIN**: `quadra` (shapefile) ↔ `gsan_setqua` (SQL)

## 🐛 Solução de Problemas

### Performance Lenta
- **Causa**: Muitas quadras com labels
- **Solução**: Use o mapa básico ou filtre dados

### Labels Muito Pequenos
- **Causa**: Configuração de fonte pequena
- **Solução**: Aumente `font-size` no código

### Erro de Conexão SQL
- **Causa**: Servidor inacessível
- **Solução**: Verifique conectividade e credenciais

### Dependências Faltando
```bash
pip install geopandas folium pyproj pyodbc pandas numpy branca shapely fiona
```

## 📊 Exemplo de Saída

```
🎨 Criando mapa temático com labels...
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

🗺️ Criando mapa temático com labels...
🎨 Criando mapa temático principal com: total_prog
🏷️ Adicionando labels nas quadras...
   ✅ Mapa temático criado para total_prog
   📊 Valores: 0 - 200
   🎨 Quadras com dados: 567
   🏷️ Labels adicionados: 567

✅ Mapa temático com labels salvo como: mapa_tematico_com_labels.html

📊 RESUMO FINAL:
   🏘️ Total de quadras: 1234
   🔗 Quadras com dados temáticos: 567 (45.9%)
   🎨 Mapa temático criado: total_prog
   🏷️ Labels adicionados: 567
   🏭 Total de setores: 15

💰 TOTAIS CALCULADOS:
   TOTAL_PED: 25,645
   TOTAL_PROG: 32,156
   TOTAL_EXE: 28,934
```

## 🎉 Dicas de Uso

1. **Comece com o mapa básico** para entender a distribuição geral
2. **Use o mapa com labels** para identificar valores específicos
3. **Explore o mapa interativo** para análises detalhadas
4. **Compare as métricas** usando o controle de camadas
5. **Use o zoom** para focar em áreas específicas

---

**🎯 Escolha o mapa que melhor atende sua necessidade e explore os dados temáticos de Ribeirão Preto!** 