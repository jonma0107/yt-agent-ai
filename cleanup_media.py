import os
import time
import django
import sys

def setup_django():
    # Add the project root to the Python path
    # This assumes the script is in the 'Backend' directory.
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    
    # Set the Django settings module
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_summary.settings')
    
    # Initialize Django
    django.setup()

def cleanup_old_files():
    """
    Deletes files from the MEDIA_ROOT directory that are older than a specified age.
    """
    setup_django()
    from django.conf import settings

    # Age limit in seconds (e.g., 24 hours = 86400 seconds)
    AGE_LIMIT_SECONDS = 86400
    
    media_dir = settings.MEDIA_ROOT
    if not os.path.isdir(media_dir):
        print(f"Media directory not found: {media_dir}")
        return

    print(f"Starting cleanup of {media_dir}...")
    current_time = time.time()

    for filename in os.listdir(media_dir):
        file_path = os.path.join(media_dir, filename)
        
        try:
            if os.path.isfile(file_path):
                file_mod_time = os.path.getmtime(file_path)
                
                if (current_time - file_mod_time) > AGE_LIMIT_SECONDS:
                    print(f"Deleting old file: {filename}")
                    os.remove(file_path)
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")

    print("Cleanup finished.")

if __name__ == "__main__":
    cleanup_old_files() 