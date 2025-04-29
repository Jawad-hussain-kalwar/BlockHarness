# app.py
import streamlit as st
import pandas as pd

from controllers.ai_controller import AIController
from engine.shapes import SHAPES

st.set_page_config(page_title="BlockHarness Testbed", layout="centered")
st.title("🧩 BlockHarness – Parameter Playground")

# ──────────────────────────── inputs ─────────────────────────────
st.header("Spawn Weights (0–10)")
weights = []
cols = st.columns(len(SHAPES))
for i, c in enumerate(cols):
    with c:
        weights.append(st.number_input(f"{i+1}", 0, 10, 2, 1))

st.subheader("Difficulty thresholds")
t1 = st.number_input("Threshold 1 score", 0, 9999, 1000, 100)
w1 = st.text_input("Weights at T1 (8 ints)", "1,2,2,2,2,2,2,3")
t2 = st.number_input("Threshold 2 score", 0, 99999, 3000, 500)
w2 = st.text_input("Weights at T2 (8 ints)", "1,1,2,3,3,3,3,4")
runs = st.number_input("Simulations to run", 1, 200, 20, 1)

if st.button("▶️ Run"):
    config = {
        "shapes": SHAPES,
        "shape_weights": weights,
        "difficulty_thresholds": [
            (t1, list(map(int, w1.split(",")))),
            (t2, list(map(int, w2.split(",")))),
        ],
    }

    def sim_one():
        # Create AI controller with our configuration
        controller = AIController(config)
        
        # Run the simulation until game over
        results = controller.run_simulation()
        
        return {
            "Score": results["score"], 
            "Moves": results["blocks_placed"], 
            "Lines": results["lines"]
        }

    data = [sim_one() for _ in range(runs)]
    df = pd.DataFrame(data)
    st.subheader("Results")
    st.write(df.describe().T)
    st.bar_chart(df[["Score", "Moves", "Lines"]])
