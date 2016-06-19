from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser
import smtplib as smtp


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
        'MSI_FE_1070' : 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814127941'}

EVGA_980TI = 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814487142'  

parser = configparser.ConfigParser()
parser.read('config.ini')
EMAIL_ADDR_FROM = parser.get('email_info', 'email')
EMAIL_PW = parser.get('email_info', 'password')
EMAIL_ADDR_TO = ['weirdotomli@gmail.com'] 

def main():
    driver = webdriver.PhantomJS()
    driver.set_page_load_timeout(45)
    item_status = dict.fromkeys(URLS, False)

    try:
        while True:
            for item, url in URLS.iteritems(): 
                print('checking: ' + item)
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