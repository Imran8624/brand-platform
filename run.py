"""Entrypoint: seed sample data, then launch the Brand Governance Platform."""

import uvicorn

from app.seed import seed
from app.seed_formats import seed_formats

if __name__ == "__main__":
    seed()
    try:
        seed_formats()
    except Exception as e:
        print("Note on seed_formats:", e)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=True)
