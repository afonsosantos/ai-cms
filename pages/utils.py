import logging
from django_q.tasks import async_task

logger = logging.getLogger(__name__)

def generate_page_in_background(page_id, generator_class=None):
    """
    Generate content for a page using Django Q.
    
    Args:
        page_id: ID of the Page object to generate content for
        generator_class: Class to use for generation (not used with Django Q)
    """
    from .models import Page
    
    try:
        # Get the page and update its status
        page = Page.objects.get(id=page_id)
        page.generation_status = Page.PageStatus.PENDING
        page.generation_error = ''
        page.save()
        
        # Schedule the task with Django Q
        task_id = async_task(
            'pages.tasks.generate_page_content',
            page_id,
            hook='pages.utils.task_completion_hook'
        )
        
        logger.info(f"Scheduled page generation task {task_id} for page {page_id}")
        return True, "Page generation scheduled in the background."
        
    except Page.DoesNotExist:
        return False, f"Page with ID {page_id} does not exist."
    except Exception as e:
        logger.exception(f"Error scheduling generation for page {page_id}: {str(e)}")
        return False, str(e)

def generate_layout_in_background(site_settings_id):
    """
    Generate layout template using Django Q.
    
    Args:
        site_settings_id: ID of the SiteSettings object to use for generation
    """
    try:
        # Schedule the task with Django Q
        task_id = async_task(
            'pages.tasks.generate_layout_template',
            site_settings_id,
            hook='pages.utils.layout_task_completion_hook'
        )
        
        logger.info(f"Scheduled layout template generation task {task_id} for site settings {site_settings_id}")
        return True, "Layout template generation scheduled in the background."
        
    except Exception as e:
        logger.exception(f"Error scheduling layout template generation: {str(e)}")
        return False, str(e)

def task_completion_hook(task):
    """
    Hook function called when a task is completed.
    
    Args:
        task: The completed task object
    """
    success = task.result[0] if isinstance(task.result, tuple) else task.result
    result = task.result[1] if isinstance(task.result, tuple) and len(task.result) > 1 else None
    
    if success:
        logger.info(f"Task {task.id} completed successfully")
    else:
        logger.error(f"Task {task.id} failed: {result}")

def layout_task_completion_hook(task):
    """
    Hook function called when a layout template generation task is completed.
    
    Args:
        task: The completed task object
    """
    success = task.result[0] if isinstance(task.result, tuple) else task.result
    result = task.result[1] if isinstance(task.result, tuple) and len(task.result) > 1 else None
    
    if success:
        logger.info(f"Layout template generation task {task.id} completed successfully")
    else:
        logger.error(f"Layout template generation task {task.id} failed: {result}")