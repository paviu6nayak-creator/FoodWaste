from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3

# Import helper modules
try:
    import database
    import analytics
    import insights
except ImportError:
    database = None
    analytics = None
    insights = None

app = FastAPI(title="FoodWise API")

# Enable CORS for frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class WasteItem(BaseModel):
    food_name: Optional[str] = None
    name: Optional[str] = None
    category: str
    quantity: float
    unit: str = "kg"
    price: Optional[float] = None
    cost: Optional[float] = None
    reason: Optional[str] = "Expired"
    date: Optional[str] = None

@app.get("/api/health")
def health_check():
    return {"status": "online", "message": "FoodWise Backend API is active!"}

@app.get("/api/waste")
def get_waste_records():
    conn = sqlite3.connect("foodwaste.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM waste_records ORDER BY id DESC")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        return []
    finally:
        conn.close()

@app.post("/api/waste")
def add_waste_record(item: WasteItem):
    name = (item.food_name or item.name or "").strip()
    if not name:
        raise HTTPException(status_code=422, detail="Food name is required")
    price = item.price if item.price is not None else (item.cost if item.cost is not None else 0.0)
    
    try:
        conn = sqlite3.connect("foodwaste.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO waste_records (food_name, category, quantity, unit, price, reason, date)
            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
        """, (name, item.category, item.quantity, item.unit, price, item.reason))
        conn.commit()
        new_id = cursor.lastrowid
        conn.close()
        return {"status": "success", "message": "Record added", "id": new_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/waste/{record_id}")
def delete_waste_record(record_id: int):
    try:
        conn = sqlite3.connect("foodwaste.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM waste_records WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Record {record_id} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analytics")
def get_analytics():
    conn = sqlite3.connect("foodwaste.db")
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*), COALESCE(SUM(quantity), 0), COALESCE(SUM(quantity * price), 0) FROM waste_records")
        total_items, total_qty, total_loss = cursor.fetchone()

        cursor.execute("SELECT category, SUM(quantity) FROM waste_records GROUP BY category ORDER BY SUM(quantity) DESC LIMIT 1")
        top_cat_row = cursor.fetchone()
        top_category = top_cat_row[0] if top_cat_row else "None"

        cursor.execute("SELECT category, SUM(quantity) FROM waste_records GROUP BY category")
        categories_breakdown = dict(cursor.fetchall())

        cursor.execute("SELECT reason, COUNT(*) FROM waste_records GROUP BY reason ORDER BY COUNT(*) DESC")
        reasons_breakdown = dict(cursor.fetchall())

        cursor.execute("SELECT food_name, COUNT(*), SUM(quantity) FROM waste_records GROUP BY food_name ORDER BY COUNT(*) DESC LIMIT 5")
        top_foods = [{"name": row[0], "count": row[1], "quantity": round(row[2], 2)} for row in cursor.fetchall()]

        return {
            "total_items": total_items,
            "total_quantity": round(total_qty, 2),
            "total_loss": round(total_loss, 2),
            "top_category": top_category,
            "by_category": categories_breakdown,
            "by_reason": reasons_breakdown,
            "top_foods": top_foods
        }
    except Exception as e:
        return {
            "total_items": 0,
            "total_quantity": 0,
            "total_loss": 0,
            "top_category": "None",
            "by_category": {},
            "by_reason": {},
            "top_foods": []
        }
    finally:
        conn.close()

@app.get("/api/insights")
def get_insights_api():
    tips = [
        "Store dairy products on interior refrigerator shelves rather than the door to maintain consistent temperature.",
        "Use clear, labeled storage containers to quickly track expiring cooked meals.",
        "Freeze surplus vegetables and herbs into portion-sized batches before expiration.",
        "Plan a 'leftover night' every week to use up ingredients before doing new grocery shopping."
    ]
    dynamic_insights = []
    score = 100
    if insights:
        try:
            dynamic_insights = insights.get_insights()
            score = insights.calculate_score()
        except Exception:
            pass

    return {
        "score": score,
        "insights": dynamic_insights,
        "tips": tips
    }

# Mount static frontend files
import os
from fastapi.staticfiles import StaticFiles

frontend_dir = os.path.join(os.path.dirname(__file__), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")