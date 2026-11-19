"""Entrypoint: seed sample data, then launch the Brand Governance Platform."""

import os
import uvicorn

from app.seed import seed
from app.seed_formats import seed_formats

if __name__ == "__main__":
    seed()
    try:
        seed_formats()
    except Exception as e:
        print("Note on seed_formats:", e)
    port = int(os.environ.get("PORT", 8080))
    is_prod = os.environ.get("ENVIRONMENT", "development").lower() == "production"
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=not is_prod)
