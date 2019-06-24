from tkinter import *
from tkinter import ttk
import cx_Oracle
from operator import itemgetter


def req_red_sites(pop):
    # Checks population to determine reduced monitoring sample sites required and verifies if there are enough listed
    # samples sites
    if pop > 100000:
        return 50
    elif pop > 10000:
        return 30
    elif pop > 3300:
        return 20
    elif pop > 500:
        return 10
    elif pop > 100:
        return 5
    else:
        return 5


def req_rt_sites(pop):
    # Checks population to determine routine monitoring sample sites required and verifies if there are enough listed
    # samples sites
    if pop > 100000:
        return 100
    elif pop > 10000:
        return 60
    elif pop > 3300:
        return 40
    elif pop > 500:
        return 20
    elif pop > 100:
        return 10
    else:
        return 5


def viewer(raw):
    if len(raw) == 7:
        raw = "TX" + str(raw)
    dsn_tns = cx_Oracle.makedsn('link', '1521', service_name='other_link')
    conn = cx_Oracle.connect('user', 'pw', dsn_tns, encoding='UTF-8', nencoding='UTF-8')
    c = conn.cursor()
    c.execute("SELECT NUMBER0, TINWSYS_IS_NUMBER, NAME, ACTIVITY_STATUS_CD, D_POPULATION_COUNT, PWS_ST_TYPE_CD "
              "FROM SDWIS2TX.TINWSYS "
              "WHERE NUMBER0 = '{}'".format(raw))
    val = c.fetchall()
    NUMBER0 = val[0][0]
    TINWSYS_IS_NUMBER = val[0][1]
    NAME = val[0][2]
    ACTIVITY_STATUS_CD = val[0][3]
    D_POPULATION_COUNT = val[0][4]
    PWS_ST_TYPE_CD = val[0][5]
    c.execute("SELECT TINWSF_IS_NUMBER "
              "FROM SDWIS2TX.TINWSF "
              "WHERE TINWSYS_IS_NUMBER = {} AND TYPE_CODE = 'DS'".format(TINWSYS_IS_NUMBER))
    tinwsf0is = c.fetchall()[0][0]  # DISTRIBUTION SYSTEM FACIILTY ID
    c.execute("SELECT TINWSF_IS_NUMBER, ST_ASGN_IDENT_CD "
              "FROM SDWIS2TX.TINWSF "
              "WHERE TINWSYS_IS_NUMBER = '{}' and ACTIVITY_STATUS_CD = 'A'".format(TINWSYS_IS_NUMBER))
    val = c.fetchall()  # ALL FACILITY IDS
    entry_points = 0
    for v in val:
        if v[1][:2] == 'EP':
            entry_points += 1
    inventory_info = ["PWS ID: ", NUMBER0, "\n",
                      "NAME: ", NAME, "\n",
                      "STATUS: ", ACTIVITY_STATUS_CD, "\n",
                      "POP: ", D_POPULATION_COUNT, "\n",
                      "Type: ", PWS_ST_TYPE_CD, "\n",
                      "TINWSYS #: ", TINWSYS_IS_NUMBER, "\n",
                      "DISTRIBUTION SYSTEM #: ", tinwsf0is, "\n",
                      "Entry Points: ", entry_points]
    c.execute("SELECT INDICATOR_NAME, INDICATOR_VALUE_CD, INDICATOR_DATE, INDICATOR_END_DATE "
              "FROM SDWIS2TX.TINWSIN "
              "WHERE TINWSYS_IS_NUMBER = {}".format(TINWSYS_IS_NUMBER))
    indicators = []
    for row in c.fetchall():
        try:
            indicator_date = row[2].date()
        except:
            indicator_date = ""
        finally:
            pass
        try:
            indicator_end_date = row[3].date()
        except:
            indicator_end_date = ""
        finally:
            pass
        if row[0] == "UNDM":
            indicators.append(["Indictors: ", row[0], "for", row[1], "on", indicator_date, "End date:", indicator_end_date])
            indicators.append("\n")
    c.execute("SELECT TYPE_CODE, ACTUAL_DATE, MEASURE "
              "FROM SDWIS2TX.TFRMEVNT "
              "WHERE TINWSYS_IS_NUMBER = {}".format(TINWSYS_IS_NUMBER))
    milestones = []
    for row in c.fetchall():
        actual_date = row[1].date()
        if row[0] == "CU90":
            if actual_date.year >= 2016:
                milestones.append(["Milestone: ", row[0], "on", actual_date, "-", row[2]])
        elif row[0] == "PB90":
            if actual_date.year >= 2016:
                milestones.append(["Milestone: ", row[0], "on", actual_date, "-", row[2]])
        else:
            if actual_date.year >= 2011:
                milestones.append(["Milestone: ", row[0], "on", actual_date, "-", row[2]])
        milestones.append("\n")
    viols = [22, 23, 24, 27, 28, 29, 30, 34, 35, 36, 87]
    types = [51, 52, 53, 56, 57, 58, 59, 63, 64, 65, 66]
    c.execute("SELECT TMNVIOL_IS_NUMBER, TMNVTYPE_IS_NUMBER, STATUS_TYPE_CODE, STATE_PRD_BEGIN_DT, STATE_PRD_END_DT "
              "FROM SDWIS2TX.TMNVIOL "
              "WHERE TINWSYS_IS_NUMBER = {}".format(TINWSYS_IS_NUMBER))
    violations = []
    closed = []
    for row in c.fetchall():
        if row[1] in viols:
            options = ["V", "P"]
            viol_status = row[2].strip()
            if viol_status in options:
                date = row[3]
                if date.year >= 2011:
                    tmnviol = row[0]
                    viol = types[viols.index(row[1])]
                    status = row[2]
                    begin = row[3].date()
                    try:
                        end = row[4].date()
                    except:
                        end = ""
                    finally:
                        pass
                    # print("Violation:", viol, status, "Begin:", begin, "End:", end)
                    results = []
                    c.execute("SELECT TENACTYP_IS_NUMBER "
                              "FROM SDWIS2TX.TMNVIEAA "
                              "WHERE TMNVIOL_IS_NUMBER = {}".format(tmnviol))
                    tenactyp_vals = [66, 72, 82]
                    for row in c.fetchall():
                        tenactyp = row[0]
                        results.append(tenactyp)
                    s1 = set(results)
                    s2 = set(tenactyp_vals)
                    if not s1.intersection(s2):
                        violations.append(["Violation:", viol, status, "Begin:", begin, "End:", end])
                        violations.append("\n")
                        for r in results:
                            c.execute("SELECT LOCATION_TYPE_CODE, FORMAL_TYPE_CODE, SUB_CATEGORY_CODE, NAME "
                                      "FROM SDWIS2TX.TENACTYP "
                                      "WHERE TENACTYP_IS_NUMBER = {}".format(r))
                            for row in c.fetchall():
                                violations.append(["           ", r, row[0], row[1], row[2], "-", row[3]])
                                violations.append("\n")
                        violations.append("\n")
                    else:
                        closed.append(["Closed Violation:", viol, status, "Begin:", begin, "End:", end])
                        closed.append("\n")
                        for r in results:
                            c.execute("SELECT LOCATION_TYPE_CODE, FORMAL_TYPE_CODE, SUB_CATEGORY_CODE, NAME "
                                      "FROM SDWIS2TX.TENACTYP "
                                      "WHERE TENACTYP_IS_NUMBER = {}".format(r))
                            for row in c.fetchall():
                                closed.append(["           ", r, row[0], row[1], row[2], "-", row[3]])
                                closed.append("\n")
                        closed.append("\n")
    compliance = ["Compliance Schedules:"]
    c.execute("SELECT TENSCHD_IS_NUMBER, STATUS_DATE, CLOSED_DATE, TYPE_CODE_CV "
              "FROM SDWIS2TX.TENSCHD "
              "WHERE TINWSYS_IS_NUMBER = '{}'".format(TINWSYS_IS_NUMBER))
    for row in c.fetchall():
        tenschd = row[0]
        close_date = row[2]
        type_code = row[3]
        if close_date is None:
            c.execute("SELECT DUE_DATE, TENACTIV_IS_NUMBER "
                      "FROM SDWIS2TX.TENSCHAT "
                      "WHERE TENSCHD_IS_NUMBER = '{}'".format(tenschd))
            for row in c.fetchall():
                due_date = row[0]
                tenactiv = row[1]
                c.execute("SELECT NAME "
                          "FROM SDWIS2TX.TENACTIV "
                          "WHERE TENACTIV_IS_NUMBER = '{}'".format(tenactiv))
                for row in c.fetchall():
                    description = row[0]
                    compliance.append([type_code, ": ", description, "by", due_date.date()])
                    compliance.append("\n")
    c.execute("SELECT DISTINCT TMNSSGRP.REASON_TEXT, TMNSSGRP.BEGIN_DATE, TMNSSGRP.END_DATE, TMNMNR.SAMPLE_TYPE_CODE, "
              "TMNMNR.SAMPLE_COUNT, TMNMNR.SMPL_CNT_UNIT_CD, TMNMNR.TMNVTYPE_IS_NUMBER "
              "FROM SDWIS2TX.TINWSYS "
              "LEFT JOIN SDWIS2TX.TMNSASCH "
              "ON TINWSYS.TINWSYS_IS_NUMBER = TMNSASCH.TINWSYS_IS_NUMBER "
              "LEFT JOIN SDWIS2TX.TMNSSGRP "
              "ON TMNSASCH.TMNSSGRP_IS_NUMBER = TMNSSGRP.TMNSSGRP_IS_NUMBER "
              "LEFT JOIN SDWIS2TX.TMNMNR "
              "ON TMNSSGRP.TMNMNR_IS_NUMBER = TMNMNR.TMNMNR_IS_NUMBER "
              "WHERE TINWSYS.D_POPULATION_COUNT > 0 "
              "AND TINWSYS.ACTIVITY_STATUS_CD = 'A' "
              # "AND TMNSASCH.END_DATE IS NULL "
              "AND TMNMNR.TSAANGRP_IS_NUMBER = 1"
              "AND TINWSYS.TINWSYS_IS_NUMBER = '{}'".format(TINWSYS_IS_NUMBER))
    scheds = []
    for row in c.fetchall():
        REASON_TEXT = row[0]
        REASON_TEXT = REASON_TEXT.replace('\r', "").replace('\n', '')
        BEGIN_DATE = row[1].date()
        year = BEGIN_DATE.year
        END_DATE = row[2]
        if END_DATE is None:
            END_DATE = "          "
        else:
            END_DATE = row[2].date()
        SAMPLE_TYPE_CODE = row[3]
        SAMPLE_COUNT = row[4]
        SMPL_CNT_UNIT_CD = row[5]
        TMNVTYPE_IS_NUMBER = row[6]
        schedule = str(year)[2:] + " " + SMPL_CNT_UNIT_CD
        lst = [schedule, REASON_TEXT, BEGIN_DATE, END_DATE, SAMPLE_TYPE_CODE, SAMPLE_COUNT, SMPL_CNT_UNIT_CD,
               TMNVTYPE_IS_NUMBER, "\n"]
        scheds.append(lst)
    # scheds = sorted(scheds, key=itemgetter(0))
    # print("HISTORICAL SCHEDULES:")
    # for s in scheds:
    #     if s[3] == "          ":
    #         print("\n")
    #         print("SCHEDULE: ", s[0])
    #         print("COMMENT: ", s[1])
    #         print("BEGIN DATE: ", s[2])
    #         print("SAMPLES REQUIRED: ", s[5])
    #         if s[6][:2] == "6M":
    #             print("SITES REQUIRED: ", req_rt_sites(D_POPULATION_COUNT))
    #         else:
    #             print("SITES REQUIRED: ", req_red_sites(D_POPULATION_COUNT))
    #     else:
    #         print(s[0], s[2], "-", s[3], s[4], "Samples:", s[5], s[6], s[7])
    #         print("       Comment:", s[1])
    # print("\n")
    summaries = []
    c.execute("SELECT TSASMPSM_IS_NUMBER, COLLECTION_STRT_DT, COLLECTION_END_DT, TSAANLYT_IS_NUMBER "
              "FROM SDWIS2TX.TSASMPSM "
              "WHERE TINWSYS_IS_NUMBER = {}".format(TINWSYS_IS_NUMBER))
    for row in c.fetchall():
        lst = [705, 803]
        TSAANLYT_IS_NUMBER = row[3]
        if TSAANLYT_IS_NUMBER in lst:
            TSASMPSM_IS_NUMBER = row[0]
            collection_start = row[1].date()
            collection_end = row[2].date()
            summary = [collection_start, collection_end]
            c.execute("SELECT NAME, CODE "
                      "FROM SDWIS2TX.TSAANLYT "
                      "WHERE TSAANLYT_IS_NUMBER = {}".format(TSAANLYT_IS_NUMBER))
            val = c.fetchall()[0]
            anlyt_name = val[0].strip()  # LEAD SUMMARY OR COPPER SUMMARY
            if len(anlyt_name) == 12:
                anlyt_name = "LEAD SUMMARY  "
            anlyt_code = val[1]  # PB90 OR CU90
            summary.insert(0, anlyt_name)
            summary.append(anlyt_code)
            c.execute("SELECT TSASSR_IS_NUMBER, TYPE_CODE, COUNT_QTY, MEASURE, UOM_CODE "
                      "FROM SDWIS2TX.TSASSR "
                      "WHERE TSASMPSM_IS_NUMBER = {}".format(TSASMPSM_IS_NUMBER))
            for row in c.fetchall():
                val = row
                TSASSR_IS_NUMBER = val[0]
                TYPE_CODE = val[1]  # 90TH OR 95TH PERCENTILE
                if TYPE_CODE is None:
                    TYPE_CODE = ""
                # COUNT_QTY = val[1]  # NUMBER OF SAMPLES
                MEASURE = val[3]  # ANALYTICAL RESULT
                if MEASURE is None:
                    MEASURE = ""
                MEASURE = '{:7}'.format(MEASURE)
                UOM_CODE = val[4]  # UNIT OF MEASUREMENT
                if UOM_CODE is None:
                    UOM_CODE = ""
                if TYPE_CODE == '90':
                    # summary[TSAANLYT_IS_NUMBER].append(COUNT_QTY)
                    summary.append(MEASURE)
                    summary.append(UOM_CODE.strip())
                    summaries.append(summary)
                    summaries.append("\n")
    # summaries = sorted(summaries, key=itemgetter(1))
    # print("SUMMARIES:")
    # for val in summaries:
    #     ale = "NO"
    #     if val[3] == "PB90":
    #         if float(val[4]) > 0.0154:
    #             ale = "YES"
    #     elif val[3] == "CU90":
    #         if float(val[4]) > 1.34:
    #             ale = "YES"
    #     print(val[0], val[1], "-", val[2], val[3], "Result:", val[4], val[5], "ALE:", ale)
    # print("\n")
    c.execute("SELECT IDENTIFICATION_CD, DESCRIPTION_TEXT, LD_CP_TIER_LEV_TXT, LD_CP_TIER_TYP_TXT, "
              "D_LAST_UPDT_TS, ACTIVITY_STATUS_CD "
              "FROM SDWIS2TX.TSASMPPT "
              "WHERE TINWSF0IS_NUMBER = '{}'".format(tinwsf0is))
    val = c.fetchall()
    sites = []
    for v in val:
        if v[0][:3] == 'LCR':
            _id = v[0]
            loc = v[1]
            loc = '{:30}'.format(loc)
            tier = v[2]
            material = v[3]
            update = v[4]
            activity = v[5]
            lst = [_id, loc, tier, material, update, activity]
            sites.append(lst)
            sites.append("\n")
    # sites = sorted(sites, key=itemgetter(0))
    c.close()
    conn.close()
    return [inventory_info, "\n", indicators, milestones, closed, violations, compliance, scheds, summaries, sites]


def calculate(*args):
    try:
        value = pws_id.get()
        lst = viewer(value)
        info = []
        for l in lst:
            info.append(l)
        inventory.set(info)
    except ValueError:
        pass


root = Tk()
root.title("Lead and Copper Rule Viewing Platform")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
# scrollbar = Scrollbar(root)
# scrollbar.pack(side=RIGHT, fill=Y)

pws_id = StringVar()
inventory = StringVar()


pws_entry = ttk.Entry(mainframe, width=8, textvariable=pws_id)
pws_entry.grid(column=2, row=1, sticky=(W, E))

ttk.Label(mainframe, textvariable=inventory, wraplength=850, justify='left').grid(column=2, row=2, sticky=(W, E))
ttk.Button(mainframe, text="Get View", command=calculate).grid(column=3, row=3, sticky=W)

ttk.Label(mainframe, text="PWS ID").grid(column=3, row=1, sticky=W)
# # ttk.Label(mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
# ttk.Label(mainframe, text="Information").grid(column=3, row=2, sticky=W)

for child in mainframe.winfo_children(): child.grid_configure(padx=5, pady=5)

pws_entry.focus()
root.bind('<Return>', calculate)

root.mainloop()
