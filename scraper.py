from models.models import  Immiscraper
import json
import re
from google.appengine.ext.db import metadata
from bs4 import BeautifulSoup
import calendar
import time
import requests
from flask import current_app, session, app, flash, views, json

class LinkCreator:


    """getting all the required a tags on the page
    links which take to the invitation round details pages
    """

    def __init__(self):
        # TODO will need to create this file in temp position in final version
        self.invitation_year_dict = {}
        self.invitation_data_dict = {}
        self.latest_data_dict = {}
        self.home_url = "https://homeaffairs.gov.au"

    def checkmodification(self, query):
        # print query
        previousupdatedate = query
        # print "last_modified", previousupdatedate
        # print "createddate", createddate
        currentdate = calendar.timegm(time.gmtime())
        # print "current", currentdate
        # print currentdate - previousupdatedate
        if(currentdate - previousupdatedate > 18000):
            return True
        else:
            return False

    def requestfile(self, url):
        current_app.logger.info("web requestung")
        html = requests.get(url)
        # #print html.text
        return html

        # #print self.soup.prettify()

    def readfile(self, query):
        html = query
        return html

    def latest_data(self):
        immitable = metadata.get_kinds()
        # current_app.logger.info(immitable)
        if('Immiscraper' in immitable):
            latest_data_home_file_status = self.checkmodification(
                query=Immiscraper.query().get().latest_page_html_update_date)
            # print "file exists"
            if(latest_data_home_file_status):
                html = self.requestfile(
                    "https://www.homeaffairs.gov.au/trav/work/skil#tab-content-2")
                self.soup = BeautifulSoup(html.text, "html.parser")
                Immiscraper(
                        latest_page_html_update_date=calendar.timegm(time.gmtime()),
                        latest_page_html=self.soup.prettify(
                            ).encode('ascii', 'ignore')
                    ).put()
            else:
                html = self.readfile(query=Immiscraper.query().get().latest_page_html)
                self.soup = BeautifulSoup(html,"html.parser")
        else:
            html = self.requestfile(
                "https://www.homeaffairs.gov.au/trav/work/skil#tab-content-2")
            self.soup = BeautifulSoup(html.text, "html.parser")
            Immiscraper(
                        latest_page_html_update_date=calendar.timegm(time.gmtime()),
                        latest_page_html=self.soup.prettify(
                            ).encode('ascii', 'ignore')
                    ).put()
        # #print latest_data_home_file_status
        latest_data_home = self.soup.find_all(class_="tabbody")[2]
        link = latest_data_home.find("a")["href"]
        # print link
        update_date = re.search(r'\d*-\D*-\d{4}', link).group()
        # print update_date
        latest_data_dict = self.get_data(self.home_url + link)
        # print latest_data_dict
        latest_data_dict["update_date"] = update_date
        # #print latest_data_dict
        # file_to_write_to_js = '{} {} {}'.format("const latest_data = ", json.dumps(
        #     latest_data_dict, indent=4, sort_keys=True), "\nexport default latest_data")
        # latest_js_file = open(os.path.join(os.path.dirname(
        #     os.getcwd()), "containers/latest_data.js"), "w")
        # latest_js_file.write(file_to_write_to_js.strip())
        # # print latest_js_file
        # latest_js_file.close()

        return json.dumps(latest_data_dict)

    def create_links(self):
        # the page has four tabbody class on page
        # the 3rd is links to all the invitations on page and 4th
        # is the occupational ceiling.
        # extract all the 'ul' which houses the links on that page
        immitable = metadata.get_kinds()
        main_page_html_property = metadata.get_representations_of_kind("Immiscraper")
        print main_page_html_property
        if('Immiscraper' in immitable and
            main_page_html_property['main_page_html_update_time'] is not None):
            main_data_home_file_status = self.checkmodification(
                query=Immiscraper.query().get().main_page_html_update_time)
            current_app.logger.info("sataus", main_data_home_file_status)
            if(main_data_home_file_status):
                html = self.requestfile(
                    "https://www.homeaffairs.gov.au/trav/work/skil#tab-content-2")
                self.soup = BeautifulSoup(html.text, "html.parser")
                Immiscraper(
                        main_page_htmi_update_time=calendar.timegm(
                            time.gmtime()),
                        main_page_html=self.soup.prettify(
                            ).encode('ascii', 'ignore')
                    ).put()
            else:
                html = self.readfile(query=Immiscraper.query().get().main_page_html)
                self.soup = BeautifulSoup(html,"html.parser")
        else:
            html = self.requestfile(
                "https://www.homeaffairs.gov.au/trav/work/skil#tab-content-2")
            self.soup = BeautifulSoup(html.text, "html.parser")
            Immiscraper(
                        main_page_html_update_time=calendar.timegm(time.gmtime()),
                        main_page_html=self.soup.prettify(
                            ).encode('ascii', 'ignore')
                    ).put()
        tab_content_invitations = self.soup.find_all(class_="tabbody")
        # ##print a
        invitation_links = tab_content_invitations[2].find_all("ul")
        # #print invitation_links
        # the 'a'  gives us list with two lists inside one list i.e  2018 and 2017.
        # the first one is 2018 and second one is 2017.
        # ##print a[0]
        for yearly_links in invitation_links:
            for dates in yearly_links:
                year = re.search(r'\d{4}', str(dates))
                date = re.search(r'\d+\s+\w+', str(dates))
                link = re.search(r'(\/[A-Za-z\/\-0-9.aspx]+)', str(dates))
                # time.sleep(2)
                # ##print link.group()
                if(year):
                    # ##print year.group()
                    # ##print date.group()
                    # ##print link.group()
                    if (year.group() in self.invitation_year_dict) and type(
                        self.invitation_year_dict[year.group()]
                    ) is dict:
                        # #print invitation_year_dict
                        self.invitation_year_dict[year.group(
                        )][date.group()] = link.group()
                        # #print invitation_year_dict
                    else:
                        self.invitation_year_dict[year.group()] = {}
                        # #print invitation_year_dict
                        self.invitation_year_dict[year.group(
                        )][date.group()] = link.group()
                        # #print invitation_year_dict
        return json.dumps(self.invitation_year_dict)

    def queryceilings(self):
        import json
        import sys
        updated_ceilings = {}
        # the page has four tabbody class on page
        # 4th is the occupatiomal ceiling.
        # extract table which houses the links on that page
        occupational_ceiling = self.soup.find_all(class_="tabbody")[3]
        for row in occupational_ceiling.find_all('table'):
            for data in row.find_all('tr')[1:]:
                # ##print "data\n"
                # ##print "----------------"
                # ##print data
                occupation_name = data.find_all("td")[1].text.strip().lower()
                occupation_code = data.find_all("td")[0].text.strip().lower()
                occupational_ceiling = data.find_all(
                    "td")[2].text.strip().lower()
                granted = data.find_all("td")[3].text.strip()
                updated_ceilings[occupation_name] = {"code": occupation_code,
                                                     "ceiling": occupational_ceiling,
                                                     "granted": granted}
        # #print json.dumps(updated_ceilings)
        # #print ("Estimated size: " + str(sys.getsizeof(json.dumps(updated_ceilings)) / 1024) + "KB")
        return json.dumps(updated_ceilings)

    def invitation_data_scraper(self):
        for year in self.invitation_year_dict.keys():
            # print year
            date_link_object = self.invitation_year_dict[year]
            # #print date_link_object
            # #print "------------------------"
            for dates, links in date_link_object.items():
                # #print "date form data", dates
                if (year in self.invitation_data_dict):
                    # #print "executing if"
                    if (dates in self.invitation_data_dict[year]):
                        self.invitation_data_dict[year][dates]["data"] = self.get_data(
                            self.home_url+links)
                    else:
                        self.invitation_data_dict[year][dates] = {
                            "data": self.get_data(self.home_url+links)}
                else:
                    # #print "executing else"
                    self.invitation_data_dict[year] = {}
                    self.invitation_data_dict[year][dates] = {"data": {}}

            # #print self.invitation_data_dict
        # file_to_write_to_js = '{} {} {}'.format("const data = ", json.dumps(
        #     self.invitation_data_dict, indent=4, sort_keys=True), "\nexport default data")
        # data_js_file = open(os.path.join(os.path.dirname(
        #     os.getcwd()), "containers/immi_data.js"), "w")
        # data_js_file.write(file_to_write_to_js.strip())
        # # #print latest_js_file
        # data_js_file.close()
        return json.dumps(self.invitation_data_dict)
# #print self.invitation_data_dict

    def get_data(self, link):

   #      headers = {
        #   'User-Agent': 'Abhijit web scrapper project 1.0',
        #   'From': 'nonestate@gmail.com'  # This is another valid field
        # }
        # #print self.home_url+link
        html = requests.get(link)
        # html = open("data.txt").read()
        # print link
        soup = BeautifulSoup(html.text, "html.parser")
        # print soup.prettify()
        total_invitation_table = soup.find_all("table")[0]
        occupation_table_cut_off = {}
        try:
            occupation_table_cut_off = soup.find_all("table")[3]
        except:
            pass
        results = {}
        results["summary"] = {}
        results["cut-off"] = {}
        results["occupation-cut-off"] = {}
        for row in total_invitation_table.find_all("tr")[1:]:
            results[(re.search(r"\d{3}", row.find_all("td")[
                     0].text).group())] = row.find_all("td")[1].text
        table_summary = soup.find_all("table")[1]
        count = 1
        for month in table_summary.find_all("th")[1:]:
            results["summary"][month.text] = table_summary.find_all("td")[
                count].text
            count = count + 1
        cut_off_table = soup.find_all("table")[2]
        for row in cut_off_table.find_all("tr")[1:]:
            # #print row.text
            results["cut-off"][re.search(r"\d{3}",
                                         row.find_all("td")[0].text).group()] = {}
            results["cut-off"][re.search(r"\d{3}", row.find_all("td")[0].text).group(
            )]["points"] = cut_off_table.find_all("td")[1].text
            results["cut-off"][re.search(r"\d{3}", row.find_all(
                "td")[0].text).group()]["date"] = cut_off_table.find_all("td")[2].text
        if(occupation_table_cut_off):
            for row in occupation_table_cut_off.find_all("tr")[1:]:
                results["occupation-cut-off"][row.find_all("td")[1].text] = {
                    "points": row.find_all("td")[2].text, "date": row.find_all("td")[3].text}
        return results
