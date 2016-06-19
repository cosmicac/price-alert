from selenium import webdriver
import smtplib as smtp

URL_1080 = 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814487243'
URL_980 = 'http://www.newegg.com/Product/Product.aspx?Item=N82E16814487142'	 

urls = [URL_1080]


def main():
	driver = webdriver.PhantomJS()
	item_status = dict.fromkeys(urls, False)

	try:
		while True:
			for url in urls: 
				before_in_stock = item_status[url]
				current_in_stock = check_stock(driver, url)
				if not before_in_stock and in_stock:
					price_element = driver.find_element_by_xpath("//ul[@class='price has-label-membership price-product-cells price-main-product']//li[@class='price-current']")
					send_emails(url, price_element.text)
				item_status[url] = current_in_stock

	except KeyboardInterrupt:
		print('Quitting...')
		driver.quit()

if __name__ == "__main__":
	main()

def check_stock(driver, url):
	driver.get(url)
	stock_element = driver.find_element_by_id('landingpage-stock')
	return stock_element.text == 'OUT OF STOCK.'

def send_emails(url, price):
	

