from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import smtplib as smtp

URL_1080 = 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814487243'
URL_980 = 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814487142'  

URLS = [URL_1080, URL_980]


parser = configparser.ConfigParser()
parser.read('config.ini')
EMAIL_ADDR_FROM = parser.get('email_info', 'email')
EMAIL_PW = parser.get('email_info', 'password')
EMAIL_ADDR_TO = ['weirdotomli@gmail.com', "cosmicac@berkeley.edu"] 

def main():
    driver = webdriver.PhantomJS()
    driver.set_page_load_timeout(45)
    item_status = dict.fromkeys(URLS, False)

    try:
        while True:
            for url in URLS: 
                print('checking: ' + url)
                before_in_stock = item_status[url]
                current_in_stock = check_stock(driver, url)
                if current_in_stock is not None: 
                    if not before_in_stock and current_in_stock:
                        price_element = driver.find_element_by_xpath("//ul[@class='price has-label-membership price-product-cells price-main-product']//li[@class='price-current']")
                        name_element = driver.find_element_by_id('grpDescrip_h')
                        send_emails(url, price_element.text, name_element.text)
                    item_status[url] = current_in_stock

    except KeyboardInterrupt:
        print('Quitting...')
        driver.quit()

def check_stock(driver, url):
    try:
        driver.get(url)
        stock_element = driver.find_element_by_id('landingpage-stock')
        return stock_element.text != 'OUT OF STOCK.'
    except TimeoutException:
        print('Timed out trying to get: ' + url)
        return None

def send_emails(url, price, item_name):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDR_FROM

        msg['To'] = ", ".join(EMAIL_ADDR_TO)
        msg['Subject'] = 'IN STOCK for {0} : {1}'.format(price, item_name)   
        body = '{0} is in stock for {1}. URL: {2}'.format(item_name, price, url)
        msg.attach(MIMEText(body, 'plain'))

        server = smtp.SMTP('smtp.gmail.com', 587)
        server.starttls()

        server.login(EMAIL_ADDR_FROM, EMAIL_PW)
        text = msg.as_string()
        server.sendmail(EMAIL_ADDR_FROM, EMAIL_ADDR_TO, text)
        server.quit()
    except: 
        print("Failed to send email.")

if __name__ == "__main__":
    main()