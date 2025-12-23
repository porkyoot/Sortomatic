class Strings:
    # CLI Help and Prompts
    APP_HELP = "Sortomatic: The Elegant File Organizer"
    SCAN_PATH_HELP = "The folder to scan"
    SCAN_RESET_HELP = "Clear database before scanning"
    SCAN_DOC = "Index a directory into the database."
    WIPE_CONFIRM = "Are you sure you want to wipe the database?"
    WIPE_SUCCESS = "Database wiped."
    STATS_DOC = "Show insights about your files."
    STATS_TITLE = "File Distribution"
    CATEGORY_LABEL = "Category"
    COUNT_LABEL = "Count"
    USER_ABORT = "Operation cancelled by user."

    # Engine messages
    PATH_NOT_FOUND = "Path '{path}' does not exist."
    CRAWLING_MSG = "Crawling {name} to estimate size..."
    INDEXING_MSG = "Indexing {name}..."
    SCAN_COMPLETE = "✨ Scan Complete! Indexed {total_files} files."

    # Categories
    CAT_IMAGES = "Images"
    CAT_VIDEOS = "Videos"
    CAT_DOCUMENTS = "Documents"
    CAT_AUDIO = "Audio"
    CAT_ARCHIVES = "Archives"
    CAT_CODE = "Code"
    CAT_OTHERS = "Others"

    @classmethod
    def get_category_name(cls, key: str) -> str:
        mapping = {
            "Images": cls.CAT_IMAGES,
            "Videos": cls.CAT_VIDEOS,
            "Documents": cls.CAT_DOCUMENTS,
            "Audio": cls.CAT_AUDIO,
            "Archives": cls.CAT_ARCHIVES,
            "Code": cls.CAT_CODE,
            "Others": cls.CAT_OTHERS
        }
        return mapping.get(key, key)
