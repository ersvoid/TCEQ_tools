import sqlite3


# VIEWING SQLITE DATA
def view(query):
    for row in query.fetchall():
        print(row)


def write_sample_sites(db, _id):
    conn = sqlite3.connect('{}.db'.format(db))
    c = conn.cursor()
    c.execute("SELECT NAME "
              "FROM TINWSYS "
              "WHERE NUMBER0 = '{}'".format(_id))
    name = c.fetchone()[0]
    c.execute("SELECT TINWSYS_IS_NUMBER "
              "FROM TINWSYS "
              "WHERE NUMBER0 = '{}'".format(_id))
    tinwsys = c.fetchone()[0]
    c.execute("SELECT TINWSF_IS_NUMBER "
              "FROM TINWSF "
              "WHERE TINWSYS_IS_NUMBER = '{}' AND NAME = 'DISTRIBUTION SYSTEM'".format(tinwsys))
    tinwsf0is = c.fetchone()[0]
    c.execute("SELECT * "
              "FROM TSASMPPT "
              "WHERE TINWSF0IS_NUMBER = '{}'".format(tinwsf0is))

    d = {}
    for row in c.fetchall():
        d[row[0]] = row
        print(row)

    def write(dct, file="sample.txt"):
        f = open(file, 'w')
        for key in dct:
            val = dct[key]
            if val[1][:3] == "LCR":
                TSASMPPT = str(val[0])
                IDENTIFICATION_CD = val[1]
                DESCRIPTION_TEXT = val[2]
                if val[3] == "":
                    LD_CP_TIER_LEV_TXT = "None"
                else:
                    LD_CP_TIER_LEV_TXT = val[3]
                if val[4] == "":
                    LD_CP_TIER_TYP_TXT = "None"
                else:
                    LD_CP_TIER_TYP_TXT = val[4]
                ACTIVITY_STATUS_CD = val[5]
                f.write(TSASMPPT + " - " + IDENTIFICATION_CD + " - " + DESCRIPTION_TEXT + " - " + LD_CP_TIER_LEV_TXT + " - " +
                    LD_CP_TIER_TYP_TXT + " - " + ACTIVITY_STATUS_CD + "\n")
        f.write("\n")
        f.write("\n")
        f.write("DATABASE ID - SAMPLE SITE ID - LOCATION - TIER - MATERIAL - ACTIVITY STATUS")
        f.close()

    file_name = "{}_sample_sites.txt".format(name)
    write(d, file=file_name)

    c.close()
    conn.close()
