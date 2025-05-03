
import streamlit as st
import pandas as pd
import random
import time
from fpdf import FPDF
import tempfile

st.set_page_config(page_title="Catering Companion", layout="centered", page_icon="🍴")

# Load style
try:
    st.markdown(open("sexy_minimal_ui_style_snippet.html").read(), unsafe_allow_html=True)
except FileNotFoundError:
    st.warning("UI style sheet not found. Using default styling.")

# App setup
affirmations = [
    "You're doing great work, keep pushing.",
    "Today's prep is tomorrow's peace.",
    "Every tray you prep is a step closer to success.",
]

if "checked_ingredients" not in st.session_state:
    st.session_state.checked_ingredients = set()

def generate_shopping_list_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Shopping List", ln=True, align="C")
    pdf.ln(10)
    for _, row in dataframe.iterrows():
        line = f"- {row['ScaledQuantity']} {row['Unit']} {row['Ingredient']}"
        pdf.cell(200, 10, txt=line, ln=True)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    return temp_file

# Load recipe data
df = pd.read_csv("master_recipe_template.csv")
recipe_name = st.selectbox("Choose a recipe:", df["RecipeName"].unique())
num_guests = st.number_input("Number of guests:", min_value=1, value=10, step=1)

recipe_df = df[df["RecipeName"] == recipe_name].copy()
base_servings = recipe_df["BaseServings"].iloc[0]
scaling_factor = num_guests / base_servings
recipe_df["ScaledQuantity"] = recipe_df["Quantity"] * scaling_factor

# Show shopping list preview with checkboxes
st.subheader("Shopping List Preview")
for idx, row in recipe_df.iterrows():
    label = f"{row['ScaledQuantity']} {row['Unit']} {row['Ingredient']}"
    if st.checkbox(label, key=f"checkbox_{idx}"):
        st.session_state.checked_ingredients.add(row["Ingredient"])
    else:
        st.session_state.checked_ingredients.discard(row["Ingredient"])

# Filter out checked items
final_df = recipe_df[~recipe_df["Ingredient"].isin(st.session_state.checked_ingredients)]

# Show final shopping list
st.markdown("---")
st.subheader("Final Shopping List")
for _, row in final_df.iterrows():
    st.write(f"- {row['ScaledQuantity']} {row['Unit']} {row['Ingredient']}")

# Export to PDF
if st.button("Export Shopping List to PDF"):
    pdf_file = generate_shopping_list_pdf(final_df)
    with open(pdf_file.name, "rb") as file:
        st.download_button(
            label="Download PDF",
            data=file,
            file_name="shopping_list.pdf",
            mime="application/pdf"
        )
