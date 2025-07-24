from django.db import models

class SiteSettings(models.Model):
    """Model for storing site-wide settings like logo, company name, colors, etc."""
    company_name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    primary_color = models.CharField(max_length=20, default='#007bff', help_text='Primary color in hex format (e.g., #007bff)')
    secondary_color = models.CharField(max_length=20, default='#6c757d', help_text='Secondary color in hex format (e.g., #6c757d)')
    accent_color = models.CharField(max_length=20, default='#28a745', help_text='Accent color in hex format (e.g., #28a745)')
    font_family = models.CharField(max_length=100, default='Arial, sans-serif')
    
    # Design preferences
    STYLE_CHOICES = [
        ('minimalist', 'Minimalist'),
        ('modern', 'Modern'),
        ('classic', 'Classic'),
        ('playful', 'Playful'),
        ('corporate', 'Corporate'),
    ]
    preferred_style = models.CharField(max_length=20, choices=STYLE_CHOICES, default='modern')
    
    # Additional settings
    footer_text = models.TextField(blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=20, blank=True)
    
    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'
    
    def __str__(self):
        return f"{self.company_name} Settings"
    
    @classmethod
    def get_settings(cls):
        """Get the site settings, creating default ones if none exist."""
        settings = cls.objects.first()
        if not settings:
            settings = cls.objects.create(company_name="My Company")
        return settings


class Page(models.Model):
    """Model for storing generated pages."""
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(help_text="Brief description of what this page should contain")
    content = models.TextField(blank=True, help_text="AI-generated HTML content")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=False)

    # Generation status
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    generation_status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES,
        default='not_started',
        help_text="Current status of content generation"
    )
    generation_error = models.TextField(blank=True, help_text="Error message if generation failed")
    
    # AI generation settings
    ai_prompt = models.TextField(help_text="The prompt used to generate this page")

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['-updated_at']