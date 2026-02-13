from flask import Flask, request, jsonify
from flask_cors import CORS


def create_app(config=None):
    """
    Application factory pattern for Flask app.
    
    Args:
        config: Optional configuration dictionary
        
    Returns:
        Flask application instance
    """
    app = Flask(__name__)
    
    # Apply configuration if provided
    if config:
        app.config.update(config)
    
    # Enable CORS
    CORS(app)
    
    # Register routes
    register_routes(app)
    
    return app


def register_routes(app):
    """Register all application routes."""
    
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


# Create app instance for backward compatibility
app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
