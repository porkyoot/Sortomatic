from functools import partial
from ....l8n import Strings

try:
    import xxhash
except ImportError:
    xxhash = None

try:
    import imagehash
    from PIL import Image
except ImportError:
    imagehash = None
    Image = None

try:
    import pyacoustid
except ImportError:
    pyacoustid = None

CHUNK_SIZE_4KB = 4 * 1024
CHUNK_SIZE_1MB = 1024 * 1024

def compute_hashes(ctx: dict):
    """Computes standard and perceptual hashes.
    
    Fast hash: First 4KB + Last 4KB (standard practice)
    Full hash: xxHash64 (10x faster than MD5, safe for non-crypto use)
    """
    fpath = ctx['path']
    file_size = ctx['size_bytes']
    
    # 1. Fast Hash (First 4KB + Last 4KB)
    # Near-instant. Good for initial grouping using standard practice.
    if file_size > 0 and xxhash:
        try:
            with open(fpath, 'rb') as f:
                # Read first 4KB
                first_chunk = f.read(CHUNK_SIZE_4KB)
                
                # Read last 4KB if file is large enough
                last_chunk = b''
                if file_size > CHUNK_SIZE_4KB:
                    f.seek(-min(CHUNK_SIZE_4KB, file_size - CHUNK_SIZE_4KB), 2)
                    last_chunk = f.read(CHUNK_SIZE_4KB)
                
                hasher = xxhash.xxh64()
                hasher.update(first_chunk)
                hasher.update(last_chunk)
                ctx['fast_hash'] = hasher.hexdigest()
        except Exception:
            ctx['fast_hash'] = None
    
    # 2. Perceptual Hash (Only for images)
    if ctx.get('category') == Strings.CAT_IMAGES and imagehash:
        try:
            with Image.open(fpath) as img:
                ctx['perceptual_hash'] = str(imagehash.average_hash(img))
        except Exception:
            pass
            
    # 3. Audio Fingerprint (Only for audio files)
    if ctx.get('category') == Strings.CAT_AUDIO and pyacoustid:
        try:
            _, fp = pyacoustid.fingerprint_file(fpath)
            ctx['fast_hash'] = fp.decode('utf-8') if isinstance(fp, bytes) else fp
        except Exception:
            pass
            
    # 4. Full Hash (xxHash64 - 10x faster than MD5)
    # Still fast, covers whole content. xxHash is perfect for file integrity.
    if xxhash:
        try:
            hasher = xxhash.xxh64()
            with open(fpath, 'rb') as f:
                for chunk in iter(partial(f.read, CHUNK_SIZE_1MB), b""):
                    hasher.update(chunk)
            ctx['full_hash'] = hasher.hexdigest()
        except Exception:
            ctx['full_hash'] = None
            
    return ctx