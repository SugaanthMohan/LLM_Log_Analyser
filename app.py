from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
# from rag_pipeline import analyze_logs  # Your RAG implementation

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

@app.route('/')
def home():
    return render_template('index.html')

# @app.route('/analyze', methods=['POST'])
# def analyze():
#     data = request.json
#     app_name = data.get("app_name")
#     component = data.get("component")
#     time_range = data.get("time_range")

#     # Process logs using your RAG pipeline
#     result = analyze_logs(app_name, component, time_range)
    
#     return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)
