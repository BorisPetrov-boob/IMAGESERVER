import os
import subprocess
import datetime
import sys

from config import Config
from utils import log_info, log_error, ensure_directories, setup_logging


def create_backup():
    try:
        db_url = Config.DATABASE_URI
        db_url_parts = db_url.replace("postgresql://", "")
        parts = db_url_parts.split('@')
        
        
        user_passs = parts[0]
        host_port_db = parts[1] 
        
        user, password = user_passs.split(':') ## посстгрес юзер и пароль
        host_port, db_name = host_port_db.split('/') ## хост порт и имя базы
        host, port = host_port.split('/') ## хост и порт
        
        if ':' in host_port:
            host, port = host.split(':')
        else:
            host = host_port
            port = '5432'  ## стандартный порт постгреса
            
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_{timestamp}.sql"
        
        


        backup_path = os.path.join(Config.BACKUP_DIR, backup_filename)
        
        ## команда для создания бэкапа
        pg_dump_cmd = [     
            "pg_dump",
            "-h", host,
            "-p", port,
            "-U", user,
            "-d", db_name,
            "-f", backup_path,
        ]
        
        
        log_info(f"Starting backup to {backup_filename}...")
        
        result = subprocess.run(
            pg_dump_cmd,
            ##env={**os.environ, "PGPASSWORD": password},
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            file_size = os.path.getsize(backup_path)
            size_mb = file_size / (1024 * 1024)
            log_info(f"Backup created successfully: {backup_filename} ({size_mb:.2f} MB)")
            return True, backup_path
        else:
            log_error(f"Backup failed: {result.stderr}")
            return False, result.stderr
    except Exception as e:
        log_error(f"Exception during backup: {str(e)}")
        return False, str(e)    
    
if __name__ == "__main__":
    setup_logging()
    
    if len(sys.argv) > 1 and sys.argv[1] == "restore":
        if len(sys.argv) > 2:
            backup_file = sys.argv[2]
            log_info(f"Restoring database from backup: {backup_file}")
            # Реализация восстановления базы данных из файла бэкапа
        else:
            print("Please provide the backup file path for restoration.")   
    else:
        success, result = create_backup()
        if success:
           print(f"Backup created successfully: {result}")  
        else:
           print(f"Backup failed: {result}")
