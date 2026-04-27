# # Define your item pipelines here
# #
# # Don't forget to add your pipeline to the ITEM_PIPELINES setting
# # See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# # useful for handling different item types with a single interface
# from itemadapter import ItemAdapter


# class SecgovPipeline:
#     def process_item(self, item, spider):
#         return item


# pipelines.py

import json
import requests

class TelegramAlertPipeline:
    
    BOT_TOKEN = "Enter YOUR TOKEN"
    CHAT_ID   = "ENTER CHAT ID"
    SEND_URL  = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    def process_item(self, item, spider):
        # Format plain text message
        message = (
            "📢 *New EDGAR Filing Alert*\n\n"
            f"*Filing Date:* {item.get('Filing_date', 'N/A')}\n"
            f"*Form Type:* {item.get('Form_type', 'N/A')}\n"
            f"*Ticker:* {item.get('Ticker', 'N/A')}\n"
            f"*Company Name:* {item.get('Company_Name', 'N/A')}\n"
            f"View Filing: {item.get('View Fillings', 'N/A')}"
        )

        data = {
            "chat_id": self.CHAT_ID,
            "text": message,
            "parse_mode": "Markdown",
            "disable_web_page_preview": False
        }

        try:
            resp = requests.post(self.SEND_URL, data=data, timeout=10)
            resp.raise_for_status()
        except Exception as e:
            spider.logger.error(f"Telegram send failed: {e}")
        return item
