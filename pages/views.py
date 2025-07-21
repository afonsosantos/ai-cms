from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import Template, Context
from .models import Page, SiteSettings
from .services import AIPageGenerator


def render_page(request, slug):
    """Render a page based on its slug."""
    # Get the page or return 404
    page = get_object_or_404(Page, slug=slug, is_published=True)
    
    # If the page has content, render it directly
    if page.content:
        # Create a Template object from the page content
        template = Template(page.content)
        
        # Get the site settings
        site_settings = SiteSettings.get_settings()
        
        # Create a context with the page and site settings
        context = Context({
            'page': page,
            'site_settings': site_settings,
        })
        
        # Render the template with the context
        rendered_content = template.render(context)
        
        return HttpResponse(rendered_content)
    else:
        # If the page doesn't have content, generate it
        generator = AIPageGenerator()
        success, content = generator.generate_page_content(page)
        
        if success:
            # Create a Template object from the generated content
            template = Template(content)
            
            # Get the site settings
            site_settings = SiteSettings.get_settings()
            
            # Create a context with the page and site settings
            context = Context({
                'page': page,
                'site_settings': site_settings,
            })
            
            # Render the template with the context
            rendered_content = template.render(context)
            
            return HttpResponse(rendered_content)
        else:
            # If generation fails, return a 500 error
            return HttpResponse(f"Error generating page content: {content}", status=500)
