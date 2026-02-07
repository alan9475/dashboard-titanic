import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Dashboard Titanic", layout="wide")
st.title("Dashboard Titanic: Estatísticas de Sobrevivência")

url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
df = pd.read_csv(url)

# Preencher valores nulos
df['Age'] = df['Age'].fillna(df['Age'].mean())
df['Fare'] = df['Fare'].fillna(df['Fare'].mean())

# Substituir valores de sexo para português
sex_map = {'male': 'Homem', 'female': 'Mulher'}
df['Sex'] = df['Sex'].map(sex_map)

# Filtros interativos
st.sidebar.header("Filtros")
sexo = st.sidebar.multiselect("Sexo", options=df['Sex'].unique(), default=list(df['Sex'].unique()))
classe = st.sidebar.multiselect("Classe", options=sorted(df['Pclass'].unique()), default=sorted(df['Pclass'].unique()))
faixa_etaria = st.sidebar.multiselect("Faixa Etária", options=['Criança', 'Adolescente', 'Adulto Jovem', 'Adulto', 'Idoso'], default=['Criança', 'Adolescente', 'Adulto Jovem', 'Adulto', 'Idoso'])

bins = [0, 12, 18, 35, 60, 120]
labels = ['Criança', 'Adolescente', 'Adulto Jovem', 'Adulto', 'Idoso']
df['Faixa Etária'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)

# Aplicar filtros
df_filtrado = df[df['Sex'].isin(sexo) & df['Pclass'].isin(classe) & df['Faixa Etária'].isin(faixa_etaria)]
if df_filtrado.empty:
    st.warning("Nenhum dado disponível para os filtros selecionados.")
    st.stop()

# Estatísticas principais com filtro
total_passageiros = len(df_filtrado)
total_mortos = (df_filtrado['Survived'] == 0).sum()
total_sobreviventes = (df_filtrado['Survived'] == 1).sum()
percentual_mortos = (total_mortos / total_passageiros * 100) if total_passageiros > 0 else 0
percentual_sobreviventes = (total_sobreviventes / total_passageiros * 100) if total_passageiros > 0 else 0

# Métricas gerais
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Passageiros", total_passageiros)
with col2:
    st.metric("Mortos", f"{total_mortos} ({percentual_mortos:.1f}%)")
with col3:
    st.metric("Sobreviventes", f"{total_sobreviventes} ({percentual_sobreviventes:.1f}%)")

# Dados para gráficos
mortos_por_sexo = df_filtrado[df_filtrado['Survived'] == 0]['Sex'].value_counts()
sobreviventes_por_sexo = df_filtrado[df_filtrado['Survived'] == 1]['Sex'].value_counts()
total_por_sexo = df_filtrado['Sex'].value_counts()

sobreviventes_por_classe = df_filtrado[df_filtrado['Survived'] == 1]['Pclass'].value_counts().sort_index()
mortos_por_classe = df_filtrado[df_filtrado['Survived'] == 0]['Pclass'].value_counts().sort_index()
total_por_classe = df_filtrado['Pclass'].value_counts().sort_index()

taxa_sobrevivencia_faixa_etaria = df_filtrado.groupby('Faixa Etária')['Survived'].mean() * 100
total_por_faixa = df_filtrado['Faixa Etária'].value_counts()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Análise por Sexo")
    st.write("Distribuição de mortes e sobrevivências por gênero.")
    if not total_por_sexo.empty:
        # Dados para stacked bar
        data = []
        for sex in total_por_sexo.index:
            mortos = mortos_por_sexo.get(sex, 0)
            sobreviventes = sobreviventes_por_sexo.get(sex, 0)
            total = total_por_sexo[sex]
            perc_mortos = (mortos / total * 100) if total > 0 else 0
            perc_sobrev = (sobreviventes / total * 100) if total > 0 else 0
            data.append(go.Bar(name=f'Mortos - {sex}', x=[sex], y=[mortos], marker_color='#e74c3c', text=f'{perc_mortos:.1f}% ({mortos})', textposition='inside'))
            data.append(go.Bar(name=f'Sobreviventes - {sex}', x=[sex], y=[sobreviventes], marker_color='#27ae60', text=f'{perc_sobrev:.1f}% ({sobreviventes})', textposition='inside'))
        
        fig1 = go.Figure(data=data)
        fig1.update_layout(barmode='stack', title='Mortos e Sobreviventes por Sexo', xaxis_title='Sexo', yaxis_title='Quantidade')
        # Adicionar total acima
        for sex in total_por_sexo.index:
            total = total_por_sexo[sex]
            fig1.add_annotation(x=sex, y=total, text=f'Total: {total}', showarrow=False, yshift=20, xanchor='center')
        st.plotly_chart(fig1)
    else:
        st.info("Não há dados para os filtros selecionados.")

with col2:
    st.subheader("Análise por Classe")
    st.write("Distribuição de mortes e sobrevivências por classe social.")
    if not total_por_classe.empty:
        classes = ['1ª Classe', '2ª Classe', '3ª Classe']
        data = []
        for i, cls in enumerate(range(1,4)):
            mortos = mortos_por_classe.get(cls, 0)
            sobreviventes = sobreviventes_por_classe.get(cls, 0)
            total = total_por_classe.get(cls, 0)
            perc_mortos = (mortos / total * 100) if total > 0 else 0
            perc_sobrev = (sobreviventes / total * 100) if total > 0 else 0
            data.append(go.Bar(name=f'Mortos - {classes[i]}', x=[classes[i]], y=[mortos], marker_color='#e74c3c', text=f'{perc_mortos:.1f}% ({mortos})', textposition='inside'))
            data.append(go.Bar(name=f'Sobreviventes - {classes[i]}', x=[classes[i]], y=[sobreviventes], marker_color='#27ae60', text=f'{perc_sobrev:.1f}% ({sobreviventes})', textposition='inside'))
        
        fig2 = go.Figure(data=data)
        fig2.update_layout(barmode='stack', title='Mortos e Sobreviventes por Classe', xaxis_title='Classe', yaxis_title='Quantidade')
        # Adicionar text com totais
        for i, cls in enumerate(range(1,4)):
            total = total_por_classe.get(cls, 0)
            fig2.add_annotation(x=classes[i], y=total, text=f'Total: {total}', showarrow=False, yshift=20, xanchor='center')
        st.plotly_chart(fig2)
    else:
        st.info("Não há dados para os filtros selecionados.")

st.subheader("Taxa de Sobrevivência por Faixa Etária")
st.write("Percentual de sobrevivência por faixa etária.")
if not taxa_sobrevivencia_faixa_etaria.empty:
    fig4 = px.bar(taxa_sobrevivencia_faixa_etaria.reset_index(), x='Faixa Etária', y='Survived', 
                  title='Taxa de Sobrevivência por Faixa Etária', labels={'Survived': 'Taxa (%)'}, color='Faixa Etária',
                  text=[f"{v:.1f}% ({total_por_faixa[faixa]})" for faixa, v in taxa_sobrevivencia_faixa_etaria.items()])
    fig4.update_layout(showlegend=False)
    fig4.update_traces(textposition='inside')
    # Adicionar total acima
    for i, (faixa, v) in enumerate(taxa_sobrevivencia_faixa_etaria.items()):
        total = total_por_faixa.get(faixa, 0)
        fig4.add_annotation(x=faixa, y=v, text=f'Total: {total}', showarrow=False, yshift=30, xanchor='center')
    st.plotly_chart(fig4)
else:
    st.info("Não há dados para os filtros selecionados.")

# Legenda das faixas etárias
st.write("**Definição das Faixas Etárias:**")
st.write("- Criança: 0-11 anos")
st.write("- Adolescente: 12-17 anos")
st.write("- Adulto Jovem: 18-34 anos")
st.write("- Adulto: 35-59 anos")
st.write("- Idoso: 60+ anos")

# Cartões com totais por faixa etária
st.subheader("Totais por Idade")
cols = st.columns(len(total_por_faixa))
for i, (faixa, total) in enumerate(total_por_faixa.items()):
    with cols[i]:
        st.metric(f"{faixa}", f"{total} pessoas")

# Gráfico de Pizza: Proporção Geral de Mortos vs Sobreviventes
st.subheader("Proporção Geral de Mortos vs Sobreviventes")
col_pie, col_line = st.columns(2)

with col_pie:
    st.write("Distribuição geral de sobrevivência (Rosca).")
    labels = ['Mortos', 'Sobreviventes']
    values = [total_mortos, total_sobreviventes]
    colors = ['#e74c3c', '#27ae60']
    fig_pie = go.Figure(data=[go.Pie(labels=labels, values=values, marker_colors=colors, hole=0.3)])  # Donut
    fig_pie.update_layout(title='Proporção Geral (Rosca)')
    st.plotly_chart(fig_pie)

with col_line:
    st.write("Tendência de sobrevivência por faixa etária (Linha).")
    if not taxa_sobrevivencia_faixa_etaria.empty:
        fig_line = px.line(taxa_sobrevivencia_faixa_etaria.reset_index(), x='Faixa Etária', y='Survived', 
                           title='Taxa de Sobrevivência por Faixa Etária', markers=True, color_discrete_sequence=['#3498db'],
                           text=[f"{v:.1f}% ({total_por_faixa[faixa]})" for faixa, v in taxa_sobrevivencia_faixa_etaria.items()])
        fig_line.update_layout(yaxis_title='Taxa (%)')
        fig_line.update_traces(textposition='top center')
        st.plotly_chart(fig_line)
    else:
        st.info("Não há dados para os filtros selecionados.")

st.markdown("---")
st.write("Fonte dos dados: [Titanic Dataset - Data Science Dojo](https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv)")
