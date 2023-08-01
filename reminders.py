from plyer import notification
import json
import os
import pytz
from datetime import datetime, date
import sys
import sched
import time
import emoji

scheduler = sched.scheduler(time.time, time.sleep)
max_notifications = 5

def save_reminder(timezone:str, date:str, message:str) -> bool:
    # Create reminders file if it doesn't exist
    if not os.path.exists('reminders.json'):
        with open('reminders.json', 'w') as file:
            json.dump({'reminders':[]}, file)

    # Read reminders file
    with open('reminders.json', 'r') as file:
        reminders = json.load(file)

    # Modify reminders
    reminders['reminders'].append({'timezone': timezone, 'day': date, 'message': message})

    # Save reminders
    with open('reminders.json', 'w') as file:
        json.dump(reminders, file)

    return True

def check_reminders():
    with open('reminders.json', 'r') as file:
        reminders = json.load(file)

    while True:
        for reminder in reminders['reminders']:
            actual_date = datetime.now().strftime('%d/%m/%Y %H:%M')

            if reminder.get('timezone'):
                try:
                    timezone = pytz.timezone(reminder['timezone'])
                except pytz.UnknownTimeZoneError:
                    print(f"Zona horaria desconocida: {reminder['timezone']}")
                    continue

                actual_date = datetime.now(timezone).strftime('%d/%m/%Y %H:%M')

            if reminder['day'] == actual_date:
                yield reminder['message']

def show_notification(msg):
      global max_notifications  # Declarar la variable max_notifications como global
      if max_notifications > 0:
        msg_with_emojis = emoji.emojize(msg)
        notification.notify(title='TE DICE:', message=msg_with_emojis)
        max_notifications -= 1

    # Decrementamos el contador de notificaciones
      max_notifications -= 1
      return max_notifications


def check_and_show_reminders(max_notifications):
    reminders = check_reminders()
    for msg in reminders:
        max_notifications = show_notification(msg, max_notifications)

    if max_notifications > 0:
        # Programamos la siguiente ejecución de check_and_show_reminders()
        scheduler.enter(60, 1, check_and_show_reminders, (max_notifications,))

def main():
    max_notifications = 5  # Puedes ajustar este valor a la cantidad deseada
    if len(sys.argv) > 1:
        mensaje = " ".join(sys.argv[1:])
        mensaje = emoji.emojize(mensaje, use_aliases=True)
        save_reminder('', '', mensaje)
        print('Tu recordatorio se ha guardado correctamente :) \n')
    else:
        print('Hola, ingrese la zona horaria y la fecha con el siguiente formato')
        print('Zona horaria: Continente/Ciudad, Fecha: dia/mes/año hora:minutos')
        print(f"Ejemplo: America/Mexico_City  -  {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

        zona_horaria = input("Ingrese la zona horaria (o déjelo en blanco para usar la local): ")
        dia_hora = input("Ingrese día y hora a acordar: ")
        while True:
            mensaje = input("Ingrese mensaje a recordar: ")
            if mensaje:
                break
            else:
                print("Por favor, ingrese un mensaje válido.")

        mensaje = emoji.emojize(mensaje)

        if save_reminder(zona_horaria, dia_hora, mensaje):
            print('Tu recordatorio se ha guardado correctamente :) \n')

    reminders = check_reminders()

    for msg in reminders:
        show_notification(msg)

    scheduler.enter(60, 1, check_and_show_reminders, (max_notifications,))

    # Iniciamos el planificador
    scheduler.run()

if __name__ == "__main__":
    main()

