"""Seed data script for testing (T088).

Inserts sample items and movements for development/testing.
"""
import asyncio
from datetime import date, timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.database import get_async_session_context
from src.models.item import Item
from src.models.movement import Movement


async def seed_data():
    """Insert 10 sample items and 20 sample movements."""
    async with get_async_session_context() as db:
        # Check if data already exists
        from sqlalchemy import select, func
        result = await db.execute(select(func.count(Item.id)))
        item_count = result.scalar_one()

        if item_count > 0:
            print(f"Database already contains {item_count} items. Skipping seed.")
            return

        print("Seeding database with sample data...")

        # Sample items
        items_data = [
            {
                "name": "Olio motore 5W30",
                "category": "Lubrificanti",
                "unit": "lt",
                "notes": "Per motori benzina/diesel",
                "min_stock": 10.0,
                "unit_cost": 15.50,
            },
            {
                "name": "Filtro olio",
                "category": "Filtri",
                "unit": "pz",
                "notes": "Universale per la maggior parte dei veicoli",
                "min_stock": 20.0,
                "unit_cost": 8.00,
            },
            {
                "name": "Pastiglie freno anteriori",
                "category": "Freni",
                "unit": "kit",
                "notes": "Set completo 4 pezzi",
                "min_stock": 5.0,
                "unit_cost": 45.00,
            },
            {
                "name": "Filtro aria",
                "category": "Filtri",
                "unit": "pz",
                "notes": "Formato standard",
                "min_stock": 15.0,
                "unit_cost": 12.00,
            },
            {
                "name": "Batteria 12V 60Ah",
                "category": "Elettrico",
                "unit": "pz",
                "notes": "Per auto medie",
                "min_stock": 3.0,
                "unit_cost": 85.00,
            },
            {
                "name": "Liquido refrigerante",
                "category": "Liquidi",
                "unit": "lt",
                "notes": "Concentrato da diluire",
                "min_stock": 20.0,
                "unit_cost": 6.50,
            },
            {
                "name": "Spazzole tergicristallo",
                "category": "Accessori",
                "unit": "coppia",
                "notes": "Varie misure disponibili",
                "min_stock": 10.0,
                "unit_cost": 18.00,
            },
            {
                "name": "Candele d'accensione",
                "category": "Motore",
                "unit": "pz",
                "notes": "Per motori benzina",
                "min_stock": 16.0,
                "unit_cost": 4.50,
            },
            {
                "name": "Bulloni ruota M12",
                "category": "Ferramenta",
                "unit": "pz",
                "notes": "Set da 20 pezzi",
                "min_stock": 100.0,
                "unit_cost": 0.80,
            },
            {
                "name": "Guarnizione testata",
                "category": "Motore",
                "unit": "pz",
                "notes": "Per vari modelli Fiat",
                "min_stock": 2.0,
                "unit_cost": 125.00,
            },
        ]

        # Insert items
        items = []
        for item_data in items_data:
            item = Item(
                id=uuid4(),
                **item_data
            )
            db.add(item)
            items.append(item)

        await db.flush()
        print(f"✓ Inserted {len(items)} items")

        # Sample movements (IN/OUT/ADJUSTMENT mix)
        movements_data = [
            # Initial stock loads (IN)
            {"item": items[0], "type": "IN", "quantity": 50.0, "days_ago": 60, "note": "Rifornimento iniziale"},
            {"item": items[1], "type": "IN", "quantity": 100.0, "days_ago": 60, "note": "Rifornimento iniziale"},
            {"item": items[2], "type": "IN", "quantity": 20.0, "days_ago": 60, "note": "Rifornimento iniziale"},
            {"item": items[3], "type": "IN", "quantity": 50.0, "days_ago": 60, "note": "Rifornimento iniziale"},
            {"item": items[4], "type": "IN", "quantity": 10.0, "days_ago": 55, "note": "Rifornimento iniziale"},

            # Recent IN movements
            {"item": items[0], "type": "IN", "quantity": 30.0, "days_ago": 10, "note": "Rifornimento settimanale", "cost": 15.00},
            {"item": items[1], "type": "IN", "quantity": 50.0, "days_ago": 8, "note": "Rifornimento settimanale"},
            {"item": items[5], "type": "IN", "quantity": 40.0, "days_ago": 7, "note": "Nuovo fornitore", "cost": 6.00},

            # OUT movements (usage)
            {"item": items[0], "type": "OUT", "quantity": -5.0, "days_ago": 5, "note": "Tagliando Alfa Romeo 159"},
            {"item": items[1], "type": "OUT", "quantity": -1.0, "days_ago": 5, "note": "Tagliando Alfa Romeo 159"},
            {"item": items[3], "type": "OUT", "quantity": -1.0, "days_ago": 5, "note": "Tagliando Alfa Romeo 159"},
            {"item": items[2], "type": "OUT", "quantity": -1.0, "days_ago": 4, "note": "Sostituzione freni Fiat Panda"},
            {"item": items[7], "type": "OUT", "quantity": -4.0, "days_ago": 3, "note": "Sostituzione candele Golf VII"},
            {"item": items[0], "type": "OUT", "quantity": -4.5, "days_ago": 2, "note": "Cambio olio BMW Serie 3"},
            {"item": items[1], "type": "OUT", "quantity": -1.0, "days_ago": 2, "note": "Cambio olio BMW Serie 3"},

            # ADJUSTMENT movements (inventory corrections)
            {"item": items[8], "type": "ADJUSTMENT", "quantity": 5.0, "days_ago": 15, "note": "Conteggio fisico - trovati 5 bulloni in più nel magazzino secondario"},
            {"item": items[3], "type": "ADJUSTMENT", "quantity": -2.0, "days_ago": 12, "note": "Rettifica conteggio mensile - 2 filtri danneggiati da umidità"},

            # More recent movements
            {"item": items[5], "type": "OUT", "quantity": -3.0, "days_ago": 1, "note": "Rabbocco liquido refrigerante Opel Corsa"},
            {"item": items[6], "type": "OUT", "quantity": -1.0, "days_ago": 1, "note": "Sostituzione tergicristalli Toyota Yaris"},
            {"item": items[4], "type": "OUT", "quantity": -1.0, "days_ago": 0, "note": "Sostituzione batteria scarica Renault Clio"},
        ]

        # Insert movements
        for mov_data in movements_data:
            movement_date = date.today() - timedelta(days=mov_data["days_ago"])

            movement = Movement(
                id=uuid4(),
                item_id=mov_data["item"].id,
                movement_type=mov_data["type"],
                quantity=mov_data["quantity"],
                movement_date=movement_date,
                note=mov_data.get("note", ""),
                unit_cost_override=mov_data.get("cost"),
            )
            db.add(movement)

        await db.commit()
        print(f"✓ Inserted {len(movements_data)} movements")
        print("\nSeed data inserted successfully!")

        # Print summary
        print("\n=== Summary ===")
        print(f"Items: {len(items)}")
        print(f"Movements: {len(movements_data)}")
        print("  - IN: 8")
        print("  - OUT: 10")
        print("  - ADJUSTMENT: 2")


if __name__ == "__main__":
    print("Starting seed data script...")
    asyncio.run(seed_data())
    print("Done!")
