import random
import time
from datetime import datetime
from locust import HttpUser, task, between
import pandas as pd
import json

df = pd.read_csv("Employee.csv")
df.columns = df.columns.str.strip().str.lower()
COMMON_PW = "AVP@2023"
df['password'] = COMMON_PW
USER_CREDENTIALS = list(df[['user', 'password']].itertuples(index=False, name=None))
formatted_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
USE_METHOD_NAME = 0
date_index = {}
dates  = [
    "2025-07-21", "2025-07-22", "2025-07-23", "2025-07-24", "2025-07-25",
    "2025-07-26", "2025-07-27", "2025-07-28", "2025-07-29", "2025-07-30",
    "2025-07-31", "2025-08-01", "2025-08-02", "2025-08-03", "2025-08-04",
    "2025-08-05", "2025-08-06", "2025-08-07", "2025-08-08", "2025-08-09",
    "2025-08-10", "2025-08-11", "2025-08-12", "2025-08-13", "2025-08-14",
    "2025-08-15", "2025-08-16", "2025-08-17", "2025-08-18", "2025-08-19",
    "2025-08-20", "2025-08-21", "2025-08-22", "2025-08-23", "2025-08-24",
    "2025-08-25", "2025-08-26", "2025-08-27", "2025-08-28", "2025-08-29",
    "2025-08-30", "2025-08-31", "2025-09-01", "2025-09-02", "2025-09-03",
    "2025-09-04", "2025-09-05", "2025-09-06", "2025-09-07", "2025-09-08",
    "2025-09-09", "2025-09-10", "2025-09-11", "2025-09-12", "2025-09-13",
    "2025-09-14", "2025-09-15", "2025-09-16", "2025-09-17", "2025-09-18",
    "2025-09-19", "2025-09-20", "2025-09-21", "2025-09-22", "2025-09-23",
    "2025-09-24", "2025-09-25", "2025-09-26", "2025-09-27", "2025-09-28",
    "2025-09-29", "2025-09-30"
]
class WebsiteUser(HttpUser):
    wait_time = between(3, 6)
    host = "http://192.168.0.227:30626"
    sid = None
    employee_data = None

    def get_list(
            self,
            name,
            doctype,
            filters=None,
            fields=None,
            order_by=None,
            limit_start=0,
            limit_page_length=0,
            as_dict=None
    ):

        headers = {
            'Cookie': f'sid={self.sid}',
            'Accept': 'application/json',
        }

        params = {
            'limit_start': str(limit_start),
        }

        if filters
            params['filters'] = json.dumps(filters)
        if fields:
            params['fields'] = json.dumps(fields)
        if order_by:
            params['order_by'] = order_by
        if limit_page_length != 0:
            params['limit_page_length'] = str(limit_page_length)
        if as_dict:
            params['as_dict'] = as_dict


        response = self.client.get(f'/api/resource/{doctype}',headers=headers,params=params,name=name)

        if self.validate_resp(response):
            return response.json().get("data", [])
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    def on_start(self):
        if not USER_CREDENTIALS:
            raise Exception("No user credentials left.")
        self.username, self.password = USER_CREDENTIALS.pop(0)
        print(f"[USER] {self.username}")

    def validate_resp(self, resp):
        try:
            resp.raise_for_status()
            # if resp.status_code >= 500:
            #     raise SystemError(resp.text)
            return True
        except Exception as e:
            print("[ERROR]", e)
            return False

    def login(self):
        name = "login"
        method_name=f"Login / {self.username} / {datetime.now()}"
        resp = self.client.post(
            "/api/method/login",
            json={"usr": self.username, "pwd": self.password},
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            name=method_name
        )
        if not self.validate_resp(resp):
            raise Exception(f"Login Failed: {resp.text} ({resp.status_code})")
        self.sid = resp.cookies.get("sid")
        if not self.sid:
            print(f"[WARN] No sid for {self.username}")
        else:
            print(f"[LOGIN] Success for {self.username}")

    def get_employee_details(self):
        name = "get_employee_details"
        method_name=f"employee_details / {self.username} / {datetime.now()}"
        headers = {
            'Cookie': f'sid={self.sid}',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        payload = {'user_id': self.username}
        resp = self.client.post(
            "/api/method/get_preferences",
            headers=headers,
            json=payload,
            name=method_name
        )
        if not self.validate_resp(resp):
            raise Exception(f"get_employee_details failed: {resp.text} ({resp.status_code})")
        self.employee_data = resp.json().get("data")

    def fetch_holiday_list(self):
        name = "fetch_holiday_list"
        if not self.employee_data:
            print("[SKIP] No employee data")
            return
        emp_id = self.employee_data.get("employee_id")
        if not emp_id:
            print("[SKIP] employee_id not found")
            return
        headers = {
            'Cookie': f'sid={self.sid}',
            'Accept': 'application/json',
        }
        resp = self.client.get(f"/api/resource/Employee/{emp_id}", headers=headers,
        name="fetch_holiday_list_employee"
        )
        if not self.validate_resp(resp):
            print(f"[ERROR] Holiday fetch failed: {resp.text}")
            return

        holiday_list = resp.json().get("data", {}).get("holiday_list")

        if holiday_list
            resp = self.client.get(f"/api/resource/Holiday List/{holiday_list}", headers=headers,name= name)
            if not self.validate_resp(resp):
                raise Exception(f"[ERROR] Holiday fetch failed: {resp.text}")

    def fetch_salary_slip(self):
        name = "fetch_salary_slip"
        if not self.employee_data:
            print("[SKIP] No employee data")
            return
        emp_id = self.employee_data.get("employee_id")
        if not emp_id:
            print("employee id not found")
            return

        headers = {
            'Cookie': f'sid={self.sid}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        payload = {
          "filters": [
            ["employee", "=", emp_id],
            ["custom_salary_month_and_year", "=", "April-2025"]
          ]
        }


        resp = self.client.get(f"/api/method/get_salary_slips", headers=headers,json = payload,
         name=name)
        if not self.validate_resp(resp):
            raise Exception(f"Salary slip fetch failed {resp.text}")

    def get_leave_balance(self):
        name = "fetch_leave_balance"
        method_name = f"{name}/ {self.username} / {datetime.now()}" if USE_METHOD_NAME else f"POST_create_leave_application_draft"
        if not self.employee_data:
            print("[SKIP] No employee data")
            return
        emp_id = self.employee_data.get("employee_id")
        if not emp_id:
            print("employee id not found")
            return

        headers = {
            'Cookie': f'sid={self.sid}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        payload = {
            "employee": emp_id
        }

        resp = self.client.get(f"/api/method/fetch_leave_balance",headers=headers, json=payload,
                               name=name)
        print(resp.text)
        if not self.validate_resp(resp):
            print(f"Getting Leave Application failed {resp.text}")

    def fetch_leave_list(self):
        method_name = f"POST_fetch_leave_list / {self.username} / {datetime.now()}" if USE_METHOD_NAME else f"POST_fetch_leave_list"
        name = "fetch_leave_list"
        if not self.employee_data:
            print("[SKIP] No employee data")
            return

        emp_id = self.employee_data.get("employee_id")
        if not emp_id:
            print("employee id not found")
            return

        leave_list = self.get_list(
            doctype = "Leave Application",
            name=method_name,
            filters=[
                ["employee", "!=", emp_id],
                ["from_date",">=", "2025-01-01"],
                ["to_date", "<=", "2025-07-12"]
            ],
            fields = [
            "name",
            "employee_name",
            "workflow_state",
            "from_date",
            "to_date",
            "total_leave_days",
            "leave_type",
            "description",
            "custom_is_hourly",
            "custom_from_date_time",
            "custom_to_date_time"
        ],
        )
        if not leave_list:
            print("no leave records")
        else:
            print(f"Found {len(leave_list)} leave applications.")

    def compensatory_leavereq(self):
        method_name = f"POST_compensatory_leave_request / {self.username} / {datetime.now()}" if USE_METHOD_NAME else f"POST_compensatory_leave_request"
        if not self.employee_data:
            print("[skip] no employee details found")
            return
        emp_id = self.employee_data.get("employee_id")
        if not emp_id:
            print("[skip] no employee id found")
            return
        com_leavelist = self.get_list(
            doctype = "Compensatory Leave Request",
            name=method_name,
            filters =[
                ["employee", "!=", emp_id],
                ["work_from_date", ">=", dates.pop(0)],
                ["work_end_date", "<=", dates.pop(0)]
            ],
            fields = [
                "name",
                "employee_name",
                "docstatus",
                "work_from_date",
                "work_end_date",
                "custom_work_from_date_time",
                "custom_work_end_date_time",
                "leave_type"
            ],)
        if not com_leavelist:
            print("no compensetory leave requests")
        else:
            print(f"found{len(com_leavelist)} leave requests")

    def fetch_notificationlog(self):
        method_name = f"POST_fetch_notification_log / {self.username} / {datetime.now()}" if USE_METHOD_NAME else f"POST_fetch_notification_log"
        if not self.employee_data:
            print("employee details not found")
            return
        emp_id = self.employee_data.get("employee_id")

        if not emp_id:
            print("employee id not found")
            return
        headers = {
            'Cookie': f'sid={self.sid}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

        resp = self.client.get("/api/method/frappe.desk.doctype.notification_log.notification_log.get_notification_logs", headers = headers,
                               name=method_name)
        print(resp.text)
        if not self.validate_resp(resp):
            print(f"failed to fetch notification log{resp.text}")

    def checkin_status(self):
        method_name = f"POST_checkin_status / {self.username} / {datetime.now()}" if USE_METHOD_NAME else f"POST_checkin_status"
        if not self.employee_data:
            print("no employee data found")
            return
        emp_id = self.employee_data.get("employee_id")

        if not emp_id:
            print("no employee id found")
            return

        checkin_list = self.get_list(
            doctype = "Employee Checkin",
            name=method_name,
            fields=[
                "name", "log_type", "shift", "time"
            ],
            filters = [
                ["employee", "=", emp_id]
            ],
        )
        if not checkin_list:
            print("there is no checkin list found")
        else:
            print(f"found{len(checkin_list)}checkin list")

    def create_leave_app(self):
        _name = "create_leave_application"
        if not self.employee_data:
            print("employee details not found")
            return
        emp_id = self.employee_data.get("employee_id")
        if not emp_id:
            print("employee id not found")
            return
        index = date_index.get(self.username, 0)
        index = index + 1
        date_index[self.username] = index
        if len(dates) >= index:
            date = dates[index]
            headers = {
                'Cookie': f"sid={self.sid}",
                'Accept': 'application/json',
                'Content-Type': 'application/json',
            }

            payload = {
                "employee": emp_id,
                "leave_type": "Leave Without Pay",
                "from_date": date,
                "to_date": date,
            }
            method_name = f"POST_create_leave_application_draft / {self.username} / {datetime.now()}" if USE_METHOD_NAME else f"POST_create_leave_application_draft"
            resp = self.client.post("/api/method/create_leave_application",headers=headers,json=payload,
                                        name=method_name)
            print(resp.text)
            print("JSON------------------",resp.json())
            if not self.validate_resp(resp):
                print(f"failed to fetch create leave application list{resp.text}")
            name = resp.json().get("data",{})
            print("Name --------- ",name)
            data = {"name":name.get('name'),'data':{'workflow_state': "Applied"}}
            method_name = f"POST_create_leave_application_submit / {self.username} / {datetime.now()}" if USE_METHOD_NAME else f"POST_create_leave_application_submit"
            submit = self.client.post("/api/method/update_leave_status",headers=headers,json=data,name=method_name)
            if not self.validate_resp(submit):
                print(f"failed to fetch create leave application list{resp.text}")


    def check_in_out(self,type):
        headers = {
            'Cookie': f"sid={self.sid}",
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        data = {
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "log_type": type,
            "employee": self.employee_data.get("employee_id"),
            "device_id": "Remote",
            "custom_distance_in_km": "0.008107787116547848",
            "custom_employee_latitude": "11.0028633",
            "custom_employee_longitude": "77.0410367",
        }
        method_name = f"POST_Employee_Check_{type} / {self.username} / {datetime.now()}" if USE_METHOD_NAME else f"POST_Employee_Check_{type}"
        print(f"Triggered for {type}")
        resp = self.client.post("/api/resource/Employee Checkin",headers=headers,json=data,
                                name=method_name
                                )
        print(resp.text)
        if not self.validate_resp(resp):
            print(f"Employee checkin got server error {resp.text}")

    def check_in(self):
        print("Check in called")
        self.check_in_out("IN")

    def check_out(self):
        print("Check out called")
        self.check_in_out("OUT")


    def execute_actions(self,random_action=0):
        actions = [
            self.check_in,
            # self.fetch_holiday_list,
            # self.checkin_status,
            # self.create_leave_app,
            # self.fetch_salary_slip,
            self.check_out,
            # self.get_leave_balance,
            # self.fetch_leave_list,
            # self.compensatory_leavereq,
            # self.fetch_notificationlog,

        ]
        if random_action ==0:
            for action in actions:
                try:
                    action()
                except Exception as e:
                    print(f"Failed on {action} error : {e}")
        else:
            while actions:
                action = random.choice(actions)
                action()
                actions.remove(action)


    @task
    def start_load_test(self):
        print("load test started")
        try:
            self.login()
            self.get_employee_details()
            self.check_in()
            self.check_out()
        except Exception as e:
            print(e)
        # self.execute_actions()
