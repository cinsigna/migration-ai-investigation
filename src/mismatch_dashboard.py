# %%
#pip install matplotlib

# %%
# Load variables from .env into the process
from dotenv import load_dotenv
import os
load_dotenv()


# Retrieve the API keys and other secrets
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")          


# Set as environment variables explicitly (optional but often useful)
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY or ""
print("OpenAI API key loaded and set as environment variable.")


# %%
import gradio as gr
import pandas as pd
import matplotlib.pyplot as plt
import os
from openai import OpenAI

# Prepare model client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))



def run_llm_analysis(summary_df, impacted_df):
    summary_text = summary_df.to_csv(index=False)
    impacted_text = impacted_df.to_csv(index=False)

    prompt = f"""
You are helping with a utility billing migration incident.

Your task is to create a structured and client friendly analysis.  
Start with a short overall summary.  
Then present each mismatch pattern clearly and consistently.

Follow this exact structure:

## Overall summary and priorities
Provide a concise three to five point summary with the main themes, the main causes, and what the client should prioritise.

## Detailed analysis by top patterns
For each pattern in the table:
1. Pattern title in the format: Legacy Product → Migrated Product, Reason Code, and number of customers affected.
2. Likely issue in simple language.
3. Suggested remediation action that a delivery team can take.
4. Whether the issue looks systematic or isolated.
5. List of impacted customer ids.

Here is the summary table:
{summary_text}

Here is the impacted customers table:
{impacted_text}

Only analyse the patterns provided.  
Keep the writing clear, concise, and client ready.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You work as a billing migration expert."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content

    except Exception as e:
        return f"AI analysis not available. Error: {e}"


def compute_stats(file_obj):
    df = pd.read_csv(file_obj.name)

    df["is_mismatch"] = df["legacy_product"] != df["migrated_product"]
    total_rows = len(df)
    total_mismatches = int(df["is_mismatch"].sum())
    mismatch_rate = (total_mismatches / total_rows * 100) if total_rows > 0 else 0.0

    mismatches = df[df["is_mismatch"]].copy()

    # Ensure output folder exists
    os.makedirs("output", exist_ok=True)

    # Zero mismatch guard
    if mismatches.empty:
        kpi_text = (
            f"Total customers: {total_rows}\n"
            f"Total mismatches: 0\n"
            f"Mismatch rate: 0.00 percent"
        )

        # Clear, readable plot when there are no mismatches
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.text(0.5, 0.5, "No mismatches detected", ha="center", va="center", fontsize=14)
        ax.axis("off")
        fig.tight_layout()

        # Clear, client-ready message
        ai_text = (
            "## Overall summary and priorities\n"
            "No mismatches were detected in this migration file.\n\n"
            "## Detailed analysis by top patterns\n"
            "No mismatch patterns to analyse. No remediation actions are required."
        )

        # Save empty outputs for consistency
        pd.DataFrame(columns=["customer_id", "legacy_product", "migrated_product", "si_reason_code"]).to_csv(
            "output/impacted_customers.csv", index=False
        )
        pd.DataFrame(columns=["legacy_product", "migrated_product", "si_reason_code", "customer_ids"]).to_csv(
            "output/impacted_customers_by_pattern.csv", index=False
        )
        with open("output/ai_mismatch_analysis.txt", "w", encoding="utf8") as f:
            f.write(ai_text)

        print("No mismatches detected. Saved empty output files in output/")

        return kpi_text, pd.DataFrame(), pd.DataFrame(), fig, ai_text

    # impacted customers per pattern
    impacted = (
        mismatches.groupby(["legacy_product", "migrated_product", "si_reason_code"])["customer_id"]
        .apply(list)
        .reset_index(name="customer_ids")
    )

    # Save impacted customers by pattern
    impacted.to_csv("output/impacted_customers_by_pattern.csv", index=False)
    print("Saved output/impacted_customers_by_pattern.csv")

    # Save flat list of impacted customers
    impacted_customers = mismatches[["customer_id", "legacy_product", "migrated_product", "si_reason_code"]].copy()
    impacted_customers.to_csv("output/impacted_customers.csv", index=False)
    print("Saved output/impacted_customers.csv")

    # mismatch summary for LLM input
    summary = (
        mismatches.groupby(["legacy_product", "migrated_product", "si_reason_code"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    by_reason = (
        mismatches.groupby("si_reason_code")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    by_pair = (
        mismatches.groupby(["legacy_product", "migrated_product"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )

    kpi_text = (
        f"Total customers: {total_rows}\n"
        f"Total mismatches: {total_mismatches}\n"
        f"Mismatch rate: {mismatch_rate:.2f} percent"
    )

    # Plot, safe even with few categories
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.barh(by_reason["si_reason_code"], by_reason["count"])
    ax.set_title("Mismatches by SI reason code")
    ax.set_xlabel("Count")
    ax.set_ylabel("SI reason code")
    ax.invert_yaxis()
    fig.tight_layout()

    # run AI analysis
    ai_text = run_llm_analysis(summary, impacted)

    # Save AI analysis to file
    with open("output/ai_mismatch_analysis.txt", "w", encoding="utf8") as f:
        f.write(ai_text)
    print("Saved output/ai_mismatch_analysis.txt")

    return kpi_text, by_reason, by_pair, fig, ai_text

with gr.Blocks(title="Migration mismatch dashboard") as demo:
    gr.Markdown(
        """
        # Migration mismatch dashboard  
        Load a migration file to see mismatch volume and root cause insights.
        """
    )

    upload = gr.File(label="Upload migration CSV file")

    kpi_box = gr.Textbox(
        label="Key metrics",
        interactive=False,
        lines=5
    )

    with gr.Tabs():
        with gr.Tab("Reason view"):
            reason_table = gr.Dataframe(
                label="Mismatches by SI reason code",
                interactive=False
            )
            reason_plot = gr.Plot(label="Graph")

        with gr.Tab("Product view"):
            pair_table = gr.Dataframe(
                label="Mismatches by product pair",
                interactive=False
            )

        with gr.Tab("AI analysis"):
            ai_box = gr.Markdown(label="Root cause and remediation analysis")

    upload.change(
        fn=compute_stats,
        inputs=upload,
        outputs=[kpi_box, reason_table, pair_table, reason_plot, ai_box]
    )


if __name__ == "__main__":
    demo.launch()


