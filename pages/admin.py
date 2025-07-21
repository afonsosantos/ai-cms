import os
from django.contrib import admin
from django.utils.html import format_html
from django.contrib import messages
from django.conf import settings
from .models import SiteSettings, Page
from .services import AIPageGenerator

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Company Information', {
            'fields': ('company_name', 'logo', 'contact_email', 'contact_phone')
        }),
        ('Design Settings', {
            'fields': ('primary_color', 'secondary_color', 'accent_color', 'font_family', 'preferred_style')
        }),
        ('Footer', {
            'fields': ('footer_text',)
        }),
        ('Layout Template', {
            'fields': ('generate_layout_template',),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('generate_layout_template',)
    
    def has_add_permission(self, request):
        # Only allow one instance of SiteSettings
        return not SiteSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of the settings
        return False
        
    def generate_layout_template(self, obj):
        """Generate a layout template based on current site settings."""
        if obj.pk:
            return "Click 'Save and continue editing' then use the 'Generate Layout Template' action"
        return "Save settings first to enable template generation"
    generate_layout_template.short_description = "Layout Template Generation"
    
    actions = ['generate_layout_template_action']
    
    def generate_layout_template_action(self, request, queryset):
        """Generate a layout template for the site based on current settings."""
        if queryset.count() != 1:
            self.message_user(
                request,
                "Please select exactly one site settings instance.",
                level=messages.ERROR
            )
            return
            
        site_settings = queryset.first()
        
        # Use Django Q to generate the layout template in the background
        from .utils import generate_layout_in_background
        success, message = generate_layout_in_background(site_settings.id)
        
        if success:
            self.message_user(
                request,
                f"Layout template generation started in the background. {message}",
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request,
                f"Error starting layout template generation: {message}",
                level=messages.ERROR
            )
    generate_layout_template_action.short_description = "Generate Layout Template"

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at', 'updated_at', 'is_published', 'generation_status', 'preview_link')
    list_filter = ('is_published', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    
    def save_model(self, request, obj, form, change):
        """Override save_model to generate content when saving a page."""
        # First save the model to ensure it has an ID
        super().save_model(request, obj, form, change)
        
        # Generate content for the page in the background
        from .utils import generate_page_in_background
        success, message = generate_page_in_background(obj.id, AIPageGenerator)
        
        if success:
            self.message_user(
                request, 
                f"Page '{obj.title}' saved. Content generation started in the background.", 
                level=messages.SUCCESS
            )
        else:
            self.message_user(
                request, 
                f"Error starting content generation for '{obj.title}': {message}", 
                level=messages.ERROR
            )
    
    fieldsets = (
        ('Page Information', {
            'fields': ('title', 'slug', 'description', 'is_published')
        }),
        ('AI Generation', {
            'fields': ('ai_prompt', 'generation_status', 'generation_error',)
        }),
        ('Content', {
            'fields': ('content',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def preview_link(self, obj):
        if obj.is_published:
            return format_html('<a href="/{0}" target="_blank">View Page</a>', obj.slug)
        return "Not published"
    preview_link.short_description = "Preview"
    
    def generate_content(self, obj):
        # This will be implemented as a custom admin action
        return "Use the 'Generate Content' action from the admin actions dropdown"
    generate_content.short_description = "Generate Content"
    
    actions = ['generate_content_action']
    
    def generate_content_action(self, request, queryset):
        """Generate content for selected pages using the AI service in the background."""
        from .utils import generate_page_in_background
        success_count = 0
        error_count = 0
        error_messages = []
        
        for page in queryset:
            success, message = generate_page_in_background(page.id, AIPageGenerator)
            if success:
                success_count += 1
            else:
                error_count += 1
                error_messages.append(f"Error starting content generation for '{page.title}': {message}")
        
        if success_count > 0:
            self.message_user(
                request, 
                f"Started background content generation for {success_count} page(s).", 
                level=messages.SUCCESS
            )
        
        if error_count > 0:
            for error in error_messages:
                self.message_user(request, error, level=messages.ERROR)
    generate_content_action.short_description = "Generate content using AI (background)"
