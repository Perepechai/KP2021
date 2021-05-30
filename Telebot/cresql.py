import csv
import mysql.connector
import datetime
import schedule
import time
import update
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="1234",
  database="sabs"
)
def job():
    endtime = "05:00"
    n =0
    update.up()
    with open("Table11.csv") as r_file:
        file_reader = csv.reader(r_file, delimiter = ";")

        mycursor = mydb.cursor()
        sql = "delete from Item"
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for p in file_reader:
            if n > 0:
                sql = "INSERT Item (identifier, addressAdminUnit, addressPostName, addressThoroughfare," + \
                    " addressLocatorDesignator, addressflat, stateofsubsidy, SubsidyamountpermonthcommunalservicesUAH," + \
                    " SubsidyamountperyearliquefiedgasUAH, Locationofrecipientspersonalfile, Dateoffirstgrantappointment," + \
                    " Entryintoforceoflastsubsidy, Endoflastsubsidyappointment, TheamountofsubsidyinthenonheatingperiodUAH," + \
                    " TheamountofsubsidyintheheatingperiodUAH) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                val = (p[0], p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8], p[9], p[10], p[11], p[12], p[13], p[14])
                mycursor.execute(sql, val)
                mydb.commit()
                if time.strftime("%H:%M") >= endtime:
                    break
                # x = datetime.datetime.now()
                # print(x)
            n = n + 1

        print(n)
