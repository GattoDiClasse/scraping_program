import requests
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from time import sleep
import xlsxwriter

http = "https://scrapingclub.com"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
           "AppleWebKit/537.36 (KHTML, like Gecko)"
           "Chrome/122.0.0.0 Safari/537.36"
           }


def find_info_catalogs(date): # A function for getting the necessary information
    try:
        response = requests.get(date, headers)
        sleep(1)
        soup = BeautifulSoup(response.text, "lxml")

        name = soup.find("h3", class_="card-title").text.replace("\n", "")
        price = soup.find("h4", class_="my-4 card-price").text.replace("\n", "")
        description = soup.find("p", class_="card-description").text.replace("\n", "")
        img_url = http + soup.find("img", class_="card-img-top").get("src")   
        yield name, price, description, img_url
    except RequestException as e:
        print(f"Error when requesting to {date}: {e}")


def find_url_catalogs(date): # A function for getting a card link
    for catalog in date:
        link = http + catalog.find("a").get("href")

        if link:
            yield from find_info_catalogs(link)
        else:
            print("The link not found.")


def find_all_catalogs_in_page(): # A function for getting all the cards from the pages
    for page_number in range(1, 7):
        url = f"https://scrapingclub.com/exercise/list_basic/?page={page_number}"

        try:
            response = requests.get(url, headers)
            soup = BeautifulSoup(response.text, "lxml")
            catalogs = soup.find_all("div", class_="w-full rounded border")
            yield from find_url_catalogs(catalogs)
        except RequestException as e:
            print(f"Error when requesting to {url}: {e}.")

        except Exception as e:
            print(f"An unexpected error has occurred: {e}.")


def write_info_excel(dates, name): # A function for write data to excel
    process = 0
    workbook = xlsxwriter.Workbook(name)
    page = workbook.add_worksheet("Page1")

    row = 1
    column = 0

    page.set_column("A:A", 20)
    page.set_column("B:B", 20)
    page.set_column("C:C", 50)
    page.set_column("D:D", 50)

    page.write(0, 0, "Name")
    page.write(0, 1, "Price")
    page.write(0, 2, "Description")
    page.write(0, 3, "Image URL")

    for item in dates():
        page.write(row, column, item[0])
        page.write(row, column + 1, item[1])
        page.write(row, column + 2, item[2])
        page.write(row, column + 3, item[3])
        row += 1

        print(f"{process}%")
        process += 1

    workbook.close()


while True:
    name_excel_file = input("Enter a name for the new excel spreadsheet: ")
    if name_excel_file.endswith(".xlsx"):
        break
    else:
        print("The name must end with \".xlsx\"")

write_info_excel(find_all_catalogs_in_page, name_excel_file)