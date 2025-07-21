import logging
from django.db import transaction
from .models import Page
from .services import AIPageGenerator

logger = logging.getLogger(__name__)

def generate_page_content(page_id):
    """
    Django Q task to generate content for a page.
    
    Args:
        page_id: ID of the Page object to generate content for
    """
    try:
        # Get the page and update its status
        with transaction.atomic():
            try:
                page = Page.objects.select_for_update().get(id=page_id)
                page.generation_status = 'in_progress'
                page.generation_error = ''
                page.save()
            except Page.DoesNotExist:
                logger.error(f"Page with ID {page_id} does not exist.")
                return False, f"Page with ID {page_id} does not exist."
        
        # Generate the content
        generator = AIPageGenerator()
        success, result = generator.generate_page_content(page)
        
        # Update the page with the result
        with transaction.atomic():
            page = Page.objects.select_for_update().get(id=page_id)
            if success:
                page.generation_status = 'completed'
            else:
                page.generation_status = 'failed'
                page.generation_error = result
            page.save()
        
        logger.info(f"Page generation completed for page {page_id} with status: {page.generation_status}")
        return success, result
        
    except Exception as e:
        logger.exception(f"Error generating page {page_id}: {str(e)}")
        try:
            with transaction.atomic():
                page = Page.objects.select_for_update().get(id=page_id)
                page.generation_status = 'failed'
                page.generation_error = str(e)
                page.save()
        except Exception:
            pass
        return False, str(e)

def generate_layout_template(site_settings_id):
    """
    Django Q task to generate a layout template based on site settings.
    
    Args:
        site_settings_id: ID of the SiteSettings object to use for generation
    """
    from .models import SiteSettings
    
    try:
        try:
            site_settings = SiteSettings.objects.get(id=site_settings_id)
        except SiteSettings.DoesNotExist:
            logger.error(f"SiteSettings with ID {site_settings_id} does not exist.")
            return False, f"SiteSettings with ID {site_settings_id} does not exist."
        
        # Generate the layout template
        generator = AIPageGenerator()
        success, result = generator.generate_layout_template(site_settings)
        
        if success:
            # Create a new file to store the template
            import os
            from django.conf import settings
            
            template_dir = os.path.join(settings.BASE_DIR, 'pages', 'templates', 'pages')
            os.makedirs(template_dir, exist_ok=True)
            
            template_path = os.path.join(template_dir, 'generated_layout.html')
            with open(template_path, 'w') as f:
                f.write(result)
                
            logger.info(f"Successfully generated layout template. Saved to {template_path}")
            return True, f"Successfully generated layout template. Saved to {template_path}"
        else:
            logger.error(f"Error generating layout template: {result}")
            return False, f"Error generating layout template: {result}"
            
    except Exception as e:
        logger.exception(f"Error generating layout template: {str(e)}")
        return False, str(e)