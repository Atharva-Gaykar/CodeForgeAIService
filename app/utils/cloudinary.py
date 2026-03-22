import cloudinary
from cloudinary import Search
from app.core.config import settings

# Configure
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

def get_resume_url(thread_id: str) -> str:
    """
    Searches Cloudinary for the resume PDF in the thread's folder
    and returns the secure URL.
    """
    result = Search() \
        .expression(f'folder:"threads/{thread_id}/*"') \
        .sort_by('public_id', 'desc') \
        .max_results(1) \
        .execute()

    resources = result.get("resources", [])

    if not resources:
        raise FileNotFoundError(f"No resume found for thread_id: {thread_id}")

    pdf_url = resources[0]["secure_url"]
    print(f"Found resume: {pdf_url}")
    return pdf_url