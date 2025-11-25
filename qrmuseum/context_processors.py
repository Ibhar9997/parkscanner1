"""
Context processors para pasar datos globales a todos los templates
"""
from qrmuseum.models import MuseoConfig

def museo_global(request):
    """Agrega la configuración del museo a todos los templates"""
    try:
        museo = MuseoConfig.objects.first()
    except:
        museo = None
    
    return {
        'museo': museo
    }
