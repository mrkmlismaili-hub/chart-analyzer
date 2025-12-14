from flask import Flask, request, jsonify, render_template
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ["OPENAI_API_KEY"]

def analyze_chart_image(image_path):
    with open(image_path, "rb") as f:
        response = openai.chat.completions.create(
            model="gpt-5-mini",
            messages=[
                {
                    "role": "user",
                    "content": "Analyze this chart and give a short trading recommendation in the format: Decision: Buy/Sell/Hold | Key Levels: Support: XXX, Resistance: XXX"
                }
            ],
            files=[{"name": "chart.png", "data": f.read()}]
        )
    return response.choices[0].message['content']

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "charts" not in request.files:
        return jsonify({"error": "No chart uploaded"}), 400

    uploaded_files = request.files.getlist("charts")
    decisions = []

    for i, chart in enumerate(uploaded_files):
        filename = f"uploaded_chart_{i}.png"
        chart.save(filename)
        try:
            decision = analyze_chart_image(filename)
        except Exception as e:
            decision = f"Error analyzing chart: {e}"
        finally:
            os.remove(filename)
        decisions.append(decision)

    return jsonify({"decisions": decisions})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
