import time

import app as a
import server as srv


print("""----- SERVER START -----""")
try:
    srv.start_server()
    print("""----- SERVER RUN SUCCESFUL -----""")
except:
    print("---- SERVER ERROR ----")

print("""----- FLASK RUN -----""")
try:
    a.run_flask()
    print("""----- PAGE RUN SUCCESFUL -----""")
except:
    print("---- FLASK ERROR ----")

time.sleep(1000)








