"""Custom `flask` commands: init-db, create-admin, seed-demo."""
import random
from datetime import timedelta

import click

from .extensions import db
from .models import Activity, Admin, Customer, CustomerNote, Order, OrderItem, Product
from .utils.time import utcnow


def register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Create all tables (safe to run repeatedly)."""
        db.create_all()
        click.echo("Database ready.")

    @app.cli.command("create-admin")
    @click.option("--email", prompt=True)
    @click.option("--name", prompt=True, default="Admin")
    @click.password_option()
    def create_admin(email, name, password):
        """Create (or reset the password of) an admin user."""
        email = email.strip().lower()
        admin = Admin.query.filter_by(email=email).first() or Admin(email=email)
        admin.name = name
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Admin {email} saved.")

    @app.cli.command("seed-demo")
    @click.option("--reset", is_flag=True, help="Delete existing customers/orders/products first.")
    def seed_demo(reset):
        """Fill the DB with realistic fake store data so the UI can be demoed without WooCommerce."""
        if reset:
            for model in (Activity, CustomerNote, OrderItem, Order, Product, Customer):
                db.session.query(model).delete()
            db.session.commit()
        elif Customer.query.count() or Order.query.count():
            raise click.ClickException("Database already has data. Re-run with --reset to replace it.")
        _seed(random.Random(42))
        click.echo("Demo data created.")


FIRST = ["Aarav", "Maya", "Liam", "Sofia", "Noah", "Isha", "Ethan", "Zara", "Mateo", "Priya", "Lucas", "Nina",
         "Omar", "Elena", "Rohan", "Chloe", "Diego", "Anika", "Jack", "Leila"]
LAST = ["Sharma", "Fernandes", "Smith", "Rossi", "Khan", "Patel", "Costa", "Nair", "Brown", "Silva"]
CITIES = [("Panaji", "GA", "IN"), ("Mumbai", "MH", "IN"), ("Austin", "TX", "US"), ("Lisbon", "", "PT"), ("Leeds", "", "GB")]
CATALOG = [("Cold-brew concentrate", 18), ("Ceramic pour-over set", 64), ("Single-origin beans 1kg", 32),
           ("Burr grinder", 89), ("Travel tumbler", 27), ("Gift subscription", 120)]
STATUSES = ["completed"] * 14 + ["processing"] * 3 + ["pending"] * 2 + ["on-hold", "cancelled", "refunded", "failed"]


def _seed(rng):
    now = utcnow()
    products = []
    for i, (name, price) in enumerate(CATALOG, start=1):
        p = Product(woo_id=9000 + i, name=name, sku=f"SKU-{i:03d}", price=price, stock_quantity=rng.randint(0, 80),
                    stock_status="instock", categories=["Coffee" if i < 4 else "Gear"])
        db.session.add(p)
        products.append(p)
    db.session.flush()

    customers = []
    for i in range(40):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        city, state, country = rng.choice(CITIES)
        created = now - timedelta(days=rng.randint(5, 360))
        c = Customer(woo_id=7000 + i, first_name=first, last_name=last, created_at=created,
                     email=f"{first}.{last}{i}@example.com".lower(), phone=f"+1555010{i:02d}",
                     city=city, state=state, country=country)
        db.session.add(c)
        customers.append(c)
        db.session.flush()
        db.session.add(Activity(type="customer.created", description=f"{c.full_name} joined",
                                customer_id=c.id, created_at=created))

    number = 1000
    for c in customers:
        weights = rng.choice([0, 1, 1, 2, 3, 5])  # some customers never order
        for _ in range(weights):
            number += 1
            placed = max(c.created_at, now - timedelta(days=rng.randint(0, 350)))
            status = rng.choice(STATUSES)
            order = Order(woo_id=number, number=str(number), customer=c, status=status, currency="USD",
                          date_created=placed, payment_method="stripe", payment_method_title="Card",
                          date_paid=placed if status in ("completed", "processing", "refunded") else None,
                          date_completed=placed + timedelta(days=3) if status == "completed" else None,
                          billing={"first_name": c.first_name, "last_name": c.last_name, "email": c.email,
                                   "city": c.city, "country": c.country},
                          shipping={"first_name": c.first_name, "last_name": c.last_name, "address_1": "12 Harbour Rd",
                                    "city": c.city, "country": c.country})
            total = 0
            for product in rng.sample(products, rng.randint(1, 3)):
                qty = rng.randint(1, 3)
                line_total = float(product.price) * qty
                total += line_total
                order.items.append(OrderItem(product=product, woo_product_id=product.woo_id, name=product.name,
                                             sku=product.sku, quantity=qty, price=product.price, total=line_total))
            order.total = total
            db.session.add(order)
            db.session.flush()
            db.session.add(Activity(type="order.created", description=f"Order #{order.number} placed · USD {total:.2f}",
                                    customer_id=c.id, order_id=order.id, created_at=placed))
    db.session.commit()
