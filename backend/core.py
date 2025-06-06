from preprocess import *
from multillm import *
import logging
import json
import requests

# logs
logging.basicConfig(
    filename="pdfapp.log",  # Save logs to app.log
    filemode="a",  # Append mode (use 'w' to overwrite)
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO,  # Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
)


class startprocess:

    @staticmethod
    def initiate(filename):
        try:

            logging.info(f"Process Initiated for file: {filename}")
            # to extract correct pages containing balance sheet, income statment and cash flow
            tablekeywords = [
                "income statement",
                "balance sheet",
                "cash flow",
                "Operating Cash Flow",
                "Cash from Operations",
                "Free Cash Flow",
                "Net Cash Flow",
                "Cash Inflow",
                "Cash Outflow",
                "Net Cash from Operating Activities",
                "Cash Generated from Operations",
                "Investing Cash Flow",
                "Financing Cash Flow",
                "Cash and Cash Equivalents",
                "Statement of Financial Position",
                "Financial Position Statement",
                "Statement of Assets and Liabilities",
                "Statement of Financial Condition",
                "Position Statement",
                "Statement of Net Worth",
                "Statement of Assets",
                "Statement of Liabilities and Equity",
                "Financial Statement",
                "Assets and Liabilities Statement",
                "Profit and Loss Statement",
                "P&L Statement",
                "Statement of Earnings",
                "Statement of Profit or Loss",
                "Operating Statement",
                "Statement of Operations",
                "Revenue Statement",
                "Earnings Statement",
                "Statement of Comprehensive Income",
                "Income and Expense Statement",
            ]

            file_path = "uploads/" + filename[:-4] + "/" + filename
            cloud_path = filename[:-4]
            processor = PDFImageProcessor(
                pdf_path=file_path, cloud_folder=cloud_path, keywords=tablekeywords
            )

            relevantPagesUrl = []
            rel_pages = []

            try:
                for result in processor.process():
                    relevantPagesUrl.append(result["url"])
                    rel_pages.append(result["page"])
            finally:
                processor.close()

            # llmprompt = "Extract Balance Sheet, Income Statement, and Cash Flow tables (only if they exist). give output in json format"
            llmprompt = """
                Extract Balance Sheet, Income Statement, and Cash Flow Statement tables exactly as shown in the image.
                Output JSON with keys: "BalanceSheet", "IncomeStatement", "CashFlowStatement".
                Under each, organize data by year: {year: [{Particular, Value}]}.
                Keep structure, years, and rows exactly.
                If a statement doesn't exist, return an empty object {}.
                Output only the final JSON, no extra text.
                Return all numeric values as strings, exactly as shown (including commas and parentheses). Do not convert them to numbers.
            """
            # relevantPagesUrl=['http://127.0.0.1:5000/upload/vodafone_annual_report_reduced/page_1_img_1.png', 'http://127.0.0.1:5000/upload/vodafone_annual_report_reduced/page_2_img_1.png', 'http://127.0.0.1:5000/upload/vodafone_annual_report_reduced/page_18_img_1.png', 'http://127.0.0.1:5000/upload/vodafone_annual_report_reduced/page_19_img_1.png', 'http://127.0.0.1:5000/upload/vodafone_annual_report_reduced/page_20_img_1.png']
            # relevantPagesUrl = [
            #     "http://52.66.73.219/upload/vodafone_annual_report_reduced/page_1_img_1.png",
            #     "http://52.66.73.219/upload/vodafone_annual_report_reduced/page_2_img_1.png",
            #     "http://52.66.73.219/upload/vodafone_annual_report_reduced/page_18_img_1.png",
            #     "http://52.66.73.219/upload/vodafone_annual_report_reduced/page_19_img_1.png",
            #     "http://52.66.73.219/upload/vodafone_annual_report_reduced/page_20_img_1.png",
            # ]
            # relevantPagesUrl = [
            #     "https://raw.githubusercontent.com/akshay-op/imgBucket/refs/heads/main/page_18.png",
            #     "https://raw.githubusercontent.com/akshay-op/imgBucket/refs/heads/main/page_19.png",
            #     "https://raw.githubusercontent.com/akshay-op/imgBucket/refs/heads/main/page_20.png",
            #     "https://raw.githubusercontent.com/akshay-op/imgBucket/refs/heads/main/page_18.png",
            #     "https://raw.githubusercontent.com/akshay-op/imgBucket/refs/heads/main/page_19.png"
            # ]

            print("relevant pages :", rel_pages)
            print("relevant page URL :", relevantPagesUrl)

            print("calling groq")
            print(
                "Internet OK"
                if requests.get("https://www.google.com", timeout=5).status_code == 200
                else "No Internet"
            )

            output = groqconnect.groqinference(relevantPagesUrl, llmprompt)
            print("output:", output)

            data_vocabulary_update, changes = VocabularyUpdate.labelchange(
                json.loads(output)
            )

            json_output = dataprocess.data_to_json(data_vocabulary_update)
            json_output["vocabulary"] = json.dumps(changes, indent=2)

            tempdata = {
                "BalanceSheet": '[{"Particular":"Non-current assets","2020":"2,368.4","2019":"2,794.1"},{"Particular":"Intangible assets","2020":"2,368.4","2019":"2,794.1"},{"Particular":"Property, plant and equipment","2020":"3,965.3","2019":"3,040.7"},{"Particular":"Investments","2020":"25.1","2019":"25.1"},{"Particular":"Deferred tax asset","2020":"1,124.2","2019":"1,014.3"},{"Particular":"Post-employment benefits - asset","2020":"489.2","2019":"81.4"},{"Particular":"Current assets","2020":"7,972.2","2019":"6,955.6"},{"Particular":"Inventories","2020":"116.4","2019":"160.9"},{"Particular":"Trade and other receivables","2020":"3,582.2","2019":"3,400.8"},{"Particular":"Cash and cash equivalents","2020":"24.3","2019":"32.5"}]',
                "IncomeStatement": '[{"Particular":"Revenue","2020":"5,657.6","2019":"5,512.9"},{"Particular":"Cost of sales","2020":"(4,045.5)","2019":"(4,222.2)"},{"Particular":"Gross profit","2020":"1,612.1","2019":"1,290.7"},{"Particular":"Selling and distribution costs","2020":"(578.1)","2019":"(637.8)"},{"Particular":"Administrative expenses","2020":"(1,284.2)","2019":"(1,255.0)"},{"Particular":"Net credit losses on financial assets","2020":"(101.3)","2019":"(74.7)"},{"Particular":"Operating loss","2020":"(351.5)","2019":"(676.8)"},{"Particular":"Net finance expense","2020":"(23.5)","2019":"(2.7)"},{"Particular":"Loss on ordinary activities before taxation","2020":"(375.0)","2019":"(679.5)"},{"Particular":"Income tax on ordinary activities","2020":"148.8","2019":"92.3"},{"Particular":"Loss for the financial year","2020":"(226.2)","2019":"(587.2)"}]',
                "CashFlowStatement": "[]",
            }

            return json_output

        except Exception as e:
            # Log any exceptions that occur during the process
            logging.error(f"Error during processing: {str(e)}")
            print(f"Error occurred: {str(e)}")
            return {
                "error": "An error occurred during the processing. Check logs for details."
            }
