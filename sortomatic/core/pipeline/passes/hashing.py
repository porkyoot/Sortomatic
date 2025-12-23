import hashlib
from functools import partial
from ....l8n import Strings

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

def compute_hashes(ctx: dict):
    """
    Pass 2: Computes standard and perceptual hashes.
    """
    fpath = ctx['path']
    
    # 1. Fast Hash (Size + Prefix)
    # Good for quick exclusion
    file_size = ctx['size_bytes']
    if file_size > 0:
        try:
            with open(fpath, 'rb') as f:
                prefix = f.read(1024 * 64) # First 64KB
                ctx['fast_hash'] = hashlib.md5(f"{file_size}".encode() + prefix).hexdigest()
        except:
             ctx['fast_hash'] = None
    
    # 2. Full Hash (MD5)
    # Still fast, but covers whole content
    hasher = hashlib.md5()
    try:
        with open(fpath, 'rb') as f:
            for chunk in iter(partial(f.read, 1024 * 1024), b""): # 1MB chunks
                hasher.update(chunk)
        ctx['full_hash'] = hasher.hexdigest()
    except:
        ctx['full_hash'] = None
    
    # 3. Perceptual Hash (Only for images)
    if ctx.get('category') == Strings.CAT_IMAGES and imagehash:
        try:
            with Image.open(fpath) as img:
                ctx['perceptual_hash'] = str(imagehash.average_hash(img))
        except:
            pass # Corrupt image or not supported
            
    # 4. Audio Fingerprint (Only for audio files)
    if ctx.get('category') == Strings.CAT_AUDIO and pyacoustid:
        try:
            # pyacoustid.fingerprint_file returns (duration, fingerprint)
            _, fp = pyacoustid.fingerprint_file(fpath)
            ctx['fast_hash'] = fp.decode('utf-8') if isinstance(fp, bytes) else fp
        except:
            pass # Corrupt audio or missing fpcalc
            
    return ctx