# importing libraries
import re
import pytesseract
from PIL import Image
import os
import fitz
import pandas as pd
import numpy as np
import logging
import spacy
import io
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

# Load pre-trained spaCy model
nlp = spacy.load("en_core_web_md")

load_dotenv()
cloudinary.config(
    cloud_name=os.environ.get("CLOUDINARY_CLOUD_NAME"),
    api_key=os.environ.get("CLOUDINARY_API_KEY"),
    api_secret=os.environ.get("CLOUDINARY_API_SECRET"),
)


class PDFImageProcessor:
    def __init__(self, pdf_path, cloud_folder, keywords=None, digit_threshold=0.05):
        self.pdf_path = pdf_path
        self.cloud_folder = cloud_folder
        self.keywords = keywords or ["revenue", "profit", "loss", "income"]
        self.digit_threshold = digit_threshold
        self.doc = fitz.open(pdf_path)

    def calculate_digit_density(self, text):
        total_chars = len(text)
        digit_chars = sum(c.isdigit() for c in text)
        return digit_chars / total_chars if total_chars > 0 else 0

    def is_relevant(self, text):
        if not any(keyword.lower() in text.lower() for keyword in self.keywords):
            return False
        return self.calculate_digit_density(text) > self.digit_threshold

    def upload_to_cloudinary(self, image, public_id):
        with io.BytesIO() as buffer:
            image.save(buffer, format="JPEG", quality=70)
            buffer.seek(0)
            response = cloudinary.uploader.upload(
                buffer, folder=self.cloud_folder, public_id=public_id
            )
        return response.get("secure_url")

    def process(self):
        logging.info(f"Process Initiated for file: {self.pdf_path}")
        for page_num in range(self.doc.page_count):
            page = self.doc.load_page(page_num)
            img_list = page.get_images(full=True)

            for img_index, img in enumerate(img_list):
                xref = img[0]
                base_image = self.doc.extract_image(xref)
                image_bytes = base_image.get("image")

                # Use with block for PIL image
                with Image.open(io.BytesIO(image_bytes)) as image:
                    image = image.resize(
                        (image.width // 2, image.height // 2), Image.LANCZOS
                    )

                    text = pytesseract.image_to_string(image)
                    if self.is_relevant(text):
                        public_id = f"page_{page_num + 1}_img_{img_index + 1}"
                        url = self.upload_to_cloudinary(image, public_id)
                        yield {"url": url, "page": page_num + 1}

    def close(self):
        self.doc.close()


class imageUrl:
    def imageurl(imagelist):
        """
        converts the saved images as web url deployment for making it accessible on network.
        """
        BASE_URL = os.environ.get("BASE_URL", "http://localhost:5000")
        base_url_complete = BASE_URL + "/upload/"

        relevantlist = []

        for img in imagelist:
            splits = re.split(r"[\\/]", img)
            relevanturl = base_url_complete + splits[1] + "/" + splits[2]
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


class VocabularyUpdate:

    vocabulary = [
        "Cash",
        "Accts Rec-Trade (Trade Debtors)",
        "Inventory (Stock)",
        "Tax Receivable",
        "Other Current Assets / Other Debtors",
        "Current Related Party Assets",
        "Prepayments and accrued income",
        "Land & Buildings",
        "Plant & Machinery",
        "Non Current Receivables",
        "Non Current Related Party Assets",
        "Other Fixed Assets",
        "Goodwill",
        "Related Party Assets - Intangible",
        "Other Intangible Assets",
        "Overdraft and Short Term Debt",
        "Current Maturities, Long Term Debt",
        "Current Maturities",
        "Subordinated Debt",
        "Accts Payable - Trade (Trade Creditors)",
        "Other Payables (Other Creditors)",
        "Income Taxes Payable",
        "Other Taxation and Social Security",
        "Current Related Party Liabilities",
        "Accrued expenses and prepaid income",
        "Other Liabilities - Current",
        "Long Term Debt",
        "Long Term Debt - Subordinated",
        "Related Party Liabilities - Non Current",
        "Provisions and Deferred Taxes",
        "Other Non-Current Liabilities",
        "Share Capital / Paid In Capital",
        "Retained Earnings",
        "Other Equity",
        "Translation Adjustment",
        "Minority Interests",
        "CURRENT ASSETS",
        "NON CURRENT ASSETS",
        "TOTAL ASSETS",
        "CURRENT LIABILITIES",
        "NON CURRENT LIABILITIES",
        "TOTAL LIABILITIES",
        "EQUITY",
        "TOTAL EQUITY & LIABILITIES",
    ]

    @staticmethod
    def precompute_vocab_vectors(vocabulary):
        return {term: nlp(term).vector for term in vocabulary}

    @staticmethod
    def find_best_match(term, vocab_vectors, threshold=0.80):
        term_clean = term.strip()
        term_vec = nlp(term_clean).vector
        if np.linalg.norm(term_vec) == 0:
            return term  # Skip if vector is zero

        similarities = []
        for vocab_term, vocab_vec in vocab_vectors.items():
            sim = np.dot(term_vec, vocab_vec) / (
                np.linalg.norm(term_vec) * np.linalg.norm(vocab_vec)
            )
            similarities.append((vocab_term, sim))

        best_match = max(similarities, key=lambda x: x[1])
        if best_match[1] >= threshold:
            return best_match[0]
        else:
            return term

    @staticmethod
    def relabel_data_using_vocabulary(data, vocabulary):
        vocab_vectors = VocabularyUpdate.precompute_vocab_vectors(vocabulary)
        changes = []

        def relabel_item(item):
            if isinstance(item, list):
                for sub_item in item:
                    if isinstance(sub_item, dict) and "Particular" in sub_item:
                        original = sub_item["Particular"]
                        new_label = VocabularyUpdate.find_best_match(
                            original, vocab_vectors
                        )
                        if original != new_label:
                            # changes.append(
                            #     f'Previous word: "{original}" changed to: "{new_label}"'
                            # )
                            changes.append({"term": original, "definition": new_label})
                        sub_item["Particular"] = new_label
            elif isinstance(item, dict):
                for key, value in item.items():
                    relabel_item(value)

        relabel_item(data)

        return data, changes

    @staticmethod
    def labelchange(data):
        print("inside label change")

        data, changes = VocabularyUpdate.relabel_data_using_vocabulary(
            data, VocabularyUpdate.vocabulary
        )

        return data, changes
