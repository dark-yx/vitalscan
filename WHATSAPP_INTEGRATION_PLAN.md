# Plan de Integración del Botón Flotante de WhatsApp

## Actualización del Número de Teléfono

**Número actualizado:** `+593967080644`

## 1. Comandos para Integrar api-whatsapp-ts al Repositorio Principal

```bash
# Consolidar archivos .gitignore
cat api-whatsapp-ts/.gitignore >> .gitignore
rm api-whatsapp-ts/.gitignore

# Agregar todos los archivos al repositorio
git add .

# Hacer commit
git commit -m "Integrar api-whatsapp-ts y agregar botón flotante de WhatsApp

- Consolidar archivos .gitignore
- Agregar proyecto TypeScript de WhatsApp API
- Implementar botón flotante de WhatsApp en todas las páginas
- Configurar mensaje inicial para asesoría nutricional Herbalife
- Actualizar número de contacto a +593967080644"

# Subir al repositorio remoto
git push origin main
```

## 2. Actualizar config.py

**Cambiar la línea 59:**
```python
# ANTES:
CONTACT_PHONE = os.environ.get('CONTACT_PHONE', '+1234567890')

# DESPUÉS:
CONTACT_PHONE = os.environ.get('CONTACT_PHONE', '+593967080644')
```

**Agregar al final del archivo (después de la línea 71):**
```python
# Configuración de WhatsApp
WHATSAPP_NUMBER = os.environ.get('WHATSAPP_NUMBER', '+593967080644')
WHATSAPP_MESSAGE_TEMPLATE = """¡Hola! 👋

Me interesa conocer más sobre sus servicios de asesoría nutricional y productos Herbalife.

He visto su plataforma WellTechFlow y me gustaría recibir información personalizada sobre:

🌿 Productos Herbalife disponibles
📋 Planes de nutrición personalizados  
💪 Programas de bienestar integral
📞 Consultas nutricionales

¿Podrían ayudarme con información detallada?

¡Gracias! 😊"""
```

## 3. Actualizar static/css/styles.css

**Agregar al final del archivo:**

```css
/* Botón flotante de WhatsApp */
.whatsapp-float {
    position: fixed;
    width: 60px;
    height: 60px;
    bottom: 20px;
    left: 20px;
    background-color: #25d366;
    color: #FFF;
    border-radius: 50px;
    text-align: center;
    font-size: 30px;
    box-shadow: 2px 2px 3px #999;
    z-index: 1000;
    transition: all 0.3s ease;
    cursor: pointer;
    text-decoration: none;
    display: flex;
    align-items: center;
    justify-content: center;
    animation: pulse-whatsapp 2s infinite;
}

.whatsapp-float:hover {
    background-color: #128c7e;
    color: #FFF;
    text-decoration: none;
    transform: scale(1.1);
}

.whatsapp-float i {
    margin-top: 2px;
}

@keyframes pulse-whatsapp {
    0% {
        box-shadow: 0 0 0 0 rgba(37, 211, 102, 0.7);
    }
    70% {
        box-shadow: 0 0 0 10px rgba(37, 211, 102, 0);
    }
    100% {
        box-shadow: 0 0 0 0 rgba(37, 211, 102, 0);
    }
}

/* Tooltip para el botón */
.whatsapp-float::before {
    content: "¿Necesitas asesoría nutricional?";
    position: absolute;
    right: 70px;
    top: 50%;
    transform: translateY(-50%);
    background-color: #333;
    color: white;
    padding: 8px 12px;
    border-radius: 6px;
    font-size: 14px;
    white-space: nowrap;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
    font-family: 'Poppins', sans-serif;
}

.whatsapp-float::after {
    content: "";
    position: absolute;
    right: 60px;
    top: 50%;
    transform: translateY(-50%);
    border: 6px solid transparent;
    border-left-color: #333;
    opacity: 0;
    visibility: hidden;
    transition: all 0.3s ease;
}

.whatsapp-float:hover::before,
.whatsapp-float:hover::after {
    opacity: 1;
    visibility: visible;
}

/* Responsive */
@media (max-width: 768px) {
    .whatsapp-float {
        width: 50px;
        height: 50px;
        font-size: 24px;
        bottom: 15px;
        left: 15px;
    }
    
    .whatsapp-float::before {
        content: "Asesoría nutricional";
        right: 60px;
        font-size: 12px;
        padding: 6px 10px;
    }
    
    .whatsapp-float::after {
        right: 50px;
        border-width: 5px;
    }
}
```

## 4. Crear templates/components/whatsapp_button.html

**Crear nuevo archivo:**

```html
<!-- Botón flotante de WhatsApp -->
<a href="javascript:void(0);" 
   class="whatsapp-float" 
   id="whatsapp-button"
   title="Contactar por WhatsApp">
    <i class="fab fa-whatsapp"></i>
</a>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const whatsappButton = document.getElementById('whatsapp-button');
    
    // Configuración del WhatsApp con número actualizado
    const whatsappConfig = {
        number: '+593967080644', // Número actualizado
        message: `¡Hola! 👋

Me interesa conocer más sobre sus servicios de asesoría nutricional y productos Herbalife.

He visto su plataforma WellTechFlow y me gustaría recibir información personalizada sobre:

🌿 Productos Herbalife disponibles
📋 Planes de nutrición personalizados  
💪 Programas de bienestar integral
📞 Consultas nutricionales

¿Podrían ayudarme con información detallada?

¡Gracias! 😊`
    };
    
    whatsappButton.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Crear URL de WhatsApp
        const encodedMessage = encodeURIComponent(whatsappConfig.message);
        const whatsappUrl = `https://wa.me/${whatsappConfig.number.replace(/[^0-9]/g, '')}?text=${encodedMessage}`;
        
        // Abrir en nueva pestaña
        window.open(whatsappUrl, '_blank', 'noopener,noreferrer');
        
        // Analytics opcional (si tienes Google Analytics)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'click', {
                'event_category': 'WhatsApp',
                'event_label': 'Botón Flotante',
                'value': 1
            });
        }
    });
});
</script>
```

## 5. Actualizar Plantillas HTML

### A. templates/index.html
**Agregar antes del cierre de `</body>` (línea 576):**
```html
    <!-- Botón flotante de WhatsApp -->
    {% include 'components/whatsapp_button.html' %}
    
    <!-- Bootstrap Bundle with Popper -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
```

### B. templates/processing.html
**Agregar antes del cierre de `</body>` (línea 229):**
```html
    <!-- Botón flotante de WhatsApp -->
    {% include 'components/whatsapp_button.html' %}
    
</body>
```

### C. templates/report.html
**Agregar antes del cierre de `</body>` (línea 441):**
```html
    <!-- Botón flotante de WhatsApp -->
    {% include 'components/whatsapp_button.html' %}
    
</body>
```

### D. templates/success.html
**Agregar antes del cierre de `</body>` (línea 565):**
```html
    <!-- Botón flotante de WhatsApp -->
    {% include 'components/whatsapp_button.html' %}
    
</body>
```

## 6. Actualizar archivo .env (opcional)

**Agregar estas variables:**
```env
CONTACT_PHONE=+593967080644
WHATSAPP_NUMBER=+593967080644
```

## 7. Características del Botón Implementado

✅ **Número actualizado**: `+593967080644`
✅ **Flotante**: Posición fija en la esquina inferior izquierda
✅ **Visible en todas las páginas**: Se incluye en todas las plantillas
✅ **Abre en nueva pestaña**: `target="_blank"` con `noopener,noreferrer`
✅ **Mensaje inicial personalizado**: Sobre asesoría nutricional y Herbalife
✅ **Header actualizado**: Número de contacto actualizado en todas las páginas
✅ **Responsive**: Se adapta a dispositivos móviles
✅ **Animación**: Efecto pulse para llamar la atención
✅ **Tooltip**: Muestra mensaje al hacer hover
✅ **Accesible**: Incluye atributos de accesibilidad

## 8. Orden de Implementación

1. **Actualizar config.py** con el nuevo número
2. **Crear directorio** `templates/components/` si no existe
3. **Crear archivo** `templates/components/whatsapp_button.html`
4. **Actualizar** `static/css/styles.css` con los estilos del botón
5. **Modificar todas las plantillas HTML** para incluir el componente
6. **Actualizar archivo .env** (opcional)
7. **Probar** en todas las páginas de la aplicación
8. **Hacer commit y push** al repositorio

## 9. Verificación

Después de implementar, verificar que:
- El botón aparece en todas las páginas
- El número en el header muestra `+593967080644`
- Al hacer clic en el botón se abre WhatsApp con el mensaje correcto
- El botón es responsive en dispositivos móviles
- La animación y tooltip funcionan correctamente

## 10. Personalización Futura

Para cambios futuros:
- **Cambiar número**: Modificar en `config.py` y `whatsapp_button.html`
- **Cambiar mensaje**: Modificar en `whatsapp_button.html`
- **Cambiar posición**: Modificar CSS en `styles.css`
- **Cambiar colores**: Modificar variables CSS
- **Cambiar tamaño**: Modificar `width` y `height` en CSS