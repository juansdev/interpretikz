from datetime import datetime   
import pytz

utc = datetime.utcnow().replace(tzinfo=pytz.utc)
utc = datetime.strftime(utc,"%Y-%m-%d %H:%M:%S")

print(utc)