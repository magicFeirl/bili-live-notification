import dataset
from dataset import Table


db = dataset.connect("sqlite:///app.db")


streamer_table: Table = db["streamer"]
user_table: Table = db["user"]
