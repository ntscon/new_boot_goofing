# -*- coding: utf-8 -*-
"""
@author: Nathan
"""
import requests
from bs4 import BeautifulSoup
import dateutil
import re
import matplotlib.pyplot as plt
import numpy as np

find_array = ["Total ICU Beds", "ICU Beds Avail", "Total Reported Ventil",
              "In-Use Ventilator", "Available Venti", "19 Patients in DC",
              "19 Patients in ICU", "COVID and non", "COVID Hospital Bed"]

class dailyData:
    def _init_(self, date, icu_cap, icu_avail, vent_cap, vent_used, vent_avail,
        cv_19_hosp, cv_19_icu, tot_hosp, perc_beds):
        self.date = date
        self.icu_cap = icu_cap
        self.icu_avail =  icu_avail
        self.vent_cap = vent_cap
        self.vent_used  = vent_used
        self.vent_avail= vent_avail
        self.cv_19_hosp= cv_19_hosp
        self.cv_19_icu= cv_19_icu
        self.tot_hosp= tot_hosp
        self.perc_beds= perc_beds
    def directory(self):
        return ['date', 'icu_cap', 'icu_avail', 'vent_cap', 'vent_used', 
            'vent_avail', 'cv_19_hosp', 'cv_19_icu', 'tot_hosp', 'perc_beds']
        
def gather_info(mydivs):
    result_array = []
    for n, ele in enumerate(find_array):
        find_array[n] = ele.lower()
    for div in mydivs:
        para = div.findAll("p")
        stop_it =  0
        for p in para:
            our_data = dailyData()
            prop = our_data.directory()
            p_date = p.text
            p_date = p_date.split("-")
            year_try = ""
            if len(p_date) > 1:
                year_arr = p_date[1].split(",")
                year_try = year_arr[1]
            p_date = p_date[0]
            if not (re.search(r"2[0-9]{3}", p_date)):  p_date = p_date + year_try
            try:
                parsed_p_date = dateutil.parser.parse(p_date)
            except:
                continue
            our_data.date = parsed_p_date
            stop_it = stop_it +1
            u_list = p.find_next("ul")
            list_i = u_list.findAll("li")
            for item in list_i:
                list_text = item.text.lower()
                for n, ele in enumerate(find_array):
                    if list_text.find(ele)>-1:
                        split_txt = list_text.split(":")
                        try: 
                            set_prop = prop[n+1]
                            setattr(our_data,set_prop,int(split_txt[1]))
                            continue
                        except: continue
            result_array.append(our_data)
    return result_array

def dc_data_viz():
    start_url = ('https://coronavirus.dc.gov/page/hospital-status-data')
    indiv_path = requests.get(start_url)
    indiv_info = indiv_path.content
    indiv_soup = BeautifulSoup(indiv_info, 'html.parser')
    mydivs = indiv_soup.findAll("div", {"class": "field-item even"})
    div_count = len(mydivs)
    if div_count == 1:
        all_data = gather_info(mydivs)

    sample = dailyData()
    slength = len(sample.directory())

    for n, var in enumerate(sample.directory()):
        x = []
        y = []
        if var == "date": continue 
        for i in all_data:
            if getattr(i, "date") < dateutil.parser.parse('12/1/21'): continue
            if hasattr(i, var):
                y.append(getattr(i, var))
                x.append(i.date)
        plt.tight_layout()
        plt.subplot(round(slength,0)/3,round(slength, 0)/3,n)
        plt.plot(x,y)
        try: 
            max_num = int(max(y)) + 25
        except: continue
        plt.yticks(np.arange(0,max_num, round(max_num/5,0)))
        plt.yticks(fontsize = 5)
        plt.xticks(fontsize = 5, rotation = 45)
        plt.xlabel(var)
    plt.savefig('icu_now.png', dpi = 300)

dc_data_viz()