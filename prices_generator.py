import pandas as pd
import random
from datetime import datetime

# Sample data categories for generating construction material data
trades = [
    'Blockwork', 'Concrete', 'Roofing', 'Electrical', 'Plumbing', 'Carpentry', 'Finishing'
]

# Dictionary mapping each trade to a list of materials associated with it
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

# List of units of measurement for the materials
units = ['pc', 'm3', 'sqm', 'ltr', 'kg']

# List of sample vendor names for generating vendor details
vendor_names = [
    'BuildMax', 'CityBuild', 'MegaSupplies', 'HomeFix', 'RoofTop Solutions',
    'ConcreteHub', 'PipeLine Supplies', 'WoodWorks', 'ElectroStore', 'TileMaster'
]

# List of cities or locations to assign to vendors
locations = [
    'Accra', 'Tema', 'Kumasi', 'Takoradi', 'Tamale', 'Sunyani',
    'Cape Coast', 'Ho', 'Koforidua', 'Bolgatanga'
]

# Get the current date in the format "dd/mm/yyyy" to timestamp the price
current_date = datetime.now().strftime("%d/%m/%Y")


# Helper function to generate random vendor details (name, contact info, and location)
def generate_vendor_details():
    # Randomly select a vendor from the vendor_names list
    vendor = random.choice(vendor_names)

    # Generate a random phone number starting with '02' and followed by 8 digits
    phone = f'02{random.randint(0, 9)}{random.randint(1000000, 9999999)}'

    # Create a generic email for the vendor based on their name
    email = f'contact@{vendor.lower().replace(" ", "")}.com'

    # Randomly select a location for the vendor
    location = random.choice(locations)

    return vendor, phone, email, location


# Create the dataset for construction material pricing
data = []
for i in range(1, 100):  # Generate 500 entries for the dataset     todo: 100 data set
    # Randomly select a trade and an associated material
    trade = random.choice(trades)
    material = random.choice(materials[trade])

    # Randomly select a unit of measurement and generate a price
    unit = random.choice(units)
    price = round(random.uniform(10.0, 500.0), 2)  # Price range: 10 to 500 GHS

    # Generate vendor details using the helper function
    vendor, phone, email, location = generate_vendor_details()

    # Generate a Material ID (Mat ID) without leading zeros, e.g., MAT-1, MAT-2, etc.
    mat_id = f'MAT-{i}'  # Unique ID for each material entry

    # Assume the currency is Ghanaian Cedi (GHS)
    currency = 'GHS'

    # Append the generated data to the dataset
    data.append({
        'Mat ID': mat_id,
        'Trade': trade,
        'Material': material,
        'Currency': currency,
        'Price': price,
        'Unit': unit,
        'Vendor': vendor,
        'Phone': phone,
        'Email': email,
        'Location': location,
        'Price Date': current_date
    })

# Convert the dataset to a DataFrame using Pandas
df = pd.DataFrame(data)

# Save the DataFrame to an Excel file
output_path = 'construction_pricelist.xlsx'
df.to_excel(output_path, index=False)  # Save without the index column

# Notify the user of the successful save operation
print(f"Data saved to {output_path}")
