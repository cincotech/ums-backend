#!/bin/bash

# -----------------------------
# Script Backend UMS (Production)
# Cible: /var/www/ums/backend
# -----------------------------

# Variables
TARGET_DIR="/var/www/ums/backend"
# Corrigé : le venv est dans /var/www/ums/venv
VENV_PATH="/var/www/ums/venv"
LOG_FILE="$HOME/deploy_backend.log"
DATE=$(date '+%Y-%m-%d_%H-%M-%S')
EMAILS="ndabubahajanvier@gmail.com ferdinand.niragira2@gmail.com"

send_email() {
    local STATUS=$1
    local SUBJECT="Déploiement UMS Backend - $STATUS"
    {
        echo "Subject: $SUBJECT"
        echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "-----------------------------------"
        tail -n 30 "$LOG_FILE"
    } | msmtp "$EMAILS"
}

echo "-------------------------------------------------" >> "$LOG_FILE"
echo "🚀 Déploiement Backend démarré le $DATE" | tee -a "$LOG_FILE"

# 1. Accès au dossier
cd "$TARGET_DIR" || { echo "❌ Dossier $TARGET_DIR introuvable" | tee -a "$LOG_FILE"; exit 1; }

# 2. Mise à jour du code
echo "🔄 Pulling latest code..." | tee -a "$LOG_FILE"
sudo git pull origin main | tee -a "$LOG_FILE"

# 3. Activation de l'environnement virtuel et installation
echo "📦 Mise à jour dépendances Python..." | tee -a "$LOG_FILE"
# On vérifie l'existence du venv avant d'activer
if [ -f "$VENV_PATH/bin/activate" ]; then
    source "$VENV_PATH/bin/activate"
else
    echo "❌ Venv introuvable dans $VENV_PATH" | tee -a "$LOG_FILE"
    exit 1
fi

pip install -r requirements.txt | tee -a "$LOG_FILE"

# 4. Migrations et Static
echo "🗄️ Migrations et Staticfiles..." | tee -a "$LOG_FILE"
python manage.py migrate --noinput | tee -a "$LOG_FILE"
python manage.py collectstatic --noinput | tee -a "$LOG_FILE"

# 5. Droits d'accès
# On applique les droits sur le backend pour que www-data puisse écrire dans les logs ou dossiers media
sudo chown -R www-data:www-data "$TARGET_DIR"

# 6. Redémarrage du service (Django/Gunicorn)
echo "🔁 Redémarrage du service..." | tee -a "$LOG_FILE"
sudo systemctl restart django.service

if [ $? -eq 0 ]; then
    echo "✅ Succès !" | tee -a "$LOG_FILE"
    send_email "SUCCÈS"
else
    echo "❌ Erreur au redémarrage du service" | tee -a "$LOG_FILE"
    send_email "ÉCHEC (Service)"
    exit 1
fi
