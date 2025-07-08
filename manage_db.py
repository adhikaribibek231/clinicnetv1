#!/usr/bin/env python
"""
Database Management Utility for ClinicNet SQLite Database
Provides backup, restore, and optimization functions
"""

import os
import shutil
import sqlite3
from datetime import datetime
import argparse

def backup_database(source_path='db.sqlite3', backup_dir='backups'):
    """Create a backup of the SQLite database"""
    if not os.path.exists(source_path):
        print(f"Error: Database file {source_path} not found!")
        return False
    
    # Create backup directory if it doesn't exist
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_filename = f"clinicnet_backup_{timestamp}.sqlite3"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        # Copy the database file
        shutil.copy2(source_path, backup_path)
        print(f"✅ Database backed up successfully to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")
        return False

def restore_database(backup_path, target_path='db.sqlite3'):
    """Restore database from backup"""
    if not os.path.exists(backup_path):
        print(f"Error: Backup file {backup_path} not found!")
        return False
    
    try:
        # Create backup of current database before restore
        if os.path.exists(target_path):
            current_backup = f"{target_path}.before_restore"
            shutil.copy2(target_path, current_backup)
            print(f"Created backup of current database: {current_backup}")
        
        # Restore from backup
        shutil.copy2(backup_path, target_path)
        print(f"✅ Database restored successfully from: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Restore failed: {str(e)}")
        return False

def optimize_database(db_path='db.sqlite3'):
    """Optimize SQLite database for better performance"""
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            print("🔄 Optimizing database...")
            
            # Enable WAL mode for better concurrency
            cursor.execute('PRAGMA journal_mode=WAL;')
            print("✅ WAL mode enabled")
            
            # Optimize synchronous mode
            cursor.execute('PRAGMA synchronous=NORMAL;')
            print("✅ Synchronous mode optimized")
            
            # Increase cache size
            cursor.execute('PRAGMA cache_size=10000;')
            print("✅ Cache size increased")
            
            # Use memory for temporary storage
            cursor.execute('PRAGMA temp_store=MEMORY;')
            print("✅ Temporary storage set to memory")
            
            # Analyze tables for better query planning
            cursor.execute('ANALYZE;')
            print("✅ Database analyzed")
            
            # Vacuum to reclaim space
            cursor.execute('VACUUM;')
            print("✅ Database vacuumed")
            
            print("✅ Database optimization completed!")
            return True
            
    except Exception as e:
        print(f"❌ Optimization failed: {str(e)}")
        return False

def get_database_info(db_path='db.sqlite3'):
    """Get information about the database"""
    if not os.path.exists(db_path):
        print(f"Error: Database file {db_path} not found!")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get database size
            cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size();")
            db_size = cursor.fetchone()[0]
            
            # Get table information
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            print(f"📊 Database Information:")
            print(f"   File: {db_path}")
            print(f"   Size: {round(db_size / (1024 * 1024), 2)} MB")
            print(f"   Tables: {len(tables)}")
            print(f"   Created: {datetime.fromtimestamp(os.path.getctime(db_path))}")
            print(f"   Modified: {datetime.fromtimestamp(os.path.getmtime(db_path))}")
            
            print(f"\n📋 Tables:")
            for table in tables:
                table_name = table[0]
                cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
                count = cursor.fetchone()[0]
                print(f"   {table_name}: {count} records")
            
            return True
            
    except Exception as e:
        print(f"❌ Error getting database info: {str(e)}")
        return False

def list_backups(backup_dir='backups'):
    """List available backups"""
    if not os.path.exists(backup_dir):
        print(f"No backup directory found: {backup_dir}")
        return False
    
    backups = []
    for file in os.listdir(backup_dir):
        if file.endswith('.sqlite3') and file.startswith('clinicnet_backup_'):
            file_path = os.path.join(backup_dir, file)
            file_size = os.path.getsize(file_path)
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            backups.append((file, file_size, file_time))
    
    if not backups:
        print("No backups found!")
        return False
    
    print(f"📦 Available Backups ({len(backups)}):")
    for backup_file, size, time in sorted(backups, key=lambda x: x[2], reverse=True):
        print(f"   {backup_file}")
        print(f"     Size: {round(size / (1024 * 1024), 2)} MB")
        print(f"     Created: {time}")
        print()

def main():
    parser = argparse.ArgumentParser(description='ClinicNet Database Management Utility')
    parser.add_argument('action', choices=['backup', 'restore', 'optimize', 'info', 'list-backups'],
                       help='Action to perform')
    parser.add_argument('--source', default='db.sqlite3', help='Source database file')
    parser.add_argument('--backup-dir', default='backups', help='Backup directory')
    parser.add_argument('--backup-file', help='Backup file for restore (required for restore action)')
    
    args = parser.parse_args()
    
    if args.action == 'backup':
        backup_database(args.source, args.backup_dir)
    elif args.action == 'restore':
        if not args.backup_file:
            print("Error: --backup-file is required for restore action")
            return
        restore_database(args.backup_file, args.source)
    elif args.action == 'optimize':
        optimize_database(args.source)
    elif args.action == 'info':
        get_database_info(args.source)
    elif args.action == 'list-backups':
        list_backups(args.backup_dir)

if __name__ == '__main__':
    main() 