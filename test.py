# import requests
# uri = 'https://www.google.com/maps/place/'
# url = uri+"New York"
# ret = requests.get(url).success_url()
# print(ret)

import sqlite3

con = sqlite3.connect("db.sqlite3")
cur = con.cursor()
cur.executescript("""DELETE FROM pages_user where id=25;
                  DELETE FROM pages_profile;
                  DELETE FROM pages_userinfo where id=7;
                  """)


# cur.execute("""Select * FROM company_jobcategory""")
# print(cur.fetchall())
# con.commit()
# con.close()

# cur.execute(""" UPDATE pages_userinfo SET purchased_package_id=5 WHERE id=4""")
# con.commit()
# con.close()