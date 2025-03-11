import os
import time
import random
import logging
from behave import *
from log_msg import *
from details import *
from selenium import webdriver
from common import FindElement
from common import * 
from locators import Locators
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from WhatsappOrderPlacementWithDiscount import *
from UpdateOrderStatusByPartner import *
from  CheckPayInAmount import *
from common import *
from API import PaymentSettlement
from  VerifyOrderWhenCustomerCancelledPODOrderatPlacedState import*
# settle_details = {}


findelement = FindElement()
wait = FindElement()
current_file_name = os.path.basename(__file__)
new_file_name = os.path.splitext(current_file_name)[0] + ".png"

def findelement(context, path):
    return WebDriverWait(context.driver, 25, 1).until(EC.element_to_be_clickable((By.XPATH, path)))

def presence_of_element_located(self, context, xpath):
        return WebDriverWait(context.driver, 30).until(
            EC.presence_of_element_located((By.XPATH, xpath)))

customer_invoice = {}
platform_charges = {}
tax_deduction = {}
Netpayment = {}



@then(u'Enter only ManualDC No')
def step_impl(context):
    try:
        time.sleep(1)
        global manual_dc
        obj = Details()
        driver_mobile, driver_name, added_tons, manual_dc = obj.trip_details()
        manual_dc_path = "//input[@placeholder='ManualDc No']"
        manual_dc_no = findelement(context,manual_dc_path)
        manual_dc_no.send_keys(manual_dc)
        time.sleep(0.5)

    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(Error.Enter_ManualDC_No.format(str(e)))
        context.driver.close()
        raise Exception from e

@when(u'search the orderid')
def step_impl(context):
    try:
        global order_to_be_searched
        order_to_be_searched = order_id_method(context)
        time.sleep(3)
        order_id = context.driver.find_element(By.XPATH, Locators.order_id_search ).send_keys(order_to_be_searched)
        time.sleep(1)
        search_bar = context.driver.find_element(By.XPATH, Locators.oms_search_button).click()
        time.sleep(5)
  
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(Error.search_the_orderid.format(str(e)))
        context.driver.close()
        raise Exception from e



@when(u'get the orderid details and hit the API')
def step_impl(context):
    global order_to_be_searched
    oms_order_details = ex.orderdetails(context)  #### orderdetails1() is in random_var.py file, it returns all the order details in a list #####
    time.sleep(1)
    logging.info(f"Order details of order {order_to_be_searched} is: {oms_order_details}")
    for order in oms_order_details:
        payment_status = order[6]
        order_status = order[8]
        if payment_status == "Paid" and order_status == "Delivered":
           payload = {
            "order_id": order[0],
            "payment_method": order[5],
            "order_status": order_status,
           }
           order_to_be_searched = order_id_method(context)
           obj = PaymentSettlement()
           obj.HitAPIwithOrderid(order[0])
           logging.info(order[0])
           logging.info("payment succesfull")
        
        else:
            logging.info("payment not succesfull")
            break
        

@when(u'store the payment mode')
def step_impl(context):  
    global payment_text
    try:
        time.sleep(2)
        amount = context.driver.find_element(By.XPATH,"//span[@class='mat-mdc-tooltip-trigger ng-star-inserted']")
        amount_text = amount.text
        logging.info(f"payment (oms)is: {amount_text}")
        context.amount_oms = amount_text
        payment = context.driver.find_element(By.XPATH,"//td[normalize-space()='NetBanking']")
        payment_text = payment.text
        logging.info(f"payment is(oms): {payment_text}")
        context.payment = payment_text
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        context.driver.close()
        raise Exception from e

@then(u'Navigate to Cost master page and store the order deatais')
def step_impl(context):
   global orders, order_to_be_searched,customer_invoice,platform_charges, tax_deduction ,Netpayment
   try:
        time.sleep(3)
        # hamburger_button = context.driver.find_element(By.XPATH, Locators.Hamburger_path)
        # hamburger_button.click()
        # time.sleep(2)
        account = wait.to_be_clickable(context, Locators.accounts_menu_xpath)
        account.click()
        time.sleep(1)
        cost_master = wait.to_be_clickable(context, Locators.cost_master_menu)
        cost_master.click()
        time.sleep(5)
        logging.info(Info.show_cost_master_page)
        order_to_be_searched = order_id_method(context)
        context.driver.find_element(By.XPATH, Locators.all_user_search ).send_keys(order_to_be_searched)
        time.sleep(1)
        search_button = context.driver.find_element(By.XPATH,Locators.oms_search_button)
        search_button.click()
        time.sleep(3)
        logging.info("Search button clicked")
        # while True:
        #     rows = context.driver.find_elements(By.XPATH, Locators.oms_rows)
        #     row_count = len(rows)
        #     if row_count == 0:
        #         break
        try:
            time.sleep(4)
            ##******** Below code is to get the cost master calculation details of the order from cost master into temp_dict ************##
            data = context.driver.find_element(By.XPATH,"//tbody/tr[1]/td[10]/a[1]/i[1]")
            data.click()
            time.sleep(1)
            columns = context.driver.find_elements(By.XPATH, "//app-cost-splitup/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr")
            for i in range(1, len(columns) + 1):
                key_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[{i}]/td[1]'
                value_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[1]/div[2]/div/table/tbody/tr[{i}]/td[2]'
                key = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, key_xpath))).text
                value = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, value_xpath))).text
                customer_invoice[key] = value
            logging.info(f"Customer invoice details are: {customer_invoice}")
            context.customer_invoice = customer_invoice

            # Extract Platform and Service Charges
            time.sleep(0.5)
            context.driver.find_element(By.XPATH, "//button[normalize-space()='Platform and Service Charges']").click()
            time.sleep(1)
            columns = context.driver.find_elements(By.XPATH,"//app-cost-splitup/div/div[2]/div[2]/div[2]/div[2]/div/table/tbody/tr")
            for i in range(1, len(columns) + 1):
                key_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[2]/div[2]/div/table/tbody/tr[{i}]/td[1]'
                value_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[2]/div[2]/div/table/tbody/tr[{i}]/td[2]'
                key = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, key_xpath))).text
                value = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, value_xpath))).text
                platform_charges[key] = value
            logging.info(f"Platform and service charges are: {platform_charges}")
            context.platform_charges = platform_charges

            # Extract Tax Deduction Details
            time.sleep(0.5)
            context.driver.find_element(By.XPATH, "//button[normalize-space()='Tax Deduction']").click()
            time.sleep(1)
            columns = context.driver.find_elements(By.XPATH,"//app-cost-splitup/div/div[2]/div[2]/div[3]/div[2]/div/table/tbody/tr")
            for i in range(1, len(columns) + 1):
                key_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[3]/div[2]/div/table/tbody/tr[{i}]/td[1]'
                value_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[3]/div[2]/div/table/tbody/tr[{i}]/td[2]'
                key = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, key_xpath))).text
                value = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, value_xpath))).text
                tax_deduction[key] = value
            logging.info(f"Tax deductions are: {tax_deduction}")
            context.tax_deduction = tax_deduction

            # Extract Net Payment Details
            time.sleep(0.5)
            context.driver.find_element(By.XPATH, "//button[normalize-space()='Net Payment']").click()
            time.sleep(1)
            columns = context.driver.find_elements(By.XPATH,"//app-cost-splitup/div/div[2]/div[2]/div[4]/div[2]/div/table/tbody/tr")
            for i in range(1, len(columns) + 1):
                key_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[4]/div[2]/div/table/tbody/tr[{i}]/td[1]'
                value_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[4]/div[2]/div/table/tbody/tr[{i}]/td[2]'
                key = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, key_xpath))).text
                value = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, value_xpath))).text
                Netpayment[key] = value
            logging.info(f"Net payments are: {Netpayment}")
            context.Netpayment = Netpayment

            # Extract Analysis Details
            time.sleep(0.5)
            context.driver.find_element(By.XPATH, "//button[normalize-space()='Analysis']").click()
            time.sleep(1)
            columns = context.driver.find_elements(By.XPATH,'//app-cost-splitup/div/div[2]/div[2]/div[5]/div[2]/div/table/tbody/tr')
            Analysis = {}
            for i in range(1, len(columns) + 1):
                key_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[5]/div[2]/div/table/tbody/tr[{i}]/td[1]'
                value_xpath = f'//app-cost-splitup/div/div[2]/div[2]/div[5]/div[2]/div/table/tbody/tr[{i}]/td[2]'
                key = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, key_xpath))).text
                val = WebDriverWait(context.driver, 10).until(EC.presence_of_element_located((By.XPATH, value_xpath))).text
                Analysis[key] = val
            logging.info(f'Analysis are: {Analysis}')
            time.sleep(2)
            # return customer_invoice,platform_charges,tax_deduction,Netpayment
            close_button = context.driver.find_element(By.XPATH,"//div[@class='prism-toggle']")
            close_button.click()
            logging.info("clicked on close button")
            time.sleep(1)
        except Exception as e:
            time.sleep(1)
            context.driver.save_screenshot(f"./{new_file_name}")
            logging.error(f'Error occurred at Get all the costmaster calculation details of the order: {str(e)}')
            context.driver.close()
            raise Exception from e
            
        ###############**************** END ******************#######################
   except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Error occurred at Get all the costmaster calculation details of the order: {str(e)}')
        context.driver.close()
        raise Exception from e



@when(u'Navigate to Master Settings page and store the Charges and Preference pages details')
def step_impl(context):
     global charges_data
     try:
        time.sleep(1)
        account = context.driver.find_element(By.XPATH, Locators.accounts_menu_xpath)
        account.click()
        time.sleep(3)
        master = context.driver.find_element(By.XPATH, Locators.master_settings_xpath)
        master.click()
        logging.info("clicked on master settings")
        time.sleep(1)
        master_page_settings = context.driver.find_element(By.XPATH, Locators.master_page_path)
        master_page_settings.click()
        logging.info("clicked on master")
        time.sleep(2)
        logging.info(Info.master_page)
        time.sleep(4)
        # ####### Below code is to get all the charges into a list #########
        time.sleep(3)
        charges_tab = context.driver.find_element(By.XPATH, Locators.charges_xpath)
        charges_tab.click()
        logging.info("Successfully clicked on charges")
        time.sleep(4)
        charges_data = ex.tablevalues1(context)  #### tablevalues1() is in random_var.py file, returns Preferences details in a list #####
        logging.info(f"charges data is: {charges_data}")
        context.charges_data = charges_data
        ####### Below code is to get all the Preferences details into a list #########
        context.driver.execute_script(Locators.scroll_down)
        time.sleep(3)
        preferences_list = []
        preferences_tab = wait.presence_of_element_located(context, Locators.master_miscellaneous_tab)
        preferences_tab.click()
        time.sleep(3)
        preferences_list = ex.tablevalues1(context)  #### tablevalues1() is in random_var.py file, returns Preferences details in a list #####
        logging.info(f"preferences details are: {preferences_list}")
        time.sleep(2)
     except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(
            f'Error occurred at navigate to Master Settings page and store the Charges and Preference pages details: {str(e)}')
        context.driver.close()
        raise Exception from e

@then(u'Navigate to PayIn page and search the order id')
def step_impl(context):
    global order_to_be_searched
    try:
        order_to_be_searched = order_id_method(context)
        time.sleep(3)
        Accounts_tab = wait.presence_of_element_located(context, Locators.accounts_menu_xpath)
        Accounts_tab.click()
        logging.info("Clicked on accounts tab")
        time.sleep(1)
        pay_in_page = context.driver.find_element(By.XPATH, Locators.pay_in_page)
        pay_in_page.click()
        logging.info("clicked on payin page")
        time.sleep(1)
        esales = context.driver.find_element(By.XPATH,Locators.payin_digitalsales)
        esales.click()
        logging.info("clicked on esales tab")
        time.sleep(5)
        search_order_id = context.driver.find_element(By.XPATH,Locators.payin_orderid)
        search_order_id.send_keys(order_to_be_searched)
        logging.info(f'searched orderid: {order_to_be_searched}')
        time.sleep(5)
        search = context.driver.find_element(By.XPATH, Locators.payin_search)
        search.click()
        logging.info("Search button clicked")
        time.sleep(3)
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error("Navigate to PayIn page and search the order ID:")
        logging.exception(e)
        context.driver.close()
        raise 

@then(u'Verify the Transaction Ref no, Date of Settlement,Status and Payment Gateway')
def step_impl(context):
    try:
        global no_payin_orders,order_to_be_searched,payinpage_details

        payinpage_details = []
        payinpage_detail = context.driver.find_element(By.XPATH, '//table/tbody/tr').text
        payinpage_detail = payinpage_detail.replace(" ", ",")
        payinpage_details = payinpage_detail.split(",")
        logging.info(f"Pay-in page details as list: {payinpage_details}")
        no_payin_orders = 0
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify the Transaction Ref no, Date of Settlement,Status and Payment Gateway: {str(e)}')
        context.driver.close()
        raise Exception from e
       
@then(u'Total Invoice = ( (Total Bill amount) - (Total Bill amount * (Accounting Fee % from Master | Charges page)) )')
def step_impl(context):
    global accounting_info,Total_invoice1,accounting_fee2,payinpage_details
    try:
        payinamount = payinpage_details[2]
        logging.info(f"Amount in payin page is: {payinamount}")
        time.sleep(1)
        account = context.driver.find_element(By.XPATH, Locators.accounts_menu_xpath)
        account.click()
        time.sleep(1)
        master = context.driver.find_element(By.XPATH, Locators.master_settings_xpath)
        master.click()
        logging.info("clicked on master settings")
        time.sleep(1)
        master_page_settings = context.driver.find_element(By.XPATH, Locators.master_page_path)
        master_page_settings.click()
        logging.info("clicked on master")
        time.sleep(5)
        charges_tab = wait.to_be_clickable(context, Locators.charges_xpath)
        charges_tab.click()
        logging.info("Successfully clicked on charges")
        time.sleep(3)
        global charges_data
        for row in charges_data:
            if "Accounting Fee %" in row:
                # row_lines = row.split(',')
                logging.info(f"Accounting fee row is: {row}")
                accounting_fee = row[1].strip()
                accounting_fee1 = float(accounting_fee)
                accounting_fee2 = accounting_fee1 / 100
                logging.info(f"accounting_fee2 is: {accounting_fee2}")
        total_invoice_costmaster = float(customer_invoice.get('Before Adj of Total Invoice', 'Value not found'))
        logging.info(f"Total invoice value from cost master: {total_invoice_costmaster}")
        Total_Invoice = float(total_invoice_costmaster * accounting_fee2)
        logging.info(f"Total_Invoice:{Total_Invoice}")
        Total_invoice_amount_byformula = float(total_invoice_costmaster - Total_Invoice)
        logging.info(f"Total invoice amount by formula is:{Total_invoice_amount_byformula}")
        payinamount1 = float(payinamount)
        assert (payinamount1 <= Total_invoice_amount_byformula + 1) and (payinamount1 >= Total_invoice_amount_byformula - 1), "Both amounts are different"
        logging.info("Both amounts are same")
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Total Invoice = ( (Total Bill amount) - (Total Bill amount * (Accounting Fee % from Master | Charges page: {str(e)}')
        context.driver.close()
        raise Exception from e
    
        


@when(u'Navigate to Request for Settle page')
def step_impl(context):
    try:
        time.sleep(2)
        account = context.driver.find_element(By.XPATH, Locators.accounts_menu_xpath)
        account.click()
        time.sleep(1)
        settle = context.driver.find_element(By.XPATH, Locators.request_for_settle_page)
        settle.click()
        logging.info("navigated to request for settle page")
        time.sleep(0.5)
 
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Navigate to Request for Settle page: {str(e)}')
        context.driver.close()
        raise Exception from e


@then(u'Verify the user in Aggregate tab')
def step_impl(context):
    try:
        time.sleep(0.5)
        user = context.driver.find_element(By.XPATH, Locators.request_for_settle_aggregate)
        user_text = user.text
        logging.info(f"User in '{user_text}' tab")
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify the user in Aggregate tab: {str(e)}')
        context.driver.close()
        raise Exception from e
    


@then(u'Set Select status as Payout, Select Company name and date range then Click on search button')
@when(u'Set Select status as Payout, Select Company name and date range then Click on search button')
def step_impl(context):
     try:
        time.sleep(8)
        status = context.driver.find_element(By.XPATH, Locators.request_for_settle_select_status )
        status.click()
        time.sleep(1)
        payout = context.driver.find_element(By.XPATH, Locators.request_for_settle_payout)
        payout.click()
        time.sleep(1)
        select_company = context.driver.find_element(By.XPATH, Locators.cost_master_company)
        select_company.click()
        time.sleep(1)
        logging.info("selected the company")
        order_id = order_id_method(context)
        parts = order_id.split("-")
        pattern = r"^[A-Za-z]\d*$"
        first_prefix = parts[0] if len(parts) > 0 else ""
        # Log the extracted prefixes
        logging.info(f"First Prefix: {first_prefix}")
        context.first_prefix = first_prefix

        logging.info(f"prefix part is : {first_prefix}")
        wait = WebDriverWait(context.driver, 10)
        search_xpath = "(//input[@placeholder = 'Search...'])[2]"
        search_bar = context.driver.find_element(By.XPATH, search_xpath)
        time.sleep(1)
        search_bar.click()
        time.sleep(3)
        search_bar.send_keys(first_prefix)
        time.sleep(1)
        company = context.driver.find_element(By.XPATH,"//div[2]/div/div/div/form/div/div[2]/div/app-custom-select/div/div[2]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div[1]")
        company.click()
        time.sleep(4)      
        calender = context.driver.find_element(By.XPATH, Locators.calender_xpath)
        calender.click()
        time.sleep(2)
        today_date = datetime.date.today()
        old_date = today_date - datetime.timedelta(days=3)
        t_date = today_date.strftime("%d-%B-%Y").split('-')
        o_date = old_date.strftime("%d-%B-%Y").split('-')
        a = o_date
        j = 1
        logging.info(f"Date range is from {old_date} to {today_date}")
        while j < 3:
            time.sleep(1)
            months = context.driver.find_element(By.XPATH, Locators.cost_master_months)
            months.click()
            i = 2
            while i >= 0:
                all_dates = context.driver.find_elements(By.XPATH, Locators.cost_master_dates_year)
                if i == 1:
                    all_dates = context.driver.find_elements(By.XPATH, Locators.cost_master_dates_month)
                if i == 0:
                    all_dates = context.driver.find_elements(By.XPATH, Locators.cost_master_dates_day)
                for date in all_dates:
                    if i == 2:
                        if date.text == a[i]:
                            date.click()
                            i = i - 1
                            time.sleep(1)
                            break
                    elif i == 0:
                        if date.text == str(int(a[i])):
                            date.click()
                            i = i - 1
                            time.sleep(1)
                            break
                    else:
                        if date.text in a[1].upper():
                            time.sleep(1)
                            date.click()
                            i = i - 1
                            time.sleep(1)
                            break
            j = j + 1
            a = t_date
        search_button = context.driver.find_element(By.XPATH,Locators.payout_search)
        search_button.click()
        logging.info("clicked on search button")
        time.sleep(5)
 
     except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Set Select status as Payout, Select Company name and date range then Click on search button: {str(e)}')
        context.driver.close()
        raise Exception from e


@then(u'Verify the order id should be same, Payment mode should be Net Banking')
def step_impl(context):
    try:
        global settle_details,settle_amount,settle_status,settle_orderstatus
        settle_details = []
        time.sleep(1)
        context.driver.execute_script(Locators.scroll_middle)
        time.sleep(1)
        settle_orderid = settle_paymentmethod = settle_amount = settle_status = settle_orderstatus = None
        while True:
            table = context.driver.find_elements(By.XPATH, "//table//tr")
            if not table:
                logging.info("Table not found. Exiting loop.")
                break

            for row in table:
                row_text = row.text.replace('\n', ',')  # Replace line breaks with commas
                settle_details.append(row_text)

                if order_to_be_searched in row_text:
                    logging.info(f"Order ID {order_to_be_searched} found: {row_text}")
                    elements = row_text.split()  # Use .split(',') if comma-separated
                    settle_orderid = elements[0]
                    settle_paymentmethod = elements[1]
                    settle_amount = elements[2]
                    settle_status = elements[3]
                    settle_orderstatus = elements[5]
                    logging.info(f"Settle Order ID: {settle_orderid}")
                    logging.info(f"Settle Payment Method: {settle_paymentmethod}")
                    logging.info(f"Settle Amount: {settle_amount}")
                    logging.info(f"Settle Status: {settle_status}")
                    logging.info(f"Settle order status is: {settle_orderstatus}")
                    context.settle_amount = settle_amount
                    context.settle_status = settle_status
                    assert order_to_be_searched == settle_orderid , "Both order IDs are different"
                    logging.info("Both order IDs are the same")
                    assert payment_text == settle_paymentmethod, "Both payment methods are different"
                    logging.info("Both payment methods are the same from OMS and settled page") 
                    logging.info(f"Settle details collected: {settle_details}")
                    return True
            next_button = context.driver.find_element(By.XPATH, Locators.next_button_xpath)
            if next_button.is_enabled():
                next_button.click()
                time.sleep(1)  # Wait for the next page to load
            else:
                logging.info("Reached the last page. Order ID not found.")
                break
        return False

    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify the order id should be same, Payment mode should be Net Banking: {str(e)}')
        context.driver.close()
        raise Exception from e
    
@then(u'Verify Aggregate Amount = Total Aggregate Value from Cost master page')
def step_impl(context):
    global customer_invoice,settle_amount
    try:
        total_aggregate_value = customer_invoice.get('Before Adj of Total Aggregate Value', 'Value not found')
        logging.info(f"Total Aggregate Value is: {total_aggregate_value}")
        assert total_aggregate_value == settle_amount, "Both Aggregate amount and Total aggregate value from costmaster page are different"
        logging.info("Both Aggregate amount and Total aggregate value from costmaster page are same")
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify Aggregate Amount = Total Aggregate Value from Cost master page: {str(e)}')
        context.driver.close()
        raise Exception from e
        


@then(u'Verify Page status should be paid')
def step_impl(context):
    global settle_status
    try:
        expected = "Paid"
        assert settle_status == expected, f"Expected payment status to be '{expected}', but got '{settle_status}'"
        logging.info("Payment status is 'Paid'.")
       
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify Page status should be paid: {str(e)}')
        context.driver.close()
        raise Exception from e


@then(u'Verify Net Payment = (Aggregate charges) - (Platform Services Charges for Aggregate) - (Income Tax TDS Aggregate) - (GST TCS Aggregate(E commerce)) from cost master page')
def step_impl(context):
    try:
        global customer_invoice,platform_charges,tax_deduction
        aggregate_value = float(customer_invoice.get('Before Adj of Aggregate Charges', 'Value not found'))
        logging.info(f"aggregate charges: {aggregate_value}")
        platfrom_serv_charges = float(platform_charges.get('Before Adj of Platform Services Charges for Aggregate','Value not found'))
        logging.info(f"platform_service_charges for aggregate: {platfrom_serv_charges}")
        income_tax_tds = float(tax_deduction.get('Before Adj of Income Tax TDS Aggregate','Value not found'))
        logging.info(f"tax_deductions_TDS for agg: {income_tax_tds}")
        gst_tcs_agg = float(tax_deduction.get('Before Adj of GST TCS Aggregate (E commerce)','Value not found'))
        logging.info(f"gst_tcs_aggregate: {gst_tcs_agg}")
        net_payment = aggregate_value - platfrom_serv_charges -income_tax_tds - gst_tcs_agg
        Net_Payment= round(net_payment,2)
        logging.info(f"Net payment for aggregate is:{ Net_Payment}")
        Netpayment_costmaster = float(Netpayment.get('Before Adj of Net Payment for Aggregate', 'Value not found'))
        logging.info(f"Netpaymnet for aggregate in costmaster:{Netpayment_costmaster}")
        assert (Net_Payment <= Netpayment_costmaster + 3) and (Net_Payment >= Netpayment_costmaster - 3), "Both are different"
        logging.info("Both amounts are same")
        # if Net_Payment == Netpayment_costmaster:
        #     logging.info(f"Both values are same:{Net_Payment,Netpayment_costmaster}")
        # else:
        #     logging.info('Both values are different')
        context.net_pay =  Net_Payment
    
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'VerifyNet Payment = (Aggregate charges) - (Platform Services Charges for Aggregate) - (Income Tax TDS Aggregate) - (GST TCS Aggregate(E commerce)) from cost master page: {str(e)}')
        context.driver.close()
        raise Exception from e

@then(u'Verify order Status should be delivered')
def step_impl(context):
    global settle_orderstatus
    try:
        expected= "Delivered"
        assert expected == settle_orderstatus, f"Expected order status to be '{expected}', but got '{settle_orderstatus}'"
        logging.info("Order status is 'delivered'.")
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify order Status should be delivered: {str(e)}')
        context.driver.close()
        raise Exception from e

@when(u'Select the order id')
def step_impl(context):
    global order_to_be_searched
    try:
        time.sleep(2)
        order_to_be_searched = order_id_method(context)
        search = context.driver.find_element(By.XPATH,"//input[@placeholder='Search..']")
        search.send_keys(order_to_be_searched)  
        time.sleep(6)      
        select_id = context.driver.find_element(By.XPATH,"//table/tbody/tr/td[1]/input")
        select_id.click()
        time.sleep(2)

    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Select the order id: {str(e)}')
        context.driver.close()
        raise Exception from e

@then(u'Send that order id for Approve for Settle.')
def step_impl(context):
    try:
        time.sleep(1)
        approve_for_settle = context.driver.find_element(By.XPATH,Locators.approveforsettle)
        approve_for_settle.click()
        time.sleep(1)
        click_yes = context.driver.find_element(By.XPATH,Locators.yesbutton)
        click_yes.click()
        time.sleep(1)
        logging.info("approved for settle")
        success_msg = WebDriverWait(context.driver, 60, 1).until(EC.visibility_of_element_located((By.XPATH, Locators.container2_xpath))).text
        assert success_msg == "Processing: Reconcile is updated successfully"
        logging.info(f"Pop up message is: {success_msg}")
        time.sleep(4)
        context.driver.execute_script(Locators.scroll_up)
        time.sleep(1)

        
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Send that order id for Approve for Settle: {str(e)}')
        context.driver.close()
        raise Exception from e


@when(u'Navigate to Logistics tab')
def step_impl(context):
    try:
        time.sleep(3)
        logistics_tab = wait.presence_of_element_located(context, Locators.master_logistic_tab)
        logistics_tab.click()
        time.sleep(0.5)
        logging.info("navigated to logistics tab")

    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Navigate to Logistics tab: {str(e)}')
        context.driver.close()
        raise Exception from e


@then(u'Verify the user in Logistics tab')
def step_impl(context):
    try:
        time.sleep(0.5)
        logistics_tab = wait.presence_of_element_located(context, Locators.master_logistic_tab)
        logistics_tab_text = logistics_tab.text
        logging.info(f"user in {logistics_tab_text} tab")
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify the user in Logistics tab: {str(e)}')
        context.driver.close()
        raise Exception from e

    
    
@then(u'Verify Logistics Amount = Total Logistics Value from Cost master page')
def step_impl(context):
    global settle_amount
    try:
        time.sleep(0.3)
        total_logistics_value = customer_invoice.get('Total Logistics Value', 'Value not found')
        logging.info(f"Total logistics value from costmasterpage is: {total_logistics_value}")
        assert total_logistics_value == settle_amount, "Both logistics amount and total logistics value from cost master page is different"
        logging.info("Both logistics amount and total logistics value from cost master page is same")
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify Logistics Amount = Total Logistics Value from Cost master page: {str(e)}')
        context.driver.close()
        raise Exception from e


@then(u'Verify Net Payment = (Logistics charges) - (Platform Services Charges for Logistics) - (Income Tax TDS Logistics) - (GST TCS Logistics(E commerce)) from cost master page')
def step_impl(context):
    global customer_invoice,Netpayment,tax_deduction,platform_charges
    try:
        logistic_charges =  float(customer_invoice.get('Logistics Charges', 'Value not found'))
        logging.info(f"Total logistics value from costmasterpage is: {logistic_charges}")
        
        platfrom_charges_logistics = float(platform_charges.get('Platform Service Charges for Logistics','Value not found'))
        logging.info(f"platform_service_charges for logistics: {platfrom_charges_logistics}")
        
        income_tax_tds_log = float(tax_deduction.get('Income Tax TDS Logistic','Value not found'))
        logging.info(f"tax_deductions_TDS for logistics: {income_tax_tds_log}")
        
        gst_tcs_log = float(tax_deduction.get('GST TCS Logistic\n(E commerce)','Value not found'))
        logging.info(f"gst_tcs_aggregate: {gst_tcs_log}")
        net_payment_log = logistic_charges - platfrom_charges_logistics -  income_tax_tds_log - gst_tcs_log
        net_payment_logistics = round(net_payment_log, 2)
        logging.info(f'net payement for logistics:{net_payment_logistics}')
        Netpaymentlog_costmaster = float(Netpayment.get('Net Payment for Logistic'))
        logging.info(f"netpayment for logistics from costmaster :{Netpaymentlog_costmaster}")
        assert (net_payment_log <= Netpaymentlog_costmaster + 1) and (net_payment_log >= Netpaymentlog_costmaster - 1), "Both values for netpayment for logistics are different"
        logging.info("Both values for netpayment for logistics are same")
        context.net_pay_log = net_payment_log

    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify Net Payment = (Logistics charges) - (Platform Services Charges for Logistics) - (Income Tax TDS Logistics) - (GST TCS Logistics(E commerce)) from cost master page: {str(e)}')
        context.driver.close()
        raise Exception from e

@then(u'show the Payout settle page for e-Sales')
def step_impl(context):
     try:
        time.sleep(1)
        account = wait.to_be_clickable(context, Locators.accounts_menu_xpath)
        account.click()
        time.sleep(0.5)
        payout_settle = context.driver.find_element(By.XPATH, "//a[normalize-space()='Pay Out Settle']")
        payout_settle.click()
        time.sleep(0.5)
        context.driver.find_element(By.XPATH, "//a[normalize-space()='e-sales']").click()
        time.sleep(1)
        logging.info("clicked on payoutsettle")
     except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'show the Payout settle page for e-Sales: {str(e)}')
        context.driver.close()
        raise Exception from e

@then(u'Search Order id from the list')
def step_impl(context):
    try:
        global payout_settle
        order_to_be_searched = order_id_method(context)
        context.driver.find_element(By.XPATH, "//input[@placeholder='Search..']").send_keys(order_to_be_searched)
        # search = context.driver.find_element(By.XPATH, "//app-comp-reconc-approval/div/div[2]/div/div/div/div/div[2]/div/div/section/mat-form-field/div[1]/div/div[2]/input")
        # search.send_keys(order_to_be_searched)
        # time.sleep(1)
        # logging.info("search orderid")
        # search_button = context.driver.find_element(By.XPATH, "//button[@type='submit']//span[@class='mdc-button__label']")
        # search_button.click()
        time.sleep(2) 
        payout_settle =  []
        while True:
            i=0      
            table = context.driver.find_elements(By.XPATH, "//table/tbody/tr")
            if not table:
                logging.info("Table not found. Exiting loop.")
                break
            for i in range(0, min(5, len(table))):
                row_text = table
                row_text = table[i].text.replace('\n',',')
                payout_settle.append(row_text)
                time.sleep(0.5)
            next_button = context.driver.find_element(By.XPATH, Locators.next_button_xpath)
            if next_button.is_enabled():
                next_button.click()
            else:
                break
        logging.info(f"payout_settle data:{ payout_settle}")
 
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Search Order id from the list: {str(e)}')
        context.driver.close()
        raise Exception from e
    
@when(u'Select the order id in payout settle')
def step_impl(context):
    try:
        time.sleep(3)
        global order_to_be_searched
        order_to_be_searched = order_id_method(context)
        search = context.driver.find_element(By.XPATH,"//input[@placeholder='Search..']")
        search.send_keys(order_to_be_searched)  
        time.sleep(1)      
        select_id = context.driver.find_element(By.XPATH,"//table/tbody/tr[1]/td[1]/input")
        select_id.click()
        time.sleep(2) 
        logging.info("slected the order id in payout settle page")
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Select the order id in payout settle: {str(e)}')
        context.driver.close()
        raise Exception from e
    


@then(u'Settle the order amount with Cash settle option.')
def step_impl(context):
    try:
        order_to_be_searched = order_id_method(context)
        time.sleep(4)
        cash_settle = context.driver.find_element(By.XPATH, Locators.cashsettle)
        cash_settle.click()
        logging.info("clicked on cash for settle tab")
        reference_no = context.driver.find_element(By.XPATH,"//input[@placeholder='Reference No']")
        reference_no.send_keys(order_to_be_searched)
        reason = context.driver.find_element(By.XPATH,"//textarea[@placeholder='Reason']")
        reason.send_keys("dfghjklfghjkml")
        time.sleep(2)
        submit = context.driver.find_element(By.XPATH,"//button[normalize-space()='Submit']").click()
        success_msg = WebDriverWait(context.driver, 60, 1).until(EC.visibility_of_element_located((By.XPATH, Locators.container2_xpath))).text
        assert success_msg == "Processing: Reconcile is updated successfully"
        logging.info(f"Pop up message is: {success_msg}")
        time.sleep(4)
        context.driver.execute_script(Locators.scroll_up)
        time.sleep(1)
        
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Settle the order amount with Cash settle option: {str(e)}')
        context.driver.close()
        raise Exception from e

    


@when(u'Naviagate to Request for settle page')
def step_impl(context):
    try:
        # time.sleep(3)
        # hamburger_button = context.driver.find_element(By.XPATH, Locators.Hamburger_path)
        # hamburger_button.click()
        # logging.info("Clicked on hamburger")
        time.sleep(1)
        account = wait.to_be_clickable(context, Locators.accounts_menu_xpath)
        account.click()
        time.sleep(1)
        settle = context.driver.find_element(By.XPATH, Locators.request_for_settle_page)
        settle.click()
        time.sleep(1)
        logging.info("Navigated to request for settle page")
 
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Naviagate to Request for settle page: {str(e)}')
        context.driver.close()
        raise Exception from e

@then(u'Then Verify the user in Aggregate tab')
def step_impl(context):
    try:
        time.sleep(0.5)
        user = context.driver.find_element(By.XPATH, "//a[normalize-space()='Aggregate']")
        user_text = user.text
        logging.info(f"User in aggregate '{user_text}' tab")

    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify the user in Aggregate tab: {str(e)}')
        context.driver.close()
        raise Exception from e
    


@then(u'Set Select status as PaidOut, Select Company name and date range then Click on search button')
def step_impl(context):
    try:
        time.sleep(4)
        status = context.driver.find_element(By.XPATH, Locators.request_for_settle_select_status )
        status.click()
        time.sleep(1)
        paidout = context.driver.find_element(By.XPATH, Locators.request_for_settle_paidout)
        paidout.click()
        time.sleep(1)
        select_company = context.driver.find_element(By.XPATH, Locators.cost_master_company)
        select_company.click()
        time.sleep(1)
        logging.info("selected the company")
        order_id = order_id_method(context)
        parts = order_id.split("-")
        pattern = r"^[A-Za-z]\d*$"
        first_prefix = parts[0] if len(parts) > 0 else ""
        logging.info(f"First Prefix: {first_prefix}")
        context.first_prefix = first_prefix
        # context.second_prefix = second_prefix

        logging.info(f"prefix part is : {first_prefix}")
        wait = WebDriverWait(context.driver, 10)
        search_xpath = "(//input[@placeholder = 'Search...'])[2]"
        search_bar = context.driver.find_element(By.XPATH, search_xpath)
        search_bar.click()
        time.sleep(3)
        search_bar.send_keys(first_prefix)
        time.sleep(1)
        company = context.driver.find_element(By.XPATH,"//div[2]/div/div/div/form/div/div[2]/div/app-custom-select/div/div[2]/div/div[2]/cdk-virtual-scroll-viewport/div[1]/div[1]")
        company.click()
        time.sleep(4)      
        calender = context.driver.find_element(By.XPATH, Locators.calender_xpath)
        calender.click()
        time.sleep(2)
        today_date = datetime.date.today()
        old_date = today_date - datetime.timedelta(days=3)
        t_date = today_date.strftime("%d-%B-%Y").split('-')
        o_date = old_date.strftime("%d-%B-%Y").split('-')
        a = o_date
        j = 1
        logging.info(f"Date range is from {old_date} to {today_date}")
        while j < 3:
            time.sleep(1)
            months = context.driver.find_element(By.XPATH, Locators.cost_master_months)
            months.click()
            i = 2
            while i >= 0:
                all_dates = context.driver.find_elements(By.XPATH, Locators.cost_master_dates_year)
                if i == 1:
                    all_dates = context.driver.find_elements(By.XPATH, Locators.cost_master_dates_month)
                if i == 0:
                    all_dates = context.driver.find_elements(By.XPATH, Locators.cost_master_dates_day)
                for date in all_dates:
                    if i == 2:
                        if date.text == a[i]:
                            date.click()
                            i = i - 1
                            time.sleep(1)
                            break
                    elif i == 0:
                        if date.text == str(int(a[i])):
                            date.click()
                            i = i - 1
                            time.sleep(1)
                            break
                    else:
                        if date.text in a[1].upper():
                            time.sleep(1)
                            date.click()
                            i = i - 1
                            time.sleep(1)
                            break
            j = j + 1
            a = t_date
        search_button = context.driver.find_element(By.XPATH,Locators.payout_search)
        search_button.click()
        logging.info("clicked on search button")
        time.sleep(5)

    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Set Select status as PaidOut, Select Company name and date range then Click on search button: {str(e)}')
        context.driver.close()
        raise Exception from e
 

@then(u'Verify the order id should be visible in the orders list')
def step_impl(context):
    try:
        global orders, order_to_be_searched,order_status
        time.sleep(2)
        # order_to_be_searched = order_id_method(context)
        # time.sleep(5)
        # search = context.driver.find_element(By.XPATH,"//mat-form-field/div[1]/div/div[2]/input")
        # search.send_keys(order_to_be_searched)
        # time.sleep(1)
        # logging.info("searched orderid")
        context.driver.execute_script(Locators.scroll_middle)
        global settle_details
        settle_details = []
        time.sleep(1)
        context.driver.execute_script(Locators.scroll_middle)
        time.sleep(1)
        settle_orderid = settle_paymentmethod = settle_amount = settle_status = settle_orderstatus = None
        while True:
            table = context.driver.find_elements(By.XPATH, "//table//tr")
            if not table:
                logging.info("Table not found. Exiting loop.")
                break

            for row in table:
                row_text = row.text.replace('\n', ',')  # Replace line breaks with commas
                settle_details.append(row_text)

                if order_to_be_searched in row_text:
                    logging.info(f"Order ID {order_to_be_searched} found: {row_text}")
                    elements = row_text.split()  # Use .split(',') if comma-separated
                    settle_orderid = elements[0]
                    settle_paymentmethod = elements[1]
                    settle_amount = elements[2]
                    settle_status = elements[3]
                    settle_orderstatus = elements[5]
                    logging.info(f"Settle Order ID: {settle_orderid}")
                    logging.info(f"Settle Payment Method: {settle_paymentmethod}")
                    logging.info(f"Settle Amount: {settle_amount}")
                    logging.info(f"Settle Status: {settle_status}")
                    logging.info(f"Settle order status is: {settle_orderstatus}")
                    context.settle_amount = settle_amount
                    context.settle_status = settle_status
                    assert order_to_be_searched == settle_orderid , "Both order IDs are different"
                    logging.info("Both order IDs are the same")
                    assert payment_text == settle_paymentmethod, "Both payment methods are different"
                    logging.info("Both payment methods are the same from OMS and settled page")  
                    logging.info(f"Settle details collected: {settle_details}")
                    time.sleep(1)
                    context.driver.execute_script(Locators.scroll_up)
                    time.sleep(1)                  
                    return True
            next_button = context.driver.find_element(By.XPATH, Locators.next_button_xpath)
            if next_button.is_enabled():
                next_button.click()
                time.sleep(1)  # Wait for the next page to load
            else:
                logging.info("Reached the last page. Order ID not found.")
                break
        
        return False
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify the order id should be visible in the orders list: {str(e)}')
        context.driver.close()
        raise Exception from e


@then(u'Verify the user in Logistic tab')
def step_impl(context):
    try:
        time.sleep(0.5)
        logistics_tab = wait.presence_of_element_located(context, Locators.master_logistic_tab)
        logistics_tab_text = logistics_tab.text
        logging.info(f"user in {logistics_tab_text} tab")
    except Exception as e:
        time.sleep(1)
        context.driver.save_screenshot(f"./{new_file_name}")
        logging.error(f'Verify the user in Logistic tab: {str(e)}')
        context.driver.close()
        raise Exception from e
