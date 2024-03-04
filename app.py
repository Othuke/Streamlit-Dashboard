import pandas as pd  # pip install pandas openpyxl
import plotly.express as px  # pip install plotly-express
import streamlit as st  # pip install streamlit
import pybase64

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="Titanic Dashboard", page_icon=":bar_chart:", layout="wide")

# Read the image file
def get_base64_img(pic):
    with open(pic, "rb") as image_file:
        return pybase64.b64encode(image_file.read()).decode()
    
background = get_base64_img("gradient.jpg")
side_bar  = get_base64_img("grad3.jpg")

# Define the CSS style with the background image
pg_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background-image: url(data:image/jpeg;base64,{background});
    background-size: cover;
}}

[data-testid="stHeader"]{{
background-color: rgba(0,0,0,0);
}}

[data-testid="stSidebar"] {{
    background-image: url(data:image/jpeg;base64,{side_bar});
    background-size: cover;
}}
</style>
"""

# Apply the CSS style
st.markdown(pg_bg_img, unsafe_allow_html=True)

# ---- READ EXCEL ----
@st.cache_data
def get_data_from_excel():
    df = pd.read_excel(
        io="Titanic.xlsx",
        engine="openpyxl",
        sheet_name="Sheet2"
    )
    # Data Cleaning and Feature Extraction
    # Example: Extracting Title from Name
    df['Title'] = df['Name'].str.extract(' ([A-Za-z]+)\.', expand=False)

    # Example: Creating a new feature 'Family Size'
    df['Family Size'] = df['SibSp'] + df['Parch'] + 1

    #Create new column
    df["Survival"] = df["Survived"].map({0: "Did not Survive", 1:"Survived"})
    
    return df

df = get_data_from_excel()

#TITLE
st.title(":bar_chart: Titanic Dashboard")
st.markdown("##")

# SIDEBAR
st.sidebar.header("Please Filter Here:")

#Survival status
st.sidebar.write("## Survival Status:")
survived = st.sidebar.checkbox("Survived", value=True)
did_not_survive = st.sidebar.checkbox("Did not Survive", value=True)

survival=[]
if survived:
    survival.append('Survived')

if did_not_survive:
    survival.append('Did not Survive')


#PCLASS
st.sidebar.write("## Passenger Class:")
one = st.sidebar.checkbox("1", value=True)
two = st.sidebar.checkbox("2", value=True)
three = st.sidebar.checkbox("3", value=True)

pclass=[]
if one:
    pclass.append(1)

if two:
    pclass.append(2)

if three:
    pclass.append(3)


#Gender
st.sidebar.write("## Gender:")
male = st.sidebar.checkbox("Male", value=True)
female = st.sidebar.checkbox("Female", value=True)

gender=[]
if male:
    gender.append('male')

if female:
    gender.append('female')


#EMBARKED
st.sidebar.write("## Embarked Port:")
c = st.sidebar.checkbox("Cherboug", value=True)
q = st.sidebar.checkbox("Queenstown", value=True)
s = st.sidebar.checkbox("Southampton", value=True)

embarked=[]
if c:
    embarked.append('C')

if q:
    embarked.append('Q')

if s:
    embarked.append('S')

df_selection = df.query('Survival in @survival and Pclass in @pclass and Sex in @gender and Embarked in @embarked')

# Generate a unique identifier for the chart
chart_key = 'heatmap'

border = f"""
<style>
     [data-testid="column"] {{
    background-color: rgba(0,0,0,0);
    border: 2px solid #CCCCff;
    padding: 1% 1% 1% 1%;
    border-radius: 20px;
}}

</style>
"""

# Apply the CSS style
st.markdown(border, unsafe_allow_html=True)

#KPI Section
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Passengers", df_selection.shape[0])
col2.metric("Total Survived", df_selection['Survived'].sum() )
col3.metric("Survival Rate", f"{df_selection['Survived'].sum()/df_selection.shape[0]*100:.2f}%")
col4.metric("Total Fare", f"$ {df_selection['Fare'].sum()/1000 :.2f}K ")
col5.metric("Average Age", f"{df_selection['Age'].mean() :.2f}" )

st.markdown("""---""")
st.write("***Hover over the charts for more information***")

# Set general properties
chart_properties = dict(
    showlegend=True,
    legend=dict(font=dict(color='white')),
    xaxis=dict(title_font=dict(size=14, color='white'), showgrid=False, tickfont=dict(color='white')),
    yaxis=dict(title_font=dict(size=14, color='white'), showgrid=False, tickfont=dict(color='white')),
    paper_bgcolor='rgba(0,0,0,0)',  # Remove white background
    plot_bgcolor='rgba(0,0,0,0)',  # Remove white gridlines
    margin=dict(l=0, r=0, t=30, b=0)  # Adjust margins
)

# Chart 1: Survival by Passenger Class
fig1 = px.histogram(df_selection, x='Pclass', color='Survived', barmode='group', title='Survival by Passenger Class',
                    labels={'Pclass': 'Passenger Class', 'Survived': 'Survival'}, color_discrete_sequence=px.colors.qualitative.Set1)

fig1.update_layout(title=dict(font=dict(size=16, color='white')), width=800, height=400, **chart_properties)


# Chart 2: Age Distribution by Gender
fig2 = px.histogram(df_selection, x='Age', color='Sex', marginal='box', title='Age Distribution by Gender',
                    labels={'Age': 'Age', 'Sex': 'Gender'}, color_discrete_sequence=px.colors.qualitative.Set1)
fig2.update_layout(title=dict(font=dict(size=16, color='white')), width=800, height=400, **chart_properties)

left, right = st.columns(2)
left.plotly_chart(fig1, use_container_width=True)
right.plotly_chart(fig2, use_container_width=True)

# Chart 3: Survival by Gender (Donut Chart)
fig3 = px.pie(df_selection, names='Sex', values='Survived', title='Survival by Gender',
                    hover_data=['Survived'], hole=0.6, color_discrete_sequence=px.colors.qualitative.Set1)

fig3.update_traces(textinfo='label+value', pull=[0.1, 0.1, 0.1],hoverinfo='label+percent+name', 
                   hovertemplate='%{label}: %{value} passengers<br>Survived: %{percent:.1%}')  # Include detailed hover info

fig3.update_layout(title=dict(font=dict(size=16, color='white')), width=800, height=400, **chart_properties)

# Chart 4: Fare Distribution by Survival
fig4 = px.box(df_selection, x='Survived', y='Fare', title='Fare Distribution by Survival',
              labels={'Survived': 'Survival', 'Fare': 'Fare'},color_discrete_sequence=px.colors.qualitative.Set1)
fig4.update_layout(title=dict(font=dict(size=16, color='white')), width=600, height=400, **chart_properties)

# Chart 5: Survival by Embarked Port (Donut Chart)
fig5 = px.pie(df_selection, names='Embarked', title='Survival by Embarked Port',
              hole=0.6, color_discrete_sequence=px.colors.qualitative.Set1,
              labels={'Embarked': 'Embarked Port'}, 
              category_orders={"Embarked": ["C", "Q", "S"]},  # Optional: Set order of categories
              )
fig5.update_traces(textinfo='label+value', pull=[0.1, 0.1, 0.1],hoverinfo='label+percent+name', 
                   hovertemplate='%{label}: %{value} passengers<br>Survived: %{percent:.1%}')  # Include detailed hover info
fig5.update_layout(title=dict(font=dict(size=16, color='white')), width=800, height=400, **chart_properties)

left, middle, right = st.columns(3)
left.plotly_chart(fig3, use_container_width=True)
middle.plotly_chart(fig4, use_container_width=True)
right.plotly_chart(fig5, use_container_width=True)


# Select columns for correlation heatmap
selected_columns = ['Survived', 'Pclass', 'Age', 'Fare', 'Family Size']
corr_matrix_selected = df_selection[selected_columns].corr()

# Chart 6: Correlation Heatmap
fig6 = px.imshow(corr_matrix_selected,
                  title='Correlation Heatmap for Selected Columns',
                  labels=dict(x='Features', y='Features', color='Correlation'),
                  x=selected_columns,
                  y=selected_columns)

fig6.update_layout(
    title=dict(font=dict(size=16, color='white')),
    width=800,
    height=500,
    **chart_properties,
    coloraxis_colorbar=dict(tickfont=dict(color='white')),  # Set legend font color to white
)

# Add data labels
for i in range(len(selected_columns)):
    for j in range(len(selected_columns)):
        fig6.add_annotation(
            x=selected_columns[j],
            y=selected_columns[i],
            text=f"{corr_matrix_selected.iloc[i, j]:.2f}",
            showarrow=False,
            font=dict(color='white')
        )

# Display the heatmap chart in a single column using Streamlit
st.plotly_chart(fig6, use_container_width=True, key=chart_key, theme=None)

# HTML string with inline styles
#html_str = f"""
 #   <div id="{chart_key}" style="background-color: rgba(0, 0, 0, 0); border: 2px solid #CCCCff; padding: 1% 1% 1% 1%; border-radius: 20px;">
  #      {st.plotly_chart(fig6, use_container_width=True, key=chart_key,theme=None)}
   # </div>
#"""

# Render the HTML string
#st.markdown(html_str, unsafe_allow_html=True)