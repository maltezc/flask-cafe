from models import City

def get_choices_vocab():
    """Gets all cities in db"""
    return [(city.code, city.name) for city in City.query.all()]