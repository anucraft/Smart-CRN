from . import analytics, auth, customers, orders, products, settings, woocommerce


def register_blueprints(app):
    for module in (auth, customers, orders, products, analytics, woocommerce, settings):
        app.register_blueprint(module.bp)
