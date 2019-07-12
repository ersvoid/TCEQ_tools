from tkinter import *
import tkinter.scrolledtext
import cx_Oracle
from operator import itemgetter
import datetime
from math import floor
import mailmerge
import xlsxwriter
from sample_sites_word_doc import export_to_word

# IDEAS OF FEATURES TO ADD

# COMBINE THE SUMMARIES WITH SCHEDULES

# POSSIBLY FILTER COMPLIANCE SCHEDULES FOR LCR
# FIND ACTUAL COMP SCHEDULES INSTEAD OF ACTIONS REQUIRED TO CLOSE

# SPLIT INFORMATION INTO SEPARATE TEXT BOXES WITH LABELFRAMES

# CHECK INDICATOR SQL (WHAT IF OLD CLOSED INDICATOR AND NEW OPEN INDICATOR?)

# EDIT/REVIEW SAMPLE SITE DOCUMENT -- CHANGE ALL FONTS TO CONSOLAS >=12PT BLACK

# ADD PAGES - LOGIN, PWS INFO, FIND ALES, OPEN MONITORING SCHEDULES, OPEN COMPLIANCE, OPEN VIOLATIONS


# USEFUL VARIABLES
pale_green3 = "PaleGreen3"
pale_green4 = "PaleGreen4"
olive = "DarkOliveGreen3"
purple = "MediumPurple3"
white = "#FFFFFF"
antique = "AntiqueWhite3"
bisque = "bisque3"
light = "LightGoldenrod3"
khaki = "khaki3"

color_main = olive
# color_accent = purple
color_text = antique


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


def viewer(user, pw, raw):
    if len(raw) == 7:
        raw = "TX" + str(raw)
    if len(raw) == 9:
        if raw[:2] == 'tx':
            raw = "TX" + raw[2:]
    dsn_tns = cx_Oracle.makedsn('aed2-scan.tceq.texas.gov', '1521', service_name='PRDEXA.TCEQ.TEXAS.GOV')
    conn = cx_Oracle.connect(user, pw, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
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
            milestones.append([row[0], actual_date, row[2]])
        elif row[0] == "PB90":
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
                    results_and_dates = []
                    c.execute("SELECT D_LAST_UPDT_TS, TENACTYP_IS_NUMBER "
                              "FROM SDWIS2TX.TMNVIEAA "
                              "WHERE TMNVIOL_IS_NUMBER = {}".format(tmnviol))
                    tenactyp_vals = [66, 72, 82, 86]
                    for row in c.fetchall():
                        last_update = row[0].date()
                        tenactyp = row[1]
                        results.append(tenactyp)
                        results_and_dates.append([last_update, tenactyp])
                    s1 = set(results)
                    s2 = set(tenactyp_vals)
                    if not s1.intersection(s2):
                        v_inv = [viol, status, begin, end]
                        v = []
                        for r in results_and_dates:
                            c.execute("SELECT LOCATION_TYPE_CODE, FORMAL_TYPE_CODE, SUB_CATEGORY_CODE, NAME "
                                      "FROM SDWIS2TX.TENACTYP "
                                      "WHERE TENACTYP_IS_NUMBER = {}".format(r[1]))
                            for row in c.fetchall():
                                v.append([r[1], row[0], row[1], row[2], row[3], r[0]])
                        violations[tmnviol] = [v_inv, v]
                    else:
                        clo_inv = [viol, status, begin, end]
                        clo = []
                        for r in results_and_dates:
                            c.execute("SELECT LOCATION_TYPE_CODE, FORMAL_TYPE_CODE, SUB_CATEGORY_CODE, NAME "
                                      "FROM SDWIS2TX.TENACTYP "
                                      "WHERE TENACTYP_IS_NUMBER = {}".format(r[1]))
                            for row in c.fetchall():
                                clo.append([r[1], row[0], row[1], row[2], row[3], r[0]])
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
                try:
                    due_date = due_date.date()
                except:
                    due_date = "NO DATE FOUND"
                finally:
                    pass
                tenactiv = row[1]
                c.execute("SELECT NAME "
                          "FROM SDWIS2TX.TENACTIV "
                          "WHERE TENACTIV_IS_NUMBER = '{}'".format(tenactiv))
                for row in c.fetchall():
                    description = row[0]
                    compliance.append([type_code, description, due_date])
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
    summaries = []
    c.execute("SELECT TSASMPSM_IS_NUMBER, COLLECTION_STRT_DT, COLLECTION_END_DT, TSAANLYT_IS_NUMBER "
              "FROM SDWIS2TX.TSASMPSM "
              "WHERE TINWSYS_IS_NUMBER = {}".format(TINWSYS_IS_NUMBER))
    for row in c.fetchall():
        lst = [705, 803]
        TSAANLYT_IS_NUMBER = row[3]
        if TSAANLYT_IS_NUMBER in lst:
            TSASMPSM_IS_NUMBER = row[0]
            try:
                collection_start = row[1].date()
            except:
                collection_start = datetime.date(1900, 1, 1)
            try:
                collection_end = row[1].date()
            except:
                collection_end = "NO DATE FOUND"
            summary = [collection_start, collection_end]
            c.execute("SELECT NAME, CODE "
                      "FROM SDWIS2TX.TSAANLYT "
                      "WHERE TSAANLYT_IS_NUMBER = {}".format(TSAANLYT_IS_NUMBER))
            val = c.fetchall()[0]
            anlyt_name = val[0].strip()  # LEAD SUMMARY OR COPPER SUMMARY
            anlyt_name = "{:14}".format(anlyt_name)
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
                    summary.append(MEASURE)
                    summary.append(UOM_CODE.strip())
                    summaries.append(summary)
    # summaries = sorted(summaries, key=itemgetter(1))
    periods = {}
    sum_keys = []
    holder = []
    for summ in summaries:
        date_key = str(summ[1].year) + "-" + str(summ[1].day)
        sum_keys.append(date_key)
    periods = periods.fromkeys(sum_keys)
    for key in periods:
        periods[key] = []
    for summ in summaries:
        date_key = str(summ[1].year) + "-" + str(summ[1].day)
        periods[date_key].append(summ)
    for key in periods:
        unsorted_period_sums = periods[key]
        periods[key] = sorted(unsorted_period_sums, key=itemgetter(0))
    for key in periods:
        val = periods[key]
        lst = [key, val]
        holder.append(lst)
    summaries = sorted(holder, key=itemgetter(0))
    c.execute("SELECT IDENTIFICATION_CD, DESCRIPTION_TEXT, LD_CP_TIER_LEV_TXT, LD_CP_TIER_TYP_TXT, "
              "D_LAST_UPDT_TS, D_USERID_CODE, ACTIVITY_STATUS_CD "
              "FROM SDWIS2TX.TSASMPPT "
              "WHERE TINWSF0IS_NUMBER = '{}'".format(tinwsf0is))
    val = c.fetchall()
    sites = []
    loc_len = []
    for v in val:
        if v[0][:3] == 'LCR':
            _id = v[0]
            loc = v[1]
            loc_len.append(len(loc))

            # loc = '{:30}'.format(loc)
            tier = v[2]
            material = v[3]
            update = v[4]
            user_id = v[5]
            activity = v[6]
            lst = [_id, loc, tier, material, update, user_id, activity]
            sites.append(lst)
    sites = sorted(sites, key=itemgetter(0))
    space = max(loc_len) + 2
    space = '{:' + str(space) + '}'
    for site in sites:
        site[1] = space.format(site[1])
    c.close()
    conn.close()
    return [inventory_info, indicators, milestones, closed, violations, compliance, scheds, summaries, sites]


class LoginFrame(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.config(bg=color_main, bd=10)
        self.username = StringVar()
        self.password = StringVar()
        self.connection = StringVar()
        self.connection.set("")

        self.top_frame = Frame(self, bg=color_main)
        self.top_frame.pack(side="top")

        self.label_username = LabelFrame(self.top_frame, bg=color_main, text="Username", padx=5, pady=5)
        self.label_username.pack(padx=10, pady=10, side='left')
        self.label_password = LabelFrame(self.top_frame, bg=color_main, text="Password", padx=5, pady=5)
        self.label_password.pack(padx=10, pady=10, side='left')

        self.entry_username = Entry(self.label_username)
        self.entry_password = Entry(self.label_password, show="*")
        self.entry_username.pack()
        self.entry_password.pack()

        self.bottom_frame = Frame(self, bg=color_main)
        self.bottom_frame.pack()

        self.label_connection = Label(self.bottom_frame, bg=color_main, textvariable=self.connection)
        self.label_connection.pack(padx=10, pady=10, side='left')

        self.logbtn = Button(self.bottom_frame, text="LOGIN", command=self._login_btn_clicked)
        self.logbtn.pack(padx=10, pady=10, side="left")

        self.pack()

    def _login_btn_clicked(self, event=None):
        self.username = self.entry_username.get()
        self.password = self.entry_password.get()

        dsn_tns = cx_Oracle.makedsn('aed2-scan.tceq.texas.gov', '1521', service_name='PRDEXA.TCEQ.TEXAS.GOV')
        try:
            conn = cx_Oracle.connect(self.username, self.password, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
            conn.close()
            self.connection.set("CONNECTION ESTABLISHED")
            self.entry_username.delete(0, END)
            self.entry_password.delete(0, END)
        except:
            self.connection.set("INCORRECT LOGIN")
        finally:
            pass
        return self.username, self.password, self.connection


class Viewer(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.config(bg=color_main)
        master.title("WATER You Looking For?")
        self.pack()

        self.user = StringVar()
        self.password = StringVar()

        Frame.__init__(self, master)
        self.config(bg=color_main)
        self.login_frame = LoginFrame(master)

        self.canvas = Canvas(master, background=color_main)
        self.canvas.pack(fill='both', expand=1)

        self.frame = Frame(self.canvas, background=color_main)

        self.canvas_frame = self.canvas.create_window((0, 0), window=self.frame, anchor='nw', tags="self.frame")

        # self.vsb = Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        # self.vsb.pack(side="right", fill='y')
        #
        # self.canvas.configure(yscrollcommand=self.vsb.set)

        # self.frame.bind("<Configure>", self.onFrameConfigure)
        self.canvas.bind('<Configure>', self.FrameWidth)

        # self.master.bind_all("<MouseWheel>", self._on_mousewheel)
        self.create_widgets()

        # self.bind_class("Button", "<Return>", self.wrapper)
        self.bind_all("<Return>", self.callback)

    def wrapper(self, e):
        e.widget.invoke()

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(floor(-1*(event.delta/120)), "units")

    def FrameWidth(self, event):
        canvas_width = event.width
        canvas_height = event.height
        self.canvas.itemconfig(self.canvas_frame, width=canvas_width, height=canvas_height)

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
        self.word_notification = StringVar()
        self.word_notification.set("")

        self.pws_frame = LabelFrame(self.frame, text="Enter PWS ID:", bg=color_main)
        self.pws_frame.pack()
        self.pws_entry = Entry(self.pws_frame)
        self.pws_entry.pack(padx=10, pady=10, side="left")
        self.pws_enter = Button(self.pws_frame, text="DISPLAY", command=self.callback)
        # self.pws_enter.bind("<Return>", self.callback)
        self.pws_enter.pack(padx=10, pady=10, side="left")

        Label(self.frame, bg=color_main).pack()

        self.pws_info = tkinter.scrolledtext.Text(self.frame, bg=color_text, font="Consolas 12")
        self.pws_info.pack(fill="both", expand=1)

        Label(self.frame, bg=color_main).pack(expand=1, side="left")
        self.sample_sites_word = Button(self.frame, text="EXPORT TO WORD", command=self.word_export).pack(side="left")
        self.word_label = Label(self.frame, bg=color_main, textvariable=self.word_notification)
        self.word_label.pack(expand=1, side="left")
        self.sample_sites_excel = Button(self.frame, text="EXPORT TO EXCEL", command=self.excel_export).pack(side="left")
        Label(self.frame, bg=color_main).pack(expand=1, side="left")

        Label(self.frame, bg=color_main).pack()
        Label(self.frame, bg=color_main).pack()
        Label(self.frame, bg=color_main).pack()

    def word_export(self):
        dsn_tns = cx_Oracle.makedsn('aed2-scan.tceq.texas.gov', '1521', service_name='PRDEXA.TCEQ.TEXAS.GOV')
        conn = cx_Oracle.connect(self.login_frame.username, self.login_frame.password, dsn_tns, encoding='UTF-8',
                                 nencoding='UTF-8')
        pws_id = self.pws_entry.get()
        if len(pws_id) == 7:
            pws_id = "TX" + str(pws_id)
        c = conn.cursor()
        c.execute("SELECT TINWSYS_IS_NUMBER, NAME "
                  "FROM SDWIS2TX.TINWSYS "
                  "WHERE NUMBER0 = '{}'".format(pws_id))
        val = c.fetchall()
        print(val)
        tinwsys = val[0][0]
        name = val[0][1]
        c.execute("SELECT TINWSF_IS_NUMBER "
                  "FROM SDWIS2TX.TINWSF "
                  "WHERE TINWSYS_IS_NUMBER = {} AND TYPE_CODE = 'DS'".format(tinwsys))
        tinwsf0is = c.fetchone()[0]
        c.execute("SELECT IDENTIFICATION_CD, DESCRIPTION_TEXT, LD_CP_TIER_LEV_TXT, "
                  "D_LAST_UPDT_TS, ACTIVITY_STATUS_CD "
                  "FROM SDWIS2TX.TSASMPPT "
                  "WHERE TINWSF0IS_NUMBER = '{}'".format(tinwsf0is))
        val = c.fetchall()
        sites = []
        for v in val:
            if v[0][:3] == 'LCR':
                YEAR = str(v[3].year)
                month = str(v[3].month)
                if len(month) == 1:
                    month = "0" + month
                day = str(v[3].day)
                DATE = month + "/" + day + "/" + YEAR
                # d = {'SAMPLE_ID': v[0][:6], 'sample_loc': v[1], 'activity': v[4], 'tier': v[2], 'last_update': DATE}
                d = [v[0][:6], v[1], v[4], v[2], DATE]
                sites.append(d)
        sites = sorted(sites, key=itemgetter(0))
        path = r'C:\Users\Estinson\Desktop' + "\\" + "sample_sites_" + pws_id + ".docx"
        try:
            export_to_word(sites, path)
            self.word_notification.set("EXPORT TO WORD COMPLETE")
        except StopIteration:
            self.word_notification.set("STOP ITERATION ERROR")
        except StopAsyncIteration:
            self.word_notification.set("STOP ASYNC ITERATION")
        except ArithmeticError:
            self.word_notification.set("ArithmeticError")
        except AssertionError:
            self.word_notification.set("AssertionError")
        except AttributeError:
            self.word_notification.set("AttributeError")
        except BufferError:
            self.word_notification.set("BufferError")
        except EOFError:
            self.word_notification.set("EOFError")
        except LookupError:
            self.word_notification.set("LookupError")
        except MemoryError:
            self.word_notification.set("MemoryError")
        except ImportError:
            self.word_notification.set("IMPORT ERROR")
        except OSError:
            self.word_notification.set("OS ERROR")
        except NameError:
            self.word_notification.set("NameError")
        except ReferenceError:
            self.word_notification.set("ReferenceError")
        except RuntimeError:
            self.word_notification.set("RuntimeError")
        except SyntaxError:
            self.word_notification.set("SyntaxError")
        except SystemError:
            self.word_notification.set("SystemError")
        except TypeError:
            self.word_notification.set("TypeError")
        except ValueError:
            self.word_notification.set("ValueError")
        except Warning:
            self.word_notification.set("Warning")
        except:
            self.word_notification.set("CANNOT EXPORT")
        # template = "sample_sites.docx"
        # today = datetime.datetime.today()
        # year = today.year
        # month = str(today.month)
        # if len(month) == 1:
        #     month = "0" + str(month)
        # day = str(today.day)
        # if len(day) == 1:
        #     day = "0" + str(month)
        # code_today = str(year) + month + day
        # document = mailmerge.MailMerge(template)
        # document.merge(pws_id=pws_id,
        #                pws_name=name,
        #                short_id=pws_id[2:],
        #                yearmonthday=code_today,
        #                SAMPLE_ID=sites)
        # path = r'C:\Users\Estinson\Desktop' + "\\" + "sample_sites_" + pws_id + ".docx"
        # document.write(path)
        c.close()
        conn.close()

    def excel_export(self):
        dsn_tns = cx_Oracle.makedsn('aed2-scan.tceq.texas.gov', '1521', service_name='PRDEXA.TCEQ.TEXAS.GOV')
        conn = cx_Oracle.connect(self.login_frame.username, self.login_frame.password, dsn_tns, encoding='UTF-8', nencoding='UTF-8')
        c = conn.cursor()
        pws_id = self.pws_entry.get()
        if len(pws_id) == 7:
            pws_id = "TX" + str(pws_id)
        c.execute("SELECT TINWSYS_IS_NUMBER, NAME "
                  "FROM SDWIS2TX.TINWSYS "
                  "WHERE NUMBER0 = '{}'".format(pws_id))
        val = c.fetchall()
        tinwsys = val[0][0]
        name = val[0][1]
        c.execute("SELECT TINWSF_IS_NUMBER "
                  "FROM SDWIS2TX.TINWSF "
                  "WHERE TINWSYS_IS_NUMBER = {} AND TYPE_CODE = 'DS'".format(tinwsys))
        tinwsf0is = c.fetchone()[0]
        c.execute("SELECT IDENTIFICATION_CD, DESCRIPTION_TEXT, LD_CP_TIER_LEV_TXT, "
                  "D_LAST_UPDT_TS, D_USERID_CODE, ACTIVITY_STATUS_CD "
                  "FROM SDWIS2TX.TSASMPPT "
                  "WHERE TINWSF0IS_NUMBER = '{}'".format(tinwsf0is))
        val = c.fetchall()
        sites = []
        for v in val:
            if v[0][:3] == 'LCR':
                YEAR = str(v[3].year)
                month = str(v[3].month)
                if len(month) == 1:
                    month = "0" + month
                day = str(v[3].day)
                DATE = month + "/" + day + "/" + YEAR
                site = [v[0][:6], v[2], v[4], DATE, v[5]]
                location = v[1].split(" ")
                ind = 1
                if len(location) < 5:
                    val = 5 - len(location)
                    for x in range(val):
                        location.append("")
                for part in location:
                    site.insert(ind, part)
                    ind += 1
                sites.append(site)
        sites = sorted(sites, key=itemgetter(0))
        today = datetime.datetime.today()
        year = today.year
        month = str(today.month)
        if len(month) == 1:
            month = "0" + str(month)
        day = str(today.day)
        if len(day) == 1:
            day = "0" + str(month)
        code_today = str(year) + month + day
        path = r'C:\Users\Estinson\Desktop' + "\\" + "sample_sites_" + pws_id + ".xlsx"
        workbook = xlsxwriter.Workbook(path)
        worksheet = workbook.add_worksheet()
        row = 0
        col = 0
        column_names = ['PWS ID', 'SAMPLE SITE ID', 'LOCATION', '', '', '', '', 'TIER', 'LAST UPDATED BY', 'UPDATED',
                        'ACTIVITY']
        for name in column_names:
            worksheet.write(row, col, name)
            col += 1
        for site in sites:
            col = 0
            row += 1
            worksheet.write(row, col, pws_id)
            for item in site:
                col += 1
                worksheet.write(row, col, item)
        workbook.close()
        c.close()
        conn.close()

    def callback(self, event=None):
        pws_id = self.pws_entry.get()
        pws_id = pws_id.strip().replace(" ", "")
        info = viewer(self.login_frame.username, self.login_frame.password, pws_id)
        inv = info[0]
        ind = info[1][0]
        if ind[0] == 0:
            ind = [0, 'NA', "NA", "NA", "NA"]
        miles = info[2]
        milestone_string = ""
        if miles:
            for stone in miles:
                milestone_string = milestone_string + """
            {} {} {}""".format(stone[0], stone[1], stone[2])
        if not miles:
            milestone_string = "No Milestones"
        viol_names = {51: 'INITIAL TAP', 52: 'ROUTINE TAP', 53: 'WQP', 56: 'SOWT', 57: 'OCCT/SOWT STUDY',
                      58: 'OCCT/SOWT INSTALL', 59: 'WQP NON-COMPLIANCE', 63: 'MPL NON-COMPLIANCE',
                      64: 'LSL REPLACEMENT', 65: 'PUBLIC EDUCATION', 66: 'LEAD CONSUMER NOTICE'}
        viol_status = {'V': "Valid", "P": "Preliminary"}
        closed = info[3]
        closed_string = ""
        if closed:
            for v in closed:
                viol = closed[v]
                desc = viol[0]
                closed_string = closed_string + """
            Vio: {} {} {} {} - {}""".format(desc[0], viol_names[desc[0]], viol_status[desc[1].strip()], desc[2],
                                            desc[3])
                for x in viol[1]:
                    closed_string = closed_string + """
                 -- {} {} {} {} {}""".format(x[1], x[2], x[3], x[4], x[5])
        if not closed:
            closed_string = "No Closed Violations"
        viols = info[4]
        viols_string = ""
        if viols:
            for v in viols:
                viol = viols[v]
                desc = viol[0]
                viols_string = viols_string + """
            Vio: {} {} {} {} - {}""".format(desc[0], viol_names[desc[0]], viol_status[desc[1].strip()], desc[2],
                                            desc[3])
                for x in viol[1]:
                    viols_string = viols_string + """
                 -- {} {} {} {} {}""".format(x[1], x[2], x[3], x[4], x[5])
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
                    sched_string = """
            SCHEDULE: {}
            COMMENT: {}
            BEGIN DATE: {}
            SAMPLES REQUIRED: {}""".format(c[0], c[1], c[2], c[5])
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
            for period in summs:
                period_sums = period[1]
                sum_string = sum_string + """
            {} - {}""".format(period_sums[0][1], period_sums[0][2],)
                for period_sum in period_sums:
                    ale = "NO"
                    rml = ""
                    if period_sum[3] == "PB90":
                        if float(period_sum[4]) > 0.0154:
                            ale = "YES"
                        elif float(period_sum[4]) > 0.0054:
                            rml = "OVER"
                        else:
                            rml = "UNDER"
                    elif period_sum[3] == "CU90":
                        if float(period_sum[4]) > 1.34:
                            ale = "YES"
                        elif float(period_sum[4]) > 0.654:
                            rml = "OVER"
                        else:
                            rml = "UNDER"
                    c = period_sum
                    sum_string = sum_string + """
                {} {} {} {} ALE: {} RML: {}""".format(c[0], c[3], c[4], c[5], ale, rml)
        if not summs:
            sum_string = "No Summaries"
        sites = info[8]
        sites_string = ""
        if sites:
            for c in sites:
                sites_string = sites_string + """
            {} --- {} --- {} - {} --- {} by {} --- {}""".format(c[0][:6], c[1], c[2], c[3], c[4].date(), c[5], c[6])
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
        # self.info.set(text_return)
        # return self.info
        self.pws_info.delete(1.0, END)
        self.pws_info.insert(END, text_return)

    def start_app(self):
        self.master.mainloop()


root = Tk()
root.geometry("1000x800")
root.config(bg=color_main)
Viewer(master=root).start_app()
