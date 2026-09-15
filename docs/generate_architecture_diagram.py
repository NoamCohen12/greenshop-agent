"""
מייצר את תרשים הארכיטקטורה הכללית של המערכת (docs/architecture_diagram.png).
הרצה: python docs/generate_architecture_diagram.py
"""

import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.patches as patches
import matplotlib.pyplot as plt

OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "architecture_diagram.png")

COLOR_CLIENT = "#E8F4F8"
COLOR_BACKEND = "#E8E4F8"
COLOR_GRAPH = "#F0E8F8"
COLOR_EXTERNAL = "#F8EEE4"
COLOR_DATA = "#E4F8E8"


def draw_box(ax, x, y, width, height, label, color, fontsize=10, bold=False):
    box = patches.FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02",
        edgecolor="#555555", facecolor=color, linewidth=1.2,
    )
    ax.add_patch(box)
    ax.text(
        x + width / 2, y + height / 2, label,
        ha="center", va="center", fontsize=fontsize,
        fontweight="bold" if bold else "normal", linespacing=1.5,
    )


def draw_arrow(ax, start, end, label="", style="-|>", color="#333333"):
    ax.annotate(
        "", xy=end, xytext=start,
        arrowprops=dict(arrowstyle=style, color=color, linewidth=1.4, shrinkA=2, shrinkB=2),
    )
    if label:
        mid_x = (start[0] + end[0]) / 2
        mid_y = (start[1] + end[1]) / 2
        ax.text(mid_x, mid_y + 0.12, label, ha="center", va="bottom", fontsize=8, color="#444444")


def build_diagram():
    fig, ax = plt.subplots(figsize=(13, 9))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 9)
    ax.axis("off")

    ax.text(6.5, 8.6, "GreenShop - System Architecture", ha="center", fontsize=15, fontweight="bold")

    # Client
    draw_box(ax, 0.4, 7.0, 2.4, 0.9, "Client\n(HTTP / curl)", COLOR_CLIENT, bold=True)

    # Flask
    draw_box(ax, 4.0, 7.0, 3.2, 0.9, "Flask Server\nPOST /chat  |  POST /n8n-callback", COLOR_BACKEND, bold=True)

    # LangGraph container
    graph_box = patches.FancyBboxPatch(
        (0.4, 1.6), 7.0, 4.9,
        boxstyle="round,pad=0.03",
        edgecolor="#8855AA", facecolor="#FBF7FD", linewidth=1.8, linestyle="--",
    )
    ax.add_patch(graph_box)
    ax.text(3.9, 6.2, "LangGraph  StateGraph", ha="center", fontsize=11, fontweight="bold", color="#663388")

    draw_box(ax, 2.4, 5.2, 3.0, 0.75, "1. Input Guardrail\n& Router", COLOR_GRAPH, fontsize=9, bold=True)
    draw_box(ax, 0.7, 3.9, 2.2, 0.7, "2. Retrieval\n(RAG)", COLOR_GRAPH, fontsize=9, bold=True)
    draw_box(ax, 3.2, 3.9, 2.2, 0.7, "3. Tool\nExecution", COLOR_GRAPH, fontsize=9, bold=True)
    draw_box(ax, 5.7, 5.2, 1.5, 0.75, "Blocked\nInput", "#F8E4E4", fontsize=9)
    draw_box(ax, 2.0, 2.8, 2.6, 0.65, "4. Generation", COLOR_GRAPH, fontsize=9, bold=True)
    draw_box(ax, 2.0, 1.85, 2.6, 0.65, "5. Output Guardrail", COLOR_GRAPH, fontsize=9, bold=True)

    # External services
    draw_box(ax, 8.6, 3.85, 3.6, 1.1, "n8n  (Docker)\nWebhook -> Switch -> Code\n-> Respond to Webhook",
             COLOR_EXTERNAL, fontsize=9, bold=True)
    draw_box(ax, 8.6, 6.0, 3.6, 0.9, "LLM Provider\nOpenAI  /  Ollama", COLOR_EXTERNAL, fontsize=9, bold=True)
    draw_box(ax, 8.6, 1.9, 3.6, 0.95, "ChromaDB\nVector Store", COLOR_DATA, fontsize=9, bold=True)
    draw_box(ax, 8.6, 0.5, 3.6, 0.85, "data/knowledge_base\npolicies + catalog", COLOR_DATA, fontsize=9)

    # Arrows - main flow
    draw_arrow(ax, (2.8, 7.45), (4.0, 7.45))
    draw_arrow(ax, (5.6, 7.0), (4.3, 5.95))
    draw_arrow(ax, (3.4, 5.2), (2.1, 4.6), "knowledge")
    draw_arrow(ax, (4.3, 5.2), (4.3, 4.6), "customer")
    draw_arrow(ax, (5.4, 5.55), (5.7, 5.55), "blocked")
    draw_arrow(ax, (2.0, 3.9), (2.8, 3.45))
    draw_arrow(ax, (4.2, 3.9), (3.6, 3.45))
    draw_arrow(ax, (3.3, 2.8), (3.3, 2.5))
    draw_arrow(ax, (2.0, 2.2), (1.3, 2.6), "retry")
    ax.annotate("", xy=(2.0, 2.85), xytext=(1.3, 2.6),
                arrowprops=dict(arrowstyle="-|>", color="#333333", linewidth=1.4))

    # Arrows - external
    draw_arrow(ax, (5.4, 4.25), (8.6, 4.35), "HTTP POST")
    ax.annotate("", xy=(5.4, 4.05), xytext=(8.6, 4.05),
                arrowprops=dict(arrowstyle="-|>", color="#888888", linewidth=1.2, linestyle="dashed"))
    ax.text(7.0, 3.75, "JSON response", ha="center", fontsize=8, color="#666666")

    # שליפה סמנטית: מנותב מתחת לצמתים כדי לא לחצות אותם
    ax.annotate(
        "", xy=(8.6, 2.45), xytext=(1.8, 3.9),
        arrowprops=dict(
            arrowstyle="-|>", color="#559955", linewidth=1.4,
            connectionstyle="arc3,rad=-0.25",
        ),
    )
    ax.text(6.0, 2.15, "similarity search", ha="center", fontsize=8, color="#448844")

    draw_arrow(ax, (10.4, 1.35), (10.4, 1.9), "", color="#559955")
    ax.text(10.75, 1.55, "ingestion", ha="left", fontsize=8, color="#448844")

    draw_arrow(ax, (7.2, 7.45), (8.6, 6.8), "invoke", color="#996633")

    fig.savefig(OUTPUT_PATH, dpi=160, bbox_inches="tight", facecolor="white")
    print(f"נשמר: {OUTPUT_PATH}")


if __name__ == "__main__":
    build_diagram()
