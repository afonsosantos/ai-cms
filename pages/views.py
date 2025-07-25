from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404
from django.template import Template, Context
from django.urls import reverse
from .models import Page, SiteSettings
from .services import AIPageGenerator
from .utils import generate_page_in_background


def render_page(request, slug):
    """Render a page based on its slug."""
    # Get the page or return 404
    page = get_object_or_404(Page, slug=slug, is_published=True)
    
    # If the page has content and generation is complete, render it directly
    if page.content and page.generation_status == Page.PageStatus.COMPLETED:
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
    
    # Check if generation is in progress or pending
    elif page.generation_status in [Page.PageStatus.PENDING, Page.PageStatus.IN_PROGRESS]:
        # Show a page indicating that generation is in progress
        return render(request, 'pages/generation_in_progress.html', {
            'page': page,
            'site_settings': SiteSettings.get_settings(),
        })
    
    # Check if generation failed
    elif page.generation_status == Page.PageStatus.FAILED:
        # Show a page with the error message
        return render(request, 'pages/generation_failed.html', {
            'page': page,
            'site_settings': SiteSettings.get_settings(),
        })
    
    # If no content and generation not started, start it in the background
    else:
        # Start generation in the background
        success, message = generate_page_in_background(page.id, AIPageGenerator)
        
        if success:
            # Redirect back to the same page to show the "in progress" template
            return redirect('render_page', slug=slug)
        else:
            # If starting generation fails, return a 500 error
            return HttpResponse(f"Error starting page generation: {message}", status=500)


def generate_page(request, slug):
    """Manually trigger page generation for a page."""
    # Get the page or return 404
    page = get_object_or_404(Page, slug=slug)
    
    # Start generation in the background
    success, message = generate_page_in_background(page.id, AIPageGenerator)
    
    if success:
        # Redirect back to the page
        return redirect('render_page', slug=slug)
    else:
        # If starting generation fails, return a 500 error
        return HttpResponse(f"Error starting page generation: {message}", status=500)
