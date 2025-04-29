# importing libraries
import re
import pytesseract
from PIL import Image
import os
import fitz
from PIL import Image
import pandas as pd
import numpy as np
import logging


class PdfImageExtractor:
    def __init__(self, pdf_name, output_folder, keywords=None):
        """
        Reads pdf provided and extract them as images fora each page and temporarily store them.

        :param pdf_path: Path to the PDF file to be processed.
        :param output_folder: Folder where the extracted images will be saved.
        :param keywords: List of keywords to search for in the text.
        """
        self.pdf_name = pdf_name
        self.output_folder = output_folder
        self.keywords = keywords if keywords else []
        self.images = []
        self.relevant_pages = []
        self.path = self.output_folder + "/" + self.pdf_name[:-4]

        # Create output folder for storing images if it doesn't exist
        if not os.path.exists(self.path):
            return " file path not found"

    def extract_images_from_pdf(self):
        logging.info(
            f"image extraction process Initiated "
        )
        """
        Extracts as image from provided pdf for each pages.
        """
        print("path :", self.path + "/" + self.pdf_name)
        doc = fitz.open(self.path + "/" + self.pdf_name)
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)
            img_list = page.get_images(full=True)
            for img_index, img in enumerate(img_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                image_path = os.path.join(
                    self.path, f"page_{page_num + 1}_img_{img_index + 1}.png"
                )
                with open(image_path, "wb") as image_file:
                    image_file.write(image_bytes)

                self.images.append(image_path)
        return self.images

    def extract_text_from_image(self, image_path):
        """
        Extract text from an image using pytesseract.

        """
        img = Image.open(image_path)
        text = pytesseract.image_to_string(img)
        return text

    def calculate_digit_density(self, text):
        """
        Calculate digit density in the text (percentage of digits to total characters).
        The calculated density is used in determinig the pages with financial data.
        """

        num_digits = sum(c.isdigit() for c in text)
        total_chars = len(text)
        if total_chars == 0:
            return 0
        return num_digits / total_chars

    def filter_relevant_pages(self, images):
        """
        Filter pages that contain both relevant keywords and high digit density aka the pages with financial data.
        """
        logging.info(
            f"relevant pages extraction running"
        )

        relevant_images = []
        for i, image in enumerate(images):
            text = self.extract_text_from_image(image)
            if any(keyword.lower() in text.lower() for keyword in self.keywords):

                digit_density = self.calculate_digit_density(text)
                if (
                    digit_density > 0.05
                ):  # Setting 0.5 as a threshold value for digit density
                    self.relevant_pages.append(i + 1)
                    relevant_images.append(image)

        return relevant_images


class imageUrl:
    def imageurl(imagelist):
        """
        converts the saved images as web url deployment for making it accessible on network.

        """
        # base_url = "http://127.0.0.1:5000/upload/"
        base_url_development = "https://crediflowassignmentrepo-production.up.railway.app/upload/"

        relevantlist = []

        for img in imagelist:
            splits = re.split(r"[\\/]", img)
            relevanturl = base_url_development + splits[1] + "/" + splits[2]
            relevantlist.append(relevanturl)

        return relevantlist


class dataprocess:
    def flatten_dict(d, parent_key="", sep=" - "):
        """Recursively flattens a nested dictionary."""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                if all(isinstance(val, (int, float, type(None))) for val in v.values()):
                    items.append((new_key, v))
                else:
                    items.extend(dataprocess.flatten_dict(v, new_key, sep=sep).items())
            else:
                # Direct value (rare case)
                items.append((new_key, {"Value": v}))
        return dict(items)

    def nested_to_dataframe(nested_dict, sep=" - "):
        """Converts a deeply nested dict into a clean sorted DataFrame."""
        flat = dataprocess.flatten_dict(nested_dict, sep=sep)
        df = pd.DataFrame.from_dict(flat, orient="index")
        df.index.name = "Item"
        df.reset_index(inplace=True)

        year_cols = sorted(
            [col for col in df.columns if col not in ["Item"]], key=lambda x: str(x)
        )
        df = df[["Item"] + year_cols]

        return df

    def format_numbers(df):
        """Optional: Format numbers with commas (but keep NaN clean)."""
        num_cols = df.select_dtypes(include=["float", "int"]).columns
        for col in num_cols:
            df[col] = df[col].map(lambda x: f"{x:,.1f}" if pd.notnull(x) else "")
        return df

    def dataclean(data):
        for datagroup in data:
            df = dataprocess.nested_to_dataframe(data[datagroup])
        return df

    def convert_to_dataframe(statement_data):
        if not statement_data:
            return pd.DataFrame()  # Return empty DataFrame if no data

        # Create a dict for DataFrame
        records = {}
        years = list(statement_data.keys())

        for year in years:
            for item in statement_data[year]:
                particular = item["Particular"]
                value = item["Value"]

                if particular not in records:
                    records[particular] = {}

                records[particular][year] = value

        # Convert to DataFrame
        df = pd.DataFrame.from_dict(records, orient="index")
        df.index.name = "Particular"
        df.reset_index(inplace=True)

        # Optional: Order the year columns
        sorted_years = sorted(years, reverse=True)
        df = df[["Particular"] + sorted_years]

        return df

    def data_to_json(data):
        """
        returns the dataframe as json format for the frontend.
        """

        balance_sheet_df = dataprocess.convert_to_dataframe(data["BalanceSheet"])
        income_statement_df = dataprocess.convert_to_dataframe(data["IncomeStatement"])
        cash_flow_statement_df = dataprocess.convert_to_dataframe(
            data["CashFlowStatement"]
        )

        json_data = {
            "BalanceSheet": balance_sheet_df.to_json(
                orient="records", date_format="iso"
            ),
            "IncomeStatement": income_statement_df.to_json(
                orient="records", date_format="iso"
            ),
            "CashFlowStatement": cash_flow_statement_df.to_json(
                orient="records", date_format="iso"
            ),
        }

        return json_data
