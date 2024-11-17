import pandas as pd
import random
from datetime import datetime

# Sample data for generation
trades = ['Blockwork', 'Concrete', 'Roofing', 'Electrical', 'Plumbing', 'Carpentry', 'Finishing']
materials = {
    'Blockwork': ['200mm solid blockwork', '250mm hollow blockwork', '300mm insulated blockwork'],
    'Concrete': ['Ready-mix concrete C20', 'Ready-mix concrete C25', 'Ready-mix concrete C30',
                 'Ready-mix concrete C35'],
    'Roofing': ['Metal roofing sheets', 'Aluminum roofing sheets', 'Asphalt shingles', 'Clay roof tiles',
                'Slate roofing'],
    'Electrical': ['Copper wiring', 'Circuit breaker', 'Switchboard', 'Electrical conduit'],
    'Plumbing': ['PVC pipes', 'Copper pipes', 'Bathroom fittings', 'Kitchen sink', 'Water pump'],
    'Carpentry': ['Hardwood door', 'Plywood sheets', 'Skirting board', 'Wooden window frame'],
    'Finishing': ['Wall tiles', 'Floor tiles', 'Paint (5L)', 'Plastering compound', 'Decorative mouldings']
}
units = ['pc', 'm3', 'sqm', 'ltr', 'kg']
vendor_names = ['BuildMax', 'CityBuild', 'MegaSupplies', 'HomeFix', 'RoofTop Solutions',
                'ConcreteHub', 'PipeLine Supplies', 'WoodWorks', 'ElectroStore', 'TileMaster']
locations = ['Accra', 'Tema', 'Kumasi', 'Takoradi', 'Tamale', 'Sunyani', 'Cape Coast', 'Ho', 'Koforidua', 'Bolgatanga']
current_date = datetime.now().strftime("%d/%m/%Y")


# Helper function to generate random vendor details
def generate_vendor_details():
    vendor = random.choice(vendor_names)
    phone = f'02{random.randint(0, 9)}{random.randint(1000000, 9999999)}'
    email = f'contact@{vendor.lower().replace(" ", "")}.com'
    location = random.choice(locations)
    return vendor, phone, email, location


# Create the dataset
data = []
for i in range(1, 101):  # Create 100 entries
    trade = random.choice(trades)
    material = random.choice(materials[trade])
    unit = random.choice(units)
    price = round(random.uniform(10.0, 500.0), 2)  # Random price between 10 and 500
    vendor, phone, email, location = generate_vendor_details()

    # Generate a Mat ID without leading zeros
    mat_id = f'MAT-{i}'  # e.g., MAT-1, MAT-2, MAT-3
    currency = 'GHS'  # Assuming Ghanaian Cedi

    data.append({
        'Mat ID': mat_id,
        'Trade': trade,
        'Material': material,
        'Currency': currency,
        'Average Price': price,
        'Unit': unit,
        'Vendor': vendor,
        'Phone': phone,
        'Email': email,
        'Location': location,
        'Price Date': current_date
    })

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to Excel
output_path = 'construction_pricelist.xlsx'
df.to_excel(output_path, index=False)

print(f"Data saved to {output_path}")
