from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import configparser
import smtplib as smtp
import datetime as dt
import time 


URLS = {'EVGA_FE_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814487243',
        'EVGA_ACX_1080' : 'http://www.newegg.com/Product/Product.aspx?item=N82E16814487246',
        'EVGA_SC_1080' : 'http://www.newegg.com/Product/Product.aspx?item=N82E16814487244',
        'EVGA_FTW_1080' : 'http://www.newegg.com/Product/Product.aspx?item=N82E16814487245',
        'GIGABYTE_FE_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814125861',
        'GIGABYTE_G1_1080' : 'http://www.newegg.com/Product/Product.aspx?item=N82E16814125869',
        'GIGABYTE_XTREME_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814125873',
        'PNY_FE_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814133629',
        'ASUS_ROG_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814126103',
        'ASUS_FE_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814126101',
        'ASUS_STRIX_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814126106',
        'MSI_AERO_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814127944',
        'MSI_FE_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814127940',
        'ZOTAC_FE_1080' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814500396',
        'EVGA_FE_1070' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814487247',
        'GIGABYTE_FE_1070' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814125870',
        'ASUS_FE_1070' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814126104',
        'PNY_FE_1070' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814133630',
        'ZOTAC_FE_1070' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814500397',
        'MSI_FE_1070' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814127941',
        'ACER_XB270HU_BPRZ' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16824009852',
        'ASUS_PG279Q' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16824236705'}

#URLS['EVGA_980TI'] = 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814487142'  

parser = configparser.ConfigParser()
parser.read('config.ini')
EMAIL_ADDR_FROM = parser.get('email_info', 'email')
EMAIL_PW = parser.get('email_info', 'password')
EMAIL_ADDR_TO = parser.get('email_info', 'email_list').split(',')

def main():
    driver = init_driver()
    item_status = dict.fromkeys(URLS.keys(), False)
    round_count = 0

    try:
        while True:
            error_count = 0

            for item, url in URLS.items(): 
                print('checking: ' + item, end = " ")
                before_in_stock = item_status[item]
                current_in_stock = check_stock(driver, url)
                if current_in_stock is not None: 
                    if not before_in_stock and current_in_stock:
                        print('{0} is in stock.---------------------------------------------------------------------'.format(item))
                        price_element = scrape_element(driver, driver.find_element_by_xpath, "//ul[@class='price has-label-membership price-product-cells price-main-product']//li[@class='price-current']")
                        name_element = scrape_element(driver, driver.find_element_by_id, 'grpDescrip_h')
                        send_emails(url, none_or_text(price_element), none_or_text(name_element))
                    item_status[item] = current_in_stock
                else:
                    error_count += 1    

                time.sleep(8)

            round_count += 1
            print('Done with round {0} at {1}.'.format(round_count, str(dt.datetime.now())))

            if error_count > 10:
                print('Restarting driver...')
                driver = init_driver()

    except KeyboardInterrupt:
        print('Quitting...')
        driver.quit()

def init_driver():
    dcap = dict(DesiredCapabilities.PHANTOMJS)
    dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/53 (KHTML, like Gecko) Chrome/15.0.87")
    dcap['phantomjs.page.settings.resourceTimeout'] = '5000'
    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    driver.set_page_load_timeout(20)
    driver.implicitly_wait(3)
    return driver

def scrape_element(driver, method, *args):
    try: 
        return method(*args)

    except NoSuchElementException:
        print('Could not find element.')
        return None

def check_stock(driver, url):
    try:
        driver.get(url)
        stock_element = scrape_element(driver, driver.find_element_by_id, 'landingpage-stock')
        if stock_element is not None:
            print(stock_element.text)
            return stock_element.text != 'OUT OF STOCK.'
        else:
            return None

    except TimeoutException as err:
        print('\nTimed out trying to get: {0}'.format(url))
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

def none_or_text(element):
    return 'None' if element is None else element.text


if __name__ == "__main__":
    main()