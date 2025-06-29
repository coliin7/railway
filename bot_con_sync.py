# bot_con_sync.py
# -*- coding: utf-8 -*-
import os
import json
from flask import Flask, request, jsonify
from twilio.twiml.messaging_response import MessagingResponse
from datetime import datetime

app = Flask(__name__)

DATOS_COMERCIOS = {}

# EDITAR: Agregar comercios autorizados
COMERCIOS_AUTORIZADOS = {
    "+5491169990651": "Qaja R",
    "+5491198765432": "Panaderia La Esquina"
}

@app.route('/webhook', methods=['POST'])
def webhook():
    mensaje = request.values.get('Body', '').strip()
    numero = request.values.get('From', '').replace('whatsapp:', '')
    
    resp = MessagingResponse()
    
    if numero in COMERCIOS_AUTORIZADOS:
        if numero in DATOS_COMERCIOS:
            datos = DATOS_COMERCIOS[numero]['datos']
            respuesta = generar_respuesta(numero, mensaje, datos)
        else:
            respuesta = f"Hola {COMERCIOS_AUTORIZADOS[numero]}! Esperando primera sincronizacion..."
    else:
        respuesta = "Numero no registrado. Contacta soporte."
    
    resp.message(respuesta)
    return str(resp)

def generar_respuesta(numero, mensaje, datos):
    comercio = COMERCIOS_AUTORIZADOS[numero]
    msg_lower = mensaje.lower()
    
    if 'hola' in msg_lower:
        return f"Hola {comercio}! Ultima actualizacion: {datos.get('hora', 'N/A')}"
    
    elif any(word in msg_lower for word in ['venta', 'vendi', 'hoy']):
        ventas_hoy = datos.get('ventas_hoy', 0)
        ventas_ayer = datos.get('ventas_ayer', 0)
        var = ((ventas_hoy - ventas_ayer) / ventas_ayer * 100) if ventas_ayer > 0 else 0
        
        return (f"{comercio} - Ventas de hoy:\n\n"
                f"Total: ${ventas_hoy:,.0f}\n"
                f"Variacion: {var:+.1f}% vs ayer\n"
                f"Cantidad: {datos.get('cantidad_ventas', 0)} ventas")
    
    elif 'producto' in msg_lower:
        return f"Producto mas vendido: {datos.get('producto_top', 'N/A')}"
    
    else:
        return "Preguntame: Cuanto vendi hoy? Que producto se vendio mas?"

@app.route('/api/sincronizar', methods=['POST'])
def sincronizar():
    data = request.get_json()
    comercio_id = data.get('comercio_id')
    
    if comercio_id:
        DATOS_COMERCIOS[comercio_id] = {
            'datos': data.get('datos', {}),
            'ultima_actualizacion': datetime.now().isoformat()
        }
        return jsonify({'status': 'ok'})
    
    return jsonify({'error': 'Datos invalidos'}), 400

@app.route('/')
def home():
    return "<h1>Bot WhatsApp Qaja R</h1><p>Estado: Activo</p>"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
