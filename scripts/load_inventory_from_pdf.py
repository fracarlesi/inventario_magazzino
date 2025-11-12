"""
Script to load inventory items from "Lista magazzino officina.pdf" into the database.

This script creates items via the backend API endpoint POST /api/items.
Run this after the backend is deployed and accessible.

Usage:
    python scripts/load_inventory_from_pdf.py
"""

import asyncio
import httpx
from decimal import Decimal
from typing import List, Dict

# Backend API URL (update if needed)
API_BASE_URL = "https://inventario-magazzino-backend.onrender.com/api"

# Inventory data extracted from the PDF
INVENTORY_ITEMS = [
    # Iniettori
    {"name": "Iniettore N°4", "category": "Iniettori", "unit": "pz", "stock": 1, "min_stock": 1, "unit_cost": 150.00},
    {"name": "Iniettore N°3", "category": "Iniettori", "unit": "pz", "stock": 1, "min_stock": 1, "unit_cost": 150.00},

    # Servofrizione
    {"name": "Servofrizione", "category": "Servofrizione", "unit": "pz", "stock": 3, "min_stock": 1, "unit_cost": 200.00},

    # Filtri Gasolio
    {"name": "Filtro Gasolio 32", "category": "Filtri Gasolio", "unit": "pz", "stock": 1, "min_stock": 2, "unit_cost": 15.00},
    {"name": "Filtro Gasolio 1942", "category": "Filtri Gasolio", "unit": "pz", "stock": 1, "min_stock": 2, "unit_cost": 15.00},
    {"name": "Filtro Gasolio 15", "category": "Filtri Gasolio", "unit": "pz", "stock": 1, "min_stock": 2, "unit_cost": 15.00},
    {"name": "Filtro Gasolio 17", "category": "Filtri Gasolio", "unit": "pz", "stock": 1, "min_stock": 2, "unit_cost": 15.00},

    # Filtri Oli
    {"name": "Filtro Olio", "category": "Filtri Oli", "unit": "pz", "stock": 17, "min_stock": 5, "unit_cost": 12.00},

    # Filtri UREA
    {"name": "Filtro UREA", "category": "Filtri UREA", "unit": "pz", "stock": 2, "min_stock": 2, "unit_cost": 25.00},

    # Filtri ARIA
    {"name": "Filtro Aria", "category": "Filtri Aria", "unit": "pz", "stock": 13, "min_stock": 5, "unit_cost": 20.00},

    # Filtri Cabina
    {"name": "Filtro Cabina", "category": "Filtri Cabina", "unit": "pz", "stock": 10, "min_stock": 5, "unit_cost": 18.00},

    # Prefiltri Gasolio
    {"name": "Prefiltro Gasolio", "category": "Prefiltri Gasolio", "unit": "pz", "stock": 10, "min_stock": 5, "unit_cost": 10.00},

    # Frizioni
    {"name": "Frizione", "category": "Frizioni", "unit": "pz", "stock": 3, "min_stock": 1, "unit_cost": 250.00},

    # Essicatori
    {"name": "Essicatore Completo", "category": "Essicatori", "unit": "pz", "stock": 2, "min_stock": 1, "unit_cost": 180.00},
    {"name": "Filtro Essicatore", "category": "Filtri Essicatori", "unit": "pz", "stock": 3, "min_stock": 2, "unit_cost": 35.00},

    # Tubi e Pistole Aria
    {"name": "Tubo Aria Stecca Rimorchio", "category": "Tubi Aria", "unit": "pz", "stock": 3, "min_stock": 2, "unit_cost": 25.00},
    {"name": "Pistola Aria con Tubo per Camion", "category": "Pistole Aria", "unit": "pz", "stock": 5, "min_stock": 2, "unit_cost": 45.00},

    # Attacchi
    {"name": "Attacco Collegamento Trattore-Rimorchio", "category": "Attacchi", "unit": "pz", "stock": 8, "min_stock": 3, "unit_cost": 30.00},

    # Luci
    {"name": "Luce Cornetto", "category": "Luci", "unit": "pz", "stock": 5, "min_stock": 3, "unit_cost": 12.00},
    {"name": "Luce Freccia", "category": "Luci", "unit": "pz", "stock": 8, "min_stock": 5, "unit_cost": 10.00},
    {"name": "Catadiottro", "category": "Luci", "unit": "pz", "stock": 6, "min_stock": 4, "unit_cost": 5.00},
    {"name": "Luce Targa", "category": "Luci", "unit": "pz", "stock": 4, "min_stock": 2, "unit_cost": 8.00},
    {"name": "Luce Arancione", "category": "Luci", "unit": "pz", "stock": 10, "min_stock": 5, "unit_cost": 8.00},
    {"name": "Luce Rossa", "category": "Luci", "unit": "pz", "stock": 12, "min_stock": 6, "unit_cost": 8.00},
    {"name": "Luce Bianca", "category": "Luci", "unit": "pz", "stock": 8, "min_stock": 4, "unit_cost": 8.00},

    # Specchietti
    {"name": "Specchietto Nuovo", "category": "Specchietti", "unit": "pz", "stock": 10, "min_stock": 3, "unit_cost": 35.00},
    {"name": "Specchietto Usato", "category": "Specchietti", "unit": "pz", "stock": 13, "min_stock": 5, "unit_cost": 15.00},

    # Carrozzeria
    {"name": "Parafango", "category": "Carrozzeria", "unit": "pz", "stock": 2, "min_stock": 1, "unit_cost": 80.00},
    {"name": "Coperchio Vano", "category": "Carrozzeria", "unit": "pz", "stock": 3, "min_stock": 1, "unit_cost": 25.00},
    {"name": "Guarnizione Porta", "category": "Guarnizioni", "unit": "pz", "stock": 4, "min_stock": 2, "unit_cost": 20.00},
    {"name": "Coprisedile", "category": "Interni", "unit": "pz", "stock": 5, "min_stock": 2, "unit_cost": 30.00},
    {"name": "Pannello Fonoassorbente", "category": "Interni", "unit": "pz", "stock": 3, "min_stock": 1, "unit_cost": 40.00},

    # Ammortizzatori
    {"name": "Ammortizzatore Cabina", "category": "Ammortizzatori", "unit": "pz", "stock": 2, "min_stock": 1, "unit_cost": 60.00},
    {"name": "Ammortizzatore Furgone Citroën", "category": "Ammortizzatori", "unit": "pz", "stock": 2, "min_stock": 1, "unit_cost": 55.00},
    {"name": "Molla a Gas", "category": "Ammortizzatori", "unit": "pz", "stock": 4, "min_stock": 2, "unit_cost": 25.00},

    # Cinghie
    {"name": "Cinghia Servizi", "category": "Cinghie", "unit": "pz", "stock": 10, "min_stock": 5, "unit_cost": 15.00},
    {"name": "Cinghia Distribuzione", "category": "Cinghie", "unit": "pz", "stock": 5, "min_stock": 3, "unit_cost": 45.00},
    {"name": "Tenda/Cinghia Carico", "category": "Cinghie", "unit": "pz", "stock": 5, "min_stock": 3, "unit_cost": 20.00},

    # Alzacristalli
    {"name": "Alzacristalli Elettrico DX", "category": "Alzacristalli", "unit": "pz", "stock": 2, "min_stock": 1, "unit_cost": 70.00},
    {"name": "Alzacristalli Manuale", "category": "Alzacristalli", "unit": "pz", "stock": 1, "min_stock": 1, "unit_cost": 30.00},

    # Centrifughe
    {"name": "Centrifuga Usata", "category": "Centrifughe", "unit": "pz", "stock": 9, "min_stock": 3, "unit_cost": 50.00},

    # Ruote
    {"name": "Ruota Carrello", "category": "Ruote", "unit": "pz", "stock": 6, "min_stock": 3, "unit_cost": 40.00},
    {"name": "Cerchio Carrello", "category": "Ruote", "unit": "pz", "stock": 2, "min_stock": 2, "unit_cost": 35.00},

    # Guarnizioni Varie
    {"name": "Guarnizione Finestrino", "category": "Guarnizioni", "unit": "pz", "stock": 5, "min_stock": 3, "unit_cost": 15.00},
    {"name": "Porcellana Freno", "category": "Guarnizioni", "unit": "pz", "stock": 8, "min_stock": 4, "unit_cost": 8.00},

    # Pompe e Motori
    {"name": "Pompa Acqua", "category": "Pompe", "unit": "pz", "stock": 2, "min_stock": 1, "unit_cost": 80.00},
    {"name": "Elettropompa", "category": "Pompe", "unit": "pz", "stock": 1, "min_stock": 1, "unit_cost": 120.00},
    {"name": "Compressore", "category": "Compressori", "unit": "pz", "stock": 1, "min_stock": 1, "unit_cost": 300.00},
    {"name": "Motorino Avviamento", "category": "Motorini", "unit": "pz", "stock": 2, "min_stock": 1, "unit_cost": 150.00},
    {"name": "Alternatore", "category": "Alternatori", "unit": "pz", "stock": 1, "min_stock": 1, "unit_cost": 200.00},

    # Pastiglie Freni (vari modelli)
    {"name": "Pastiglie Freno Daily", "category": "Pastiglie Freni", "unit": "kit", "stock": 3, "min_stock": 2, "unit_cost": 45.00},
    {"name": "Pastiglie Freno Eurocargo", "category": "Pastiglie Freni", "unit": "kit", "stock": 3, "min_stock": 2, "unit_cost": 50.00},
    {"name": "Pastiglie Freno Mercedes", "category": "Pastiglie Freni", "unit": "kit", "stock": 2, "min_stock": 2, "unit_cost": 55.00},
    {"name": "Pastiglie Freno MAN", "category": "Pastiglie Freni", "unit": "kit", "stock": 2, "min_stock": 2, "unit_cost": 60.00},
    {"name": "Pastiglie Freno Transit", "category": "Pastiglie Freni", "unit": "kit", "stock": 2, "min_stock": 2, "unit_cost": 40.00},
    {"name": "Pastiglie Freno Renault", "category": "Pastiglie Freni", "unit": "kit", "stock": 2, "min_stock": 2, "unit_cost": 45.00},
    {"name": "Pastiglie Freno Iveco", "category": "Pastiglie Freni", "unit": "kit", "stock": 3, "min_stock": 2, "unit_cost": 48.00},

    # Dischi Freno
    {"name": "Disco Freno", "category": "Dischi Freni", "unit": "pz", "stock": 11, "min_stock": 5, "unit_cost": 70.00},
    {"name": "Ganascia Freno", "category": "Dischi Freni", "unit": "pz", "stock": 1, "min_stock": 1, "unit_cost": 90.00},

    # Paraoli e Cuscinetti
    {"name": "Paraoliokit", "category": "Paraoli", "unit": "kit", "stock": 19, "min_stock": 8, "unit_cost": 12.00},
    {"name": "Cuscinetto Ruota", "category": "Cuscinetti", "unit": "pz", "stock": 12, "min_stock": 6, "unit_cost": 25.00},
    {"name": "Cuscinetto Vario", "category": "Cuscinetti", "unit": "pz", "stock": 9, "min_stock": 5, "unit_cost": 20.00},

    # Dadi e Coperchi
    {"name": "Dado Mozzo", "category": "Dadi Mozzo", "unit": "pz", "stock": 2, "min_stock": 2, "unit_cost": 15.00},
    {"name": "Coprimozzo", "category": "Dadi Mozzo", "unit": "pz", "stock": 3, "min_stock": 2, "unit_cost": 10.00},

    # Vari
    {"name": "Barra Stabilizzatrice", "category": "Sospensioni", "unit": "pz", "stock": 3, "min_stock": 2, "unit_cost": 80.00},
    {"name": "Fermo Retainer", "category": "Vari", "unit": "pz", "stock": 5, "min_stock": 3, "unit_cost": 5.00},
    {"name": "Sensore ABS", "category": "Sensori", "unit": "pz", "stock": 4, "min_stock": 2, "unit_cost": 35.00},
    {"name": "Boccola Sospensione", "category": "Sospensioni", "unit": "pz", "stock": 8, "min_stock": 5, "unit_cost": 12.00},
    {"name": "Pompa Servofreno", "category": "Pompe", "unit": "pz", "stock": 2, "min_stock": 1, "unit_cost": 150.00},
]


async def create_item(client: httpx.AsyncClient, item: Dict) -> bool:
    """
    Create a single item via POST /api/items.

    Returns True if successful, False otherwise.
    """
    payload = {
        "name": item["name"],
        "category": item["category"],
        "unit": item["unit"],
        "notes": f"Caricato da PDF - Stock iniziale: {item['stock']} {item['unit']}",
        "min_stock": str(item["min_stock"]),
        "unit_cost": str(item["unit_cost"]),
    }

    try:
        response = await client.post(f"{API_BASE_URL}/items", json=payload)

        if response.status_code == 201:
            item_data = response.json()
            item_id = item_data["id"]
            print(f"✓ Creato: {item['name']} (ID: {item_id})")

            # Now create an initial IN movement to set the stock
            if item["stock"] > 0:
                movement_payload = {
                    "item_id": item_id,
                    "movement_type": "IN",
                    "quantity": str(item["stock"]),
                    "movement_date": "2025-11-12",
                    "note": "Stock iniziale da PDF",
                }

                movement_response = await client.post(f"{API_BASE_URL}/movements", json=movement_payload)

                if movement_response.status_code == 201:
                    print(f"  ✓ Movimento IN creato: {item['stock']} {item['unit']}")
                else:
                    print(f"  ✗ Errore creazione movimento: {movement_response.status_code}")
                    print(f"    {movement_response.text}")

            return True
        else:
            print(f"✗ Errore creazione {item['name']}: {response.status_code}")
            print(f"  {response.text}")
            return False

    except Exception as e:
        print(f"✗ Eccezione creazione {item['name']}: {str(e)}")
        return False


async def main():
    """Main function to load all inventory items."""
    print(f"Inizio caricamento di {len(INVENTORY_ITEMS)} articoli...\n")

    async with httpx.AsyncClient(timeout=30.0) as client:
        success_count = 0
        fail_count = 0

        for item in INVENTORY_ITEMS:
            result = await create_item(client, item)
            if result:
                success_count += 1
            else:
                fail_count += 1

            # Small delay to avoid overwhelming the API
            await asyncio.sleep(0.5)

        print(f"\n{'='*60}")
        print(f"Caricamento completato!")
        print(f"Successi: {success_count}")
        print(f"Fallimenti: {fail_count}")
        print(f"{'='*60}")


if __name__ == "__main__":
    asyncio.run(main())
