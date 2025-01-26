# from django.contrib import admin
# from django.utils.html import format_html
# from .models import *

# @admin.register(Session)
# class SessionAdmin(admin.ModelAdmin):
#     list_display = ('session_id', 'session_start', 'session_end')
#     list_filter = ('session_start', 'session_end')
#     search_fields = ('session_id',)
#     readonly_fields = ('session_start', 'session_end')
#     actions = ['end_session']

#     def end_session(self, request, queryset):
#         """
#         Admin action to mark selected sessions as ended.
#         """
#         for session in queryset:
#             session.end_session()
#         self.message_user(request, "Selected sessions have been ended.")
    
#     end_session.short_description = "Mark selected sessions as ended"

# class OtherInfoInline(admin.TabularInline):
#     model = OtherInfo
#     extra = 1  # Number of empty fields to display for adding new items
#     can_delete = True  # Allows cart items to be deleted from the inline

# class CartItemInline(admin.TabularInline):
#     model = CartItem
#     extra = 1  # Number of empty fields to display for adding new items
#     readonly_fields = ('line_total',)
#     fields = ('product', 'quantity', 'instructions', 'line_total')

# class LLMModelConfigInline(admin.TabularInline):
#     model = LLMModelConfig
#     extra = 0

# class LLMModelAdmin(admin.ModelAdmin):
#     inlines = [LLMModelConfigInline]


# @admin.register(Cart)
# class CartAdmin(admin.ModelAdmin):
#     list_display = ('session', 'total')
#     search_fields = ('session__session_id',)
#     readonly_fields = ('total',)
    
#     # Adding the Tabular Inline for Cart Items
#     inlines = [CartItemInline]

# class ConfigurationAdmin(admin.ModelAdmin):
#     model = Configuration
#     list_display = ['key', 'value']

# class ProductAdmin(admin.ModelAdmin):
#     list_display = ('preview_thumbnail','name', 'category', 'price', 'english_keywords', 'spanish_keywords')
#     list_filter = ('category',)
#     search_fields = ('name', 'description', 'category')
#     readonly_fields = ('preview_image', 'preview_thumbnail')
#     fields = ('name', 'description', 'price', 'category', 'image', 'thumbnail', 'english_keywords', 'spanish_keywords','audio_key')
#     inlines = [OtherInfoInline]

#     def preview_image(self, obj):
#         """
#         Display the uploaded image in the admin panel as a preview.
#         """
#         if obj.image:
#             return format_html('<img src="{}" width="100" height="100" />'.format(obj.image.url))
#         return "(No image)"

#     preview_image.short_description = 'Image Preview'

#     def preview_thumbnail(self, obj):
#         """
#         Display the generated thumbnail in the admin panel as a preview.
#         """
#         if obj.thumbnail:
#             return format_html('<img src="{}" width="100" height="100" />'.format(obj.thumbnail.url))
#         return "(No thumbnail)"

#     preview_thumbnail.short_description = 'Thumbnail Preview'


# # Register the Product model with the customized admin class
# admin.site.register(Product, ProductAdmin)
# admin.site.register(ModelConfigurations)
# admin.site.register(ModelSetting)
# admin.site.register(LLMModel,LLMModelAdmin)
# admin.site.register(Configuration, ConfigurationAdmin)