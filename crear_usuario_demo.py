#!/usr/bin/env python
"""
Script para crear un usuario de prueba rápidamente
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parkscanner.settings')
django.setup()

from django.contrib.auth.models import User
from qrmuseum.models import UsuarioMuseo

def crear_usuario_demo():
    """Crear usuario de demo para pruebas"""
    
    username = "demo"
    email = "demo@museo.local"
    password = "demo123"
    first_name = "Usuario Demo"
    
    if User.objects.filter(username=username).exists():
        print(f"❌ El usuario '{username}' ya existe")
        print(f"   Contraseña: {password}")
        return
    
    print("\n" + "="*50)
    print("Creando usuario de demostración...")
    print("="*50)
    
    try:
        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name
        )
        
        # Crear perfil de museo
        usuario_museo = UsuarioMuseo.objects.create(
            usuario=user,
            apodo_juego="Explorador",
            puntos=0,
            nivel=1
        )
        
        print(f"\n✅ Usuario creado exitosamente!")
        print(f"\n📋 Credenciales:")
        print(f"   Usuario: {username}")
        print(f"   Email: {email}")
        print(f"   Contraseña: {password}")
        print(f"\n👤 Información de Perfil:")
        print(f"   Apodo: Explorador")
        print(f"   Nivel: 1")
        print(f"   Puntos: 0")
        print(f"\n🔗 Accede en: http://localhost:8000/login/")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    
    print("\n" + "="*50 + "\n")

if __name__ == '__main__':
    crear_usuario_demo()
