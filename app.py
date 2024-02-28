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
    
    return df

df = get_data_from_excel()

#TITLE
st.title(":bar_chart: Titanic Dashboard")
st.markdown("##")

# SIDEBAR
st.sidebar.header("Please Filter Here:")
survival = st.sidebar.multiselect(
    "Survival Status:",
    options=["Survived", "Did not Survive"],
    default=[]
)

pclass = st.sidebar.multiselect(
    "Passenger Class",
    options=df["Pclass"].unique(),
)

gender = st.sidebar.multiselect(
    "Gender",
    options=df["Sex"].unique()

)
embarked = st.sidebar.multiselect(
    "Embarked Port",
    options=df["Embarked"].unique()

)
border = f"""
<style>
[data-testid="column"] {{
    background-color: rgba(0,0,0,0);
    border: 2px solid #CCCCff;
    padding: 1% 1% 1% 1%;
    border-radius: 20px;
}}

    #{"heatmap"} .stPlot {{
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
col1.metric("Total Passengers", df.shape[0])
col2.metric("Total Survived", df['Survived'].sum() )
col3.metric("Survival Rate", f"{df['Survived'].sum()/df.shape[0]*100:.2f}%")
col4.metric("Total Fare", f"$ {df['Fare'].sum()/1000 :.2f}K ")
col5.metric("Average Age", f"{df['Age'].mean() :.2f}" )

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
fig1 = px.histogram(df, x='Pclass', color='Survived', barmode='group', title='Survival by Passenger Class',
                    labels={'Pclass': 'Passenger Class', 'Survived': 'Survival'})

fig1.update_layout(title=dict(font=dict(size=12, color='white')), width=800, height=400, **chart_properties)


# Chart 2: Age Distribution by Gender
fig2 = px.histogram(df, x='Age', color='Sex', marginal='box', title='Age Distribution by Gender',
                    labels={'Age': 'Age', 'Sex': 'Gender'})
fig2.update_layout(title=dict(font=dict(size=16, color='white')), width=800, height=400, **chart_properties)

left, right = st.columns(2)
left.plotly_chart(fig1, use_container_width=True)
right.plotly_chart(fig2, use_container_width=True)

# Chart 3: Survival by Gender (Donut Chart)
fig3 = px.pie(df, names='Sex', values='Survived', title='Survival by Gender',
                    hover_data=['Survived'], hole=0.6, color_discrete_sequence=px.colors.qualitative.Set1)

fig3.update_traces(textinfo='label+value', pull=[0.1, 0.1, 0.1],hoverinfo='label+percent+name', 
                   hovertemplate='%{label}: %{value} passengers<br>Survived: %{percent:.1%}')  # Include detailed hover info

fig3.update_layout(title=dict(font=dict(size=12, color='white')), width=800, height=400, **chart_properties)

# Chart 4: Fare Distribution by Survival
fig4 = px.box(df, x='Survived', y='Fare', title='Fare Distribution by Survival',
              labels={'Survived': 'Survival', 'Fare': 'Fare'})
fig4.update_layout(title=dict(font=dict(size=16, color='white')), width=600, height=400, **chart_properties)

# Chart 5: Survival by Embarked Port (Donut Chart)
fig5 = px.pie(df, names='Embarked', title='Survival by Embarked Port',
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
corr_matrix_selected = df[selected_columns].corr()

# Chart 10: Correlation Heatmap
fig6 = px.imshow(corr_matrix_selected,
                  title='Correlation Heatmap for Selected Columns',
                  labels=dict(x='Features', y='Features', color='Correlation'),
                  x=selected_columns,
                  y=selected_columns)

fig6.update_layout(
    title=dict(font=dict(size=16, color='white')),
    width=800,
    height=400,
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



# Generate a unique identifier for the chart
chart_id = 'my_chart_id'

# Display the figure in a single column using Streamlit
st.markdown(f"""
    <style>
        #{chart_id} .stPlot {{
            background-color: rgba(0,0,0,0);
            border: 2px solid #CCCCff;
            padding: 1% 1% 1% 1%;
            border-radius: 20px;
        }}
    </style>
""", unsafe_allow_html=True)

# Add the chart with the unique identifier
st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar': False}, key=chart_id)