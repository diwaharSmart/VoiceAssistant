import requests
import json
from django.core.files import File
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from django.db import models
from django.conf import settings
from datetime import datetime

class Product(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    category = models.CharField(max_length=100, blank=True, null=True)
    
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

        # Generate thumbnail if image is provided and thumbnail is empty
        if self.image and not self.thumbnail:
            self.thumbnail = self.make_thumbnail(self.image)

        super().save(*args, **kwargs)

    def make_thumbnail(self, image, size=(300, 300)):
        """
        Generate a thumbnail for the image
        """
        img = Image.open(image)
        img.convert('RGB')
        img.thumbnail(size)
        
        thumb_io = BytesIO()
        img.save(thumb_io, 'JPEG', quality=85)
        
        thumbnail = File(thumb_io, name=image.name)
        return thumbnail

    def __str__(self):
        return self.name


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