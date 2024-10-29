import requests
import json
from django.core.files import File
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from django.db import models
from django.conf import settings
from datetime import datetime
import os

class Product(models.Model):
    name      = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price     = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category  = models.CharField(max_length=100, blank=True, null=True)
    audio_key = models.CharField(max_length=100, blank=True, null=True)
    # Fields for storing different pronunciation variations
    english_keywords = models.TextField(default="", blank=True, null=True)
    spanish_keywords = models.TextField(default="", blank=True, null=True)
 
    # Image fields
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    thumbnail = models.ImageField(upload_to='product_thumbnails/', blank=True, null=True)

    def get_pronunciations_from_genai(self, text, language):
        """
        Function to call Google Gemini API and get different pronunciations or slang variations.
        Modify this function based on the actual API URL and response structure.
        """
        generation_config = {
            "temperature": 0.5,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_mime_type": "application/json"
        }
        
        genai.configure(api_key=settings.GENAI_API_KEY)

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
            system_instruction="""
            Instructions:
            - Generate pronunciation variations or slang variations for the given input in English and Spanish.
            - if the product name is 'Burger', then the varuable will be Buger, Bogout, Bugol upto twenty comma separated variations
            """
        )

        data = {
            'input': text,
            'languageCode': language
        }
        
        try:
            response = model.start_chat(history=[]).send_message(json.dumps(data))
            # response = model.generate(data)
            if response:
                print(response)
                return response.text
            else:
                return []
        except Exception as e:
            print(f"Error in Gemini API: {e}")
            return []

    def save(self, *args, **kwargs):
        # Generate English keywords if they don't exist
        if not self.english_keywords:
            self.english_keywords = self.get_pronunciations_from_genai(self.name, 'en')

        # Generate Spanish keywords if they don't exist
        if not self.spanish_keywords:
            self.spanish_keywords = self.get_pronunciations_from_genai(self.name, 'es')

        super().save(*args, **kwargs)

        self.save_to_json()

    def save_to_json(self):
        # Define the JSON file path
        json_file_path = os.path.join(settings.MEDIA_ROOT, 'product.json')

        # Prepare the data to save
        product_data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': str(self.price),
            'category': self.category,
            'english_keywords': self.english_keywords,
            'spanish_keywords': self.spanish_keywords,
            'other_info': [{"name": info.name, "value": info.value} for info in self.infos.all()]  # Collect other info
        }

        # Load existing products from the JSON file, if it exists
        products = []
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r') as json_file:
                products = json.load(json_file)

        # Check if the product already exists in the list
        existing_product = next((item for item in products if item['id'] == self.id), None)

        if existing_product:
            # Update existing product
            existing_product.update(product_data)
        else:
            # Add new product
            products.append(product_data)

        # Write the updated list back to the JSON file
        with open(json_file_path, 'w') as json_file:
            json.dump(products, json_file, indent=4)

    def __str__(self):
        return self.name


class OtherInfo(models.Model):
    product = models.ForeignKey(Product, related_name='infos', on_delete=models.CASCADE)
    name = models.CharField(max_length=255,blank=True,null=True)
    value= models.CharField(max_length=255,blank=True,null=True)

class Session(models.Model):
    session_id = models.CharField(max_length=255, unique=True)
    session_start = models.DateTimeField(auto_now_add=True)  # Automatically set when the session is created
    session_end = models.DateTimeField(null=True, blank=True)  # To be set when the session ends

    def end_session(self):
        """
        Marks the session as ended by setting the session_end time.
        """
        self.session_end = datetime.now()
        self.save()

    def __str__(self):
        return f"Session {self.session_id} (Start: {self.session_start}, End: {self.session_end})"

class Cart(models.Model):
    session = models.OneToOneField(Session, on_delete=models.CASCADE)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0, blank=True, null=True)

    def update_total(self):
        """
        Update the total price of the cart by summing the line totals of all cart items.
        """
        total = self.items.aggregate(models.Sum('line_total'))['line_total__sum'] or Decimal('0.00')
        self.total = total
        self.save()

    def __str__(self):
        return f"Cart for Session {self.session.session_id} - Total: {self.total}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    instructions = models.TextField(blank=True, null=True)
    line_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        """
        Override save method to automatically calculate the line total for the cart item.
        """
        self.line_total = self.product.price * self.quantity
        super().save(*args, **kwargs)
        self.cart.update_total()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} (Line Total: {self.line_total})"

class ModelConfigurations(models.Model):
    name               = models.CharField(max_length=255,blank=True,null=True)
    system_instruction = models.TextField(blank=True,null=True)
    temperature        = models.CharField(max_length=255,blank=True,null=True)
    top_p              = models.CharField(max_length=255,blank=True,null=True)
    top_k              = models.CharField(max_length=255,blank=True,null=True)
    max_output_tokens  = models.CharField(max_length=255,blank=True,null=True)
    response_mime_type = models.CharField(max_length=255,blank=True,null=True)
    welcome_text = models.TextField(blank=True,null=True)
    post_welcome_text = models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name


class LLMModel(models.Model):
    name         =    models.CharField(max_length=255,blank=True,null=True)
    other_info   =    models.TextField(blank=True,null=True)

    def __str__(self):
        return self.name

class LLMModelConfig(models.Model):
    model   =    models.ForeignKey(LLMModel, on_delete=models.CASCADE,)
    key     =    models.CharField(max_length=255,blank=True,null=True)
    value   =    models.TextField(blank=True,null=True)

    def __str__(self):
        return self.key


class Configuration(models.Model):
    key     =    models.CharField(max_length=255,unique=True,blank=True,null=True)
    value   =    models.TextField(blank=True,null=True)

    def __str__(self):
        return self.key

class Setting(models.Model):
    model = models.ForeignKey(LLMModel, on_delete=models.CASCADE, blank=True, null=True, related_name="settings_model")
    speech_to_text = models.ForeignKey(LLMModel, on_delete=models.CASCADE, blank=True, null=True, related_name="settings_speech_to_text")
    text_to_speech = models.ForeignKey(LLMModel, on_delete=models.CASCADE, blank=True, null=True, related_name="settings_text_to_speech")

    def __unicode__(self):
        return str(self.id)