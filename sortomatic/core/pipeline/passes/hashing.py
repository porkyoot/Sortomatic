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
    # Near-instant. Good for initial grouping.
    file_size = ctx['size_bytes']
    if file_size > 0:
        try:
            with open(fpath, 'rb') as f:
                prefix = f.read(1024 * 64) # First 64KB
                ctx['fast_hash'] = hashlib.md5(f"{file_size}".encode() + prefix).hexdigest()
        except:
             ctx['fast_hash'] = None
    
    # 2. Perceptual Hash (Only for images) - CPU INTENSIVE
    # We do this before Full Hash to overlap CPU work with I/O from other threads
    if ctx.get('category') == Strings.CAT_IMAGES and imagehash:
        try:
            with Image.open(fpath) as img:
                ctx['perceptual_hash'] = str(imagehash.average_hash(img))
        except:
            pass # Corrupt image or not supported
            
    # 3. Audio Fingerprint (Only for audio files) - CPU INTENSIVE
    if ctx.get('category') == Strings.CAT_AUDIO and pyacoustid:
        try:
            # External process 'fpcalc' or local FFmpeg decoding happens here
            _, fp = pyacoustid.fingerprint_file(fpath)
            ctx['fast_hash'] = fp.decode('utf-8') if isinstance(fp, bytes) else fp
        except:
            pass # Corrupt audio
            
    # 4. Full Hash (MD5) - I/O INTENSIVE
    # Still fast, but covers whole content. Performed last to use remaining I/O bandwidth.
    hasher = hashlib.md5()
    try:
        with open(fpath, 'rb') as f:
            for chunk in iter(partial(f.read, 1024 * 1024), b""): # 1MB chunks
                hasher.update(chunk)
        ctx['full_hash'] = hasher.hexdigest()
    except:
        ctx['full_hash'] = None
            
    return ctx