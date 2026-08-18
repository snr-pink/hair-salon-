"""Run with: python manage.py shell < seed_data.py
Populates sample services and stylists so the app has demo data.
"""
from scheduler.models import Service, Stylist

services = [
    ("Women's Haircut", "Wash, cut, and style tailored to you.", 45, 35.00),
    ("Men's Haircut", "Classic or modern cut, finished with a clean fade.", 30, 25.00),
    ("Full Color", "Single-process color from root to tip.", 90, 85.00),
    ("Highlights", "Foil highlights with a toner finish.", 120, 110.00),
    ("Blowout & Style", "Wash and professional blow-dry styling.", 40, 30.00),
]
for name, desc, duration, price in services:
    Service.objects.get_or_create(
        name=name, defaults={"description": desc, "duration_minutes": duration, "price": price}
    )

stylists = [
    ("Amara Chukwu", "Color specialist with 8 years behind the chair.", "09:00", "17:00"),
    ("Diego Fontaine", "Precision cuts and modern men's styling.", "10:00", "18:00"),
    ("Priya Nair", "Known for effortless blowouts and bridal styling.", "09:00", "16:00"),
]
for name, bio, start, end in stylists:
    Stylist.objects.get_or_create(
        name=name, defaults={"bio": bio, "work_start": start, "work_end": end}
    )

print(f"Services: {Service.objects.count()}, Stylists: {Stylist.objects.count()}")
