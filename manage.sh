#!/bin/bash

# UMS Backend Management Script
# Comprehensive command execution for Django project

set -e

PROJECT_DIR="/home/ndikumana/Documents/Python/Django/ums-backend"
VENV_DIR="$PROJECT_DIR/venv"
PYTHON="$VENV_DIR/bin/python"
MANAGE="$PYTHON manage.py"

cd "$PROJECT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Activate virtual environment
activate_venv() {
    if [ -d "$VENV_DIR" ]; then
        source "$VENV_DIR/bin/activate"
        print_success "Virtual environment activated"
    else
        print_error "Virtual environment not found at $VENV_DIR"
        exit 1
    fi
}

# Setup commands
setup() {
    print_header "Setting up project"
    python3 -m venv venv
    activate_venv
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Setup complete"
}

# Database commands
makemigrations() {
    print_header "Creating migrations"
    $MANAGE makemigrations
    print_success "Migrations created"
}

migrate() {
    print_header "Running migrations"
    $MANAGE migrate
    print_success "Migrations applied"
}

showmigrations() {
    print_header "Showing migrations"
    $MANAGE showmigrations
}

reset_db() {
    print_header "Resetting database"
    print_warning "This will delete all data!"
    read -p "Are you sure? (yes/no): " confirm
    if [ "$confirm" = "yes" ]; then
        rm -f db.sqlite3
        find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
        find . -path "*/migrations/*.pyc" -delete
        $MANAGE makemigrations
        $MANAGE migrate
        print_success "Database reset complete"
    else
        print_warning "Database reset cancelled"
    fi
}

# Server commands
runserver() {
    print_header "Starting development server"
    $MANAGE runserver 0.0.0.0:8000
}

# User management
createsuperuser() {
    print_header "Creating superuser"
    $MANAGE createsuperuser
}

# Testing commands
test() {
    print_header "Running tests"
    $MANAGE test
}

test_coverage() {
    print_header "Running tests with coverage"
    coverage run --source='.' manage.py test
    coverage report
    coverage html
    print_success "Coverage report generated in htmlcov/"
}

# Static files
collectstatic() {
    print_header "Collecting static files"
    $MANAGE collectstatic --noinput
    print_success "Static files collected"
}

# Shell commands
shell() {
    print_header "Opening Django shell"
    $MANAGE shell
}

shell_plus() {
    print_header "Opening Django shell_plus"
    $MANAGE shell_plus
}

# Database inspection
dbshell() {
    print_header "Opening database shell"
    $MANAGE dbshell
}

# Check commands
check() {
    print_header "Running system checks"
    $MANAGE check
    print_success "System check passed"
}

check_deploy() {
    print_header "Running deployment checks"
    $MANAGE check --deploy
}

# Code quality
lint() {
    print_header "Running linters"
    if command -v flake8 &> /dev/null; then
        flake8 . --exclude=venv,migrations --max-line-length=120
        print_success "Linting complete"
    else
        print_warning "flake8 not installed"
    fi
}

format() {
    print_header "Formatting code"
    if command -v black &> /dev/null; then
        black . --exclude=venv
        print_success "Code formatted"
    else
        print_warning "black not installed"
    fi
}

# Cleanup commands
clean() {
    print_header "Cleaning project"
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete
    find . -type f -name ".DS_Store" -delete
    print_success "Project cleaned"
}

# Logs
logs() {
    print_header "Showing logs"
    if [ -f "logs/django.log" ]; then
        tail -f logs/django.log
    else
        print_warning "No log file found"
    fi
}

# Backup
backup() {
    print_header "Creating backup"
    BACKUP_DIR="backups"
    mkdir -p "$BACKUP_DIR"
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    
    if [ -f "db.sqlite3" ]; then
        cp db.sqlite3 "$BACKUP_DIR/db_$TIMESTAMP.sqlite3"
        print_success "Database backed up to $BACKUP_DIR/db_$TIMESTAMP.sqlite3"
    fi
    
    $MANAGE dumpdata --natural-foreign --natural-primary -e contenttypes -e auth.Permission > "$BACKUP_DIR/data_$TIMESTAMP.json"
    print_success "Data backed up to $BACKUP_DIR/data_$TIMESTAMP.json"
}

# Restore
restore() {
    print_header "Restoring from backup"
    if [ -z "$1" ]; then
        print_error "Usage: ./manage.sh restore <backup_file.json>"
        exit 1
    fi
    $MANAGE loaddata "$1"
    print_success "Data restored from $1"
}

# Custom management commands


# University structure
setup_university() {
    print_header "Setting up university structure"
    $MANAGE setup_university_structure
    print_success "University structure created"
}

# Geo data
refresh_geo() {
    print_header "Refreshing geo data"
    $MANAGE refresh_geo_data
    print_success "Geo data refreshed"
}

# Backup universities
backup_universities() {
    print_header "Backing up universities"
    $MANAGE backup_universities
    print_success "Universities backed up"
}

# Seed commands
seed_roles() {
    print_header "Seeding roles"
    $MANAGE seed_roles
    print_success "Roles seeded"
}

seed_professions() {
    print_header "Seeding professions"
    $MANAGE seed_professions
    print_success "Professions seeded"
}

seed_document_requirements() {
    print_header "Seeding document requirements"
    $MANAGE seed_document_requirements
    print_success "Document requirements seeded"
}

# Create data
create_upg_data() {
    print_header "Creating UPG data"
    $MANAGE create_upg_data
    print_success "UPG data created"
}

create_rooms() {
    print_header "Creating rooms"
    $MANAGE create_rooms
    print_success "Rooms created"
}

create_schedule_slots() {
    print_header "Creating schedule slots"
    $MANAGE create_schedule_slots
    print_success "Schedule slots created"
}

create_fake_students() {
    print_header "Creating fake students"
    $MANAGE create_fake_students "$2"
    print_success "Fake students created"
}


# API schema
generate_schema() {
    print_header "Generating API schema"
    $MANAGE spectacular --color --file schema.yml
    print_success "Schema generated: schema.yml"
}

# Token management
flush_tokens() {
    print_header "Flushing expired tokens"
    $MANAGE flushexpiredtokens
    print_success "Expired tokens flushed"
}

# Sessions
clear_sessions() {
    print_header "Clearing expired sessions"
    $MANAGE clearsessions
    print_success "Expired sessions cleared"
}



# Full initialization
init_all() {
    print_header "Full initialization"
    activate_venv
    $MANAGE migrate
    $MANAGE seed_roles
    $MANAGE seed_professions
    $MANAGE seed_document_requirements
    $MANAGE refresh_geo_data
    $MANAGE create_schedule_slots
    print_success "Full initialization complete"
}

# Full deployment
deploy() {
    print_header "Running full deployment"
    activate_venv
    git pull
    pip install -r requirements.txt
    $MANAGE makemigrations
    $MANAGE migrate
    $MANAGE collectstatic --noinput
    $MANAGE check --deploy
    print_success "Deployment complete"
}

# Show help
show_help() {
    cat << EOF
UMS Backend Management Script

Usage: ./manage.sh [command] [args]

${BLUE}Setup Commands:${NC}
  setup                      - Initial project setup
  init_all                   - Full initialization (migrate + seed all data)
  
${BLUE}Database Commands:${NC}
  makemigrations             - Create new migrations
  migrate                    - Apply migrations
  showmigrations             - Show migration status
  reset_db                   - Reset database (WARNING: deletes all data)
  reset_db_ext               - Reset database (django-extensions)
  
${BLUE}Server Commands:${NC}
  runserver                  - Start development server
  
${BLUE}User Management:${NC}
  createsuperuser            - Create superuser account
  changepassword <username>  - Change user password
  
${BLUE}Testing:${NC}
  test                       - Run tests
  test_coverage              - Run tests with coverage report
  
${BLUE}Static Files:${NC}
  collectstatic              - Collect static files
  
${BLUE}Shell:${NC}
  shell                      - Open Django shell
  shell_plus                 - Open Django shell_plus (enhanced)
  dbshell                    - Open database shell
  
${BLUE}Checks:${NC}
  check                      - Run system checks
  check_deploy               - Run deployment checks
  
${BLUE}Data Seeding:${NC}
  seed_roles                 - Seed user roles
  seed_professions           - Seed parent professions
  seed_document_requirements - Seed document requirements for roles
  refresh_geo                - Refresh geographical data
  
${BLUE}University Setup:${NC}
  setup_university           - Setup university structure
  create_upg_data            - Create UPG specific data
  backup_universities        - Backup all universities
  
${BLUE}Infrastructure:${NC}
  create_rooms               - Create room data
  create_schedule_slots      - Create schedule time slots
  
${BLUE}Test Data:${NC}
  create_fake_students [n]   - Create n fake students
  
${BLUE}Django Extensions:${NC}
  show_urls                  - Show all URL patterns
  show_models                - Show all models info
  graph_models               - Generate model relationship diagram
  clean_pyc                  - Clean .pyc files
  
${BLUE}Maintenance:${NC}
  flush_tokens               - Flush expired JWT tokens
  clear_sessions             - Clear expired sessions
  clean_history              - Clean old history records
  clean                      - Clean __pycache__ and .pyc files
  
${BLUE}Code Quality:${NC}
  lint                       - Run linters
  format                     - Format code with black
  
${BLUE}Utilities:${NC}
  logs                       - Show logs
  backup                     - Create backup
  restore <file>             - Restore from backup
  generate_schema            - Generate API schema (OpenAPI)
  
${BLUE}Deployment:${NC}
  deploy                     - Full deployment process
  
${BLUE}Help:${NC}
  help                       - Show this help message

EOF
}

# Main command handler
case "$1" in
    # Setup
    setup) setup ;;
    init_all) init_all ;;
    
    # Database
    makemigrations) activate_venv && makemigrations ;;
    migrate) activate_venv && migrate ;;
    showmigrations) activate_venv && showmigrations ;;
    reset_db) activate_venv && reset_db ;;
    reset_db_ext) activate_venv && reset_db_ext ;;
    
    # Server
    runserver) activate_venv && runserver ;;
    
    # User management
    createsuperuser) activate_venv && createsuperuser ;;
    changepassword) activate_venv && changepassword "$2" ;;
    
    # Testing
    test) activate_venv && test ;;
    test_coverage) activate_venv && test_coverage ;;
    
    # Static files
    collectstatic) activate_venv && collectstatic ;;
    
    # Shell
    shell) activate_venv && shell ;;
    shell_plus) activate_venv && shell_plus ;;
    dbshell) activate_venv && dbshell ;;
    
    # Checks
    check) activate_venv && check ;;
    check_deploy) activate_venv && check_deploy ;;
    
    # Seeding
    seed_roles) activate_venv && seed_roles ;;
    seed_professions) activate_venv && seed_professions ;;
    seed_document_requirements) activate_venv && seed_document_requirements ;;
    refresh_geo) activate_venv && refresh_geo ;;
    
    # University
    setup_university) activate_venv && setup_university ;;
    create_upg_data) activate_venv && create_upg_data ;;
    backup_universities) activate_venv && backup_universities ;;
    
    # Infrastructure
    create_rooms) activate_venv && create_rooms ;;
    create_schedule_slots) activate_venv && create_schedule_slots ;;
    
    # Test data
    create_fake_students) activate_venv && create_fake_students "$2" ;;
    
    # Django extensions
    show_urls) activate_venv && show_urls ;;
    show_models) activate_venv && show_models ;;
    graph_models) activate_venv && graph_models ;;
    clean_pyc) activate_venv && clean_pyc ;;
    
    # Maintenance
    flush_tokens) activate_venv && flush_tokens ;;
    clear_sessions) activate_venv && clear_sessions ;;
    clean_history) activate_venv && clean_history ;;
    clean) clean ;;
    
    # Code quality
    lint) activate_venv && lint ;;
    format) activate_venv && format ;;
    
    # Utilities
    logs) logs ;;
    backup) activate_venv && backup ;;
    restore) activate_venv && restore "$2" ;;
    generate_schema) activate_venv && generate_schema ;;
    
    # Deployment
    deploy) deploy ;;
    
    # Help
    help|--help|-h) show_help ;;
    
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac
