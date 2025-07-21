import os
import json
from openai import OpenAI
from django.conf import settings
from .models import SiteSettings, Page

class AIPageGenerator:
    """Service for generating page content using OpenAI API."""
    
    def __init__(self):
        """Initialize the OpenAI client."""
        self.client = OpenAI(base_url="https://api.deepseek.com", api_key=settings.DEEPSEEK_API_KEY)
    
    def _get_site_context(self):
        """Get the site context from the SiteSettings model."""
        site_settings = SiteSettings.get_settings()
        return {
            'company_name': site_settings.company_name,
            'primary_color': site_settings.primary_color,
            'secondary_color': site_settings.secondary_color,
            'accent_color': site_settings.accent_color,
            'font_family': site_settings.font_family,
            'preferred_style': site_settings.preferred_style,
            'footer_text': site_settings.footer_text,
            'contact_email': site_settings.contact_email,
            'contact_phone': site_settings.contact_phone,
        }
    
    def generate_page_content(self, page):
        """Generate HTML content for a page using OpenAI API."""
        site_context = self._get_site_context()
        
        # Read the generated layout template if it exists
        layout_template = ""
        template_path = os.path.join(settings.BASE_DIR, 'pages', 'templates', 'pages', 'generated_layout.html')
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                layout_template = f.read()
        
        # Construct the prompt
        prompt = f"""
        You are a web page generator for a content management system.
        
        SITE CONTEXT:
        - Company Name: {site_context['company_name']}
        - Design Style: {site_context['preferred_style']}
        - Color Scheme: Primary: {site_context['primary_color']}, Secondary: {site_context['secondary_color']}, Accent: {site_context['accent_color']}
        - Font Family: {site_context['font_family']}
        
        PAGE DETAILS:
        - Title: {page.title}
        - Description: {page.description}
        - User Prompt: {page.ai_prompt}
        
        LAYOUT TEMPLATE:
        ```html
        {layout_template}
        ```
        
        TASK:
        Generate a complete, valid HTML page based on the above information. The HTML should:
        1. Follow the structure and styling of the provided LAYOUT TEMPLATE
        2. Replace the placeholder content in the main section with appropriate content based on the page description and user prompt
        3. Keep the header, navigation, footer, and styling consistent with the layout template
        4. Ensure the page is responsive and mobile-friendly
        5. Make sure the page title reflects the current page's title
        
        Return ONLY the HTML code without any explanations or markdown formatting.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.DEEPSEEK_API_MODEL,
                messages=[
                    {"role": "system", "content": "You are a web page generator that creates HTML pages based on user requirements."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the generated HTML content
            generated_content = response.choices[0].message.content.strip()
            
            # Update the page with the generated content
            page.content = generated_content
            page.save()
            
            return True, generated_content
        
        except Exception as e:
            return False, str(e)
    
    def generate_layout_template(self, site_settings=None):
        """Generate a base layout template based on site settings."""
        if site_settings is None:
            site_settings = SiteSettings.get_settings()
        
        prompt = f"""
        You are a web layout designer for a content management system.
        
        SITE CONTEXT:
        - Company Name: {site_settings.company_name}
        - Design Style: {site_settings.preferred_style}
        - Color Scheme: Primary: {site_settings.primary_color}, Secondary: {site_settings.secondary_color}, Accent: {site_settings.accent_color}
        - Font Family: {site_settings.font_family}
        
        TASK:
        Generate a base HTML layout template that can be used for all pages on the site. The template should:
        1. Include proper HTML5 structure with head and body
        2. Include a header with the company name and navigation placeholder
        3. Include a main content area with a placeholder for page-specific content
        4. Include a footer with the company's contact information if available
        5. Include inline CSS that matches the company's color scheme and preferred style
        6. Be responsive and mobile-friendly
        
        Return ONLY the HTML code without any explanations or markdown formatting.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=settings.DEEPSEEK_API_MODEL,
                messages=[
                    {"role": "system", "content": "You are a web layout designer that creates HTML templates based on user requirements."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract the generated HTML template
            return True, response.choices[0].message.content.strip()
        
        except Exception as e:
            return False, str(e)