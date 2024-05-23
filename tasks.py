from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.FileSystem import FileSystem
from RPA.Archive import Archive

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """
    browser.configure(
        slowmo=100,
    )
    create_folder()
    open_robot_order_website()
    download_csv_with_orders()
    orders = get_orders()
    close_annoying_modal()
    for order in orders: 
        fill_the_form(order)
        store_receipt_as_pdf(order['Order number'])
        screenshot_robot(order['Order number'])
        embed_screenshot_to_receipt(order['Order number'])      
    archive_receipts() 

def create_folder(): 
    fs = FileSystem()
    fs.create_directory("output/receipts")

def open_robot_order_website():
    """Navigates to the order website"""
    browser.goto("https://robotsparebinindustries.com/#/robot-order")

def download_csv_with_orders(): 
    """Download csv file """
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders(): 
    library = Tables()
    orders_list = library.read_table_from_csv(
        "orders.csv", columns=["Order number", "Head", "Body", "Legs", "Address"]
    )
    return orders_list

def close_annoying_modal(): 
    page = browser.page()
    page.click("text=OK")

def fill_the_form(order): 
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.check(f"input[name='body'][value='{order['Body']}']")
    page.fill("input[placeholder='Enter the part number for the legs']", order["Legs"])
    page.fill("#address", str(order["Address"]))
    page.click("#preview", strict=True)
    page.click("#order", strict=True)
    while page.is_visible("div[class='alert alert-danger']"):
        page.click("#order", strict=True)

def store_receipt_as_pdf(order_number):
    """Export the data to a pdf file"""
    page = browser.page()
    receipt_html = page.locator("#receipt").inner_html()

    pdf = PDF()
    pdf.html_to_pdf(receipt_html, f"output/receipt_{order_number}.pdf")

def screenshot_robot(order_number):
    page = browser.page()
    screenshot = page.screenshot(path = f"output/screenshot_{order_number}.png")


def embed_screenshot_to_receipt(order_number):
    page = browser.page()
    pdf = PDF()
    pdf.add_files_to_pdf([f"output/receipt_{order_number}.pdf", f"output/screenshot_{order_number}.png"], f"output/receipts/receipt_{order_number}.pdf")
    page.click("#order-another", strict=True)
    close_annoying_modal()

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip(folder = "output/receipts", archive_name = "ZIP_with_receipts.zip")











