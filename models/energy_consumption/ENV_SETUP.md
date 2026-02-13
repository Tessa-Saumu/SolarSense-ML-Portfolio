# Environment Setup for Secure API

## .env File Configuration

Create a `.env` file in the `models/energy_consumption/` directory with the following content:

```env
# API Key for Energy Consumption API Authentication
# Generate a strong, random API key using:
# python -c "import secrets; print(secrets.token_urlsafe(32))"
API_KEY=your-secure-api-key-here-change-this-in-production

# Optional: Port configuration (defaults to 8001)
# MODEL1_PORT=8001
```

## Generating a Secure API Key

Run this command to generate a secure random API key:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as the value for `API_KEY` in your `.env` file.

## Important Notes

1. **Never commit `.env` to version control** - It should be in `.gitignore`
2. **Use different API keys for different environments** (dev, staging, production)
3. **Rotate API keys regularly** for security
4. **Keep API keys secret** - Don't share them in code, logs, or documentation

## File Location

The `.env` file should be located at:
```
models/energy_consumption/.env
```

The `app_ml.py` will automatically load it using `python-dotenv`.




