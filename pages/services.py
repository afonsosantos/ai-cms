import os
from openai import OpenAI
from django.conf import settings
from .models import SiteSettings, Page


class AIPageGenerator:
    """Service for generating HTML pages using OpenAI based on site settings and user prompts."""

    def __init__(self):
        self.client = OpenAI(base_url=settings.AI_BASE_URL, api_key=settings.AI_API_KEY)

    def _get_site_context(self) -> dict:
        """Returns a dictionary with relevant site settings for layout and styling."""
        site_settings = SiteSettings.get_settings()
        return {
            "company_name": site_settings.company_name,
            "primary_color": site_settings.primary_color,
            "secondary_color": site_settings.secondary_color,
            "accent_color": site_settings.accent_color,
            "font_family": site_settings.font_family,
            "preferred_style": site_settings.preferred_style,
            "footer_text": site_settings.footer_text,
            "contact_email": site_settings.contact_email,
            "contact_phone": site_settings.contact_phone,
        }

    def _get_previous_page_examples(self, exclude_page_id=None, limit=2) -> str:
        """Fetch a few previous pages to use as examples in the prompt."""
        pages = Page.objects.exclude(id=exclude_page_id).order_by("-created_at")[:limit]
        examples = []
        for p in pages:
            content_snippet = p.content[:2000]  # avoid token overflow
            examples.append(f"### PAGE: {p.title}\n{content_snippet}")
        return "\n\n".join(examples)

    def _get_layout_template(self) -> str:
        """Loads the layout template from the file system or generates one if missing."""
        template_path = os.path.join(
            settings.BASE_DIR, "pages", "templates", "pages", "generated_layout.html"
        )
        if os.path.exists(template_path):
            with open(template_path, "r") as f:
                return f.read()
        else:
            success, layout = self.generate_layout_template()
            if success:
                return layout
            return ""

    def generate_page_content(self, page) -> tuple[bool, str]:
        """Generates and saves HTML content for a given page using OpenAI."""
        site_context = self._get_site_context()
        layout_template = self._get_layout_template()
        examples = self._get_previous_page_examples(exclude_page_id=page.id)

        if not layout_template:
            return False, "Missing or failed to generate layout template."

        # Construct a structured prompt
        prompt = f"""
You are an expert HTML page generator for a content management system.

=== SITE CONTEXT ===
Company Name: {site_context["company_name"]}
Design Style: {site_context["preferred_style"]}
Color Scheme: Primary: {site_context["primary_color"]}, Secondary: {site_context["secondary_color"]}, Accent: {site_context["accent_color"]}
Font Family: {site_context["font_family"]}

=== PAGE DETAILS ===
Title: {page.title}
Description: {page.description}
User Prompt: {page.ai_prompt}

=== PREVIOUS PAGES ===
{examples}

=== LAYOUT TEMPLATE ===
{layout_template}

=== TASK ===
Generate a full HTML5 page using the layout above.
- Preserve the layout's header, navigation, and footer
- Replace <main> content with new content based on this page
- Use a heading that reflects the page title
- Make the page mobile-friendly
- Return ONLY the HTML code without markdown or explanation
- The generated code should be accessible and semantic, following WCAG 2.2 guidelines.
"""

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_API_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You generate valid, responsive HTML pages for CMS systems.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )

            generated_content = response.choices[0].message.content.strip()
            page.content = generated_content
            page.save()

            return True, generated_content

        except Exception as e:
            return False, str(e)

    def generate_layout_template(self, site_settings=None) -> tuple[bool, str]:
        """Generates a base layout template using OpenAI based on site settings."""
        if site_settings is None:
            site_settings = SiteSettings.get_settings()

        # Check if logo exists
        has_logo = site_settings.logo is not None

        prompt = f"""
You are a web layout designer for a content management system.

=== SITE CONTEXT ===
Company Name: {site_settings.company_name}
Has Logo: {has_logo}
Logo URL: {site_settings.logo.url if has_logo else ""}
Design Style: {site_settings.preferred_style}
Color Scheme: Primary: {site_settings.primary_color}, Secondary: {site_settings.secondary_color}, Accent: {site_settings.accent_color}
Font Family: {site_settings.font_family}
Footer Contact: {site_settings.contact_email or ""}, {site_settings.contact_phone or ""}

=== TASK ===
Generate a base HTML layout for all pages on this website. It should:
- Use proper HTML5 structure (with head, meta, title, body)
- Include a <header> with navigation placeholder
- In the navbar, include the logo (if Has Logo is True) and insert the logo URL in the src attribute of the <img> tag
- If Has Logo is False, display the company name in the navbar instead
- Use a <main> section with a placeholder comment for page-specific content
- Include a <footer> with contact details if available
- Apply inline or embedded CSS (you may use <style>) that fits the site's style
- Be responsive and mobile-friendly
- Return ONLY the HTML, no explanations or markdown
- The generated code should be accessible and semantic, following WCAG 2.2 guidelines.
"""

        try:
            response = self.client.chat.completions.create(
                model=settings.AI_API_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You generate clean and professional HTML layout templates.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            return True, response.choices[0].message.content.strip()

        except Exception as e:
            return False, str(e)
