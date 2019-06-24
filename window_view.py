from tkinter import *
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
    dsn_tns = cx_Oracle.makedsn('aed2-scan.tceq.texas.gov', '1521', service_name='PRDEXA.TCEQ.TEXAS.GOV')
    conn = cx_Oracle.connect('ESTINSON', 'Sartre05', dsn_tns, encoding='UTF-8', nencoding='UTF-8')
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
    inventory_info = [NUMBER0, NAME, ACTIVITY_STATUS_CD, D_POPULATION_COUNT, PWS_ST_TYPE_CD, TINWSYS_IS_NUMBER,
                      tinwsf0is, entry_points]
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
            indicators.append([1, row[0], row[1], indicator_date, indicator_end_date])
    if not indicators:
        indicators.append([0, 0, 0, 0, 0])
    c.execute("SELECT TYPE_CODE, ACTUAL_DATE, MEASURE "
              "FROM SDWIS2TX.TFRMEVNT "
              "WHERE TINWSYS_IS_NUMBER = {}".format(TINWSYS_IS_NUMBER))
    milestones = []
    for row in c.fetchall():
        actual_date = row[1].date()
        if row[0] == "CU90":
            if actual_date.year >= 2016:
                milestones.append([row[0], actual_date, row[2]])
        elif row[0] == "PB90":
            if actual_date.year >= 2016:
                milestones.append([row[0], actual_date, row[2]])
        else:
            if actual_date.year >= 2011:
                milestones.append([row[0], actual_date, row[2]])
    viols = [22, 23, 24, 27, 28, 29, 30, 34, 35, 36, 87]
    types = [51, 52, 53, 56, 57, 58, 59, 63, 64, 65, 66]
    c.execute("SELECT TMNVIOL_IS_NUMBER, TMNVTYPE_IS_NUMBER, STATUS_TYPE_CODE, STATE_PRD_BEGIN_DT, STATE_PRD_END_DT "
              "FROM SDWIS2TX.TMNVIOL "
              "WHERE TINWSYS_IS_NUMBER = {}".format(TINWSYS_IS_NUMBER))
    violations = {}
    closed = {}
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
                        v_inv = [viol, status, begin, end]
                        v = []
                        for r in results:
                            c.execute("SELECT LOCATION_TYPE_CODE, FORMAL_TYPE_CODE, SUB_CATEGORY_CODE, NAME "
                                      "FROM SDWIS2TX.TENACTYP "
                                      "WHERE TENACTYP_IS_NUMBER = {}".format(r))
                            for row in c.fetchall():
                                v.append([r, row[0], row[1], row[2], row[3]])
                        violations[tmnviol] = [v_inv, v]
                    else:
                        clo_inv = [viol, status, begin, end]
                        clo = []
                        for r in results:
                            c.execute("SELECT LOCATION_TYPE_CODE, FORMAL_TYPE_CODE, SUB_CATEGORY_CODE, NAME "
                                      "FROM SDWIS2TX.TENACTYP "
                                      "WHERE TENACTYP_IS_NUMBER = {}".format(r))
                            for row in c.fetchall():
                                clo.append([r, row[0], row[1], row[2], row[3]])
                        closed[tmnviol] = [clo_inv, clo]
    compliance = []
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
                    compliance.append([type_code, description, due_date.date()])
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
               TMNVTYPE_IS_NUMBER]
        scheds.append(lst)
    scheds = sorted(scheds, key=itemgetter(0))
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
                anlyt_name = "LEAD SUMMARY     "
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
    summaries = sorted(summaries, key=itemgetter(1))
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
    sites = sorted(sites, key=itemgetter(0))
    c.close()
    conn.close()
    return [inventory_info, indicators, milestones, closed, violations, compliance, scheds, summaries, sites]


class Viewer(Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()

        Frame.__init__(self, root)
        self.canvas = Canvas(root, borderwidth=0, background="#ffffff")
        self.frame = Frame(self.canvas, background="#ffffff")
        self.vsb = Scrollbar(root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)

        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((4, 4), window=self.frame, anchor="nw",
                                  tags="self.frame")

        self.frame.bind("<Configure>", self.onFrameConfigure)

        self.create_widgets()

    def onFrameConfigure(self, event):
        # Reset the scroll region to encompass the inner frame
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def create_widgets(self):
        self.info = StringVar()
        self.indicators = StringVar()
        self.milestones = StringVar()
        self.closed = StringVar()
        self.viols = StringVar()
        self.comp = StringVar()
        self.scheds = StringVar()
        self.sums = StringVar()
        self.sites = StringVar()
        self.pws_entry = Entry(self.frame)
        self.pws_entry.pack()
        self.pws_enter = Button(self.frame, text="ENTER", command=self.callback)
        self.pws_enter.pack()
        self.pws_info = Label(self.frame, textvariable=self.info, font="Arial 10", justify="left")
        self.pws_info.pack()

        self.quit = Button(self.frame, text="QUIT", fg="red", command=self.master.destroy)
        self.quit.pack()

    def callback(self):
        # [inventory_info, indicators, milestones, closed, violations, compliance, scheds, summaries, sites]
        #
        # NUMBER0, NAME, ACTIVITY_STATUS_CD, D_POPULATION_COUNT, PWS_ST_TYPE_CD, TINWSYS_IS_NUMBER,
        #                       tinwsf0is, entry_points
        pws_id = self.pws_entry.get()
        info = viewer(pws_id)
        inv = info[0]
        ind = info[1][0]
        if ind[0] == 0:
            ind[1] = "NA"
            ind[2] = "NA"
            ind[3] = "NA"
            ind[4] = "NA"
        miles = info[2]
        milestone_string = ""
        if miles:
            for stone in miles:
                milestone_string = milestone_string + """
                {} {} {}""".format(stone[0], stone[1], stone[2])
        if not miles:
            milestone_string = "No Milestones"
        closed = info[3]
        closed_string = ""
        if closed:
            for v in closed:
                viol = closed[v]
                desc = viol[0]
                closed_string = closed_string + """
                Vio: {} {} {} - {}""".format(desc[0], desc[1], desc[2], desc[3])
                for x in viol[1]:
                    closed_string = closed_string + """
                         {} {} {} {} {}""".format(x[0], x[1], x[2], x[3], x[4])
        if not closed:
            closed_string = "No Closed Violations"
        viols = info[4]
        viols_string = ""
        if viols:
            for v in viols:
                viol = viols[v]
                desc = viol[0]
                viols_string = viols_string + """
                Vio: {} {} {} - {}""".format(desc[0], desc[1], desc[2], desc[3])
                for x in viol[1]:
                    viols_string = viols_string + """
                         {} {} {} {} {}""".format(x[0], x[1], x[2], x[3], x[4])
        if not viols:
            viols_string = "No Open Violations"
        comp = info[5]
        comp_string = ""
        if comp:
            for c in comp:
                comp_string = comp_string + """
                {} {} {}""".format(c[0], c[1], c[2])
        if not comp:
            comp_string = "No Compliance Schedules"
        sched = info[6]
        sched_string = ""
        hist_string = ""
        if sched:
            for c in sched:
                if c[3] == "          ":
                    if len(c[1]) > 100:
                        comment = """{}
                        {}""".format(c[1][:50], c[1][50:])
                        sched_string = """
                        SCHEDULE: {}
                        COMMENT: {}
                        BEGIN DATE: {}
                        SAMPLES REQUIRED: {}""".format(c[0], comment, c[2], c[5])
                    else:
                        sched_string = """
                        SCHEDULE: {}
                        COMMENT: {}
                        BEGIN DATE: {}
                        SAMPLES REQUIRED: {}""".format(c[0], comment, c[2], c[5])
                else:
                    if len(c[1]) > 100:
                        comment = """{}
                        {}""".format(c[1][:50], c[1][50:])
                        hist_string = hist_string + """
                        {}: {} - {}
                        Comment: {}""".format(c[0], c[2], c[3], c[1])
                    else:
                        hist_string = hist_string + """
                        {}: {} - {}
                        Comment: {}""".format(c[0], c[2], c[3], c[1])
        if not sched:
            sched_string = "No Schedules"
            hist_string = "No Schedules"
        summs = info[7]
        sum_string = ""
        if summs:
            for c in summs:
                ale = "NO"
                if c[3] == "PB90":
                    if float(c[4]) > 0.0154:
                        ale = "YES"
                elif c[3] == "CU90":
                    if float(c[4]) > 1.34:
                        ale = "YES"
                sum_string = sum_string + """
                {} {} - {} {} {} {} ALE: {}""".format(c[0], c[1], c[2], c[3], c[4], c[5], ale)
        if not summs:
            sum_string = "No Summaries"
        sites = info[8]
        sites_string = ""
        if sites:
            for c in sites:
                sites_string = sites_string + """
                {} {} - Tier: {} - {} Update: {} - {}""".format(c[0][:6], c[1], c[2], c[3], c[4].date(), c[5])
        if not sites:
            sites_string = "No Sample Sites"
        text_return = """
        PWS ID: {}
        PWS NAME: {}
        ACTIVITY: {}
        POPULATION: {}
        SYSTEM: {}
        TINWSYS #: {}
        DISTRIBUTION #: {}
        ENTRY POINTS: {} \n
        INDICATOR: {}
        TYPE: {}
        BEGIN: {}
        END: {} \n
        MILESTONES-
        {} \n
        CLOSED VIOLATIONS-
        {} \n
        OPEN VIOLATIONS-
        {} \n
        COMPLIANCE SCHEDULES-
        {} \n
        CURRENT SCHEDULE-
        {} \n
        HISTORICAL SCHEDULES-
        {} \n
        SUMMARIES-
        {} \n
        SAMPLE SITES-
        {}
        """.format(inv[0], inv[1], inv[2], inv[3], inv[4], inv[5], inv[6], inv[7], ind[1], ind[2], ind[3], ind[4],
                   milestone_string, closed_string, viols_string, comp_string, sched_string, hist_string, sum_string,
                   sites_string)
        self.info.set(text_return)
        return self.info


root = Tk()
app = Viewer(master=root)
app.mainloop()
