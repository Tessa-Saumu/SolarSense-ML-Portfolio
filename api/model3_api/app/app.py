from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/calculate-roi", methods=["POST"])
def calculate_roi():
    try:
        data = request.get_json()

        result = {
            "status": "success",
            "message": "ROI calculation not implemented yet",
            "input_received": data
        }

        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)
